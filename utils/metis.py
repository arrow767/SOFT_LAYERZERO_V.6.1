from utils.wallet import Wallet
from loguru import logger
from web3 import Web3
import json as js
from utils.func import sleeping
from settings import SLIPPAGE_STARGATE
from utils.retry_bridge import exception_handler


class MetisBridge(Wallet):

    def __init__(self, private_key, number):
        super().__init__(private_key, 'Metis', number)
        self.abi = js.load(open('./abi/stargate/stargate.txt'))
        self.address = Web3.to_checksum_address('0x2F6F07CDcf3588944Bf4C42aC74ff24bF56e7590')
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)

    def get_fees(self):
        return self.contract.functions.quoteLayerZeroFee(102, 1, "0x0000000000000000000000000000000000000001",
                                                         "0x",
                                                         [0, 0, "0x0000000000000000000000000000000000000001"]).call()[0]

    @exception_handler
    def start_bridge(self):
        logger.info(f'Stargate bridge USDT || Metis -> BSC')

        allowance = self.get_allowance_token('USDC', self.address)
        if allowance < 100000 * 10 ** self.get_decimal_token("USDC"):
            logger.info('Need Approve')
            self.approve('USDC', self.address)
            sleeping(50, 70)

        token_balance = self.get_balance_token('USDC')
        amount_out_min = int(token_balance - (token_balance * SLIPPAGE_STARGATE // 100))
        lz_tx_obj = [0, 0, '0x0000000000000000000000000000000000000001']

        fees = self.get_fees()

        dick = {
            'from': self.address_wallet,
            'value': fees,
            'nonce': self.web3.eth.get_transaction_count(self.address_wallet),
            'gas': 500_000,
            ** self.get_gas_price()
        }

        swap_txn = self.contract.functions.swap(102, 19, 19,
                                                self.address_wallet,
                                                token_balance,
                                                amount_out_min,
                                                lz_tx_obj, self.address_wallet, '0x').build_transaction(dick)

        tx_hash = self.send_transaction_and_wait(swap_txn, f'Stargate bridge USDT || {self.chain} -> BSC')

        self.check_transaction_stargate(tx_hash.hex())
