import io
from msoffcrypto.exceptions import DecryptionError, InvalidKeyError
from loguru import logger
from settings import EXCEL_PASSWORD
import random
from tqdm import tqdm
import time
import msoffcrypto
import pandas as pd

lz_id_chain = {
    'Arbitrum': 110,
    'Optimism': 111,
    'Polygon': 109,
    'BSC': 102,
    'Avax': 106,
    'Fantom': 112,
    'Base': 184,
    'Linea': 183,
    'Kava': 177,
    'zkSync': 165,
    'CELO': 125,
    'Gnosis': 145,
    'CORE': 153,
    'Moonriver': 167,
    'Arbitrum Nova': 175,
    'Conflux': 212,
    'Moonbeam': 126,
    'Nova': 175,
    'Harmony': 116,
    'Canto': 159,
    'Mantle': 181,
    'ShimmerEVM': 230,
    'Fuse': 138,
    'Beam': 198,
    'Tomo': 196,
    'DFK' : 115,
    'Metis': 151

}

chain_id = {
    'Arbitrum' : 42161,
    'Optimism' : 10,
    'Polygon'  : 137,
    'BSC'      : 56,
    'Avax'     : 43114,
    'Base'     : 8453,
    'Gnosis'   : 100,
    'CORE'     : 1116,
    'CELO'     : 42220,
    'Moonriver': 1285,
    'Fantom'   : 250,
    'Kava'     : 2222,
    'Linea'    : 59144,
    'Moonbeam' : 1284,
    'zkSync'   : 324,
    'Nova'     : 42170,
    'Harmony'  : 1666600000,
    'Canto'    : 7700,
    'Mantle'   : 5000,
}


def sleeping(sleep_from: int, sleep_to: int):
    delay = random.randint(sleep_from, sleep_to)
    time.sleep(1)
    with tqdm(
            total=delay,
            desc="💤 Sleep",
            bar_format="{desc}: |{bar:20}| {percentage:.0f}% | {n_fmt}/{total_fmt}",
            colour="green"
    ) as pbar:
        for _ in range(delay):
            time.sleep(1)
            pbar.update(1)
    time.sleep(1)
    print()


def get_accounts_data():
    decrypted_data = io.BytesIO()
    with open('./data/accounts_data.xlsx', 'rb') as file:
        if EXCEL_PASSWORD:
            time.sleep(1)
            password = input('Enter the password: ')
            office_file = msoffcrypto.OfficeFile(file)

            try:
                office_file.load_key(password=password)
            except msoffcrypto.exceptions.DecryptionError:
                logger.info('\n⚠️ Incorrect password to decrypt Excel file! ⚠️\n')
                raise DecryptionError('Incorrect password')

            try:
                office_file.decrypt(decrypted_data)
            except msoffcrypto.exceptions.InvalidKeyError:
                logger.info('\n⚠️ Incorrect password to decrypt Excel file! ⚠️\n')
                raise InvalidKeyError('Incorrect password')

            except msoffcrypto.exceptions.DecryptionError:
                logger.info('\n⚠️ Set password on your Excel file first! ⚠️\n')
                raise DecryptionError('Excel without password')

            office_file.decrypt(decrypted_data)

            try:
                wb = pd.read_excel(decrypted_data)
            except ValueError as error:
                logger.info('\n⚠️ Wrong page name! ⚠️\n')
                raise ValueError(f"{error}")
        else:
            try:
                wb = pd.read_excel(file)
            except ValueError as error:
                logger.info('\n⚠️ Wrong page name! ⚠️\n')
                raise ValueError(f"{error}")

        accounts_data = {}
        for index, row in wb.iterrows():
            private_key_evm = row["Private Key EVM"]
            okx_address = row['OKX address']
            accounts_data[int(index) + 1] = {
                "private_key_evm": private_key_evm,
                "okx_wallet": okx_address,
            }

        priv_key_evm, okx_wallet = [], []
        for k, v in accounts_data.items():
            priv_key_evm.append(v['private_key_evm'])
            okx_wallet.append(v['okx_wallet'] if isinstance(v['okx_wallet'], str) else None)

        return combine_lists(priv_key_evm, okx_wallet)


def combine_lists(list1, list2):
    combined_list = []
    length = len(list1)

    for i in range(length):
        combined_list.append((list1[i], list2[i]))

    return combined_list
