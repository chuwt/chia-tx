# coding:utf-8
"""
@Time :    2021/6/2 下午4:57
@Author:  chuwt
"""
from typing import List, Dict, Optional, Any

from blspy import G1Element

from chia.util.byte_types import hexstr_to_bytes
from chia.util.bech32m import decode_puzzle_hash, encode_puzzle_hash
from chia.consensus.coinbase import create_puzzlehash_for_pk
from chia.types.blockchain_format.coin import Coin
from chia.types.blockchain_format.program import Program, SerializedProgram
from chia.wallet.puzzles.p2_delegated_puzzle_or_hidden_puzzle import puzzle_for_pk
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.util.ints import uint64
from chia.types.coin_solution import CoinSolution
from chia.util.hash import std_hash
from chia.wallet.puzzles.puzzle_utils import (
    make_assert_coin_announcement,
    make_assert_puzzle_announcement,
    make_assert_my_coin_id_condition,
    make_assert_absolute_seconds_exceeds_condition,
    make_create_coin_announcement,
    make_create_puzzle_announcement,
    make_create_coin_condition,
    make_reserve_fee_condition,
)
from chia.wallet.puzzles.p2_delegated_puzzle_or_hidden_puzzle import solution_for_conditions
from chia.wallet.puzzles.announcement import Announcement


def generate_xch_address_from_pk(pk: str) -> str:
    return encode_puzzle_hash(create_puzzlehash_for_pk(G1Element.from_bytes(hexstr_to_bytes(pk))), "xch")


def puzzle_hash_to_xch_address(puzzle_hash: str) -> str:
    return encode_puzzle_hash(hexstr_to_bytes(puzzle_hash), "xch")


def xch_address_to_puzzle_hash(xch_address: str) -> str:
    return decode_puzzle_hash(xch_address).hex()


def create_unsigned_tx(from_pk: str, to_address: str, amount: uint64,  fee: int, coins: List):
    """
    """
    outputs = []

    if not to_address:
        raise ValueError(f"Address is null in send list")
    if amount <= 0:
        raise ValueError(f"Amount must greater than 0")
    # address to puzzle hash
    puzzle_hash = xch_address_to_puzzle_hash(to_address)
    puzzle_hash = hexstr_to_bytes(puzzle_hash)
    total_amount = amount + fee

    outputs.append({"puzzle_hash": puzzle_hash, "amount": amount})

    # 余额判断
    coins = set([Coin.from_json_dict(coin_json) for coin_json in coins])
    spend_value = sum([coin.amount for coin in coins])
    change = spend_value - total_amount
    if change < 0:
        raise ValueError("Insufficient balance")

    spends: List[CoinSolution] = []
    primary_announcement_hash: Optional[bytes32] = None

    for coin in coins:
        puzzle: Program = puzzle_for_pk(G1Element.from_bytes(hexstr_to_bytes(from_pk)))

        if primary_announcement_hash is None:
            primaries = [{"puzzlehash": puzzle_hash, "amount": amount}]
            if change > 0:
                # todo 获取puzzle hash
                pass
                # change_puzzle_hash: bytes32 = get_new_puzzlehash()
                # primaries.append({"puzzlehash": change_puzzle_hash, "amount": change})
            message_list: List[bytes32] = [c.name() for c in coins]
            for primary in primaries:
                message_list.append(Coin(coin.name(), primary["puzzlehash"], primary["amount"]).name())
            message: bytes32 = std_hash(b"".join(message_list))
            solution: Program = make_solution(primaries=primaries, fee=fee, coin_announcements=[message])
            primary_announcement_hash = Announcement(coin.name(), message).name()
        else:
            solution = make_solution(coin_announcements_to_assert=[primary_announcement_hash])

        spends.append(
            CoinSolution(
                coin, SerializedProgram.from_bytes(bytes(puzzle)), SerializedProgram.from_bytes(bytes(solution))
            )
        )
    print(spends)
    return spends


def make_solution(
    primaries: Optional[List[Dict[str, Any]]] = None,
    min_time=0,
    me=None,
    coin_announcements: Optional[List[bytes32]] = None,
    coin_announcements_to_assert: Optional[List[bytes32]] = None,
    puzzle_announcements=None,
    puzzle_announcements_to_assert=None,
    fee=0,
) -> Program:
    assert fee >= 0
    condition_list = []
    if primaries:
        for primary in primaries:
            condition_list.append(make_create_coin_condition(primary["puzzlehash"], primary["amount"]))
    if min_time > 0:
        condition_list.append(make_assert_absolute_seconds_exceeds_condition(min_time))
    if me:
        condition_list.append(make_assert_my_coin_id_condition(me["id"]))
    if fee:
        condition_list.append(make_reserve_fee_condition(fee))
    if coin_announcements:
        for announcement in coin_announcements:
            condition_list.append(make_create_coin_announcement(announcement))
    if coin_announcements_to_assert:
        for announcement_hash in coin_announcements_to_assert:
            condition_list.append(make_assert_coin_announcement(announcement_hash))
    if puzzle_announcements:
        for announcement in puzzle_announcements:
            condition_list.append(make_create_puzzle_announcement(announcement))
    if puzzle_announcements_to_assert:
        for announcement_hash in puzzle_announcements_to_assert:
            condition_list.append(make_assert_puzzle_announcement(announcement_hash))
    return solution_for_conditions(condition_list)


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

    create_unsigned_tx(
        from_pk="900c653808c7a1227e65af3bd989bc88bf2a30b13531fb2d8159c9321b84379e4c66e5924adf044bf414f80a2def359f",
        to_address="xch1avpafhgdnf4ze55th72y6xw4uuem8dugne8z8e8m86gkxnkhdczs7rtn9z",
        amount=uint64(1750000000000),
        fee=0,
        coins=[{
            'amount': 1750000000000,
            'parent_coin_info': '0xe3b0c44298fc1c149afbf4c8996fb92400000000000000000000000000000001',
            'puzzle_hash': '0xeb03d4dd0d9a6a2cd28bbf944d19d5e733b3b7889e4e23e4fb3e91634ed76e05'
        }])
