# chia-tx
chia离线签名，主要用于根据输入，返回未签名的交易

# 进度
- 离线签名 √
- 生成服务 todo

# 注意事项
```
这里阐述一些与官方不同的地方，需要仔细权衡，具体影响暂时未知
1. 当inputs 大于 outputs时，会将inputs剩余的币重新生成一个新的output, 
官方代码中这个output的puzzle_hash会找到未使用的walletSk的index（数据库中记录已使用的index）来
进行生成output，而本项目使用的始终是index=0的walletSk。因为这里不会涉及数据库，没法保存index
的使用状态
2. 由于没有使用数据库保存index的使用状态，所以有的input的私钥的index不是0，则无法进行签名，
所以创建签名时coins的私钥一定要与签名的sk保持一致
```

# 测试助记词
```
despair monster syrup maximum switch shaft monitor smooth cause panel check beef weasel this suffer ritual again donkey dizzy head prize satisfy crater daring
```
里面有80mojo，可以用来测试

# 部分信息
- sk ----> pk ----> puzzle_hash <----> xch_address
- xch开头的钱包地址默认是使用`wallet-sk`的第`0`个私钥的公钥生成的
- chia的账户模型与UTXO类似，需要输入和输出，叫做coin，他们都是master-sk根据index 
  派生的wallet的私钥（挖矿所得的coin具有相同的puzzle_hash, index=0)，当新的coin产生时（转账后有剩余），
  会迭代index，找到未使用的index，然后使用此index对应的公钥生成的puzzle_hash，同时会生成一个合成私钥，
  此私钥是签名coin的私钥。

# 方法
- create_signed_tx
```
签名的交易信息
已测试通过 √
```

- create_unsigned_tx
```
创建未签名的交易
已测试通过 √
```

- sign_tx
```
签名未签名的交易
已测试通过 √
```

