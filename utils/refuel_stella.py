import random
from utils.wallet import Wallet
from loguru import logger
from utils.retry_refuel import exception_handler_refuel
from web3 import Web3
from settings import REFUEL_BUNGEE, REFUEL_CHAIN_LIST_STELLA
from utils.token_price import crypto_prices
from utils.func import chain_id

chain_accept = [
    'Arbitrum',
    'Optimism',
    'Polygon',
    'BSC',
    'Avax',
    'Base',
    'CELO',
    'Fantom',
    'Kava',
    'Linea'
]


class RefuelStella(Wallet):

    def __init__(self, private_key, number):
        self.private_key = private_key
        super().__init__(private_key, self.get_refuel_chain(), number)

    @exception_handler_refuel
    def get_refuel_chain(self):

        balance_chain = 0
        chan = None

        for chain in REFUEL_CHAIN_LIST_STELLA:
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

        from_token = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
        if chain_id[chain_to] == 42220:
            to_token = '0x471ece3750da237f93b8e339c536989b8978a438'  # celo native token
        else:
            to_token = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'

        if self.web3.eth.chain_id == chain_id[chain_to]:
            logger.error('ChainId refuel from == ChainId refuel to')
            raise ValueError('balance refuel')

        rand = round(random.uniform(REFUEL_BUNGEE[self.chain]['token min'], REFUEL_BUNGEE[self.chain]['token max']), 5)
        value = Web3.to_wei(REFUEL_BUNGEE[self.chain]['min value'] + rand, "ether")
        url = f'https://api.0xsquid.com/v1/route?fromChain={chain_id[self.chain]}&fromToken={from_token}&fromAmount={value}&toChain={chain_id[chain_to]}&toToken={to_token}&toAddress={self.address_wallet}&quoteOnly=false&slippage=0.5&enableExpress=true'
        data = self.get_api_call_data(url)
        value = int(data['route']['transactionRequest']['value'])

        balance = self.get_native_balance()

        if balance < value:
            logger.error('У вас нехватает нативных токенов для рефуела')
            raise ValueError('balance refuel')

        dick = {
            'chainId': self.web3.eth.chain_id,
            'from': self.address_wallet,
            'to': data['route']['transactionRequest']['targetAddress'],
            'data': data['route']['transactionRequest']['data'],
            'value': value,
            'nonce': self.web3.eth.get_transaction_count(self.address_wallet),
            **self.get_gas_price()
        }

        gas = self.web3.eth.estimate_gas(dick)
        dick.update({'gas': int(gas * 2)})

        tx_hash = self.send_transaction_and_wait(dick, f'Refuel {Web3.from_wei(value, "ether")} || {self.chain} -> {chain_to}')

        self.check_transaction_refuel_stella(tx_hash.hex())
