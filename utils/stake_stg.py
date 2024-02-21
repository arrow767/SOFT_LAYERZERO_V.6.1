from utils.wallet import Wallet
from loguru import logger
from web3 import Web3
import json as js
from utils.retry_bridge import exception_handler
from utils.func import sleeping
import time
import random

contract_address = {
    'Arbitrum': Web3.to_checksum_address('0xfbd849e6007f9bc3cc2d6eb159c045b8dc660268'),
    'Polygon': Web3.to_checksum_address('0x3ab2da31bbd886a7edf68a6b60d3cde657d3a15d'),
    'BSC': Web3.to_checksum_address('0xd4888870c8686c748232719051b677791dbda26d'),
    'Avax': Web3.to_checksum_address('0xca0f57d295bbce554da2c07b005b7d6565a58fce'),
}


class StakeSTG(Wallet):

    def __init__(self, private_key, chain, number):
        super().__init__(private_key, chain, number)
        self.abi = js.load(open('./abi/stargate/stake_stg.txt'))
        self.contract = self.web3.eth.contract(address=contract_address[self.chain], abi=self.abi)

    @exception_handler
    def stake(self):

        balance_stg = self.get_balance_token('STG')
        if balance_stg == 0:
            logger.error('Balance STG - 0\n')
            return False

        allowance = self.get_allowance_token('STG', contract_address[self.chain])
        if allowance < 100000 * 10 ** self.get_decimal_token("STG"):
            logger.info('Need Approve')
            self.approve('STG', contract_address[self.chain])
            sleeping(50, 70)

        month = 2592000
        result = time.localtime()
        year = result.tm_year
        mon = result.tm_mon
        day = result.tm_mday
        t = (year, mon, day, 3, 0, 0, 0, 0, 0)
        now_time = time.mktime(t)

        dick = {
            'from': self.address_wallet,
            'nonce': self.web3.eth.get_transaction_count(self.address_wallet),
            ** self.get_gas_price()
        }

        check_stake = self.contract.functions.locked(self.address_wallet).call()
        if check_stake[0] == 0:
            rand = random.randint(6, 36)
            time_lock = int(now_time + rand * month)
            contract_txn = self.contract.functions.create_lock(balance_stg, time_lock).build_transaction(dick)
        else:
            contract_txn = self.contract.functions.increase_amount(balance_stg).build_transaction(dick)

        self.send_transaction_and_wait(contract_txn, f'Stake {round(Web3.from_wei(balance_stg, "ether"), 6)} STG on {self.chain}')

