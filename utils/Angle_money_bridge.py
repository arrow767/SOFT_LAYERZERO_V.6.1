from utils.wallet import Wallet
from loguru import logger
from web3 import Web3
import json as js
from utils.retry_bridge import exception_handler
from utils.func import sleeping
from utils.func import lz_id_chain


address_angle = {
    'CELO': Web3.to_checksum_address('0xf1ddcaca7d17f8030ab2eb54f2d9811365efe123'),
    'Gnosis': Web3.to_checksum_address('0xfa5ed56a203466cbbc2430a43c66b9d8723528e7'),
    'Polygon': Web3.to_checksum_address('0x0c1EBBb61374dA1a8C57cB6681bF27178360d36F'),
}


class AngleMoney(Wallet):

    def __init__(self, private_key, chain_from, chain_to, number):
        super().__init__(private_key, chain_from, number)
        self.abi = js.load(open('./abi/angle/angle.txt'))
        self.chain_to = chain_to

    def get_fees(self):
        adapter_params = '0x00010000000000000000000000000000000000000000000000000000000000030d40'
        angl_contract = self.web3.eth.contract(address=address_angle[self.chain], abi=self.abi)
        return angl_contract.functions.estimateSendFee(lz_id_chain[self.chain_to], self.address_wallet, 0, False, adapter_params).call()[0]

    @exception_handler
    def start_bridge(self):
        logger.info(f'Angle Money bridge || {self.chain} -> {self.chain_to}')

        angl_contract = self.web3.eth.contract(address=address_angle[self.chain], abi=self.abi)
        token_balance = self.get_balance_token('EUR')

        if token_balance == 0:
            logger.info('Balance EUR - 0')
            return False

        allowance = self.get_allowance_token('EUR', address_angle[self.chain])
        if allowance < 100000 * 10 ** self.get_decimal_token("EUR"):
            logger.info('Need Approve')
            self.approve('USDC', address_angle[self.chain])
            sleeping(50, 70)

        balance = self.get_native_balance()
        fees = self.get_fees()

        self.check_gas_cost()

        if int(fees * 1.3) > int(balance):
            raise ValueError('balance')

        adapter_params = '0x00010000000000000000000000000000000000000000000000000000000000030d40'
        zro_payment_address = '0x0000000000000000000000000000000000000000'

        dick = {
            'from': self.address_wallet,
            'value': fees,
            'nonce': self.web3.eth.get_transaction_count(self.address_wallet),
            **self.get_gas_price()
        }
        swap_txn = angl_contract.functions.send(lz_id_chain[self.chain_to],
                                                self.address_wallet,
                                                token_balance,
                                                self.address_wallet,
                                                zro_payment_address,
                                                adapter_params).build_transaction(dick)

        tx_hash = self.send_transaction_and_wait(swap_txn, f'Angle Money bridge || {self.chain} -> {self.chain_to}')

        self.check_transaction_stargate(tx_hash.hex())
