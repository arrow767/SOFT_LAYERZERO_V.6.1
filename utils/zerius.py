from web3 import Web3
from eth_abi.packed import encode_packed
from utils.wallet import Wallet
from utils.func import lz_id_chain, sleeping
from settings import VALUE_33, RETRY, CHAIN_MINT_31, CHAIN_FROM_32, CHAIN_TO_32, TIME_DELAY_ERROR, CHAIN_FROM_33, CHAIN_TO_33
from loguru import logger
import json as js
import random

contracts = {
    'Optimism': Web3.to_checksum_address('0x178608fFe2Cca5d36f3Fc6e69426c4D3A5A74A41'),
    'BSC': Web3.to_checksum_address('0x250c34D06857b9C0A036d44F86d2c1Abe514B3Da'),
    'Polygon': Web3.to_checksum_address('0x178608fFe2Cca5d36f3Fc6e69426c4D3A5A74A41'),
    'Arbitrum': Web3.to_checksum_address('0x250c34D06857b9C0A036d44F86d2c1Abe514B3Da'),
    'Avax': Web3.to_checksum_address('0x178608fFe2Cca5d36f3Fc6e69426c4D3A5A74A41'),
    'Base': Web3.to_checksum_address('0x178608fFe2Cca5d36f3Fc6e69426c4D3A5A74A41'),
    'zkSync': Web3.to_checksum_address('0x7dA50bD0fb3C2E868069d9271A2aeb7eD943c2D6'),
    'Linea': Web3.to_checksum_address('0x5188368a92B49F30f4Cf9bEF64635bCf8459c7A7'),
    'Nova': Web3.to_checksum_address('0x5188368a92B49F30f4Cf9bEF64635bCf8459c7A7'),
    'CORE': Web3.to_checksum_address('0x5188368a92B49F30f4Cf9bEF64635bCf8459c7A7'),
    'CELO': Web3.to_checksum_address('0x4c5AeDA35d8F0F7b67d6EB547eAB1df75aA23Eaf'),
    'Fantom': Web3.to_checksum_address('0x5188368a92B49F30f4Cf9bEF64635bCf8459c7A7'),
    'Gnosis': Web3.to_checksum_address('0x5188368a92B49F30f4Cf9bEF64635bCf8459c7A7'),
    'Moonbeam': Web3.to_checksum_address('0x4c5AeDA35d8F0F7b67d6EB547eAB1df75aA23Eaf'),
    'Harmony': Web3.to_checksum_address('0x5188368a92B49F30f4Cf9bEF64635bCf8459c7A7'),
    'Canto': Web3.to_checksum_address('0x5188368a92B49F30f4Cf9bEF64635bCf8459c7A7'),
    'Mantle': Web3.to_checksum_address('0x5188368a92B49F30f4Cf9bEF64635bCf8459c7A7'),
}

chain_token = {
    'Optimism': 'ETH',
    'BSC': 'BNB',
    'Polygon': 'Matic',
    'Arbitrum': 'ETH',
    'Avax': 'Avax',
    'Base': 'ETH',
    'zkSync': 'ETH',
    'Linea': 'ETH',
    'Nova': 'ETH',
    'CORE': 'Core',
    'CELO': 'Celo',
    'Fantom': 'FTM',
    'Gnosis': 'xDai',
    'Moonbeam': 'GLMR',
    'Harmony': 'HRM',
    'Canto': 'CANTO',
    'Mantle': 'MNT',
    'Metis': 'Metis'
}


REFUEL_CONTRACTS = {
    'Optimism'      : Web3.to_checksum_address('0x2076BDd52Af431ba0E5411b3dd9B5eeDa31BB9Eb'),
    'BSC'           : Web3.to_checksum_address('0x5B209E7c81DEaad0ffb8b76b696dBb4633A318CD'),
    'Arbitrum'      : Web3.to_checksum_address('0x412aea168aDd34361aFEf6a2e3FC01928Fba1248'),
    'Polygon'       : Web3.to_checksum_address('0x2ef766b59e4603250265EcC468cF38a6a00b84b3'),
    'zkSync'        : Web3.to_checksum_address('0xec8afef7afe586eb523c228b6baf3171b1f6dd95'),
    'Avalanche'     : Web3.to_checksum_address('0x5B209E7c81DEaad0ffb8b76b696dBb4633A318CD'),
    'Gnosis'        : Web3.to_checksum_address('0x1fe2c567169d39CCc5299727FfAC96362b2Ab90E'),
    'Fantom'        : Web3.to_checksum_address('0xBFd3539e4e0b1B29e8b08d17f30F1291C837a18E'),
    'Nova'          : Web3.to_checksum_address('0x3Fc5913D35105f338cEfcB3a7a0768c48E2Ade8E'),
    'CORE'          : Web3.to_checksum_address('0xB47D82aA70f839dC27a34573f135eD6dE6CED9A5'),
    'CELO'          : Web3.to_checksum_address('0xFF21d5a3a8e3E8BA2576e967888Deea583ff02f8'),
    'BASE'          : Web3.to_checksum_address('0x9415AD63EdF2e0de7D8B9D8FeE4b939dd1e52F2C'),
    'Linea'         : Web3.to_checksum_address('0x5B209E7c81DEaad0ffb8b76b696dBb4633A318CD'),
    'Avax'          : Web3.to_checksum_address('0x5B209E7c81DEaad0ffb8b76b696dBb4633A318CD'),
    'Base'          : Web3.to_checksum_address('0x9415AD63EdF2e0de7D8B9D8FeE4b939dd1e52F2C'),
    'Moonbeam'      : Web3.to_checksum_address('0xb0bea3bB2d6EDDD2014952ABd744660bAeF9747d'),
    'Harmony'       : None,
    'Canto'         : None,
    'Mantle'        : Web3.to_checksum_address('0x4F1C698e5cA32b28030E9d9F17C164F27aB5D866'),
    'Metis'         : Web3.to_checksum_address('0x1b07F1f4F860e72c9367e718a30e38130114AD22'),

}


def zerius(key, number, act):

    for _ in range(RETRY):
        try:

            if act == 'mint':
                from_chain = random.choice(CHAIN_MINT_31)

                zer = Zerius(key, from_chain, from_chain, number)
                return zer.mint_nft()

            elif act == 'bridge':

                chain_path = CHAIN_FROM_32.copy()
                random.shuffle(chain_path)

                for chain in chain_path:

                    from_chain = chain

                    zer = Zerius(key, from_chain, from_chain, number)
                    nft_id = zer.get_nft_id()
                    if nft_id == 0:
                        continue

                    to_chain = random.choice(CHAIN_TO_32)
                    if from_chain == to_chain:
                        continue

                    zer = Zerius(key, from_chain, to_chain, number)
                    return zer.bridge_nft(nft_id)

            elif act == 'refuel':
                from_chain = random.choice(CHAIN_FROM_33)
                to_chain = random.choice(CHAIN_TO_33)

                if from_chain == to_chain:
                    raise ValueError

                zer = Zerius(key, from_chain, to_chain, number)
                value = round(random.uniform(VALUE_33[0], VALUE_33[1]), VALUE_33[2])
                return zer.refuel(value)

        except Exception as error:
            logger.error(f'{error}\n')
            sleeping(TIME_DELAY_ERROR[0], TIME_DELAY_ERROR[1])
            continue


class Zerius(Wallet):

    def __init__(self, private_key, chain_from, chain_to, number):
        super().__init__(private_key, chain_from, number)
        self.abi_bridge = js.load(open('./abi/zerius/bridge_nft.txt'))
        self.abi_refuel = js.load(open('./abi/zerius/refuel.txt'))
        self.chain_to = chain_to
        self.contract_bridge = self.web3.eth.contract(address=contracts[self.chain], abi=self.abi_bridge)
        self.contract_refuel = self.web3.eth.contract(address=REFUEL_CONTRACTS[self.chain], abi=self.abi_refuel)

    def get_nft_id(self):
        count = self.contract_bridge.functions.balanceOf(self.address_wallet).call()
        if count == 0:
            return 0
        tokens_arr = [self.contract_bridge.functions.tokenOfOwnerByIndex(self.address_wallet, i).call() for i in range(count)]
        return random.choice(tokens_arr)

    def mint_nft(self):

        logger.info(f'Mint NFT {self.chain} on Zerius')

        contract_bridge = self.web3.eth.contract(address=contracts[self.chain], abi=self.abi_bridge)

        value = contract_bridge.functions.mintFee().call()
        dick = {
            'from': self.address_wallet,
            'value': value,
            'nonce': self.web3.eth.get_transaction_count(self.address_wallet),
            **self.get_gas_price()
        }
        txn = contract_bridge.functions.mint(Web3.to_checksum_address('0xCC05E5454D8eC8F0873ECD6b2E3da945B39acA6C')).build_transaction(dick)

        self.send_transaction_and_wait(txn, f'Mint NFT {self.chain} on Zerius')

    def bridge_nft(self, token_id):
        logger.info(f'Bridge {token_id} NFT || {self.chain} -> {self.chain_to}')

        min_dst_gas = self.contract_bridge.functions.minDstGasLookup(lz_id_chain[self.chain_to], 1).call()

        if min_dst_gas == 0:
            logger.error(f'You cannot bridge on the {self.chain_to} network')
            raise ValueError

        adapter_params = encode_packed(
            ["uint16", "uint256"],
            [1, min_dst_gas]
        )

        native_fee, _ = self.contract_bridge.functions.estimateSendFee(
            lz_id_chain[self.chain_to],
            self.address_wallet,
            token_id,
            False,
            adapter_params
        ).call()

        contract_txn = self.contract_bridge.functions.sendFrom(
                self.address_wallet,
                lz_id_chain[self.chain_to],
                self.address_wallet,
                token_id,
                self.address_wallet,
                '0x0000000000000000000000000000000000000000',
                adapter_params
            ).build_transaction(
                {
                    "from": self.address_wallet,
                    "value": native_fee,
                    "nonce": self.web3.eth.get_transaction_count(self.address_wallet),
                    ** self.get_gas_price()
                }
            )

        self.send_transaction_and_wait(contract_txn, f'Bridge {token_id} NFT || {self.chain} -> {self.chain_to}')

    def check_price_nft(self):

        text = f'{self.chain} -> {self.chain_to}'.center(19)

        min_dst_gas = self.contract_bridge.functions.minDstGasLookup(lz_id_chain[self.chain_to], 1).call()

        if min_dst_gas == 0:
            logger.error(f'{text} || You cannot bridge on the {self.chain_to} network')
            return 1000

        adapter_params = encode_packed(
            ["uint16", "uint256"],
            [1, min_dst_gas]
        )

        native_fee, _ = self.contract_bridge.functions.estimateSendFee(
            lz_id_chain[self.chain_to],
            self.address_wallet,
            1,
            False,
            adapter_params
        ).call()

        logger.info(f'{text} || Network bridge costs - {Web3.from_wei(native_fee, "ether")} {chain_token[self.chain]}')

        return {Web3.from_wei(native_fee, "ether")}

    def refuel(self, value):

        logger.info(f'Zerius refuel from {self.chain} to {self.chain_to}')
        amount = Web3.to_wei(value, 'ether')

        min_dst_gas = self.contract_refuel.functions.minDstGasLookup(lz_id_chain[self.chain_to], 0).call()

        if REFUEL_CONTRACTS[self.chain_to] is None:
            logger.error(f'You cannot get refuel on the {self.chain_to} network')
            raise ValueError

        if min_dst_gas == 0:
            logger.error(f'You cannot get gas on the {self.chain_to} network')
            raise ValueError

        adapter_params = encode_packed(
            ["uint16", "uint256", "uint256", "address"],
            [2, min_dst_gas, amount, self.address_wallet]
        )

        dst_contract_address = encode_packed(["address"], [REFUEL_CONTRACTS[self.chain_to]])
        send_value = self.contract_refuel.functions.estimateSendFee(lz_id_chain[self.chain_to], dst_contract_address, adapter_params).call()

        contract_txn = self.contract_refuel.functions.refuel(
            lz_id_chain[self.chain_to],
            dst_contract_address,
            adapter_params
        ).build_transaction(
            {
                "from": self.address_wallet,
                "value": send_value[0],
                "nonce": self.web3.eth.get_transaction_count(self.address_wallet),
                ** self.get_gas_price()
            }
        )

        self.send_transaction_and_wait(contract_txn, f'Zerius refuel from {self.chain} to {self.chain_to}')

    def check_price_gas(self):

        text = f'{self.chain} -> {self.chain_to}'.center(19)

        if REFUEL_CONTRACTS[self.chain_to] is None:
            logger.error(f'{text} || You cannot get refuel on the {self.chain_to} network')
            return 1000

        min_dst_gas = self.contract_refuel.functions.minDstGasLookup(lz_id_chain[self.chain_to], 0).call()

        if min_dst_gas == 0:
            logger.error(f'{text} || You cannot get refuel on the {self.chain_to} network')
            return 1000

        amount = Web3.to_wei(0.000000000000001, 'ether')

        adapter_params = encode_packed(
            ["uint16", "uint256", "uint256", "address"],
            [2, min_dst_gas, amount, self.address_wallet]
        )

        dst_contract_address = encode_packed(["address"], [REFUEL_CONTRACTS[self.chain_to]])

        send_value = self.contract_refuel.functions.estimateSendFee(lz_id_chain[self.chain_to], dst_contract_address, adapter_params).call()

        logger.info(f'{text} || Network refuel costs - {Web3.from_wei(send_value[0], "ether")} {chain_token[self.chain]}')

        return Web3.from_wei(send_value[0], "ether")
