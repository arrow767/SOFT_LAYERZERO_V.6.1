from web3 import Web3
import json as js
import time
from settings import CHAIN_RPC, BSC_GWEI, OX_API_KEY
from web3.middleware import geth_poa_middleware
from requests.adapters import Retry
from utils.retry_wallet import exception_handler_wallet
import requests
from loguru import logger
import random

SCAN = {
    'Arbitrum': 'https://arbiscan.io/tx/',
    'Optimism': 'https://optimistic.etherscan.io/tx/',
    'Polygon': 'https://polygonscan.com/tx/',
    'BSC': 'https://bscscan.com/tx/',
    'Avax': 'https://snowtrace.io/tx/',
    'Base': 'https://basescan.org/tx/',
    'Fantom': 'https://ftmscan.com/tx/',
    'Kava': 'https://kavascan.com/tx/',
    'Linea': 'https://lineascan.build/tx/',
    'Moonriver': 'https://moonriver.moonscan.io/tx/',
    'CELO': 'https://celoscan.io/tx/',
    'Gnosis': 'https://gnosisscan.io/tx/',
    'CORE': 'https://scan.coredao.org/tx/',
    'Metis': 'https://andromeda-explorer.metis.io/tx/'
}

ADDRESS = {

    'USDC': {
        'Arbitrum': Web3.to_checksum_address('0xff970a61a04b1ca14834a43f5de4533ebddb5cc8'),
        'Optimism': Web3.to_checksum_address('0x7F5c764cBc14f9669B88837ca1490cCa17c31607'),
        'Polygon': Web3.to_checksum_address('0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174'),
        'BSC': Web3.to_checksum_address('0x55d398326f99059fF775485246999027B3197955'),
        'Avax': Web3.to_checksum_address('0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E'),
        'Base': Web3.to_checksum_address('0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA'),
        'Fantom': Web3.to_checksum_address('0x28a92dde19D9989F39A49905d7C9C2FAc7799bDf'),
        'CORE': Web3.to_checksum_address('0xa4151b2b3e269645181dccf2d426ce75fcbdeca9'),
        'Metis': Web3.to_checksum_address('0xbB06DCA3AE6887fAbF931640f67cab3e3a16F4dC'),
    },

    'USDCE': {
        'Polygon': Web3.to_checksum_address('0x3c499c542cef5e3811e1192ce70d8cc03d5c3359'),
        'Arbitrum': Web3.to_checksum_address('0xaf88d065e77c8cC2239327C5EDb3A432268e5831'),
    },

    'STG': {
        'Arbitrum': Web3.to_checksum_address('0x6694340fc020c5e6b96567843da2df01b2ce1eb6'),
        'Optimism': Web3.to_checksum_address('0x296F55F8Fb28E498B858d0BcDA06D955B2Cb3f97'),
        'Polygon': Web3.to_checksum_address('0x2f6f07cdcf3588944bf4c42ac74ff24bf56e7590'),
        'BSC': Web3.to_checksum_address('0xb0d502e938ed5f4df2e681fe6e419ff29631d62b'),
        'Avax': Web3.to_checksum_address('0x2f6f07cdcf3588944bf4c42ac74ff24bf56e7590'),
        'Fantom': Web3.to_checksum_address('0x2F6F07CDcf3588944Bf4C42aC74ff24bF56e7590'),
        'Base': Web3.to_checksum_address('0xE3B53AF74a4BF62Ae5511055290838050bf764Df'),
        'Linea': Web3.to_checksum_address('0x808d7c71ad2ba3FA531b068a2417C63106BC0949'),
        'Kava': Web3.to_checksum_address('0x83c30eb8bc9ad7c56532895840039e62659896ea')
    },

    'MIM': {
        'Arbitrum': Web3.to_checksum_address('0xFEa7a6a0B346362BF88A9e4A88416B77a57D6c2A'),
        'Optimism': Web3.to_checksum_address('0xB153FB3d196A8eB25522705560ac152eeEc57901'),
        'Polygon': Web3.to_checksum_address('0x49a0400587A7F65072c87c4910449fDcC5c47242'),
        'BSC': Web3.to_checksum_address('0xfE19F0B51438fd612f6FD59C1dbB3eA319f433Ba'),
        'Avax': Web3.to_checksum_address('0x130966628846BFd36ff31a822705796e8cb8C18D'),
        'Moonriver': Web3.to_checksum_address('0x0caE51e1032e8461f4806e26332c030E34De3aDb'),
        'Fantom': Web3.to_checksum_address('0x82f0B8B456c1A451378467398982d4834b6829c1'),
        'Base': Web3.to_checksum_address('0x4A3A6Dd60A34bB2Aba60D73B4C88315E9CeB6A3D'),
        'Kava': Web3.to_checksum_address('0x471ee749ba270eb4c1165b5ad95e614947f6fceb'),
        'Linea': Web3.to_checksum_address('0xDD3B8084AF79B9BaE3D1b668c0De08CCC2C9429A')
    },

    'BTC': {
        'Avax': Web3.to_checksum_address('0x152b9d0FdC40C096757F570A51E494bd4b943E50'),
        'Arbitrum': Web3.to_checksum_address('0x2297aebd383787a160dd0d9f71508148769342e3'),
        'Optimism': Web3.to_checksum_address('0x2297aebd383787a160dd0d9f71508148769342e3'),
        'Polygon': Web3.to_checksum_address('0x2297aebd383787a160dd0d9f71508148769342e3'),
        'BSC': Web3.to_checksum_address('0x2297aebd383787a160dd0d9f71508148769342e3'),
    },

    'EUR': {
        'Polygon': Web3.to_checksum_address('0xE0B52e49357Fd4DAf2c15e02058DCE6BC0057db4'),
        'CELO': Web3.to_checksum_address('0xC16B81Af351BA9e64C1a069E3Ab18c244A1E3049'),
        'Gnosis': Web3.to_checksum_address('0x4b1E2c2762667331Bc91648052F646d1b0d35984'),
    }
}


class Wallet:

    def __init__(self, private_key, chain, number):
        self.private_key = private_key
        self.chain = chain
        self.number = number
        self.web3 = self.get_web3(chain)
        self.scan = self.get_scan(chain)
        self.address_wallet = self.web3.eth.account.from_key(private_key).address
        self.token_abi = js.load(open('./abi/Token.txt'))

    @staticmethod
    def get_web3(chain):
        retries = Retry(total=10, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        adapter = requests.adapters.HTTPAdapter(max_retries=retries)
        session = requests.Session()
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return Web3(Web3.HTTPProvider(CHAIN_RPC[chain], request_kwargs={'timeout': 60}, session=session))

    @staticmethod
    def get_scan(chain):
        return SCAN[chain]

    @staticmethod
    def to_wei(decimal, amount):
        if decimal == 6:
            unit = 'picoether'
        else:
            unit = 'ether'

        return Web3.to_wei(amount, unit)

    @staticmethod
    def from_wei(decimal, amount):
        if decimal == 6:
            unit = 'picoether'
        elif decimal == 8:
            return float(amount / 10 ** 8)
        else:
            unit = 'ether'

        return Web3.from_wei(amount, unit)

    def send_transaction_and_wait(self, tx, message):
        signed_txn = self.web3.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        logger.info('Отправил транзакцию')
        time.sleep(5)
        tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=900, poll_latency=5)
        if tx_receipt.status == 1:
            logger.success('Транзакция смайнилась успешно')
        else:
            logger.error('Транзакция сфейлилась, пытаюсь еще раз')
            raise ValueError('')

        logger.success(f'[{self.number}] {message} || {self.scan}{tx_hash.hex()}\n')
        return tx_hash

    def approve(self, token_to_approve, address_to_approve):
        gas = 40_000
        gas_cost = gas * self.web3.eth.gas_price * 2

        if self.get_native_balance() < gas_cost:
            raise ValueError('balance')

        token_contract = self.web3.eth.contract(address=ADDRESS[token_to_approve][self.chain], abi=self.token_abi)
        max_amount = 2 ** 256 - 1
        dick = {
            'from': self.address_wallet,
            'nonce': self.web3.eth.get_transaction_count(self.address_wallet),
            **self.get_gas_price()
        }
        txn = token_contract.functions.approve(address_to_approve, max_amount).build_transaction(dick)

        self.send_transaction_and_wait(txn, 'approve')

    def get_balance_token(self, token):
        contract = self.web3.eth.contract(address=ADDRESS[token][self.chain], abi=self.token_abi)
        return contract.functions.balanceOf(self.address_wallet).call()

    def get_allowance_token(self, token, address):
        contract = self.web3.eth.contract(address=ADDRESS[token][self.chain], abi=self.token_abi)
        return contract.functions.allowance(self.address_wallet, address).call()

    def get_decimal_token(self, token):
        contract = self.web3.eth.contract(address=ADDRESS[token][self.chain], abi=self.token_abi)
        return contract.functions.decimals().call()

    def get_native_balance(self):
        return self.web3.eth.get_balance(self.address_wallet)

    def get_gas_price(self):
        if self.chain in ["Polygon", "Avax"]:
            try:
                self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
            except:
                pass

        if self.chain in ["BSC", "Fantom", 'Metis', 'Harmony', 'CORE', 'Linea', 'Kava']:
            if self.chain == 'BSC':
                gwei = round(random.uniform(BSC_GWEI[0], BSC_GWEI[1]), 1)
                return {'gasPrice': Web3.to_wei(gwei, 'gwei')}
            else:
                return {'gasPrice': self.web3.eth.gas_price}

        return {'maxFeePerGas': self.web3.eth.gas_price, 'maxPriorityFeePerGas': self.web3.eth.max_priority_fee}

    def check_transaction_stargate(self, tx_hash):
        while True:
            time.sleep(60)
            try:
                url = 'https://api-mainnet.layerzero-scan.com/tx/' + tx_hash
                json_data = self.get_api_call_data(url)

                logger.info(json_data['messages'])

                if not json_data['messages']:
                    continue
                if json_data['messages'][0]['status'] != 'DELIVERED':
                    continue
                else:
                    time.sleep(1)
                    print()
                    return
            except:
                continue

    def check_transaction_refuel_stella(self, tx_hash):
        while True:
            time.sleep(60)
            try:
                url = 'https://api.0xsquid.com/v1/status?transactionId=' + tx_hash
                json_data = self.get_api_call_data(url)

                logger.info(json_data)

                if not json_data['messages']:
                    continue
                if json_data['messages'][0]['status'] != 'DELIVERED':
                    continue
                else:
                    return
            except:
                continue

    def check_transaction_refuel_bungee(self, tx_hash):
        while True:
            time.sleep(60)
            try:
                url = 'https://refuel.socket.tech/transaction?sourceTxHash=' + tx_hash
                data = self.get_api_call_data(url)
                if data['success'] is False:
                    continue
                if data['result']['status'] != 'Tx is confirmed & processed':
                    continue
                else:
                    return
            except:
                continue

    @staticmethod
    def get_api_call_data(url):
        headers = {
            '0x-api-key': OX_API_KEY
        }
        with requests.Session() as s:
            call_data = s.get(url, headers=headers, timeout=60)
        if call_data.status_code < 400:
            api_data = call_data.json()
            return api_data
        else:
            logger.error("Couldn't get a response")
            raise ValueError('')

    @exception_handler_wallet
    def transfer_token(self, token, address):

        contract = self.web3.eth.contract(address=ADDRESS[token][self.chain], abi=self.token_abi)
        amount = self.get_balance_token(token)

        if amount == 0:
            logger.error(f'Balance {token} - 0\n')
            return False

        dick = {
            'from': self.address_wallet,
            'nonce': self.web3.eth.get_transaction_count(self.address_wallet),
            **self.get_gas_price()
        }
        tx = contract.functions.transfer(Web3.to_checksum_address(address), amount).build_transaction(dick)

        self.send_transaction_and_wait(tx, f'Transfer {self.from_wei(self.get_decimal_token(token), amount)} {token} to {address}')

        return round(self.from_wei(self.get_decimal_token(token), amount), 4)

    @exception_handler_wallet
    def transfer_native(self, address):

        balance = self.get_native_balance()

        amount = balance - Web3.to_wei(0.0005, 'ether')
        if amount < 0:
            logger.error(f'Balance ETH < 0.0005\n')
            return False

        dick = {
            'chainId': self.web3.eth.chain_id,
            'from': self.address_wallet,
            'to': Web3.to_checksum_address(address),
            'value': amount,
            'nonce': self.web3.eth.get_transaction_count(self.address_wallet),
            'gas': 21_000,
            **self.get_gas_price()
        }

        self.send_transaction_and_wait(dick, f'Transfer {Web3.from_wei(amount, "ether")} ETH to {address}')

        return round(Web3.from_wei(amount, "ether"), 6)

    def check_gas_cost(self):
        balance = self.get_native_balance()
        gas = 500_000
        gas_cost = (gas * self.web3.eth.gas_price * 2) + self.web3.eth.max_priority_fee
        if gas_cost > balance:
            raise ValueError('balance')
