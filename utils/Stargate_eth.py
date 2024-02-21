from utils.wallet import Wallet
from loguru import logger
from web3 import Web3
import json as js
from settings import SLIPPAGE_STARGATE
from utils.retry_bridge import exception_handler
from utils.func import lz_id_chain

address_stargate = {
    'Arbitrum': Web3.to_checksum_address('0x53bf833a5d6c4dda888f69c22c88c9f356a41614'),
    'Optimism': Web3.to_checksum_address('0xb0d502e938ed5f4df2e681fe6e419ff29631d62b'),
    'Base': Web3.to_checksum_address('0x45f1a95a4d3f3836523f5c83673c797f4d4d263b'),
    'Linea': Web3.to_checksum_address('0x2F6F07CDcf3588944Bf4C42aC74ff24bF56e7590')
}

address_stargate_eth = {
    'Arbitrum': Web3.to_checksum_address('0xbf22f0f184bCcbeA268dF387a49fF5238dD23E40'),
    'Optimism': Web3.to_checksum_address('0xB49c4e680174E331CB0A7fF3Ab58afC9738d5F8b'),
    'Base': Web3.to_checksum_address('0x50B6EbC2103BFEc165949CC946d739d5650d7ae4'),
    'Linea': Web3.to_checksum_address('0x8731d54E9D02c286767d56ac03e8037C07e01e98')
}

gas_chain = {
    'Arbitrum': 3_000_000,
    'Optimism': 2_000_000,
    'Base': 1_000_000,
    'Linea': 1_000_000
}


class StrargateETH(Wallet):

    def __init__(self, private_key, chain_from, chain_to, number):
        super().__init__(private_key, chain_from, number)
        self.abi = js.load(open('./abi/stargate/stargate.txt'))
        self.abi_eth = js.load(open('./abi/stargate/stargate_eth.txt'))
        self.chain_to = chain_to

    def get_fees(self):
        stargate_contract = self.web3.eth.contract(address=address_stargate[self.chain], abi=self.abi)
        return stargate_contract.functions.quoteLayerZeroFee(lz_id_chain[self.chain_to], 1,
                                                             "0x0000000000000000000000000000000000000001",
                                                             "0x",
                                                             [0, 0, "0x0000000000000000000000000000000000000001"]
                                                             ).call()[0]

    @exception_handler
    def start_bridge(self):
        logger.info(f'Stargate bridge ETH || {self.chain} -> {self.chain_to}')

        stargate_contract_eth = self.web3.eth.contract(address=address_stargate_eth[self.chain], abi=self.abi_eth)
        gas = gas_chain[self.chain]
        balance = self.get_native_balance()
        fees = self.get_fees()
        gas_cost = gas * self.web3.eth.gas_price

        amount_in = balance - int(fees * 1.3) - gas_cost
        if amount_in < 0:
            logger.error(f'Balance ETH - {Web3.from_wei(balance, "ether")}')
            logger.error(f'Fees - {Web3.from_wei(fees + gas_cost, "ether")}')
            logger.error('Continuation is impossible\n')
            return

        amount_out_min = amount_in - (amount_in * SLIPPAGE_STARGATE // 100)

        dick = {
            'from': self.address_wallet,
            'value': fees + amount_in,
            'nonce': self.web3.eth.get_transaction_count(self.address_wallet),
            ** self.get_gas_price()
        }

        swap_txn = stargate_contract_eth.functions.swapETH(lz_id_chain[self.chain_to],
                                                           self.address_wallet,
                                                           self.address_wallet,
                                                           amount_in,
                                                           amount_out_min).build_transaction(dick)

        tx_hash = self.send_transaction_and_wait(swap_txn, f'Stargate bridge ETH || {self.chain} -> {self.chain_to}')

        self.check_transaction_stargate(tx_hash.hex())
