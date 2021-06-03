# coding:utf-8
"""
@Time :    2021/6/2 下午4:57
@Author:  chuwt
"""
from typing import List, Dict, Optional

from blspy import G1Element

from chia.util.byte_types import hexstr_to_bytes
from chia.util.bech32m import decode_puzzle_hash, encode_puzzle_hash
from chia.consensus.coinbase import create_puzzlehash_for_pk
from chia.types.blockchain_format.coin import Coin
from chia.types.blockchain_format.program import Program
from chia.wallet.puzzles.p2_delegated_puzzle_or_hidden_puzzle import puzzle_for_pk
from chia.types.blockchain_format.sized_bytes import bytes32


def generate_xch_address_from_pk(pk: str) -> str:
    return encode_puzzle_hash(create_puzzlehash_for_pk(G1Element.from_bytes(hexstr_to_bytes(pk))), "xch")


def puzzle_hash_to_xch_address(puzzle_hash: str) -> str:
    return encode_puzzle_hash(hexstr_to_bytes(puzzle_hash), "xch")


def xch_address_to_puzzle_hash(xch_address: str) -> str:
    return "0x" + decode_puzzle_hash(xch_address).hex()


def create_unsigned_tx(from_pk: str, send_list: List[Dict], utxo: List, fee: int):
    """
    from_pk
    send_list
    utxo
    """
    outputs = []
    for to in send_list:
        address = to.get("address", None)
        if not address:
            raise ValueError(f"Address is null in send list")
        amount = to.get("amount", 0)
        if amount <= 0:
            raise ValueError(f"Amount must greater than 0")
        # address to puzzle hash
        puzzle_hash = xch_address_to_puzzle_hash(address)

        outputs.append({"puzzle_hash": puzzle_hash, "amount": amount})
    # 判断utxo的数量和发送的数量关系
    coins = set([Coin.from_json_dict(coin_json) for coin_json in utxo])

    if sum([t.get("amount") for t in outputs]) + fee > sum([coin.amount for coin in coins]):
        raise ValueError("Insufficient balance")

    primary_announcement_hash: Optional[bytes32] = None

    for coin in coins:
        puzzle: Program = puzzle_for_pk(G1Element.from_bytes(hexstr_to_bytes(from_pk)))


if __name__ == "__main__":
    """测试私钥
    Fingerprint: 563730848
    
    master private key: 6971ac2114952dfa1e4c8e8053308aa115bd75aa890a7d82a45718f334329191
    
    master public key: b2d709611a67e5224cbe9010739b138356e88bbdc4b91a833a489213bab9ad39cfee9c93e0fc3c70a0c4a6b6c5ada8b5
    
    Farmer public key (m/12381/8444/0/0): b69b74794fa16c4569af42401615948094ad076795627d88f08e5f1626ec3e2dda47376db481dd3ecdf0585b960b80cf
    
    Pool public key (m/12381/8444/1/0): 8b417b4310ecb7fd68e8c39e0fa0e334edd3c8c93eca9985a3f398846f9429142993196416199436718f3ec26609e618
    """
    print("xch_address:",
          generate_xch_address_from_pk(
              "aaf079d607cabb95c0039c51317cd6e84e66bb6b5c9aecf8fdc4f0ba97c7f2ec8bb2b1831ad3ea0ba8f701a26177e43e"))

    print("puzzle_hash:",
          xch_address_to_puzzle_hash("xch1knrllhacj7j2m7xqt64klys3kfalewr5p94dg9cpxfygpr70secqdnnl9r"))
    print("xch_address:",
          puzzle_hash_to_xch_address("0xb4c7ffdfb897a4adf8c05eab6f9211b27bfcb874096ad417013248808fcf8670"))
