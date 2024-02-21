from utils.wallet import Wallet, ADDRESS
from web3 import Web3
from loguru import logger
from utils.func import sleeping
from utils.retry_bridge import exception_handler
from settings import SLIPPAGE_OX_SWAP

url_chains = {
    'BSC': 'bsc.',
    'Arbitrum': 'arbitrum.',
    'Polygon': 'polygon.',
    'Avax': 'avalanche.',
    'Optimism': 'optimism.',
    'Fantom': 'fantom.'
}

token_list = {
    'Arbitrum': 'ETH',
    'Optimism': 'ETH',
    'Polygon': 'MATIC',
    'Fantom': 'FTM',
    'BSC': 'BNB',
    'Avax': 'AVAX'
}


class OxSwap(Wallet):

    def __init__(self, private_key, chain, number):
        super().__init__(private_key, chain, number)

    @exception_handler
    def swap_from_native_to_token(self, to_token, amount):

        decimal = self.get_decimal_token(to_token)

        value = Web3.to_wei(amount, 'ether')
        url = f'https://{url_chains[self.chain]}api.0x.org/swap/v1/quote?buyToken={ADDRESS[to_token][self.chain]}&sellToken=0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE&sellAmount={value}&slippagePercentage={SLIPPAGE_OX_SWAP / 100}'
        data = self.get_api_call_data(url)

        logger.info(f'OxSwap {amount} {token_list[self.chain]} to {self.from_wei(decimal, int(data["buyAmount"]))} {to_token}')

        self.check_gas_cost()

        txn = {
            'chainId': self.web3.eth.chain_id,
            'data': data['data'],
            'from': self.address_wallet,
            'to': Web3.to_checksum_address(data['to']),
            'value': int(data['value']),
            'nonce': self.web3.eth.get_transaction_count(self.address_wallet),
            ** self.get_gas_price()
        }

        gas = self.web3.eth.estimate_gas(txn)
        txn.update({'gas': gas})

        self.send_transaction_and_wait(txn, f'OxSwap {amount} {token_list[self.chain]} to {self.from_wei(decimal, int(data["buyAmount"]))} {to_token}')

    @exception_handler
    def swap_from_token_to_native(self, from_token, amount):
        decimal = self.get_decimal_token(from_token)
        value = self.to_wei(decimal, amount)
        balance_token = self.get_balance_token(from_token)

        if balance_token == 0:
            logger.info(f'Balance {from_token} - 0')
            return False

        if value > balance_token:
            value = balance_token

        url = f'https://{url_chains[self.chain]}api.0x.org/swap/v1/quote?buyToken=0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE&sellToken={ADDRESS[from_token][self.chain]}&sellAmount={value}&slippagePercentage={SLIPPAGE_OX_SWAP / 100}'
        data = self.get_api_call_data(url)

        logger.info(f'OxSwap {self.from_wei(decimal, value)} {from_token} to {Web3.from_wei(int(data["buyAmount"]), "ether")} {token_list[self.chain]}')

        spender = Web3.to_checksum_address(data['allowanceTarget'])
        allowance = self.get_allowance_token(from_token, spender)
        if allowance < 100000 * 10 ** decimal:
            logger.info('Need Approve')
            self.approve(from_token, spender)
            sleeping(50, 70)

        self.check_gas_cost()

        txn = {
            'chainId': self.web3.eth.chain_id,
            'data': data['data'],
            'from': self.address_wallet,
            'to': Web3.to_checksum_address(data['to']),
            'nonce': self.web3.eth.get_transaction_count(self.address_wallet),
            ** self.get_gas_price()
        }

        gas = self.web3.eth.estimate_gas(txn)
        txn.update({'gas': gas})

        self.send_transaction_and_wait(txn, f'OxSwap {self.from_wei(decimal, value)} {from_token} to {Web3.from_wei(int(data["buyAmount"]), "ether")} {token_list[self.chain]}')

    @exception_handler
    def swap_from_token_to_token(self, token_from, token_to, amount):

        decimal_from_token = self.get_decimal_token(token_from)
        decimal_to_token = self.get_decimal_token(token_to)

        value = self.to_wei(decimal_from_token, amount)
        balance_token = self.get_balance_token(token_from)

        if balance_token == 0:
            logger.info(f'Balance {token_from} - 0')
            return False

        if value > balance_token:
            value = balance_token

        url = f'https://{url_chains[self.chain]}api.0x.org/swap/v1/quote?buyToken={ADDRESS[token_to][self.chain]}&sellToken={ADDRESS[token_from][self.chain]}&sellAmount={value}&slippagePercentage={SLIPPAGE_OX_SWAP / 100}'

        data = self.get_api_call_data(url)

        logger.info(f'OxSwap {self.from_wei(decimal_from_token, value)} {token_from} to {self.from_wei(decimal_to_token, int(data["buyAmount"]))} {token_to}')

        spender = Web3.to_checksum_address(data['allowanceTarget'])
        allowance = self.get_allowance_token(token_from, spender)
        if allowance < 100000 * 10 ** decimal_from_token:
            logger.info('Need Approve')
            self.approve(token_from, spender)
            sleeping(50, 70)

        gas = 500_000
        self.check_gas_cost()

        txn = {
            'chainId': self.web3.eth.chain_id,
            'data': data['data'],
            'from': self.address_wallet,
            'to': Web3.to_checksum_address(data['to']),
            'nonce': self.web3.eth.get_transaction_count(self.address_wallet),
            ** self.get_gas_price()
        }

        gas = self.web3.eth.estimate_gas(txn)
        txn.update({'gas': gas})

        self.send_transaction_and_wait(txn, f'OxSwap {self.from_wei(decimal_from_token, value)} {token_from} to {self.from_wei(decimal_to_token, int(data["buyAmount"]))} {token_to}')
