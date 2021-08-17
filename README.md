# chia-tx
chia离线签名，主要用于根据输入，返回未签名的交易

# 进度
- 离线签名 √
- 生成服务 √

# 注意事项
```
这里阐述一些与官方不同的地方，需要仔细权衡，具体影响暂时未知
1. 官方找零机制是根据（walletSK, index) 来派生公钥地址的，index会记录在数据库中，由于当前
我们是无状态的，所以在这里我们找零的地址是恒定的, 是index=0的钱包地址
2. 所以如果input的私钥的index不是0，则无法进行签名，所以创建签名时coins的私钥一定要与签名的sk保持一致
```

# 测试助记词
```
despair monster syrup maximum switch shaft monitor smooth cause panel check beef weasel this suffer ritual again donkey dizzy head prize satisfy crater daring
```
里面有70mojo，可以用来测试

# 部分信息
- sk ----> pk ----> puzzle_hash <----> xch_address
- xch开头的钱包地址默认是使用`wallet-sk`的第`0`个私钥的公钥生成的
- chia的账户模型与UTXO类似，需要输入和输出，叫做coin，他们都是master-sk根据index 
  派生的wallet的私钥（挖矿所得的coin具有相同的puzzle_hash, index=0)，当新的coin产生时（转账后有剩余），
  会迭代index，找到未使用的index，然后使用此index对应的公钥生成的puzzle_hash，同时会生成一个合成私钥，
  此私钥是签名coin的私钥。

# 方法
- create_signed_tx
- 参数
```
{
    "sk": "0x58a8b3237c9981ff476a897fc0d6b377bd5b2e57cbfcdf664c76963a52041012", // coin对应的私钥
    "to_address": "xch14452k0srjew8f865ej3dj7wgfc2qg5t0epzjmg7pwca03z3pkl4q2ekruc", // to地址
    "amount": 10, // 数量，单位mojo
    "coins": [
        {
            "amount": 80,
            "parent_coin_info": "0xb5d31c65960840ea826be97ef7dae140a680a047d48434475eef8bd9062b63e8",
            "puzzle_hash": "0x2c68ed218bd3dc011237a1b79c2669905f763dc3f1ed4fea6ddb1760d12edb78"
        }
    ] // coins是通过节点查询获取的coins
}
```
- 返回
```
{
    "data": {
        "tx_hash": "9b89bfdccbf010499172588005ed25391b2e90a0ef44592f31aef1611429dac6",
        "sign_tx_dict": {
            "coin_solutions": [
                {
                    "coin": {
                        "parent_coin_info": "0xb5d31c65960840ea826be97ef7dae140a680a047d48434475eef8bd9062b63e8",
                        "puzzle_hash": "0x2c68ed218bd3dc011237a1b79c2669905f763dc3f1ed4fea6ddb1760d12edb78",
                        "amount": 80
                    },
                    "puzzle_reveal": "0xff02ffff01ff02ffff01ff02ffff03ff0bffff01ff02ffff03ffff09ff05ffff1dff0bffff1effff0bff0bffff02ff06ffff04ff02ffff04ff17ff8080808080808080ffff01ff02ff17ff2f80ffff01ff088080ff0180ffff01ff04ffff04ff04ffff04ff05ffff04ffff02ff06ffff04ff02ffff04ff17ff80808080ff80808080ffff02ff17ff2f808080ff0180ffff04ffff01ff32ff02ffff03ffff07ff0580ffff01ff0bffff0102ffff02ff06ffff04ff02ffff04ff09ff80808080ffff02ff06ffff04ff02ffff04ff0dff8080808080ffff01ff0bffff0101ff058080ff0180ff018080ffff04ffff01b0a9cc8198f9453fa1945c74a45a32037aa42b406896d966118cab49786938d7082bd13a61d36fc24208f9fc491baffd01ff018080",
                    "solution": "0xff80ffff01ffff33ffa0ad68ab3e03965c749f54cca2d979c84e1404516fc8452da3c1763af88a21b7eaff0a80ffff33ffa02c68ed218bd3dc011237a1b79c2669905f763dc3f1ed4fea6ddb1760d12edb78ff4680ffff3cffa0ac13b120c3aa90755a5cd41f3679c694ce0a2fa6d691309dbd6a30863d6ca27a8080ff8080"
                }
            ],
            "aggregated_signature": "0xb166d38fa4b84eccd3da941264c8b3c6decd97f3ad020bc48b8e51d2013a7e200f3ac54c676e9eb6786a6cc29c3bcc070040c5c5fd608295461e9c918959b608e1a9b9a0911aac425d22d8068fbd538e5468692eccfbaaf36a5f9267d3170c22"
        }
    },
    "err": ""
}
```
- 说明
```
创建签名的交易：可以直接通过节点发送交易
已测试通过 √
```

- create_unsigned_tx
- 参数
```
{
    "from_pk": "0xb00d72059e10b375275688497476e188066eebfaf7f226daa80cf7a7ad1d4f7ab298a161c453390903a790b11e747789", // 公钥
    "to_address": "xch14452k0srjew8f865ej3dj7wgfc2qg5t0epzjmg7pwca03z3pkl4q2ekruc", // to地址
    "amount": 10, // 数量，单位mojo
    "coins": [
        {
            "amount": 80,
            "parent_coin_info": "0xb5d31c65960840ea826be97ef7dae140a680a047d48434475eef8bd9062b63e8",
            "puzzle_hash": "0x2c68ed218bd3dc011237a1b79c2669905f763dc3f1ed4fea6ddb1760d12edb78"
        }
    ] // coins是通过节点查询获取的coins
}
```
- 返回
```
{
    "data": {
        "unsigned_tx": {
            "coin_solutions": [
                {
                    "coin": {
                        "parent_coin_info": "0xb5d31c65960840ea826be97ef7dae140a680a047d48434475eef8bd9062b63e8",
                        "puzzle_hash": "0x2c68ed218bd3dc011237a1b79c2669905f763dc3f1ed4fea6ddb1760d12edb78",
                        "amount": 80
                    },
                    "puzzle_reveal": "0xff02ffff01ff02ffff01ff02ffff03ff0bffff01ff02ffff03ffff09ff05ffff1dff0bffff1effff0bff0bffff02ff06ffff04ff02ffff04ff17ff8080808080808080ffff01ff02ff17ff2f80ffff01ff088080ff0180ffff01ff04ffff04ff04ffff04ff05ffff04ffff02ff06ffff04ff02ffff04ff17ff80808080ff80808080ffff02ff17ff2f808080ff0180ffff04ffff01ff32ff02ffff03ffff07ff0580ffff01ff0bffff0102ffff02ff06ffff04ff02ffff04ff09ff80808080ffff02ff06ffff04ff02ffff04ff0dff8080808080ffff01ff0bffff0101ff058080ff0180ff018080ffff04ffff01b0a9cc8198f9453fa1945c74a45a32037aa42b406896d966118cab49786938d7082bd13a61d36fc24208f9fc491baffd01ff018080",
                    "solution": "0xff80ffff01ffff33ffa0ad68ab3e03965c749f54cca2d979c84e1404516fc8452da3c1763af88a21b7eaff0a80ffff33ffa02c68ed218bd3dc011237a1b79c2669905f763dc3f1ed4fea6ddb1760d12edb78ff4680ffff3cffa0ac13b120c3aa90755a5cd41f3679c694ce0a2fa6d691309dbd6a30863d6ca27a8080ff8080"
                }
            ],
            "aggregated_signature": ""
        },
        "msg_list": [
            "10f4962dfabb2e21217ae886084a10a8626e873d692c353b9004331d0e9966e33445218ca583311ea1490b1a8cdf2af8ad84d583adb31c2cfa141bace8cc9fc3ccd5bb71183532bff220ba46c268991a3ff07eb358e8255a65c30a2dce0e5fbb"
        ],
        "pk_list": [
            "a9cc8198f9453fa1945c74a45a32037aa42b406896d966118cab49786938d7082bd13a61d36fc24208f9fc491baffd01"
        ]
    },
    "err": ""
}
```
- 说明
```
创建未签名的交易：需要经过sign_tx签名才能使用，也可以通过其他方式进行签名
已测试通过 √
```

- sign_tx
- 参数
```
{
    "sk": "0x58a8b3237c9981ff476a897fc0d6b377bd5b2e57cbfcdf664c76963a52041012", // 私钥
    "msg_list": [
        "10f4962dfabb2e21217ae886084a10a8626e873d692c353b9004331d0e9966e33445218ca583311ea1490b1a8cdf2af8ad84d583adb31c2cfa141bace8cc9fc3ccd5bb71183532bff220ba46c268991a3ff07eb358e8255a65c30a2dce0e5fbb"
    ], // create_unsigned_tx 返回的数据
    "pk_list": [
        "a9cc8198f9453fa1945c74a45a32037aa42b406896d966118cab49786938d7082bd13a61d36fc24208f9fc491baffd01"
    ], // create_unsigned_tx 返回的数据
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
    } // create_unsigned_tx 返回的数据
}
```
- 返回
```
{
    "data": {
        "tx_hash": "9b89bfdccbf010499172588005ed25391b2e90a0ef44592f31aef1611429dac6",
        "signed_tx": {
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
            ],
            "aggregated_signature": "0xb166d38fa4b84eccd3da941264c8b3c6decd97f3ad020bc48b8e51d2013a7e200f3ac54c676e9eb6786a6cc29c3bcc070040c5c5fd608295461e9c918959b608e1a9b9a0911aac425d22d8068fbd538e5468692eccfbaaf36a5f9267d3170c22"
        }
    },
    "err": ""
}
```
- 说明
```
签名未签名的交易：将create_unsigned_tx生成的交易进行签名，签名后的数据可以直接通过节点发送
已测试通过 √
```

# http服务
```
使用aiohttp写了个简单的http服务，主要提供上面三个方法的调用
```