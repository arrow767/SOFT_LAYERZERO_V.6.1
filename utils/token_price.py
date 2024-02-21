import requests
from loguru import logger
import json as js
import time

crypto_ids = ['avalanche-2', 'binancecoin', 'ethereum', 'wmatic']

url = 'https://api.coingecko.com/api/v3/simple/price'
param = {'vs_currencies': 'usd'}

crypto_prices = {}

logger.info('I get price tokens: Avax, BNB, ETH, Matic')
logger.info('Please, wait 3 minutes\n')

for crypto_id in crypto_ids:
    param['ids'] = crypto_id
    res = requests.get(url, params=param, timeout=60)
    time.sleep(40)

    jsres = js.loads(res.text)

    if crypto_id in jsres:
        crypto_prices[crypto_id] = float(jsres[crypto_id]['usd'])
    else:
        logger.error(f"Failed to fetch price for {crypto_id}")
        raise ValueError

logger.info('Token price received\n')
