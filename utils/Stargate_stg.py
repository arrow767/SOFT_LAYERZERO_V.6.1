from utils.wallet import Wallet
from loguru import logger
from web3 import Web3
import json as js
from utils.retry_bridge import exception_handler
from utils.func import lz_id_chain


address_stargate = {
    'Arbitrum': Web3.to_checksum_address('0x6694340fc020c5e6b96567843da2df01b2ce1eb6'),
    'Optimism': Web3.to_checksum_address('0x296F55F8Fb28E498B858d0BcDA06D955B2Cb3f97'),
    'Polygon': Web3.to_checksum_address('0x2f6f07cdcf3588944bf4c42ac74ff24bf56e7590'),
    'BSC': Web3.to_checksum_address('0xb0d502e938ed5f4df2e681fe6e419ff29631d62b'),
    'Avax': Web3.to_checksum_address('0x2f6f07cdcf3588944bf4c42ac74ff24bf56e7590'),
    'Fantom': Web3.to_checksum_address('0x2F6F07CDcf3588944Bf4C42aC74ff24bF56e7590'),
    'Base': Web3.to_checksum_address('0xE3B53AF74a4BF62Ae5511055290838050bf764Df'),
    'Linea': Web3.to_checksum_address('0x808d7c71ad2ba3FA531b068a2417C63106BC0949'),
    'Kava': Web3.to_checksum_address('0x83c30eb8bc9ad7c56532895840039e62659896ea')
}


class StrargateSTG(Wallet):

    def __init__(self, private_key, chain_from, chain_to, number):
        super().__init__(private_key, chain_from, number)
        self.abi = js.load(open('./abi/stargate/stg.txt'))
        self.chain_to = chain_to

    def get_fees(self):
        stargate_contract = self.web3.eth.contract(address=address_stargate[self.chain], abi=self.abi)
        tx_param = '0x00010000000000000000000000000000000000000000000000000000000000014c08'
        return stargate_contract.functions.estimateSendTokensFee(lz_id_chain[self.chain_to], True, tx_param).call()[0]

    @exception_handler
    def start_bridge(self):
        logger.info(f'Stargate bridge STG || {self.chain} -> {self.chain_to}')

        stargate_contract = self.web3.eth.contract(address=address_stargate[self.chain], abi=self.abi)

        token_balance = stargate_contract.functions.balanceOf(self.address_wallet).call()
        balance = self.get_native_balance()

        fees = self.get_fees()
        self.check_gas_cost()

        if int(fees * 1.3) > int(balance):
            raise ValueError('balance')

        dick = {
            'from': self.address_wallet,
            'value': int(fees * 1.2),
            'nonce': self.web3.eth.get_transaction_count(self.address_wallet),
            ** self.get_gas_price()
        }

        zero_param = '0x0000000000000000000000000000000000000000'
        tx_param = '0x00010000000000000000000000000000000000000000000000000000000000014c08'
        swap_txn = stargate_contract.functions.sendTokens(lz_id_chain[self.chain_to],
                                                          self.address_wallet,
                                                          token_balance,
                                                          zero_param,
                                                          tx_param).build_transaction(dick)

        tx_hash = self.send_transaction_and_wait(swap_txn, f'Stargate bridge STG || {self.chain} -> {self.chain_to}')

        self.check_transaction_stargate(tx_hash.hex())
