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

# http服务
```
使用aiohttp写了个简单的http服务，主要提供上面三个方法的调用
```