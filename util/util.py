# coding:utf-8
"""
@Time :    2021/6/16 上午10:03
@Author:  chuwt
"""

from chia.util.byte_types import hexstr_to_bytes
from blspy import G1Element, PrivateKey, G2Element, AugSchemeMPL
from chia.util.bech32m import decode_puzzle_hash, encode_puzzle_hash
from chia.consensus.coinbase import create_puzzlehash_for_pk


def generate_xch_address_from_pk(pk: str) -> str:
    return encode_puzzle_hash(create_puzzlehash_for_pk(G1Element.from_bytes(hexstr_to_bytes(pk))), "xch")


def pk_str_to_puzzle_hash(pk: str) -> str:
    return create_puzzlehash_for_pk(G1Element.from_bytes(hexstr_to_bytes(pk))).hex()


def puzzle_hash_to_xch_address(puzzle_hash: str) -> str:
    return encode_puzzle_hash(hexstr_to_bytes(puzzle_hash), "xch")


def xch_address_to_puzzle_hash(xch_address: str) -> str:
    return decode_puzzle_hash(xch_address).hex()