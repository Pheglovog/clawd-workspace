# Web3.py 开发指南

## 📋 概述

Web3.py 是一个用于与以太坊交互的 Python 库。它提供了简洁的接口来连接节点、发送交易、部署合约、调用合约方法等。

## 🚀 快速开始

### 安装

```bash
pip install web3
```

### 基本连接

```python
from web3 import Web3

# 连接到以太坊节点
w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/YOUR_PROJECT_ID'))

# 检查连接
if w3.is_connected():
    print("Connected to Ethereum!")
else:
    print("Connection failed")
```

## 🔑 账户管理

### 创建账户

```python
from web3 import Web3
from eth_account import Account

# 启用助记词功能（可选）
Account.enable_unaudited_hdwallet_features()

# 创建新账户
acct = Account.create('my secret key')

print(f"Private Key: {acct.key.hex()}")
print(f"Address: {acct.address}")
```

### 从私钥导入

```python
private_key = '0x...'
acct = Account.from_key(private_key)
print(f"Address: {acct.address}")
```

### 从助记词导入

```python
mnemonic = 'word1 word2 word3 ...'
acct = Account.from_mnemonic(mnemonic)
print(f"Address: {acct.address}")

# 指定路径（HD Wallet）
acct = Account.from_mnemonic(mnemonic, account_path="m/44'/60'/0'/0/0")
```

## 💰 余额查询

### 查询 ETH 余额

```python
address = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'

# 查询余额（Wei）
balance_wei = w3.eth.get_balance(address)
print(f"Balance (Wei): {balance_wei}")

# 转换为 Ether
balance_eth = w3.from_wei(balance_wei, 'ether')
print(f"Balance (ETH): {balance_eth}")

# 其他单位
gwei = w3.from_wei(balance_wei, 'gwei')
print(f"Balance (Gwei): {gwei}")
```

### 单位转换

```python
from web3 import Web3

# ETH 转 Wei
eth_amount = 1.5
wei_amount = Web3.to_wei(eth_amount, 'ether')
print(f"{eth_amount} ETH = {wei_amount} Wei")

# Wei 转 ETH
wei_amount = 1500000000000000000
eth_amount = Web3.from_wei(wei_amount, 'ether')
print(f"{wei_amount} Wei = {eth_amount} ETH")

# 其他单位
print(Web3.to_wei(1, 'gwei'))      # 1000000000
print(Web3.to_wei(1, 'ether'))     # 1000000000000000000
print(Web3.to_wei(1, 'wei'))       # 1
```

## 📤 发送交易

### 构建和签名交易

```python
from eth_account import Account
import json

# 私钥和账户
private_key = '0x...'
sender = Account.from_key(private_key)
receiver = '0x...'

# 构建交易
nonce = w3.eth.get_transaction_count(sender.address)
tx = {
    'nonce': nonce,
    'to': receiver,
    'value': w3.to_wei(0.1, 'ether'),
    'gas': 21000,
    'gasPrice': w3.eth.gas_price,
    'chainId': 1  # 主网 ID
}

# 签名交易
signed_tx = w3.eth.account.sign_transaction(tx, private_key)

# 发送交易
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
print(f"Transaction Hash: {tx_hash.hex()}")

# 等待交易确认
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"Transaction Confirmed: {receipt['status']}")
```

### 使用 EIP-1559 交易类型

```python
from web3.types import TxParams

# 获取当前基础费用
latest_block = w3.eth.get_block('latest')
base_fee = latest_block['baseFeePerGas']

# 计算优先费用（小费）
max_priority_fee_per_gas = w3.to_wei(2, 'gwei')
max_fee_per_gas = base_fee + max_priority_fee_per_gas

# 构建交易
tx = {
    'type': '0x2',  # EIP-1559 交易类型
    'nonce': nonce,
    'to': receiver,
    'value': w3.to_wei(0.1, 'ether'),
    'gas': 21000,
    'maxPriorityFeePerGas': max_priority_fee_per_gas,
    'maxFeePerGas': max_fee_per_gas,
    'chainId': 1
}

signed_tx = w3.eth.account.sign_transaction(tx, private_key)
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
```

## 📜 智能合约交互

### 部署合约

```python
from web3 import Web3
from eth_account import Account

# 合约 ABI 和 Bytecode
contract_abi = [...]  # 合约 ABI
contract_bytecode = '0x...'  # 合约字节码

# 创建合约实例
Contract = w3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)

# 构建部署交易
nonce = w3.eth.get_transaction_count(sender.address)
construct_txn = Contract.constructor().build_transaction({
    'nonce': nonce,
    'gas': 2000000,
    'gasPrice': w3.eth.gas_price,
    'chainId': 1
})

# 签名并发送
signed_txn = w3.eth.account.sign_transaction(construct_txn, private_key)
tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

# 获取合约地址
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
contract_address = receipt['contractAddress']
print(f"Contract deployed at: {contract_address}")
```

### 调用合约方法（读）

```python
# 连接到已部署的合约
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# 调用 read 方法（不消耗 gas）
result = contract.functions.getBalance(sender.address).call()
print(f"Balance: {result}")

# 调用带参数的方法
total_supply = contract.functions.totalSupply().call()
print(f"Total Supply: {total_supply}")
```

### 调用合约方法（写）

```python
# 调用 write 方法（消耗 gas）
nonce = w3.eth.get_transaction_count(sender.address)

# 构建交易
txn = contract.functions.transfer(
    receiver,
    w3.to_wei(10, 'ether')
).build_transaction({
    'nonce': nonce,
    'gas': 100000,
    'gasPrice': w3.eth.gas_price,
    'chainId': 1
})

# 签名并发送
signed_txn = w3.eth.account.sign_transaction(txn, private_key)
tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

# 等待确认
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"Transfer completed: {tx_hash.hex()}")
```

### 批量调用

```python
# 同时调用多个方法
call_data = [
    contract.functions.getBalance(sender.address),
    contract.functions.totalSupply(),
    contract.functions.symbol()
]

results = [func.call() for func in call_data]
print(f"Results: {results}")
```

## 🎭 事件监听

### 监听新事件

```python
from web3.contract import ContractEvents

# 获取事件对象
transfer_event = contract.events.Transfer

# 创建过滤器
filter = transfer_event.create_filter(fromBlock='latest')

# 持续监听
while True:
    for event in filter.get_new_entries():
        print(f"Transfer event detected:")
        print(f"  From: {event.args['from']}")
        print(f"  To: {event.args['to']}")
        print(f"  Value: {event.args['value']}")

    time.sleep(2)
```

### 查询历史事件

```python
# 查询特定区块范围的事件
from_block = w3.eth.block_number - 1000
to_block = 'latest'

filter = transfer_event.create_filter(
    fromBlock=from_block,
    toBlock=to_block,
    argument_filters={'from': sender.address}
)

events = filter.get_all_entries()
print(f"Found {len(events)} events")

for event in events:
    print(f"Block {event['blockNumber']}: {event.args}")
```

## 🌐 多网络支持

### 连接到不同的网络

```python
# Mainnet
w3_mainnet = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/YOUR_ID'))

# Sepolia 测试网
w3_sepolia = Web3(Web3.HTTPProvider('https://sepolia.infura.io/v3/YOUR_ID'))

# Polygon
w3_polygon = Web3(Web3.HTTPProvider('https://polygon-rpc.com'))

# BSC
w3_bsc = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org'))

# 本地节点
w3_local = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
```

### WebSocket 连接

```python
w3_ws = Web3(Web3.WebsocketProvider('wss://mainnet.infura.io/ws/v3/YOUR_ID'))

if w3_ws.is_connected():
    print("WebSocket connected!")

# 订阅新区块
def handle_new_block(block_hash):
    block = w3_ws.eth.get_block(block_hash)
    print(f"New block: {block['number']}")

new_block_filter = w3_ws.eth.filter('latest')
new_block_filter.watch(handle_new_block)
```

## 🔧 常用工具函数

### 地址验证

```python
from web3 import Web3

# 验证地址格式
address = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'

is_valid = Web3.is_address(address)
print(f"Valid address: {is_valid}")

# 转换为校验和格式
checksum_address = Web3.to_checksum_address(address.lower())
print(f"Checksum: {checksum_address}")

# 验证校验和
is_checksum = Web3.is_checksum_address(checksum_address)
print(f"Is checksum: {is_checksum}")
```

### 数据编码/解码

```python
from eth_abi import encode

# 编码函数参数
data = encode(
    ['address', 'uint256', 'string'],
    [sender.address, 100, 'Hello']
)
print(f"Encoded: {data.hex()}")

# 解码函数返回值
from eth_abi import decode
decoded = decode(['uint256', 'bool'], b'\x00...\x01')
print(f"Decoded: {decoded}")
```

### Keccak 哈希

```python
from web3 import Web3

# 字符串哈希
hash_value = Web3.keccak(text="Hello World")
print(f"Hash: {hash_value.hex()}")

# 字节哈希
hash_value = Web3.keccak(b'Hello World')
print(f"Hash: {hash_value.hex()}")

# 数组哈希
hash_value = Web3.keccak([1, 2, 3])
print(f"Hash: {hash_value.hex()}")
```

## ⛽ Gas 优化

### 估算 Gas

```python
# 估算合约调用 Gas
gas_estimate = contract.functions.transfer(
    receiver,
    w3.to_wei(1, 'ether')
).estimate_gas({'from': sender.address})

print(f"Estimated Gas: {gas_estimate}")

# 增加 20% 缓冲
gas_limit = int(gas_estimate * 1.2)
```

### 动态 Gas 价格

```python
# 获取当前 Gas 价格
gas_price = w3.eth.gas_price
print(f"Current gas price: {w3.from_wei(gas_price, 'gwei')} Gwei")

# 获取历史 Gas 价格
latest_block = w3.eth.get_block('latest')
historical_gas_price = latest_block['baseFeePerGas']

# 使用中等 Gas 价格策略
medium_gas_price = w3.eth.gas_price
```

## 🧪 测试

### 使用 Ganache/Hardhat 本地节点

```python
# 连接到本地节点
w3_local = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

# 查询所有账户
accounts = w3_local.eth.accounts
print(f"Accounts: {accounts}")

# 查询默认账户余额
balance = w3_local.eth.get_balance(accounts[0])
print(f"Balance: {w3_local.from_wei(balance, 'ether')} ETH")
```

### pytest 测试

```python
import pytest
from web3 import Web3

@pytest.fixture
def w3():
    return Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

@pytest.fixture
def account(w3):
    return w3.eth.accounts[0]

def test_transfer(w3, account):
    # 发送测试交易
    tx_hash = w3.eth.send_transaction({
        'from': account,
        'to': w3.eth.accounts[1],
        'value': w3.to_wei(1, 'ether')
    })

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    assert receipt['status'] == 1
```

## 🔐 安全最佳实践

### 私钥管理

```python
import os
from eth_account import Account

# ✅ 从环境变量读取
private_key = os.getenv('PRIVATE_KEY')

# ❌ 永远不要在代码中硬编码私钥
# private_key = '0x123...'  # 不要这样做！

# ✅ 使用 Keyfile 加密
encrypted = Account.encrypt(private_key, 'my_password')
with open('keystore.json', 'w') as f:
    json.dump(encrypted, f)

# 解密
with open('keystore.json', 'r') as f:
    encrypted_key = json.load(f)

decrypted_key = Account.decrypt(encrypted_key, 'my_password')
```

### 交易安全

```python
# ✅ 总是验证接收地址
if not Web3.is_address(receiver):
    raise ValueError("Invalid receiver address")

# ✅ 检查余额
balance = w3.eth.get_balance(sender.address)
if balance < amount + gas_fee:
    raise ValueError("Insufficient balance")

# ✅ 设置合理的 Gas 限制
gas_estimate = contract.functions.someMethod().estimate_gas()
gas_limit = int(gas_estimate * 1.2)  # 20% 缓冲

# ✅ 验证交易
# 在测试网先测试
# 使用模拟器（如 Tenderly）预览交易
```

## 📊 常用 RPC 提供商

| 提供商 | URL | 说明 |
|-------|-----|------|
| Infura | https://infura.io | 免费额度，稳定 |
| Alchemy | https://www.alchemy.com | 免费，支持增强 API |
| QuickNode | https://www.quicknode.com | 专业支持 |
| Ankr | https://www.ankr.com | 免费公共节点 |
| Cloudflare | https://cloudflare-eth.com | 免费公共节点 |

---

**更新时间**: 2026-02-03
