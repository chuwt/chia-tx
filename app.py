# coding:utf-8
"""
@Time :    2021/6/23 上午11:33
@Author:  chuwt
"""

from aiohttp import web
from chia.util.ints import uint64
from tx import create_signed_tx, create_unsigned_tx, sign_tx
from blspy import G1Element
from chia.util.byte_types import hexstr_to_bytes


def response(msg: any, err: str = ""):
    return web.json_response({
        "data": msg,
        "err": err
    })


async def _create_signed_tx(req):
    """
    {
        "sk": "0x58a8b3237c9981ff476a897fc0d6b377bd5b2e57cbfcdf664c76963a52041012",
        "to_address": "xch14452k0srjew8f865ej3dj7wgfc2qg5t0epzjmg7pwca03z3pkl4q2ekruc",
        "amount": 10,
        "coins": [
            {
                "amount": 80,
                "parent_coin_info": "0xb5d31c65960840ea826be97ef7dae140a680a047d48434475eef8bd9062b63e8",
                "puzzle_hash": "0x2c68ed218bd3dc011237a1b79c2669905f763dc3f1ed4fea6ddb1760d12edb78"
            }
        ]
    }
    :return:
    """
    try:
        data = await req.json()
    except Exception as e:
        return response("invalid body", str(e))
    sk = data.get("sk", "")
    if not sk:
        return response("sk can't be null")

    to_address = data.get("to_address", "")
    if not to_address:
        return response("to_address can't be null")

    amount = data.get("amount", 0)
    if amount == 0:
        return response("amount can't be 0")

    fee = data.get("fee", 0)

    coins = data.get("coins", [])

    try:
        sign_tx_dict = create_signed_tx(
            sk=sk,
            to_address=to_address,
            amount=uint64(10),
            fee=fee,
            coins=coins,
        )
    except Exception as e:
        return response("create_signed_tx err", str(e))

    return response(sign_tx_dict)


async def _create_unsigned_tx(req):
    """
    {
        "from_pk": "0xb00d72059e10b375275688497476e188066eebfaf7f226daa80cf7a7ad1d4f7ab298a161c453390903a790b11e747789",
        "to_address": "xch14452k0srjew8f865ej3dj7wgfc2qg5t0epzjmg7pwca03z3pkl4q2ekruc",
        "amount": 10,
        "coins": [
            {
                "amount": 80,
                "parent_coin_info": "0xb5d31c65960840ea826be97ef7dae140a680a047d48434475eef8bd9062b63e8",
                "puzzle_hash": "0x2c68ed218bd3dc011237a1b79c2669905f763dc3f1ed4fea6ddb1760d12edb78"
            }
        ]
    }
    :return:
    """
    try:
        data = await req.json()
    except Exception as e:
        return response("invalid body", str(e))

    from_pk = data.get("from_pk", "")
    if not from_pk:
        return response("from_pk can't be null")

    to_address = data.get("to_address", "")
    if not to_address:
        return response("to_address can't be null")

    amount = data.get("amount", 0)
    if amount == 0:
        return response("amount can't be 0")

    fee = data.get("fee", 0)

    coins = data.get("coins", [])

    try:
        unsigned_tx, msg_list, pk_list = create_unsigned_tx(
            from_pk=from_pk,
            to_address=to_address,
            amount=uint64(10),
            fee=fee,
            coins=coins
        )
    except Exception as e:
        return response("create_signed_tx err", str(e))

    return response(
        {
            "unsigned_tx": unsigned_tx,
            "msg_list": [msg.hex() for msg in msg_list],
            "pk_list": [bytes(pk).hex() for pk in pk_list],
        }
    )


async def _sign_tx(req):
    """
    {
        "sk": "0x58a8b3237c9981ff476a897fc0d6b377bd5b2e57cbfcdf664c76963a52041012",
        "msg_list": [
                "10f4962dfabb2e21217ae886084a10a8626e873d692c353b9004331d0e9966e33445218ca583311ea1490b1a8cdf2af8ad84d583adb31c2cfa141bace8cc9fc3ccd5bb71183532bff220ba46c268991a3ff07eb358e8255a65c30a2dce0e5fbb"
            ],
            "pk_list": [
                "a9cc8198f9453fa1945c74a45a32037aa42b406896d966118cab49786938d7082bd13a61d36fc24208f9fc491baffd01"
            ],
            "unsigned_tx": {
                "aggregated_signature": "",
                "coin_solutions": [
                    {
                        "coin": {
                            "amount": 80,
                            "parent_coin_info": "0xb5d31c65960840ea826be97ef7dae140a680a047d48434475eef8bd9062b63e8",
                            "puzzle_hash": "0x2c68ed218bd3dc011237a1b79c2669905f763dc3f1ed4fea6ddb1760d12edb78"
                        },
                        "puzzle_reveal": "0xff02ffff01ff02ffff01ff02ffff03ff0bffff01ff02ffff03ffff09ff05ffff1dff0bffff1effff0bff0bffff02ff06ffff04ff02ffff04ff17ff8080808080808080ffff01ff02ff17ff2f80ffff01ff088080ff0180ffff01ff04ffff04ff04ffff04ff05ffff04ffff02ff06ffff04ff02ffff04ff17ff80808080ff80808080ffff02ff17ff2f808080ff0180ffff04ffff01ff32ff02ffff03ffff07ff0580ffff01ff0bffff0102ffff02ff06ffff04ff02ffff04ff09ff80808080ffff02ff06ffff04ff02ffff04ff0dff8080808080ffff01ff0bffff0101ff058080ff0180ff018080ffff04ffff01b0a9cc8198f9453fa1945c74a45a32037aa42b406896d966118cab49786938d7082bd13a61d36fc24208f9fc491baffd01ff018080",
                        "solution": "0xff80ffff01ffff33ffa0ad68ab3e03965c749f54cca2d979c84e1404516fc8452da3c1763af88a21b7eaff0a80ffff33ffa02c68ed218bd3dc011237a1b79c2669905f763dc3f1ed4fea6ddb1760d12edb78ff4680ffff3cffa0ac13b120c3aa90755a5cd41f3679c694ce0a2fa6d691309dbd6a30863d6ca27a8080ff8080"
                    }
                ]
            }
    }
    :return:
    """
    try:
        data = await req.json()
    except Exception as e:
        return response("invalid body", str(e))

    sk = data.get("sk", "")
    if not sk:
        return response("sk can't bee null")

    unsigned_tx = data.get("unsigned_tx", {})
    if not unsigned_tx:
        return response("unsigned_tx can't be null")

    msg_list = data.get("msg_list", [])
    if not msg_list:
        return response("msg_list can't be null")

    pk_list = data.get("pk_list", [])
    if not msg_list:
        return response("pklist can't be null")
    try:
        signed_tx = sign_tx(
            sk=sk,
            unsigned_tx=unsigned_tx,
            msg_list=[bytes.fromhex(msg) for msg in msg_list],
            pk_list=[G1Element.from_bytes(hexstr_to_bytes(pk)) for pk in pk_list]
        )
    except Exception as e:
        return response("sign_tx error", str(e))
    return response(signed_tx)


if __name__ == "__main__":
    app = web.Application()
    app.add_routes([
        web.post('/tx/signed/create', _create_signed_tx),
        web.post('/tx/unsigned/create', _create_unsigned_tx),
        web.post('/tx/sign', _sign_tx),
    ])
    web.run_app(app)
