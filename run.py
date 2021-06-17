# coding:utf-8
"""
@Time :    2021/6/2 下午4:57
@Author:  chuwt
"""
from typing import (
    List,
    Dict,
    Optional,
    Any,
)

from blspy import G1Element, PrivateKey, G2Element, AugSchemeMPL

from chia.util.byte_types import hexstr_to_bytes
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
from chia.types.spend_bundle import SpendBundle
from chia.wallet.sign_coin_solutions import sign_coin_solutions, unsigned_coin_solutions
from chia.consensus.coinbase import DEFAULT_HIDDEN_PUZZLE_HASH
from chia.wallet.puzzles.p2_delegated_puzzle_or_hidden_puzzle import calculate_synthetic_secret_key
from util.util import (
    generate_xch_address_from_pk,
    puzzle_hash_to_xch_address,
    xch_address_to_puzzle_hash
)


def create_signed_tx(sk: str, to_address: str, amount: uint64, fee: int, coins: List) -> dict:
    """
    创建签名后的交易

    注意: 这里的utxo必须是sk作为私钥进行授权的，不然无法通过签名
    注意2: 官方的walletSk的index使用过后会+1生成，但是此包的index使用的总是index=0的
    walletSk，望悉知

    当有输入的UTXO有剩余时，将UTXO重新倒入到sk中
    :param sk: 私钥字符串, 这里的私钥是wallet和index对应的私钥
    :param to_address: 转账地址
    :param amount: 数量
    :param fee: 手续费
    :param coins: UTXO的输入
    :return: 签名后的交易
    """
    to_puzzle_hash = xch_address_to_puzzle_hash(to_address)

    synthetic = calculate_synthetic_secret_key(PrivateKey.from_bytes(hexstr_to_bytes(sk)), DEFAULT_HIDDEN_PUZZLE_HASH)
    # print(synthetic)
    pk = PrivateKey.from_bytes(hexstr_to_bytes(sk)).get_g1()

    transaction = _create_transaction(pk, to_puzzle_hash, amount, fee, coins)
    spend_bundle: SpendBundle = sign_coin_solutions(
        transaction,
        synthetic,
        bytes.fromhex("ccd5bb71183532bff220ba46c268991a3ff07eb358e8255a65c30a2dce0e5fbb"),
        11000000000,
    )
    json_dict = spend_bundle.to_json_dict()
    return json_dict


def sign_tx(sk: str, unsigned_tx: dict, msg_list: List[bytes], pk_list: List[bytes]) -> dict:
    """
    签名交易
    :param unsigned_tx:
    :param sk: 是wallet的私钥
    :param msg_list: create_unsigned_tx生成的
    :param pk_list: create_unsigned_tx生成的
    :return:
    """
    synthetic = calculate_synthetic_secret_key(PrivateKey.from_bytes(hexstr_to_bytes(sk)), DEFAULT_HIDDEN_PUZZLE_HASH)
    signatures: List[G2Element] = []
    for msg in msg_list:
        index = msg_list.index(msg)
        assert bytes(synthetic.get_g1()) == bytes(pk_list[index])
        signature = AugSchemeMPL.sign(synthetic, msg)
        assert AugSchemeMPL.verify(pk_list[index], msg, signature)
        signatures.append(signature)
    aggsig = AugSchemeMPL.aggregate(signatures)
    assert AugSchemeMPL.aggregate_verify(pk_list, msg_list, aggsig)

    unsigned_tx["aggregated_signature"] = "0x" + bytes(aggsig).hex()

    return unsigned_tx


def create_unsigned_tx(from_pk: str, to_address: str, amount: uint64, fee: int, coins: List):
    """
    创建未签名的交易
    :param from_pk: wallet sk 对应的pk
    :param to_address: 转账地址
    :param amount: 数量
    :param fee: 手续费
    :param coins: coin输入
    :return:
    """
    to_puzzle_hash = xch_address_to_puzzle_hash(to_address)

    transaction = _create_transaction(G1Element.from_bytes(hexstr_to_bytes(from_pk)), to_puzzle_hash, amount, fee,
                                      coins)
    msg_list, pk_list = unsigned_coin_solutions(
        transaction,
        bytes.fromhex("ccd5bb71183532bff220ba46c268991a3ff07eb358e8255a65c30a2dce0e5fbb"),
        11000000000)
    unsigned_tx = {
        "coin_solutions": [t.to_json_dict() for t in transaction],
        "aggregated_signature": "",
    }
    return unsigned_tx, msg_list, pk_list


def _create_transaction(pk: G1Element, to_puzzle_hash: str, amount: uint64, fee: int, coins: List):
    outputs = []

    if not to_puzzle_hash:
        raise ValueError(f"Address is null in send list")
    if amount <= 0:
        raise ValueError(f"Amount must greater than 0")
    # address to puzzle hash
    to_puzzle_hash = hexstr_to_bytes(to_puzzle_hash)
    total_amount = amount + fee

    outputs.append({"puzzle_hash": to_puzzle_hash, "amount": amount})

    # 余额判断
    coins = set([Coin.from_json_dict(coin_json) for coin_json in coins])
    spend_value = sum([coin.amount for coin in coins])
    change = spend_value - total_amount
    if change < 0:
        raise ValueError("Insufficient balance")

    transaction: List[CoinSolution] = []
    primary_announcement_hash: Optional[bytes32] = None

    for coin in coins:
        puzzle: Program = puzzle_for_pk(pk)

        if primary_announcement_hash is None:
            primaries = [{"puzzlehash": to_puzzle_hash, "amount": amount}]
            if change > 0:
                # 源码这里是通过index来派生新的wallet私钥，然后转成公钥，最后根据公钥生成puzzle_hash,
                # 这些会记录在数据库里，然后后面会通过puzzle_hash查找index，然后推出公钥
                # todo 这里我们直接使用index=0的公钥生成的puzzle_hash, 不知道会不会有问题
                change_puzzle_hash: bytes32 = create_puzzlehash_for_pk(pk)
                primaries.append({"puzzlehash": change_puzzle_hash, "amount": change})
            message_list: List[bytes32] = [c.name() for c in coins]
            for primary in primaries:
                message_list.append(Coin(coin.name(), primary["puzzlehash"], primary["amount"]).name())
            message: bytes32 = std_hash(b"".join(message_list))
            solution: Program = make_solution(primaries=primaries, fee=fee, coin_announcements=[message])
            primary_announcement_hash = Announcement(coin.name(), message).name()
        else:
            solution = make_solution(coin_announcements_to_assert=[primary_announcement_hash])

        transaction.append(
            CoinSolution(
                coin, SerializedProgram.from_bytes(bytes(puzzle)), SerializedProgram.from_bytes(bytes(solution))
            )
        )
    if len(transaction) <= 0:
        raise ValueError("spends is zero")
    return transaction


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
    print("xch_address:",
          generate_xch_address_from_pk(
              "aaf079d607cabb95c0039c51317cd6e84e66bb6b5c9aecf8fdc4f0ba97c7f2ec8bb2b1831ad3ea0ba8f701a26177e43e"))

    print("puzzle_hash:",
          xch_address_to_puzzle_hash("xch1knrllhacj7j2m7xqt64klys3kfalewr5p94dg9cpxfygpr70secqdnnl9r"))
    print("xch_address:",
          puzzle_hash_to_xch_address("0xb4c7ffdfb897a4adf8c05eab6f9211b27bfcb874096ad417013248808fcf8670"))

    tx, msg_list, pk_list = create_unsigned_tx(
        from_pk="900c653808c7a1227e65af3bd989bc88bf2a30b13531fb2d8159c9321b84379e4c66e5924adf044bf414f80a2def359f",
        to_address="xch1avpafhgdnf4ze55th72y6xw4uuem8dugne8z8e8m86gkxnkhdczs7rtn9z",
        amount=uint64(175000000000),
        fee=0,
        coins=[{
            'amount': 1750000000000,
            'parent_coin_info': '0xe3b0c44298fc1c149afbf4c8996fb92400000000000000000000000000000001',
            'puzzle_hash': '0xeb03d4dd0d9a6a2cd28bbf944d19d5e733b3b7889e4e23e4fb3e91634ed76e05'
        }])
    assert bytes(sign_tx(
        "6a2f110a535bf8160d8825570bb63742183ef020c118b2db36bb056070898bf0",
        msg_list,
        pk_list)).hex() == "b6b0e152c2929b36edd0172dcee8d2a2046adf52459864e8ef4af27cb0e61a4c5493d25aedfb9f08fa571339" \
                           "f7acd16c15acead762f65d9b2c0caf0e3e1057e3a869b9f471b83ea13203a7a2d166d51afd4cd811add3d611" \
                           "3c9b45df28523d3f"

    create_signed_tx(
        sk="6a2f110a535bf8160d8825570bb63742183ef020c118b2db36bb056070898bf0",
        to_address="xch1avpafhgdnf4ze55th72y6xw4uuem8dugne8z8e8m86gkxnkhdczs7rtn9z",
        amount=uint64(175000000000),
        fee=0,
        coins=[{
            'amount': 1750000000000,
            'parent_coin_info': '0xe3b0c44298fc1c149afbf4c8996fb92400000000000000000000000000000001',
            'puzzle_hash': '0xeb03d4dd0d9a6a2cd28bbf944d19d5e733b3b7889e4e23e4fb3e91634ed76e05'
        }])
