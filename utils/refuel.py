from utils.okx import Okx
from utils.refuel_stella import RefuelStella
from utils.refuel_bungee import RefuelBungee
from loguru import logger
from utils.func import sleeping


class Refuel(Okx, RefuelBungee, RefuelStella):
    def __init__(self, private_key, number):
        self.private_key = private_key
        self.number = number

    def refuel(self, chain_to):
        refuel_func = [Okx(self.private_key, self.number).withdrawl,
                       RefuelBungee(self.private_key, self.number).refuel,
                       RefuelStella(self.private_key, self.number).refuel]

        for func in refuel_func:
            try:
                res = func(chain_to)
                if res is False:
                    continue
                break
            except:
                continue
        else:
            logger.error('It is impossible to make a refuel. Withdraw money manually\n')
            sleeping(200, 250)
