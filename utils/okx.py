import random
import time
from utils.retry_refuel import exception_handler_refuel
from utils.wallet import Wallet
import ccxt
from settings import OKX_KEYS, OKX_CHAIN_REFUEL, REFUEL_OKX
from loguru import logger

token_list = {
    'Arbitrum': 'ETH',
    'Optimism': 'ETH',
    'Base': 'ETH',
    'Polygon': 'MATIC',
    'Fantom': 'FTM',
    'BSC': 'BNB',
    'Avax': 'AVAX',
    'CORE': 'CORE',
    'Moonriver': 'MOVR',
    'CELO': 'CELO',
    'Linea': 'ETH'
}


class Okx(Wallet):

    def __init__(self, private_key, number):
        super().__init__(private_key, 'Arbitrum', number)
        self.exchange = ccxt.okx({
            'apiKey': OKX_KEYS['api_key'],
            'secret': OKX_KEYS['api_secret'],
            'password': OKX_KEYS['password'],
        })

    def token_fee(self, token, network):
        info = self.exchange.fetch_currencies()
        return info[token]['networks'][network]['fee']

    def check_withdrawl_address(self, chain, value, token=False):
        pass

    def check_status_id(self, dick_withdrawl):
        while True:
            try:
                time.sleep(10)
                res = self.exchange.fetch_withdrawal(id=dick_withdrawl['id'])
                if res['info']['state'] == '2':
                    break
            except Exception as error:
                logger.error(error)
                time.sleep(5)
                continue

    @exception_handler_refuel
    def withdrawl(self, chain, value=None, token=False):

        if chain not in OKX_CHAIN_REFUEL:
            return False

        if token is False:
            token = token_list[chain]

        if value is None:
            rand = round(random.uniform(REFUEL_OKX[chain]['token min'], REFUEL_OKX[chain]['token max']), 6)
            value = REFUEL_OKX[chain]['min value'] + rand

        if chain == 'Avax':
            chain = 'Avalanche C'
        if chain == 'Arbitrum':
            chain = 'Arbitrum One'

        if token == 'USDC' and chain == 'Optimism':
            chain += ' (Bridged)'

        if token == 'USDC' and chain == 'Polygon':
            chain += ' (Bridged)'

        balance = float(self.get_balance(False, token))
        if balance < value:
            value = balance

        fee = self.token_fee(token, chain)
        if token == 'CELO':
            fee = 0.0008
        logger.info(f'Sent a withdrawal from the exchange || Network: {chain} || Token: {token} || Amount: {value} || Token fee: {fee} || Address: {self.address_wallet}')

        res = self.exchange.withdraw(token, value, self.address_wallet, params={
            'chainName': chain,
            'dest': 4,
            'fee': fee,
            'pwd': '-',
            'amt': value,
            'network': chain
        })

        logger.info('Check status withdrawl')
        self.check_status_id(res)
        logger.success('Withdrawl successfully\n')
        return True

    def get_subaccount_list(self):
        return [acc for acc in self.exchange.private_get_users_subaccount_list()['data']]

    def get_balance(self, account, token):

        if account is False:
            return self.exchange.private_get_asset_balances({'ccy': token})['data'][0]['bal']

        account.update({'ccy': token})
        return self.exchange.private_get_asset_subaccount_balances(account)['data'][0]['bal']

    @exception_handler_refuel
    def wait_deposit(self, min_value, token):

        subacc_list = self.get_subaccount_list()
        logger.info(f'Subaccount balance {token}\n')
        while True:
            bal = 0
            ac = None
            for acc in subacc_list:
                balance = self.get_balance(acc, token)
                logger.info(f'{acc["label"]} - {balance}')
                if float(balance) > bal:
                    bal = float(balance)
                    ac = acc

            if bal > min_value:
                self.exchange.transfer(token, bal, ac["label"], 'master')
                break
            else:
                main_balance = float(self.get_balance(False, token))
                logger.info(f'main account - {main_balance}\n')
                if main_balance > min_value:
                    break

            time.sleep(60)



