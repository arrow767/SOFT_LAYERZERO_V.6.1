from utils.wallet import Wallet
from loguru import logger
from web3 import Web3
import json as js
from utils.retry_bridge import exception_handler
from utils.func import lz_id_chain
from utils.func import sleeping
from settings import SLIPPAGE_STARGATE


class BitcoinBridge(Wallet):

    def __init__(self, private_key, chain_from, chain_to, number):
        super().__init__(private_key, chain_from, number)
        self.abi = js.load(open('./abi/Bitcoin/bitcoin.txt'))
        self.chain_to = chain_to
        self.address = Web3.to_checksum_address('0x2297aebd383787a160dd0d9f71508148769342e3')

    def get_fees(self):
        bitcoin_contract = self.web3.eth.contract(address=self.address, abi=self.abi)
        to_address = '0x000000000000000000000000' + self.address_wallet[2:]
        if self.chain_to == 'Arbitrum':
            adapter_params = '0x000200000000000000000000000000000000000000000000000000000000002dc6c000000000000000000000000000000000000000000000000000000000000000000000' + self.address_wallet[2:]
        else:
            adapter_params = '0x0002000000000000000000000000000000000000000000000000000000000003d0900000000000000000000000000000000000000000000000000000000000000000' + self.address_wallet[2:]
        return bitcoin_contract.functions.estimateSendFee(lz_id_chain[self.chain_to], to_address, 100000, False, adapter_params).call()[0]

    @exception_handler
    def start_bridge(self):
        logger.info(f'Bitcoin bridge || {self.chain} -> {self.chain_to}\n')

        bitcoin_contract = self.web3.eth.contract(address=self.address, abi=self.abi)

        if self.chain_to == 'Arbitrum':
            adapter_params = '0x000200000000000000000000000000000000000000000000000000000000002dc6c000000000000000000000000000000000000000000000000000000000000000000000' + self.address_wallet[2:]
        else:
            adapter_params = '0x0002000000000000000000000000000000000000000000000000000000000003d0900000000000000000000000000000000000000000000000000000000000000000' + self.address_wallet[2:]

        if self.chain == 'Avax':
            amount_in = self.get_balance_token('BTC')
            allowance = self.get_allowance_token('BTC', self.address)
            if allowance < 100000 * 10 ** self.get_decimal_token("BTC"):
                logger.info('Need Approve')
                self.approve('BTC', self.address)
                sleeping(50, 70)

        else:
            amount_in = bitcoin_contract.functions.balanceOf(self.address_wallet).call()

        amount_out_min = int(amount_in - (amount_in * SLIPPAGE_STARGATE // 100))

        zro_payment_address = '0x0000000000000000000000000000000000000000'
        call_params = (self.address_wallet, zro_payment_address, adapter_params)
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
        to_address = '0x000000000000000000000000' + self.address_wallet[2:]

        swap_txn = bitcoin_contract.functions.sendFrom(self.address_wallet,
                                                       lz_id_chain[self.chain_to],
                                                       to_address,
                                                       amount_in,
                                                       amount_out_min,
                                                       call_params).build_transaction(dick)

        tx_hash = self.send_transaction_and_wait(swap_txn, f'Bitcoin bridge || {self.chain} -> {self.chain_to}')

        self.check_transaction_stargate(tx_hash.hex())
