from utils.Stargate_usdc import StrargateUSDC
from utils.Stargate_stg import StrargateSTG
from utils.Stargate_eth import StrargateETH
from utils.Bitcoin_bridge import BitcoinBridge
from utils.Abracadabra_bridge import Abracadabra
from utils.Core_bridge import CoreBridge
from utils.Angle_money_bridge import AngleMoney
from utils.zerius import Zerius, zerius
from utils.merkly import merkly
from utils.stake_stg import StakeSTG
from utils.metis import MetisBridge
from settings import *
import random
from utils.okx import Okx
from utils.func import get_accounts_data
from loguru import logger
from web3 import Web3
from utils.func import sleeping
import time
from utils.wallet import Wallet
from utils.ox_swap import OxSwap
import sys

logger.remove()  # Удаляет стандартные обработчики, чтобы избежать дублирования
logger.add("./data/log.txt")
logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <7}</level> | <cyan>{message}</cyan>")
web3_eth = Web3(Web3.HTTPProvider('https://rpc.ankr.com/eth', request_kwargs={'timeout': 60}))


def shuffle(wallets_list):
    if SHUFFLE_WALLETS is True:
        numbered_wallets = list(enumerate(wallets_list, start=1))
        random.shuffle(numbered_wallets)
    elif SHUFFLE_WALLETS is False:
        numbered_wallets = list(enumerate(wallets_list, start=1))
    else:
        raise ValueError("\nНеверное значение переменной 'shuffle_wallets'. Ожидается 'True' or 'False'.")
    return numbered_wallets


class Worker:

    def __init__(self, action):
        self.action = action
        self.balance = 0

    @staticmethod
    def chek_gas_eth():
        while True:
            try:
                res = int(round(Web3.from_wei(web3_eth.eth.gas_price, 'gwei')))
                logger.info(f'Газ сейчас - {res} gwei\n')
                if res <= MAX_GAS:
                    break
                else:
                    time.sleep(60)
                    continue
            except Exception as error:
                logger.error(error)
                time.sleep(30)
                continue

    @staticmethod
    def check_rpc(chain_path):

        for chain in chain_path:
            web3 = Wallet.get_web3(chain)
            if web3.is_connected() is True:
                logger.info(f'RPC {chain} is connected')
            else:
                logger.info(f'RPC {chain} is not connected')
                raise ValueError('')
        time.sleep(0.1)
        print()

    @staticmethod
    def get_start_chain(private_key, path, token):

        balance = 0
        chain = None

        for chaen in path:

            wal = Wallet(private_key, chaen, '1')
            if token == 'ETH':
                bal = wal.get_native_balance()
                logger.info(f'Balance {token} in {chaen} - {Web3.from_wei(bal, "ether")}')
            else:
                bal = wal.get_balance_token(token)
                logger.info(f'Balance {token} in {chaen} - {wal.from_wei(wal.get_decimal_token(token), bal)}')

            if bal > balance:
                balance = bal
                chain = chaen

        logger.info(f'Start chain - {chain}\n')
        return chain

    def work(self):

        count = 0

        for number, account in keys_list:

            str_number = f'{number} / {all_wallets}'
            key, okx_receipt = account

            address = web3_eth.eth.account.from_key(key).address

            count += 1
            logger.info(f'Account #{count} || {address}\n')

            if self.action == 1:

                chain_path = CHAIN_PATH_1.copy()

                self.check_rpc(chain_path)

                if okx_receipt is None:
                    logger.error("You didn't enter an address okx")
                    continue

                start_chain = random.choice(START_CHAIN_1)
                chain_path.remove(start_chain)
                random.shuffle(chain_path)

                okx = Okx(key, str_number)
                if count == 1:
                    sum_usdc = round(random.uniform(USDC_OKX_WIHDRAWL_1[0], USDC_OKX_WIHDRAWL_1[1]), 4)

                else:
                    sum_usdc = self.balance
                logger.info(f'Withdrawal amount - {sum_usdc} USDC')
                okx.wait_deposit(sum_usdc, 'USDC')
                if okx.withdrawl(start_chain, sum_usdc, 'USDC') is False:
                    raise ValueError('')
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

                chain_path.insert(0, start_chain)

                i = 0  # Starting index
                while i < len(chain_path):
                    current_chain = chain_path[i]
                    next_chain = chain_path[(i + 1) % len(chain_path)]
                    bridger = StrargateUSDC(key, current_chain, next_chain, str_number)
                    self.chek_gas_eth()
                    res = bridger.start_bridge()
                    if res == 'error':
                        if next_chain == chain_path[0]:
                            logger.error("Can't send USDC to the start chain")
                            raise ValueError
                        chain_path.remove(next_chain)
                    elif res is False:
                        raise ValueError
                    else:
                        i += 1
                    sleeping(TIME_DELAY[0], TIME_DELAY[1])

                wall = Wallet(key, start_chain, str_number)
                res = wall.transfer_token('USDC', okx_receipt)
                self.balance = round(float(res - (res * 1 / 100)), 4)
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

            elif self.action == 2:

                chain_path = CHAIN_PATH_2.copy()
                self.check_rpc(chain_path)

                start_chain = self.get_start_chain(key, chain_path, 'USDC')
                if start_chain is None:
                    continue

                chain_path.remove(start_chain)
                random.shuffle(chain_path)
                chain_path.insert(0, start_chain)

                i = 0  # Starting index
                while i < len(chain_path):
                    current_chain = chain_path[i]
                    next_chain = chain_path[(i + 1) % len(chain_path)]
                    bridger = StrargateUSDC(key, current_chain, next_chain, str_number)
                    self.chek_gas_eth()
                    res = bridger.start_bridge()
                    if res == 'error':
                        chain_path.remove(next_chain)
                    elif res is False:
                        break
                    else:
                        i += 1
                    sleeping(TIME_DELAY[0], TIME_DELAY[1])

            elif self.action == 3:

                self.check_rpc(CHAIN_PATH_3)

                if AUTO_CHAIN_3 is True:
                    start_chain = self.get_start_chain(key, CHAIN_PATH_3, 'USDC')
                    if start_chain is None:
                        continue
                else:
                    start_chain = CHAIN_FROM_3

                bridger = StrargateUSDC(key, start_chain, CHAIN_TO_3, str_number)
                self.chek_gas_eth()
                bridger.start_bridge()
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

            elif self.action == 4:

                chain_path = CHAIN_PATH_4.copy()

                self.check_rpc(chain_path)

                if okx_receipt is None:
                    logger.error("You didn't enter an address okx")
                    continue

                start_chain = Arbitrum
                random.shuffle(chain_path)

                okx = Okx(key, str_number)
                if count == 1:
                    sum_usdc = round(random.uniform(USDC_OKX_WIHDRAWL_4[0], USDC_OKX_WIHDRAWL_4[1]), 4)

                else:
                    sum_usdc = self.balance
                logger.info(f'Withdrawal amount - {sum_usdc} USDC')
                okx.wait_deposit(sum_usdc, 'USDC')
                if okx.withdrawl(start_chain, sum_usdc, 'USDC') is False:
                    raise ValueError('')
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

                chain_path.insert(0, start_chain)

                swap = OxSwap(key, start_chain, str_number)
                swap.swap_from_token_to_token('USDCE', 'STG', 1000000)
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

                i = 0  # Starting index
                while i < len(chain_path):
                    current_chain = chain_path[i]
                    next_chain = chain_path[(i + 1) % len(chain_path)]
                    bridger = StrargateSTG(key, current_chain, next_chain, str_number)
                    self.chek_gas_eth()
                    res = bridger.start_bridge()
                    if res == 'error':
                        if next_chain == chain_path[0]:
                            logger.error("Can't send STG to the start chain")
                            raise ValueError
                        chain_path.remove(next_chain)
                    elif res is False:
                        raise ValueError
                    else:
                        i += 1
                    sleeping(TIME_DELAY[0], TIME_DELAY[1])

                swap.swap_from_token_to_token('STG', 'USDCE', 1000000)
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

                wall = Wallet(key, start_chain, str_number)
                res = wall.transfer_token('USDCE', okx_receipt)
                self.balance = round(float(res - (res * 1 / 100)), 4)
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

            elif self.action == 5:

                sum_usdc = round(random.uniform(USDC_AMOUNT_SWAP_5[0], USDC_AMOUNT_SWAP_5[1]), 4)

                swap = OxSwap(key, Arbitrum, str_number)
                swap.swap_from_token_to_token('USDC', 'STG', sum_usdc)
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

            elif self.action == 6:

                chain_path = CHAIN_PATH_6.copy()
                self.check_rpc(chain_path)

                start_chain = self.get_start_chain(key, chain_path, 'STG')
                if start_chain is None:
                    continue

                chain_path.remove(start_chain)
                random.shuffle(chain_path)
                chain_path.insert(0, start_chain)

                i = 0  # Starting index
                while i < len(chain_path):
                    current_chain = chain_path[i]
                    next_chain = chain_path[(i + 1) % len(chain_path)]
                    bridger = StrargateSTG(key, current_chain, next_chain, str_number)
                    self.chek_gas_eth()
                    res = bridger.start_bridge()
                    if res == 'error':
                        chain_path.remove(next_chain)
                    elif res is False:
                        break
                    else:
                        i += 1
                    sleeping(TIME_DELAY[0], TIME_DELAY[1])

            elif self.action == 7:

                if AUTO_CHAIN_7 is True:
                    start_chain = self.get_start_chain(key, CHAIN_PATH_7, 'STG')
                    if start_chain is None:
                        continue
                else:
                    start_chain = CHAIN_FROM_7

                self.check_rpc([start_chain])

                bridger = StrargateSTG(key, start_chain, CHAIN_TO_7, str_number)
                self.chek_gas_eth()
                bridger.start_bridge()
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

            elif self.action == 8:

                swap = OxSwap(key, Arbitrum, str_number)
                res = swap.swap_from_token_to_token('STG', 'USDCE', 1000000)
                if res is False:
                    continue
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

            elif self.action == 9:

                chain_path = CHAIN_PATH_9.copy()

                self.check_rpc(chain_path)

                if okx_receipt is None:
                    logger.error("You didn't enter an address okx")
                    continue
                start_chain = random.choice(START_CHAIN_9)
                chain_path.remove(start_chain)
                random.shuffle(chain_path)

                okx = Okx(key, str_number)
                if count == 1:
                    sum_eth = round(random.uniform(ETH_OKX_WIHDRAWL_9[0], ETH_OKX_WIHDRAWL_9[1]), 6)

                else:
                    sum_eth = self.balance
                logger.info(f'Withdrawal amount - {sum_eth} ETH')
                okx.wait_deposit(sum_eth, 'ETH')
                if okx.withdrawl(start_chain, sum_eth, 'ETH') is False:
                    raise ValueError('')
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

                chain_path.insert(0, start_chain)

                i = 0  # Starting index
                while i < len(chain_path):
                    current_chain = chain_path[i]
                    next_chain = chain_path[(i + 1) % len(chain_path)]
                    bridger = StrargateETH(key, current_chain, next_chain, str_number)
                    self.chek_gas_eth()
                    res = bridger.start_bridge()
                    if res == 'error':
                        if next_chain == chain_path[0]:
                            logger.error("Can't send ETH to the start chain")
                            raise ValueError
                        chain_path.remove(next_chain)
                    elif res is False:
                        raise ValueError
                    else:
                        i += 1
                    sleeping(TIME_DELAY[0], TIME_DELAY[1])

                wall = Wallet(key, start_chain, str_number)
                res = wall.transfer_native(okx_receipt)
                self.balance = round(float(res - (res * 1 / 100)), 6)
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

                okx.wait_deposit(self.balance, 'ETH')

            elif self.action == 10:

                chain_path = CHAIN_PATH_10.copy()
                self.check_rpc(chain_path)

                start_chain = self.get_start_chain(key, chain_path, 'ETH')
                if start_chain is None:
                    continue

                chain_path.remove(start_chain)
                random.shuffle(chain_path)
                chain_path.insert(0, start_chain)

                i = 0  # Starting index
                while i < len(chain_path):
                    current_chain = chain_path[i]
                    next_chain = chain_path[(i + 1) % len(chain_path)]
                    bridger = StrargateETH(key, current_chain, next_chain, str_number)
                    self.chek_gas_eth()
                    res = bridger.start_bridge()
                    if res == 'error':
                        chain_path.remove(next_chain)
                    elif res is False:
                        break
                    else:
                        i += 1
                    sleeping(TIME_DELAY[0], TIME_DELAY[1])

            elif self.action == 11:

                if AUTO_CHAIN_11 is True:
                    start_chain = self.get_start_chain(key, CHAIN_PATH_11, 'ETH')
                    if start_chain is None:
                        continue
                else:
                    start_chain = CHAIN_FROM_11

                self.check_rpc([start_chain])

                bridger = StrargateETH(key, start_chain, CHAIN_TO_11, str_number)
                self.chek_gas_eth()
                bridger.start_bridge()
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

            elif self.action == 12:

                sum_usdc = round(random.uniform(USDC_AMOUNT_SWAP_13[0], USDC_AMOUNT_SWAP_13[1]), 4)

                swap = OxSwap(key, Avax, str_number)
                swap.swap_from_token_to_token('USDC', 'BTC', sum_usdc)
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

            elif self.action == 13:

                chain_path = CHAIN_PATH_14.copy()
                self.check_rpc(chain_path)

                start_chain = self.get_start_chain(key, chain_path, 'BTC')
                if start_chain is None:
                    continue

                chain_path.remove(start_chain)
                random.shuffle(chain_path)
                chain_path.insert(0, start_chain)
                i = 0  # Starting index
                while i < len(chain_path):
                    current_chain = chain_path[i]
                    next_chain = chain_path[(i + 1) % len(chain_path)]
                    bridger = BitcoinBridge(key, current_chain, next_chain, str_number)
                    self.chek_gas_eth()
                    res = bridger.start_bridge()
                    if res == 'error':
                        chain_path.remove(next_chain)
                    elif res is False:
                        break
                    else:
                        i += 1
                    sleeping(TIME_DELAY[0], TIME_DELAY[1])

            elif self.action == 14:

                if AUTO_CHAIN_15 is True:
                    start_chain = self.get_start_chain(key, CHAIN_PATH_15, 'BTC')
                    if start_chain is None:
                        continue
                else:
                    start_chain = CHAIN_FROM_15

                self.check_rpc([start_chain])

                bridger = BitcoinBridge(key, start_chain, CHAIN_TO_15, str_number)
                self.chek_gas_eth()
                bridger.start_bridge()
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

            elif self.action == 15:

                swap = OxSwap(key, Avax, str_number)
                res = swap.swap_from_token_to_token('BTC', 'USDC', 10000000)
                if res is False:
                    continue
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

            elif self.action == 16:

                chain_path = CHAIN_PATH_17.copy()

                self.check_rpc(chain_path)

                if okx_receipt is None:
                    logger.error("You didn't enter an address okx")
                    continue

                start_chain = Arbitrum
                random.shuffle(chain_path)

                okx = Okx(key, str_number)
                if count == 1:
                    sum_usdc = round(random.uniform(USDC_OKX_WIHDRAWL_17[0], USDC_OKX_WIHDRAWL_17[1]), 4)

                else:
                    sum_usdc = self.balance
                logger.info(f'Withdrawal amount - {sum_usdc} USDC')
                okx.wait_deposit(sum_usdc, 'USDC')
                if okx.withdrawl(start_chain, sum_usdc, 'USDC') is False:
                    raise ValueError('')
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

                chain_path.insert(0, start_chain)

                swap = OxSwap(key, start_chain, str_number)
                swap.swap_from_token_to_token('USDCE', 'MIM', 1000000)
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

                i = 0  # Starting index
                while i < len(chain_path):
                    current_chain = chain_path[i]
                    next_chain = chain_path[(i + 1) % len(chain_path)]
                    bridger = Abracadabra(key, current_chain, next_chain, str_number)
                    self.chek_gas_eth()
                    res = bridger.start_bridge()
                    if res == 'error':
                        if next_chain == chain_path[0]:
                            logger.error("Can't send MIM to the start chain")
                            raise ValueError
                        chain_path.remove(next_chain)
                    elif res is False:
                        raise ValueError
                    else:
                        i += 1
                    sleeping(TIME_DELAY[0], TIME_DELAY[1])

                swap.swap_from_token_to_token('MIM', 'USDCE', 1000000)
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

                wall = Wallet(key, start_chain, str_number)
                res = wall.transfer_token('USDCE', okx_receipt)
                self.balance = round(float(res - (res * 1 / 100)), 4)
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

            elif self.action == 17:

                sum_usdc = round(random.uniform(USDC_AMOUNT_SWAP_18[0], USDC_AMOUNT_SWAP_18[1]), 4)

                swap = OxSwap(key, Arbitrum, str_number)
                swap.swap_from_token_to_token('USDC', 'MIM', sum_usdc)
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

            elif self.action == 18:

                chain_path = CHAIN_PATH_19.copy()
                self.check_rpc(chain_path)

                start_chain = self.get_start_chain(key, chain_path, 'MIM')
                if start_chain is None:
                    continue

                chain_path.remove(start_chain)
                random.shuffle(chain_path)
                chain_path.insert(0, start_chain)

                i = 0  # Starting index
                while i < len(chain_path):
                    current_chain = chain_path[i]
                    next_chain = chain_path[(i + 1) % len(chain_path)]
                    bridger = Abracadabra(key, current_chain, next_chain, str_number)
                    self.chek_gas_eth()
                    res = bridger.start_bridge()
                    if res == 'error':
                        chain_path.remove(next_chain)

                    elif res is False:
                        break

                    else:
                        i += 1
                    sleeping(TIME_DELAY[0], TIME_DELAY[1])

            elif self.action == 19:

                if AUTO_CHAIN_20 is True:
                    start_chain = self.get_start_chain(key, CHAIN_PATH_20, 'MIM')
                    if start_chain is None:
                        continue
                else:
                    start_chain = CHAIN_FROM_20

                self.check_rpc([start_chain])

                bridger = Abracadabra(key, start_chain, CHAIN_TO_20, str_number)
                self.chek_gas_eth()
                bridger.start_bridge()
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

            elif self.action == 20:

                swap = OxSwap(key, Arbitrum, str_number)
                swap.swap_from_token_to_token('MIM', 'USDCE', 10000000)
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

            elif self.action == 21:

                self.check_rpc([Polygon, Core])

                if okx_receipt is None:
                    logger.error("You didn't enter an address okx")
                    continue

                start_chain = Polygon

                okx = Okx(key, str_number)
                if count == 1:
                    sum_usdc = round(random.uniform(USDC_OKX_WIHDRAWL_21[0], USDC_OKX_WIHDRAWL_21[1]), 4)

                else:
                    sum_usdc = self.balance

                logger.info(f'Withdrawal amount - {sum_usdc} USDC')
                okx.wait_deposit(sum_usdc, 'USDC')
                if okx.withdrawl(start_chain, sum_usdc, 'USDC') is False:
                    raise ValueError('')
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

                core = CoreBridge(key, Polygon, str_number)
                core.deposit()
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

                core = CoreBridge(key, Core, str_number)
                core.withdrawl()
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

                wall = Wallet(key, start_chain, str_number)
                res = wall.transfer_token('USDC', okx_receipt)
                self.balance = round(float(res - (res * 1 / 100)), 4)
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

            elif self.action == 22:

                self.check_rpc([Polygon])
                core = CoreBridge(key, Polygon, str_number)

                number_trans = random.randint(NUMBER_OF_TRANSACTIONS_22[0], NUMBER_OF_TRANSACTIONS_22[1])
                logger.info(f'Number of transactions - {number_trans}')

                core.multiple_deposit(number_trans)
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

            elif self.action == 23:

                self.check_rpc([Polygon])
                core = CoreBridge(key, Polygon, str_number)

                res = core.deposit()
                if res is False:
                    continue
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

            elif self.action == 24:
                self.check_rpc([Core])
                core = CoreBridge(key, Core, str_number)

                res = core.withdrawl()
                if res is False:
                    continue
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

            elif self.action == 25:

                sum_matic = round(random.uniform(MATIC_AMOUNT_SWAP_25[0], MATIC_AMOUNT_SWAP_25[1]), 4)

                swap = OxSwap(key, Polygon, str_number)
                swap.swap_from_native_to_token('EUR', sum_matic)
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

            elif self.action == 26:

                chain_path = [Gnosis, Celo]
                self.check_rpc([Polygon])

                chain_to = random.choice(chain_path)

                angle = AngleMoney(key, Polygon, chain_to, str_number)
                res = angle.start_bridge()
                if res is False:
                    continue
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

            elif self.action == 27:

                chain_path = [Gnosis, Celo]
                self.check_rpc(chain_path)

                start_chain = self.get_start_chain(key, chain_path, 'EUR')
                chain_path.remove(start_chain)
                chain_to = random.choice(chain_path)
                angle = AngleMoney(key, start_chain, chain_to, str_number)
                res = angle.start_bridge()
                if res is False:
                    continue
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

            elif self.action == 28:

                chain_path = [Gnosis, Celo]
                self.check_rpc(chain_path)

                number_trans = random.randint(NUMBER_OF_TRANSACTIONS_28[0], NUMBER_OF_TRANSACTIONS_28[1])
                logger.info(f'Number of transactions - {number_trans}')

                for _ in range(number_trans):

                    chain_path = [Gnosis, Celo]

                    start_chain = self.get_start_chain(key, chain_path, 'EUR')
                    chain_to = chain_path.remove(start_chain)
                    angle = AngleMoney(key, start_chain, chain_to, str_number)

                    number_trans = random.randint(NUMBER_OF_TRANSACTIONS_28[0], NUMBER_OF_TRANSACTIONS_28[1])
                    logger.info(f'Number of transactions - {number_trans}')

                    res = angle.start_bridge()
                    if res is False:
                        continue
                    sleeping(TIME_DELAY[0], TIME_DELAY[1])

            elif self.action == 29:

                chain_path = [Gnosis, Celo]
                self.check_rpc(chain_path)

                start_chain = self.get_start_chain(key, chain_path, 'EUR')
                chain_to = Polygon
                angle = AngleMoney(key, start_chain, chain_to, str_number)
                res = angle.start_bridge()
                if res is False:
                    continue
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

            elif self.action == 30:

                swap = OxSwap(key, Polygon, str_number)
                swap.swap_from_token_to_native('EUR', 1000000)
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

            elif self.action == 31:
                zerius(key, str_number, 'mint')
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

            elif self.action == 32:
                zerius(key, str_number, 'bridge')
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

            elif self.action == 33:
                zerius(key, str_number, 'refuel')
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

            elif self.action == 34:
                merkly(key, str_number)
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

            elif self.action == 35:
                chain = random.choice(CHAIN_35)

                summ = round(random.uniform(VALUE_35[chain][0], VALUE_35[chain][1]), VALUE_35[chain][2])

                swap = OxSwap(key, chain, str_number)
                swap.swap_from_native_to_token('STG', summ)
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

                stg = StakeSTG(key, chain, str_number)
                res = stg.stake()
                if res is False:
                    continue
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

            elif self.action == 36:

                if okx_receipt is None:
                    continue

                start_chain = CHAIN_FROM_37

                if start_chain == Arbitrum:
                    token = 'USDCE'
                else:
                    token = 'USDC'

                wall = Wallet(key, start_chain, str_number)
                res = wall.transfer_token(token, okx_receipt)
                if res is False:
                    continue
                sleeping(TIME_DELAY[0], TIME_DELAY[1])

            elif self.action == 37:
                for chain_from in CHAIN_FROM_32:
                    for chain_to in CHAIN_TO_32:
                        zer = Zerius(key, chain_from, chain_to, str_number)
                        try:
                            zer.check_price_nft()
                            time.sleep(0.5)
                        except:
                            continue
                    time.sleep(1)
                    print()
                break

            elif self.action == 38:
                for chain_from in CHAIN_FROM_33:
                    for chain_to in CHAIN_TO_33:
                        zer = Zerius(key, chain_from, chain_to, str_number)
                        try:
                            zer.check_price_gas()
                            time.sleep(0.5)
                        except:
                            continue
                    time.sleep(1)
                    print()
                break

            elif self.action == 39:
                self.check_rpc([BSC, Metis])

                for _ in range(RETRY):
                    try:
                        zer = Zerius(key, BSC, Metis, str_number)
                        met = MetisBridge(key, str_number)
                        value = round(float(Web3.from_wei(met.get_fees(), 'ether')) * 1.3, 3)

                        zer.refuel(value)
                        sleeping(TIME_DELAY[0], TIME_DELAY[1])

                    except Exception as error:
                        logger.error(f'{error}\n')
                        sleeping(TIME_DELAY_ERROR[0], TIME_DELAY_ERROR[1])
                        continue

            elif self.action == 40:
                met = MetisBridge(key, str_number)
                met.start_bridge()
                sleeping(TIME_DELAY[0], TIME_DELAY[1])


if __name__ == '__main__':
    list1 = get_accounts_data()
    all_wallets = len(list1)
    logger.info(f'Number of wallets: {all_wallets}\n')
    keys_list = shuffle(list1)

    while True:
        while True:
            logger.info('1 - Stargate bridge USDC with OKX')
            logger.info('2 - Stargate bridge USDC without OKX')
            logger.info('3 - Stargate bridge USDC Lite\n')

            logger.info('4 - Stargate bridge STG with OKX')
            logger.info('5 - Buy STG Token (Chain - Arbitrum)')
            logger.info('6 - Stargate bridge STG without OKX')
            logger.info('7 - Stargate bridge STG Lite')
            logger.info('8 - Sold STG Token (Chain - Arbitrum)\n')

            logger.info('9 - Stargate bridge ETH with OKX')
            logger.info('10 - Stargate bridge ETH without OKX')
            logger.info('11 - Stargate bridge ETH Lite\n')

            logger.info('12 - Buy BTC Token (Chain - Avax)')
            logger.info('13 - Bitcoin bridge without OKX')
            logger.info('14 - Bitcoin bridge Lite')
            logger.info('15 - Sold BTC Token (Chain - Avax)\n')

            logger.info('16 - Abracadabra bridge with OKX')
            logger.info('17 - Buy MIM Token (Chain - Arbitrum)')
            logger.info('18 - Abracadabra bridge without OKX')
            logger.info('19 - Abracadabra bridge Lite')
            logger.info('20 - Sold MIM Token (Chain - Arbitrum)\n')

            logger.info('21 - CORE bridge with OKX')
            logger.info('22 - CORE bridge')
            logger.info('23 - CORE bridge all balance')
            logger.info('24 - Withdrawl USDC CORE\n')

            logger.info('25 - Angle Money buy EUR (Polygon)')
            logger.info('26 - Angle Money bridge from Polygon to Gnosis/Celo')
            logger.info('27 - Angle Money bridge from Gnosis/Celo to Gnosis/Celo (no repetitions)')
            logger.info('28 - Angle Money bridge from Gnosis/Celo to Gnosis/Celo (repetitions)')
            logger.info('29 - Angle Money bridge from Gnosis/Celo to Polygon')
            logger.info('30 - Angle Money sold EUR (Polygon)\n')

            logger.info('31 - Zerius Mint NFT')
            logger.info('32 - Zerius Bridge NFT')
            logger.info('33 - Zerius Refuel\n')

            logger.info('34 - Merkly refuel\n')

            logger.info('35 - Stake STG\n')

            logger.info('36 - Transfer USDC to OKX recepient\n')

            logger.info('37 - Check price NFT bridge')
            logger.info('38 - Check price Refuel\n')

            logger.info('39 - Refuel from BSC to Metis')
            logger.info('40 - Withdrawl USDT from Metis to BSC\n')

            time.sleep(0.1)
            act = int(input('Choose an action: '))

            if act in [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40]:
                break

        worker = Worker(act)
        worker.work()
