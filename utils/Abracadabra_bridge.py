from utils.wallet import Wallet
from loguru import logger
from web3 import Web3
import json as js
from utils.retry_bridge import exception_handler
from utils.func import lz_id_chain, sleeping


address_abracadabra = {
    'Arbitrum': Web3.to_checksum_address('0x287176dfBEC7E8cee0f876FC7B52960ee1784AdC'),
    'Optimism': Web3.to_checksum_address('0x287176dfBEC7E8cee0f876FC7B52960ee1784AdC'),
    'Polygon': Web3.to_checksum_address('0x287176dfBEC7E8cee0f876FC7B52960ee1784AdC'),
    'BSC': Web3.to_checksum_address('0x287176dfBEC7E8cee0f876FC7B52960ee1784AdC'),
    'Avax': Web3.to_checksum_address('0x287176dfBEC7E8cee0f876FC7B52960ee1784AdC'),
    'Moonriver': Web3.to_checksum_address('0x287176dfBEC7E8cee0f876FC7B52960ee1784AdC'),
    'Fantom': Web3.to_checksum_address('0x287176dfBEC7E8cee0f876FC7B52960ee1784AdC'),
    'Base': Web3.to_checksum_address('0x4035957323fc05ad9704230e3dc1e7663091d262'),
    'Kava': Web3.to_checksum_address('0x287176dfBEC7E8cee0f876FC7B52960ee1784AdC'),
    'Linea': Web3.to_checksum_address('0x60bbefe16dc584f9af10138da1dfbb4cdf25a097')
}


class Abracadabra(Wallet):

    def __init__(self, private_key, chain_from, chain_to, number):
        super().__init__(private_key, chain_from, number)
        self.abi = js.load(open('./abi/abracadabra/abracadabra.txt'))
        self.abi_old = js.load(open('./abi/abracadabra/abracadabra_old.txt'))
        self.chain_to = chain_to

    def get_fees(self):

        address_bytes = bytes.fromhex(self.address_wallet[2:])
        address_bytes_32 = bytes(12) + address_bytes
        tx_data = (
            "0x000200000000000000000000000000000000000000000000000000000000000186a"
            "00000000000000000000000000000000000000000000000000000000000000000"
            f"{self.address_wallet[2:]}"
        )

        if self.chain in ['Linea', 'Base']:
            abracadabra_contract = self.web3.eth.contract(address=address_abracadabra[self.chain], abi=self.abi_old)
            return abracadabra_contract.functions.estimateSendFee(lz_id_chain[self.chain_to], address_bytes_32, 1, True, tx_data).call()[0]
        else:
            abracadabra_contract = self.web3.eth.contract(address=address_abracadabra[self.chain], abi=self.abi)
            return abracadabra_contract.functions.estimateSendFeeV2(lz_id_chain[self.chain_to], address_bytes_32, 1, tx_data).call()[0]

    @exception_handler
    def start_bridge(self):
        logger.info(f'Abracadabra bridge || {self.chain} -> {self.chain_to}')

        if self.chain in ['Linea', 'Base']:
            abracadabra_contract = self.web3.eth.contract(address=address_abracadabra[self.chain], abi=self.abi_old)
        else:
            abracadabra_contract = self.web3.eth.contract(address=address_abracadabra[self.chain], abi=self.abi)

        address_bytes = bytes.fromhex(self.address_wallet[2:])
        address_bytes_32 = bytes(12) + address_bytes
        tx_data = (
            "0x000200000000000000000000000000000000000000000000000000000000000186a"
            "00000000000000000000000000000000000000000000000000000000000000000"
            f"{self.address_wallet[2:]}"
        )
        if self.chain not in ['Linea', 'Base']:
            allowance = self.get_allowance_token('MIM', address_abracadabra[self.chain])
            if allowance < 100000 * 10 ** self.get_decimal_token("MIM"):
                logger.info('Need Approve')
                self.approve('MIM', address_abracadabra[self.chain])
                sleeping(50, 70)

        token_balance = self.get_balance_token('MIM')
        balance = self.get_native_balance()
        fees = self.get_fees()
        self.check_gas_cost()

        if int(fees * 1.4) > int(balance):
            raise ValueError('balance')

        dick = {
            'from': self.address_wallet,
            'value': int(fees * 1.2),
            'nonce': self.web3.eth.get_transaction_count(self.address_wallet),
            ** self.get_gas_price()
        }

        zro_payment_address = '0x0000000000000000000000000000000000000000'
        call_params = (self.address_wallet, zro_payment_address, tx_data)

        if self.chain in ['Linea', 'Base']:
            swap_txn = abracadabra_contract.functions.sendFrom(self.address_wallet,
                                                               lz_id_chain[self.chain_to],
                                                               address_bytes_32,
                                                               token_balance,
                                                               call_params).build_transaction(dick)
        else:
            swap_txn = abracadabra_contract.functions.sendProxyOFTV2(lz_id_chain[self.chain_to],
                                                                     address_bytes_32,
                                                                     token_balance,
                                                                     call_params).build_transaction(dick)

        tx_hash = self.send_transaction_and_wait(swap_txn, f'Abracadabra bridge || {self.chain} -> {self.chain_to}')

        self.check_transaction_stargate(tx_hash.hex())
