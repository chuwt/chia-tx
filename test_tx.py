# coding:utf-8
"""
@Time :    2021/6/16 上午10:01
@Author:  chuwt
"""

from chia.util.ints import uint64
from util.util import generate_xch_address_from_pk, xch_address_to_puzzle_hash, puzzle_hash_to_xch_address

from tx import create_signed_tx, create_unsigned_tx, sign_tx


def test_create_signed_tx():
    sign_tx_dict = create_signed_tx(
        sk="0x58a8b3237c9981ff476a897fc0d6b377bd5b2e57cbfcdf664c76963a52041012",
        to_address="xch14452k0srjew8f865ej3dj7wgfc2qg5t0epzjmg7pwca03z3pkl4q2ekruc",
        amount=uint64(10),
        fee=0,
        coins=[{
            'amount': 80,
            'parent_coin_info': '0xb5d31c65960840ea826be97ef7dae140a680a047d48434475eef8bd9062b63e8',
            'puzzle_hash': '0x2c68ed218bd3dc011237a1b79c2669905f763dc3f1ed4fea6ddb1760d12edb78'
        }])
    print("test_create_signed_tx: sign_tx", sign_tx_dict)
    return sign_tx_dict


def test_create_unsigned_tx():
    unsigned_tx, msg_list, pk_list = create_unsigned_tx(
        from_pk="0xb00d72059e10b375275688497476e188066eebfaf7f226daa80cf7a7ad1d4f7ab298a161c453390903a790b11e747789",
        to_address="xch14452k0srjew8f865ej3dj7wgfc2qg5t0epzjmg7pwca03z3pkl4q2ekruc",
        amount=uint64(10),
        fee=0,
        coins=[{
            'amount': 80,
            'parent_coin_info': '0xb5d31c65960840ea826be97ef7dae140a680a047d48434475eef8bd9062b63e8',
            'puzzle_hash': '0x2c68ed218bd3dc011237a1b79c2669905f763dc3f1ed4fea6ddb1760d12edb78'
        }])
    print("test_create_unsigned_tx: unsigned_tx", unsigned_tx)
    print("test_create_unsigned_tx: msg_list", msg_list)
    print("test_create_unsigned_tx: pk_list", pk_list)
    return unsigned_tx, msg_list, pk_list


def test_signed_tx(*args):
    unsigned_tx = args[0]
    msg_list = args[1]
    pk_list = args[2]
    sign_tx_dict = sign_tx("0x58a8b3237c9981ff476a897fc0d6b377bd5b2e57cbfcdf664c76963a52041012", unsigned_tx, msg_list, pk_list)
    print("test_signed_tx: sign_tx_dict", sign_tx_dict)
    return sign_tx_dict


def test_address_puzzle_hash():
    print("xch_address:",
          generate_xch_address_from_pk(
              "aaf079d607cabb95c0039c51317cd6e84e66bb6b5c9aecf8fdc4f0ba97c7f2ec8bb2b1831ad3ea0ba8f701a26177e43e"))

    print("puzzle_hash:",
          xch_address_to_puzzle_hash("xch1knrllhacj7j2m7xqt64klys3kfalewr5p94dg9cpxfygpr70secqdnnl9r"))
    print("xch_address:",
          puzzle_hash_to_xch_address("0xb4c7ffdfb897a4adf8c05eab6f9211b27bfcb874096ad417013248808fcf8670"))


if __name__ == "__main__":
    test_address_puzzle_hash()

    first_signed_tx = test_create_signed_tx()
    unsigned_tx, msg_list, pk_list = test_create_unsigned_tx()
    second_signed_tx = test_signed_tx(unsigned_tx, msg_list, pk_list)

    assert first_signed_tx == second_signed_tx






