from web3 import Web3
from eth_abi import encode
from utils.wallet import Wallet
from utils.func import lz_id_chain, sleeping
from settings import VALUE_34, RETRY, TIME_DELAY_ERROR, CHAIN_FROM_34, CHAIN_TO_34
from loguru import logger
import json as js
import random

contracts = {
    'Optimism': Web3.to_checksum_address('0xD7bA4057f43a7C4d4A34634b2A3151a60BF78f0d'),
    'BSC': Web3.to_checksum_address('0xeF1eAE0457e8D56A003d781569489Bc5466E574b'),
    'Polygon': Web3.to_checksum_address('0x0E1f20075C90Ab31FC2Dd91E536e6990262CF76d'),
    'Arbitrum': Web3.to_checksum_address('0x4Ae8CEBcCD7027820ba83188DFD73CCAD0A92806'),
    'Avax': Web3.to_checksum_address('0x5C9BBE51F7F19f8c77DF7a3ADa35aB434aAA86c5'),
    'zkSync': Web3.to_checksum_address('0x5673B6e6e51dE3479B8deB22dF46B12308db5E1e'),
    'Nova': Web3.to_checksum_address('0xB6789dACf323d60F650628dC1da344d502bC41E3'),
    'CORE': Web3.to_checksum_address('0xa513F61Bc23F0eB1FC0aC4d9dab376d79bC7F3cB'),
    'CELO': Web3.to_checksum_address('0xC20A842e1Fc2681920C1A190552A2f13C46e7fCF'),
    'Fantom': Web3.to_checksum_address('0xF56605276cefffe32DFD8B6bF80B93c2A6840136'),
    'Gnosis': Web3.to_checksum_address('0x556F119C7433b2232294FB3De267747745A1dAb4'),
    'Moonbeam': Web3.to_checksum_address('0x671861008497782F7108D908D4dF18eBf9598b82'),
    'Moonriver': Web3.to_checksum_address('0xd379c3D0930d70022B3C6EBA8217e4B990705540'),
}


def merkly(key, number):

    for _ in range(RETRY):
        try:
            from_chain = random.choice(CHAIN_FROM_34)
            to_chain = random.choice(CHAIN_TO_34)

            if from_chain == to_chain:
                raise ValueError

            zer = Merkly(key, from_chain, to_chain, number)
            zer.refuel()
            return

        except Exception as error:
            logger.error(f'{error}\n')
            sleeping(TIME_DELAY_ERROR[0], TIME_DELAY_ERROR[1])
            continue


class Merkly(Wallet):

    def __init__(self, private_key, chain_from, chain_to, number):
        super().__init__(private_key, chain_from, number)
        self.abi = js.load(open('./abi/merkly/refuel.txt'))
        self.chain_to = chain_to
        self.contract = self.web3.eth.contract(address=contracts[self.chain], abi=self.abi)

    def refuel(self):

        logger.info(f'Merkly refuel from {self.chain} to {self.chain_to}')
        # amount = Web3.to_wei(round(random.uniform(VALUE_34[0], VALUE_34[1]), VALUE_34[2]), 'ether')
        amount = Web3.to_wei(0.000000001, 'ether')
        amount_wei = Web3.to_hex(encode(["uint"], [amount]))
        adapter_params = "0x00020000000000000000000000000000000000000000000000000000000000030d40" + amount_wei[2:] + self.address_wallet[2:]
        send_value = self.contract.functions.estimateSendFee(lz_id_chain[self.chain_to], '0x', adapter_params).call()[0]

        dick = {
            'from': self.address_wallet,
            'value': int(send_value * 1.1),
            'nonce': self.web3.eth.get_transaction_count(self.address_wallet),
            **self.get_gas_price()
        }

        contract_txn = self.contract.functions.bridgeGas(lz_id_chain[self.chain_to],
                                                         self.address_wallet,
                                                         adapter_params).build_transaction(dick)

        self.send_transaction_and_wait(contract_txn, f'Merkly refuel from {self.chain} to {self.chain_to}')
