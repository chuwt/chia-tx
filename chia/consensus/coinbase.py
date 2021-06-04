# coding:utf-8
"""
@Time :    2021/6/2 下午5:42
@Author:  chuwt
"""
from blspy import G1Element

from chia.types.blockchain_format.program import Program
from chia.types.blockchain_format.coin import Coin
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.util.ints import uint32, uint64
from chia.wallet.puzzles.p2_delegated_puzzle_or_hidden_puzzle import puzzle_for_pk

DEFAULT_HIDDEN_PUZZLE = Program.from_bytes(bytes.fromhex("ff0980"))
DEFAULT_HIDDEN_PUZZLE_HASH = DEFAULT_HIDDEN_PUZZLE.get_tree_hash()  # this puzzle `(x)` always fails


def create_puzzlehash_for_pk(pub_key: G1Element) -> bytes32:
    return puzzle_for_pk(pub_key).get_tree_hash()


def pool_parent_id(block_height: uint32, genesis_challenge: bytes32) -> uint32:
    return bytes32(genesis_challenge[:16] + block_height.to_bytes(16, "big"))


def farmer_parent_id(block_height: uint32, genesis_challenge: bytes32) -> uint32:
    return bytes32(genesis_challenge[16:] + block_height.to_bytes(16, "big"))


def create_pool_coin(block_height: uint32, puzzle_hash: bytes32, reward: uint64, genesis_challenge: bytes32):
    parent_id = pool_parent_id(block_height, genesis_challenge)
    return Coin(parent_id, puzzle_hash, reward)


def create_farmer_coin(block_height: uint32, puzzle_hash: bytes32, reward: uint64, genesis_challenge: bytes32):
    parent_id = farmer_parent_id(block_height, genesis_challenge)
    return Coin(parent_id, puzzle_hash, reward)
