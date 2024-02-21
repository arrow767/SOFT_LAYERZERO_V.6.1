from utils.chain import *

CHAIN_RPC = {
    'Arbitrum' : 'https://1rpc.io/arb',
    'Optimism' : 'https://1rpc.io/op',
    'Polygon'  : 'https://1rpc.io/matic',
    'BSC'      : 'https://rpc.ankr.com/bsc/',
    'Avax'     : 'https://rpc.ankr.com/avalanche/',
    'Base'     : 'https://1rpc.io/base',
    'Gnosis'   : 'https://rpc.ankr.com/gnosis',
    'CORE'     : 'https://1rpc.io/core',
    'CELO'     : 'https://rpc.ankr.com/celo',
    'Moonriver': 'https://moonriver.publicnode.com',
    'Fantom'   : 'https://rpc.ankr.com/fantom',
    'Kava'     : 'https://kava-pokt.nodies.app',
    'Linea'    : 'https://1rpc.io/linea',
    'Metis'    : 'https://metis-pokt.nodies.app'
}

REFUEL_CHAIN_LIST_BUNGEE = [Arbitrum, Polygon, BSC]
REFUEL_CHAIN_LIST_STELLA = [Arbitrum, Polygon, BSC]

REFUEL_BUNGEE = {

    'Arbitrum': {
        'min value': 0.001,
        'token min': 0.000001,
        'token max': 0.000005,
    },

    'Polygon': {
        'min value': 1,
        'token min': 0.1,
        'token max': 0.5,
    },

    'BSC': {
        'min value': 0.005,
        'token min': 0.0001,
        'token max': 0.0005,
    },

    'Avax': {
        'min value': 0.025,
        'token min': 0.0001,
        'token max': 0.0005,
    },
}

RETRY = 10
TIME_DELAY = [300, 400]           # Задержка после транзакций  [min, max]
TIME_DELAY_ERROR = [10, 15]      # Задержка после ошибок      [min, max]

SHUFFLE_WALLETS = False

BSC_GWEI = [1.1, 1.2]

SLIPPAGE_STARGATE = 1

OX_API_KEY = '951f01b4-073b-415b-be7d-60d2087876d5'
SLIPPAGE_OX_SWAP = 1    # При свапе больших сумма ставьте слипаж 0.01

EXCEL_PASSWORD = False  # Если поставиили пароль на Exel таблицу пишет True. В консоли попросят его ввести

MAX_GAS = 500

OKX_REFUEL = True
OKX_CHAIN_REFUEL = [Arbitrum, Optimism, Polygon, BSC, Fantom, Base, Core, Linea, Celo, Moonriver]

REFUEL_OKX = {

    'Arbitrum': {
        'min value': 0.001,
        'token min': 0.000001,
        'token max': 0.000005,
    },

    'Optimism': {
        'min value': 0.001,
        'token min': 0.000001,
        'token max': 0.000005,
    },

    'Polygon': {
        'min value': 1,
        'token min': 0.2,
        'token max': 0.5,
    },

    'BSC': {
        'min value': 0.005,
        'token min': 0.0001,
        'token max': 0.0005,
    },

    'Avax': {
        'min value': 0.025,
        'token min': 0.0001,
        'token max': 0.0005,
    },

    'Fantom': {
        'min value': 4,
        'token min': 0.1,
        'token max': 0.5,
    },

    'Base': {
        'min value': 0.002,
        'token min': 0.00001,
        'token max': 0.00005,
    },

    'CORE': {
        'min value': 0.8,
        'token min': 0.01,
        'token max': 0.05,
    },

    'Linea': {
        'min value': 0.002,
        'token min': 0.00001,
        'token max': 0.00005,
    },

    'CELO': {
        'min value': 1,
        'token min': 0.01,
        'token max': 0.03,
    },

    'Moonriver': {
        'min value': 0.35,
        'token min': 0.01,
        'token max': 0.02,
    }
}

OKX_KEYS = {             # обязательно юзать
    'api_key'   : '867e5254-b764-4e9f-b365-22dd44f26427',
    'api_secret': '22943F39DA044C4F0230E0A4A6F21DC1',
    'password'  : 'Dolgi_debil1',
    }

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Stargate bridge USDC (Список доступных сетей: Arbitrum, Optimism, Polygon, BSC, Avax, Fantom, Base

# Module 1 - Stargate bridge USDC with OKX

USDC_OKX_WIHDRAWL_1 = [1300, 1500]                          # Кол-во USDC для вывода [min, max]
START_CHAIN_1       = [Polygon]                             # Стартовая сеть (Можно указать несколько через запятую, будет рандомная)
                                                              # Доступны Optimism, Polygon  (Если сеть будет Polygon то выведутся обычные USDC которые свапнуться в USDC.E (Так дешевле))

CHAIN_PATH_1        = [Polygon, Base]                       # Сюда пишем список сетей для круга + тут должны быть все стартовые сети которые вы указали

# Module 2 - Stargate bridge USDC without OKX

CHAIN_PATH_2        = [Arbitrum, Polygon, BSC]              # Сюда пишем список сетей для круга
                                                              # Стартовая сеть выберется из списка там где больше баланса

# Module 3 - Stargate bridge USDC Lite

AUTO_CHAIN_3 = True
CHAIN_PATH_3 = [Arbitrum, Polygon, BSC, Fantom]                 # Список сетей которые будут смотреться (Если AUTO_CHAIN_3 = True)
CHAIN_FROM_3 = Arbitrum                                         # Стартовая сеть если AUTO_CHAIN_3 = False
CHAIN_TO_3   = Polygon                                          # Конечная сеть

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Stargate bridge STG (Список доступных сетей: Arbitrum, Optimism, Polygon, BSC, Avax, Fantom, Base, Linea, Kava]

# Module 4 - Stargate bridge STG with OKX  # Стартовая сеть всегда Arbitrum
# Refuel в сеть Kava пока не доступен, поэтому выводите или руками или не включайте эту сеть

USDC_OKX_WIHDRAWL_4 = [400, 500]                                        # Кол-во USDC для вывода [min, max]
CHAIN_PATH_4        = [Optimism, Polygon, BSC, Fantom, Base, Linea]     # Сюда пишем список сетей для круга (Сеть Arbitrum вписывать ненадо)

# Module 5 - Buy STG Token (Chain - Arbitrum)

USDC_AMOUNT_SWAP_5 = [100, 200]  # Сумма свапа USDC -> STG

# Module 6 - Stargate bridge STG without OKX (Стартовая сеть там где больше баланса STG)

CHAIN_PATH_6        = [Arbitrum, Polygon, BSC, Fantom, Base]            # Сюда пишем список сетей для круга

# Module 7 - Stargate bridge STG Lite

AUTO_CHAIN_7 = True
CHAIN_PATH_7 = [Arbitrum, Polygon, BSC, Fantom, Linea]              # Список сетей которые будут смотреться (Если AUTO_CHAIN_7 = True)
CHAIN_FROM_7 = Polygon                                              # Стартовая сеть если AUTO_CHAIN_7 = False
CHAIN_TO_7   = Arbitrum                                             # Конечная сеть

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Module 9 - Stargate bridge ETH with OKX     # (Список доступных сетей: Arbitrum, Optimism, Base, Linea

ETH_OKX_WIHDRAWL_9  = [0.1, 0.2]              # Количество ETH для вывода [min, max]
START_CHAIN_9       = [Arbitrum, Base]        # Вывод доступен в любую сеть
CHAIN_PATH_9        = [Arbitrum, Base]        # Сюда пишем списк сетей для круга (должны быть вписаны все стартовые сети)

# Module 10 - Stargate bridge ETH without OKX

CHAIN_PATH_10        = [Arbitrum, Optimism, Base, Linea]      # Сюда пишем список сетей для круга
                                                              # Стартовая сеть выберется из списка там где больше баланса

# Module 11 - Stargate bridge ETH Lite

AUTO_CHAIN_11 = True
CHAIN_PATH_11 = [Arbitrum, Optimism, Base, Linea]  # Список сетей которые будут смотреться (Если AUTO_CHAIN_3 = True)
CHAIN_FROM_11 = 0
CHAIN_TO_11   = Base

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Bitcoin Bridge  # (Список доступных сетей: Arbitrum, Optimism, Polygon, BSC, Avax

# Module 13 - Buy BTC Token (Chain - Avax)

USDC_AMOUNT_SWAP_13 = [100, 200]            # Кол-во USDC для свапа на BTC [min, max]

# Module 14 - Bitcoin bridge without OKX

CHAIN_PATH_14       = [Arbitrum, Polygon, BSC, Optimism, Avax]      # Сюда пишем список сетей для круга
                                                              # Стартовая сеть выберется из списка там где больше баланса

# Module 15 - Bitcoin bridge Lite

AUTO_CHAIN_15 = True
CHAIN_PATH_15 = [Arbitrum, Polygon, BSC, Optimism]  # Список сетей которые будут смотреться (Если AUTO_CHAIN_3 = True)
CHAIN_FROM_15 = 0                                   # Стартовая сеть если AUTO_CHAIN_15 = False
CHAIN_TO_15   = Avax                             # Конечная сеть

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Module 17 - Abracadabra bridge with OKX     ( У Abracadabra окх всегда стартовая сеть это Arbitrum тк там есть ликвидность для свапа USDC -> MIM )
# Список доступных сетей: Polygon, BSC, Base, Moonriver, Optimism, Avax, Fantom, Kava

USDC_OKX_WIHDRAWL_17 = [600, 700]                                                             # Кол-во USDC для вывода [min, max]
CHAIN_PATH_17        = [Base, Moonriver, Linea]                                                      # Стартовую сеть Arbitrum сюда не пишите

# Module 18 - Buy MIM Token (Chain - Arbitrum)

USDC_AMOUNT_SWAP_18 = [100, 200]   # Кол-во USDC для свапа на MIM

# Module 19 - Abracadabra bridge without OKX

CHAIN_PATH_19        = [Arbitrum, Polygon, BSC, Base, Moonriver, Optimism, Avax, Fantom, Kava]  # Сюда пишем список сетей для круга
                                                                                                # Стартовая сеть выберется из списка там где больше баланса

# Module 20 - Abracadabra bridge Lite

AUTO_CHAIN_20 = True
CHAIN_PATH_20 = [Arbitrum, Polygon, BSC, Fantom, Base, Linea]        # Список сетей которые будут смотреться (Если AUTO_CHAIN_20 = True)
CHAIN_FROM_20 = 0                                       # Стартовая сеть если AUTO_CHAIN_20 = False
CHAIN_TO_20   = Arbitrum                                 # Конечная сеть

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Module 21 - CORE bridge with OKX     (У CORE bridge сеть только Polygon )

USDC_OKX_WIHDRAWL_21 = [700, 800]       # Кол-во USDC для вывода [min, max]

# Module 22 - CORE bridge (Тут количество транз набивается только из Polygon -> CORE (Без ОКХ)

NUMBER_OF_TRANSACTIONS_22 = [2, 3]  # Количество транзакций [min, max]

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Angle Money    Поддерживаемые сети: (Polygon, Gnosis, CELO)

# Свап MATIC -> EUR (Сеть Polygon)

MATIC_AMOUNT_SWAP_25 = [0.1, 0.2]   # Количество МАТИКА для свапа на EUR [min, max]

# Module 28 Angle Money bridge EUR from Gnosis/CELO to Gnosis/CELO (С повторениями)

NUMBER_OF_TRANSACTIONS_28 = [2, 3]  # Количество транзакций [min, max]

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Zerius  Поддерживаемые сети:  From : Optimism, BSC, Polygon, Arbitrum, Avax, Base, Linea, Core, Celo, Fantom, Gnosis
#                                 To : Optimism, BSC, Polygon, Arbitrum, Avax, Base, Linea, Core, Celo, Fantom, Gnosis, Moonbeam, Harmony, Canto, Mantle, Nova, zkSync

# Module 31 - Mint NFT

CHAIN_MINT_31 = [BSC, Polygon, Fantom, Celo, Gnosis]                                   # Сеть для минта НФТ (Будет выбрана рандомно из списка)

# Module 32 - Bridge NFT

CHAIN_FROM_32 = [BSC]                                   # Пройдется по этому списку. Там где будет НФТ там и будет стартовая сеть
CHAIN_TO_32   = [Metis]   # Сеть получения (Будет выбрана рандомно из списка)

# Module 33 - Refuel

VALUE_33      = [0.0000001, 0.00000001, 9]                                             # от какого кол-ва нативного токена сети CHAIN_TO_33 получаем [min, max, decimal]
CHAIN_FROM_33 = [BSC]                                   # Сеть старта (Будет выбрана рандомно из списка)
CHAIN_TO_33   = [Metis]   # Сеть получения (Будет выбрана рандомно из списка)

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Merkly  Поддерживаемые сети:  From : Optimism, BSC, Polygon, Arbitrum, Avax, Core, Celo, Fantom, Gnosis,
#                                 To : Optimism, BSC, Polygon, Arbitrum, Avax, Base, Linea, Core, Celo, Fantom, Gnosis, Moonbeam, Harmony, Canto, Mantle, Nova, Moonriver, zkSync,
#                                      ShimmerEVM, Fuse, Beam, Tomo, DFK

# Module 34 - Merkly Refuel

VALUE_34      = [0.0000001, 0.00000001, 9]                                                                                              # от какого кол-ва нативного токена сети CHAIN_TO_34 получаем [min, max, decimal]
CHAIN_FROM_34 = [BSC, Polygon, Fantom, Celo, Gnosis]                                                                                    # Сеть старта (Будет выбрана рандомно из списка)
CHAIN_TO_34   = [Core, Celo, Fantom, Gnosis, Moonbeam, Harmony, Canto, Mantle, Nova, Moonriver, ShimmerEVM, Fuse, Beam, Tomo, DFK]      # Сеть получения (Будет выбрана рандомно из списка)

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Module 35 - Stake STG  Поддерживаемые сети: Polygon, BSC, Arbitrum, Avax

VALUE_35      = {                # Какое кол-во нативных токенов менять на STG токен
    Polygon : [0.01, 0.02, 3],      # [min, max, decimal]
    BSC     : [0.00004, 0.00005, 6],
    Arbitrum: [0.00001, 0.00002, 6],
    Avax    : [0.001, 0.002, 4]
}
CHAIN_35 = [BSC, Polygon] # Сеть для стейкинга. Если сетей будет несколько то будет выбрана рандомная

# Module 36 - Transfer USDC to OKX recepient

CHAIN_FROM_37 = Polygon  # Где лежат USDC для трансфера   Arbitrum or Optimism or Polygon
