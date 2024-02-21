import random
from utils.wallet import Wallet
from loguru import logger
from utils.retry_refuel import exception_handler_refuel
from web3 import Web3
from settings import REFUEL_BUNGEE, REFUEL_CHAIN_LIST_BUNGEE
from utils.token_price import crypto_prices
import json as js
from utils.func import chain_id
import requests
import json


bungee_address = {
    'Arbitrum': Web3.to_checksum_address('0xc0e02aa55d10e38855e13b64a8e1387a04681a00'),
    'Avax': Web3.to_checksum_address('0x040993fbf458b95871cd2d73ee2e09f4af6d56bb'),
    'BSC': Web3.to_checksum_address('0xbe51d38547992293c89cc589105784ab60b004a9'),
    'Polygon': Web3.to_checksum_address('0xac313d7491910516e06fbfc2a0b5bb49bb072d91')
}

chain_accept = ['Arbitrum',
                'Optimism',
                'Polygon',
                'BSC',
                'Avax',
                'Base',
                'Gnosis'
                ]


def get_bungee_data():
    url = "https://refuel.socket.tech/chains"
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.text)
        return data
    else:
        return False


def get_bungee_limits(from_chain, to_chain):
    from_chain_id = chain_id[from_chain]
    to_chain_id = chain_id[to_chain]

    data = get_bungee_data()

    for i in range(len(data['result'])):
        if data['result'][i]['chainId'] == from_chain_id:
            infos = data['result'][i]['limits']

            try:

                if [x for x in infos if x['chainId'] == to_chain_id][0] and [x for x in infos if x['chainId'] == to_chain_id][0]['isEnabled'] is True:

                    info = [x for x in infos if x['chainId'] == to_chain_id][0]
                    return int(info['minAmount']), int(info['maxAmount'])
                else:
                    logger.error(f'Refuel из {from_chain} в {to_chain} невозможен\n')
                    return False

            except Exception as error:
                logger.error(error)


class RefuelBungee(Wallet):

    def __init__(self, private_key, number):
        self.private_key = private_key
        super().__init__(private_key, self.get_refuel_chain(), number)
        self.abi = js.load(open('./abi/bungee/bungee.txt'))

    @exception_handler_refuel
    def get_refuel_chain(self):

        balance_chain = 0
        chan = None

        for chain in REFUEL_CHAIN_LIST_BUNGEE:
            web3 = self.get_web3(chain)
            address_wallet = web3.eth.account.from_key(self.private_key).address
            balance = web3.eth.get_balance(address_wallet)
            if chain == 'BSC':
                value = float(Web3.from_wei(balance, "ether")) / (1/crypto_prices['binancecoin'])
            elif chain == 'Avax':
                value = float(Web3.from_wei(balance, "ether")) / (1/crypto_prices['avalanche-2'])
            elif chain == 'Arbitrum' or chain == 'Optimism':
                value = float(Web3.from_wei(balance, "ether")) / (1/crypto_prices['ethereum'])
            else:
                value = float(Web3.from_wei(balance, "ether")) / (1/crypto_prices['wmatic'])

            logger.info(f'Баланс в {chain} - {Web3.from_wei(balance, "ether")}')

            if balance_chain > value:
                continue
            else:
                balance_chain = value
                chan = chain

        logger.success(f'Cеть для рефуела - {chan}\n')
        return chan

    @exception_handler_refuel
    def refuel(self, chain_to):

        if chain_to not in chain_accept:
            return False

        if self.web3.eth.chain_id == chain_id[chain_to]:
            logger.error('ChainId refuel from == ChainId refuel to')
            raise ValueError('balance refuel')

        limits = get_bungee_limits(self.chain, chain_to)

        contract = self.web3.eth.contract(address=bungee_address[self.chain], abi=self.abi)

        rand = round(random.uniform(REFUEL_BUNGEE[self.chain]['token min'], REFUEL_BUNGEE[self.chain]['token max']), 5)
        value = Web3.to_wei(REFUEL_BUNGEE[self.chain]['min value'] + rand, "ether")

        if value < limits[0]:
            value = limits[0]

        balance = self.get_native_balance()

        if balance < value:
            logger.error('У вас нехватает нативных токенов для рефуела')
            logger.error(f'Bakance - {Web3.from_wei(balance, "ether")}')
            logger.error(f'Amount {Web3.from_wei(value, "ether")} but bungee_limits : {Web3.from_wei(limits[0], "ether")} - {Web3.from_wei(limits[1], "ether")}\n')
            raise ValueError('balance refuel')

        self.check_gas_cost()

        dick = {
            'from': self.address_wallet,
            'value': value,
            'nonce': self.web3.eth.get_transaction_count(self.address_wallet),
            **self.get_gas_price()
        }

        contract_txn = contract.functions.depositNativeToken(chain_id[chain_to], self.address_wallet).build_transaction(dick)

        tx_hash = self.send_transaction_and_wait(contract_txn, f'Refuel Bungee {Web3.from_wei(value, "ether")} || {self.chain} -> {chain_to}')

        self.check_transaction_refuel_bungee(tx_hash.hex())
