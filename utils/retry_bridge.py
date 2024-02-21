from web3.exceptions import TransactionNotFound
from utils.func import sleeping
from settings import RETRY, TIME_DELAY_ERROR
from loguru import logger
from utils.refuel import Refuel


def exception_handler(func):
    def wrapper(self, *args, **kwargs):
        for _ in range(RETRY):

            try:
                return func(self, *args, **kwargs)

            except TransactionNotFound:
                logger.error('Транзакция не смайнилась за долгий промежуток времени, пытаюсь еще раз')
                sleeping(TIME_DELAY_ERROR[0], TIME_DELAY_ERROR[1])

            except ConnectionError:
                logger.error('Ошибка подключения к интернету или проблемы с РПЦ')
                sleeping(TIME_DELAY_ERROR[0], TIME_DELAY_ERROR[1])

            except Exception as error:
                logger.error('Произошла ошибка')

                if isinstance(error.args[0], str):
                    if 'not enough balance' in error.args[0]:
                        logger.info('Нет ликвидности для трансфера в эту сеть')
                        sleeping(TIME_DELAY_ERROR[0], TIME_DELAY_ERROR[1])
                        return 'error'

                    elif error.args[0] == "balance":
                        logger.info('Need Refuel\n')
                        refuel = Refuel(self.private_key, self.number)
                        refuel.refuel(self.chain)

                    elif 'is not in the chain after' in error.args[0]:
                        logger.info('Транзакция не смайнилась за долгий промежуток времени. Пытаюсь еще раз')

                    elif 'swap 0' in error.args[0]:
                        logger.info('Нечего переводить. У вас 0 usdc на балансе\n')

                    elif 'slippage too' in error.args[0]:
                        logger.info('Огромный slippage для трансфера в эту сеть, удаляю ее\n')
                        sleeping(TIME_DELAY_ERROR[0], TIME_DELAY_ERROR[1])
                        return 'error'

                    else:
                        logger.info(error)

                elif isinstance(error.args[0], dict):
                    if 'nsufficien' in error.args[0]['message'] or 'required exceeds allowance' in error.args[0]['message']:
                        logger.info('Need Refuel\n')
                        refuel = Refuel(self.private_key, self.number)
                        refuel.refuel(self.chain)

                    elif 'execute this request' in error.args[0]['message']:
                        logger.info('Ошибка запроса на RPC, пытаюсь еще раз')

                    elif 'ax fee per gas' in error.args[0]['message']:
                        logger.info('Ошибка газа, пытаюсь еще раз')

                    else:
                        logger.info(f'{error}\n')

                else:
                    logger.info(f'{error}\n')
                sleeping(TIME_DELAY_ERROR[0], TIME_DELAY_ERROR[1])
        else:
            logger.error('The number of iterations of the loop has ended\n')
            return False
    return wrapper
