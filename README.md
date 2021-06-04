# chia-tx
chia未签名交易生成服务，主要用于根据输入，返回未签名的交易

# 部分信息
- sk ----> pk ----> puzzle_hash <----> xch_address
- xch开头的钱包地址默认是使用`wallet-sk`的第`0`个私钥的公钥生成的
- chia的账户模型与UTXO类似，需要输入和输出，叫做coin，他们都是master-sk根据index 
  派生的wallet的私钥（挖矿所得的coin具有相同的puzzle_hash, index=0)，当新的coin产生时（转账后有剩余），
  会迭代index， 找到未使用的index，然后使用此index对应的公钥生成的puzzle_hash，同时会生成一个合成私钥，
  此私钥是签名coin的私钥。
  