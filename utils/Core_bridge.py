from utils.wallet import Wallet
from loguru import logger
from web3 import Web3
import json as js
from utils.func import sleeping
from utils.retry_bridge import exception_handler
import random
from settings import TIME_DELAY


def split_into_parts(number, num_parts):
    if num_parts <= 0:
        return number

    # Generate random split points
    split_points = sorted(random.sample(range(1, number), num_parts - 1))

    # Add the start and end points
    split_points = [0] + split_points + [number]

    # Calculate the parts
    parts = [split_points[i + 1] - split_points[i] for i in range(num_parts)]

    return parts


class CoreBridge(Wallet):

    def __init__(self, private_key, chain, number):
        super().__init__(private_key, chain, number)
        self.address_deposit = Web3.to_checksum_address('0x52e75D318cFB31f9A2EdFa2DFee26B161255B233')
        self.address_withdrawl = Web3.to_checksum_address('0xA4218e1F39DA4AaDaC971066458Db56e901bcbdE')

        self.abi_deposit = js.load(open('./abi/core/core_deposit.txt'))
        self.abi_withdrawl = js.load(open('./abi/core/core_withdrawl.txt'))

        self.contract_deposit = self.web3.eth.contract(address=self.address_deposit, abi=self.abi_deposit)
        self.contract_withdrawl = self.web3.eth.contract(address=self.address_withdrawl, abi=self.abi_withdrawl)

    def get_fees_deposit(self):
        return self.contract_deposit.functions.estimateBridgeFee(True, '0x').call()[0]

    def get_fees_withdrawl(self):
        return self.contract_withdrawl.functions.estimateBridgeFee(109, True, '0x').call()[0]

    @exception_handler
    def deposit(self, value=None):
        logger.info(f'CORE bridge USDC || Polygon -> CORE')

        balance_usdc = self.get_balance_token('USDC')
        if value is None:
            value = balance_usdc
        else:
            if value > balance_usdc:
                value = balance_usdc

        if value == 0:
            logger.error('Balance USDC - 0')
            return False

        allowance = self.get_allowance_token('USDC', self.address_deposit)
        if allowance < 1000000 * 10 ** self.get_decimal_token('USDC'):
            logger.info('Need Approve')
            self.approve('USDC', self.address_deposit)
            sleeping(50, 70)

        balance = self.get_native_balance()
        fees = self.get_fees_deposit()
        self.check_gas_cost()

        if int(fees * 1.3) > int(balance):
            raise ValueError('balance')

        dick = {
            'from': self.address_wallet,
            'value': fees,
            'nonce': self.web3.eth.get_transaction_count(self.address_wallet),
            ** self.get_gas_price()
        }

        zro_payment_address = '0x0000000000000000000000000000000000000000'
        swap_txn = self.contract_deposit.functions.bridge(Web3.to_checksum_address('0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174'),
                                                          value,
                                                          self.address_wallet,
                                                          (self.address_wallet, zro_payment_address), '0x').build_transaction(dick)

        tx_hash = self.send_transaction_and_wait(swap_txn, f'CORE bridge USDC || Polygon -> CORE')

        self.check_transaction_stargate(tx_hash.hex())

    @exception_handler
    def withdrawl(self):
        logger.info(f'CORE bridge USDC || CORE -> Polygon')

        balance_usdc = self.get_balance_token('USDC')

        if balance_usdc == 0:
            logger.error('Balance USDC - 0')
            return False

        allowance = self.get_allowance_token('USDC', self.address_withdrawl)
        if allowance < 1000000 * 10 ** self.get_decimal_token('USDC'):
            logger.info('Need Approve')
            self.approve('USDC', self.address_withdrawl)
            sleeping(50, 70)

        balance = self.get_native_balance()
        fees = self.get_fees_withdrawl()
        self.check_gas_cost()

        if int(fees * 1.1) > int(balance):
            raise ValueError('balance')

        dick = {
            'from': self.address_wallet,
            'value': fees,
            'nonce': self.web3.eth.get_transaction_count(self.address_wallet),
            **self.get_gas_price()
        }

        zro_payment_address = '0x0000000000000000000000000000000000000000'
        swap_txn = self.contract_withdrawl.functions.bridge(Web3.to_checksum_address('0xa4151b2b3e269645181dccf2d426ce75fcbdeca9'),
                                                            109,
                                                            balance_usdc,
                                                            self.address_wallet,
                                                            False,
                                                            (self.address_wallet, zro_payment_address), '0x').build_transaction(dick)

        tx_hash = self.send_transaction_and_wait(swap_txn, f'CORE bridge USDC || CORE -> Polygon')

        self.check_transaction_stargate(tx_hash.hex())

    @exception_handler
    def multiple_deposit(self, num_trans):

        balance_usdc = self.get_balance_token('USDC')

        for value in split_into_parts(balance_usdc, num_trans):
            self.deposit(value)
            sleeping(TIME_DELAY[0], TIME_DELAY[1])
