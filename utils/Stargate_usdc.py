from utils.wallet import Wallet
from loguru import logger
from web3 import Web3
import json as js
from utils.func import sleeping
from settings import SLIPPAGE_STARGATE
from utils.retry_bridge import exception_handler
from utils.func import lz_id_chain


address_stargate = {
    'Arbitrum': Web3.to_checksum_address('0x53bf833a5d6c4dda888f69c22c88c9f356a41614'),
    'Optimism': Web3.to_checksum_address('0xb0d502e938ed5f4df2e681fe6e419ff29631d62b'),
    'Polygon': Web3.to_checksum_address('0x45A01E4e04F14f7A4a6702c74187c5F6222033cd'),
    'BSC': Web3.to_checksum_address('0x4a364f8c717cAAD9A442737Eb7b8A55cc6cf18D8'),
    'Avax': Web3.to_checksum_address('0x45a01e4e04f14f7a4a6702c74187c5f6222033cd'),
    'Fantom': Web3.to_checksum_address('0xAf5191B0De278C7286d6C7CC6ab6BB8A73bA2Cd6'),
    'Base': Web3.to_checksum_address('0x45f1a95a4d3f3836523f5c83673c797f4d4d263b')
}

pool_id = {
    'Arbitrum': 1,
    'Optimism': 1,
    'Polygon': 1,
    'BSC': 2,
    'Avax': 1,
    'Fantom': 21,
    'Base': 1
}


class StrargateUSDC(Wallet):

    def __init__(self, private_key, chain_from, chain_to, number):
        super().__init__(private_key, chain_from, number)
        self.abi = js.load(open('./abi/stargate/stargate.txt'))
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
        logger.info(f'Stargate bridge USDC || {self.chain} -> {self.chain_to}')

        if self.chain == 'Fantom' and self.chain_to == 'Base':
            return 'error'
        if self.chain == 'Base' and self.chain_to == 'Fantom':
            return 'error'

        stargate_contract = self.web3.eth.contract(address=address_stargate[self.chain], abi=self.abi)
        allowance = self.get_allowance_token('USDC', address_stargate[self.chain])
        if allowance < 100000 * 10 ** self.get_decimal_token("USDC"):
            logger.info('Need Approve')
            self.approve('USDC', address_stargate[self.chain])
            sleeping(50, 70)

        token_balance = self.get_balance_token('USDC')
        amount_out_min = int(token_balance - (token_balance * SLIPPAGE_STARGATE // 100))
        lz_tx_obj = [0, 0, '0x0000000000000000000000000000000000000001']

        balance = self.get_native_balance()
        fees = self.get_fees()
        self.check_gas_cost()

        if int(fees * 1.3) > int(balance):
            raise ValueError('balance')

        dick = {
            'from': self.address_wallet,
            'value': fees,
            'nonce': self.web3.eth.get_transaction_count(self.address_wallet),
            ** self.get_gas_price()
        }

        swap_txn = stargate_contract.functions.swap(lz_id_chain[self.chain_to],
                                                    pool_id[self.chain],
                                                    pool_id[self.chain_to],
                                                    self.address_wallet,
                                                    token_balance,
                                                    amount_out_min,
                                                    lz_tx_obj, self.address_wallet, '0x').build_transaction(dick)

        tx_hash = self.send_transaction_and_wait(swap_txn, f'Stargate bridge USDC || {self.chain} -> {self.chain_to}')

        self.check_transaction_stargate(tx_hash.hex())
