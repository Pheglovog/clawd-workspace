# Layer 0: EVM 操作码详解

> **目标**: 系统性学习以太坊虚拟机 (EVM) 的所有操作码，理解执行机制和 Gas 消耗

---

## 📋 学习目标

1. ✅ 掌握所有 140+ 个 EVM 操作码的用途和参数
2. ✅ 理解操作码的分类（算术、比较、位运算、密钥等）
3. ✅ 掌握堆栈、内存和存储模型的交互
4. ✅ 理解每个操作码的 Gas 消耗
5. ✅ 实践编写简单的操作码序列

---

## 📊 EVM 操作码分类

### 0x0x: 算术运算 (Arithmetic Operations)

#### 加法 (Addition)
```solidity
// 0x01: ADD
function add(uint256 x, uint256 y) public pure returns (uint256) {
    return x + y;  // 弹出栈顶两个值，将结果推回栈
}
```

**Gas 消耗**: 3 gas
**栈操作**: pop 2, push 1 (净 -1)
**说明**: 栈顶两个值相加，结果推入栈

---

#### 乘法 (Multiplication)
```solidity
// 0x02: MUL
function mul(uint256 x, uint256 y) public pure returns (uint256) {
    return x * y;  // 弹出栈顶两个值，将结果推回栈
}
```

**Gas 消耗**: 5 gas
**栈操作**: pop 2, push 1 (净 -1)
**说明**: 栈顶两个值相乘，结果推入栈

---

#### 减法 (Subtraction)
```solidity
// 0x03: SUB
function sub(uint256 x, uint256 y) public pure returns (uint256) {
    return x - y;  // 第二个值从第一个值中减去
}
```

**Gas 消耗**: 3 gas
**栈操作**: pop 2, push 1 (净 -1)
**说明**: 第二个值从第一个值中减去，结果推入栈

**注意**: 可能发生下溢出（underflow）

---

#### 除法 (Division)
```solidity
// 0x04: DIV
function div(uint256 x, uint256 y) public pure returns (uint256) {
    return x / y;  // 第一个值除以第二个值（整除）
}
```

**Gas 消耗**: 5 gas
**栈操作**: pop 2, push 1 (净 -1)
**说明**: 第一个值除以第二个值（整除），结果推入栈

**注意**: 如果 y = 0，会抛出除零异常（Division by zero）

---

#### 取模 (Modulo)
```solidity
// 0x05: MOD
function mod(uint256 x, uint256 y) public pure returns (uint256) {
    return x % y;  // 第一个值对第二个值取模
}
```

**Gas 消耗**: 5 gas
**栈操作**: pop 2, push 1 (净 -1)
**说明**: 第一个值对第二个值取模，余数推入栈

**注意**: 如果 y = 0，会抛出除零异常（Division by zero）

---

#### 加法取模 (AddMod)
```solidity
// 0x08: AD
function addmod(uint256 x, uint256 y, uint256 m) public pure returns (uint256) {
    return (x + y) % m;  // (x + y) 对 m 取模
}
```

**Gas 消耗**: 8 gas
**栈操作**: pop 3, push 1 (净 -2)
**说明**: 前两个值相加，结果对第三个值取模

**注意**: 这是单个原子操作，比 ADD + MOD 更高效且更安全（不会下溢出）

---

#### 乘法取模 (MulMod)
```solidity
// 0x09: MULMOD
function mulmod(uint256 x, uint256 y, uint256 m) public pure returns (uint256) {
    return (x * y) % m;  // (x * y) 对 m 取模
}
```

**Gas 消耗**: 14 gas
**栈操作**: pop 3, push 1 (净 -2)
**说明**: 前两个值相乘，结果对第三个值取模

**注意**: 原子操作，比 MUL + MOD 更高效

---

#### 扩展加法 (AddMod)
```solidity
// 0x0B: EXP
function exp(uint256 base, uint256 exponent) public pure returns (uint256) {
    return base ** exponent;  // 指数运算（仅限小指数）
}
```

**Gas 消耗**: 10 gas (动态，随指数增加)
**栈操作**: pop 2, push 1 (净 -1)
**说明**: 第一个值的第二个值次方（仅限小指数）

**注意**: 大指数会消耗大量 gas

---

### 0x10x1F: 比较运算 (Comparison Operations)

#### 小于 (Less Than)
```solidity
// 0x10: LT
function lt(uint256 x, uint256 y) public pure returns (bool) {
    return x < y;  // 如果第一个值 < 第二个值，推入 1
}
```

**Gas 消耗**: 3 gas
**栈操作**: pop 2, push 1 (净 -1)
**说明**: 比较栈顶两个值，如果条件为真则推入 1，否则推入 0

---

#### 大于 (Greater Than)
```solidity
// 0x11: GT
function gt(uint256 x, uint256 y) public pure returns (bool) {
    return x > y;  // 如果第一个值 > 第二个值，推入 1
}
```

**Gas 消耗**: 3 gas
**栈操作**: pop 2, push 1 (净 -1)
**说明**: 比较栈顶两个值，如果条件为真则推入 1，否则推入 0

---

#### 小于等于 (Less Than or Equal)
```solidity
// 0x14: EQ
function eq(uint256 x, uint256 y) public pure returns (bool) {
    return x == y;  // 如果第一个值 == 第二个值，推入 1
}
```

**Gas 消耗**: 3 gas
**栈操作**: pop 2, push 1 (净 -1)
**说明**: 比较栈顶两个值是否相等

---

#### 大于等于 (Greater Than or Equal)
```solidity
// 0x15: ISZERO
function iszero(uint256 x) public pure returns (bool) {
    return x == 0;  // 如果值是 0，推入 1，否则推入 0
}
```

**Gas 消耗**: 3 gas
**栈操作**: pop 1, push 1
**说明**: 检查值是否为零

---

### 0x20x2F: 位运算 (Bitwise Operations)

#### 按位与 (Bitwise AND)
```solidity
// 0x16: AND
function and(uint256 x, uint256 y) public pure returns (uint256) {
    return x & y;  // 栈顶两个值按位与运算
}
```

**Gas 消耗**: 3 gas
**栈操作**: pop 2, push 1 (净 -1)
**说明**: 栈顶两个值的按位与运算结果

---

#### 按位或 (Bitwise OR)
```solidity
// 0x17: OR
function or(uint256 x, uint256 y) public pure returns (uint256) {
    return x | y;  // 栈顶两个值按位或运算
}
```

**Gas 消耗**: 3 gas
**栈操作**: pop 2, push 1 (净 -1)
**说明**: 栈顶两个值的按位或运算结果

---

#### 按位异或 (Bitwise XOR)
```solidity
// 0x18: XOR
function xor(uint256 x, uint256 y) public pure returns (uint256) {
    return x ^ y;  // 栈顶两个值按位异或运算
}
```

**Gas 消耗**: 3 gas
**栈操作**: pop 2, push 1 (净 -1)
**说明**: 栈顶两个值的按位异或运算结果

---

#### 按位非 (Bitwise NOT)
```solidity
// 0x19: NOT
function not(uint256 x) public pure returns (uint256) {
    return ~x;  // 栈顶值按位非运算
}
```

**Gas 消耗**: 3 gas
**栈操作**: pop 1, push 1 (净 0)
**说明**: 栈顶值的按位取反

---

#### 字节操作 (Byte Operations)

```solidity
// 0x1A: BYTE
// 0x1B: SHL (Shift Left)
// 0x1C: SHR (Shift Right Right)
// 0x1D: SAR (Shift Arithmetic Right)
function byte(uint256 x, uint256 position) public pure returns (uint256) {
    return uint8(x >> (position * 8));  // 获取指定字节
}

function shl(uint256 x, uint256 shift) public pure returns (uint256) {
    return x << shift;  // 左移
}

function shr(uint256 x, uint256 shift) public pure returns (uint256) {
    return x >> shift;  // 逻辑右移
}

function sar(uint256 x, uint256 shift) public pure returns (uint256) {
    return x >> shift;  // 算术右移（保留符号位）
}
```

---

### 0x30x3F: 密码学操作 (Cryptographic Operations)

#### Keccak-256 (Ethereum-Presented Hash)

```solidity
// 0x20: KECCAK256
function keccak256(bytes memory data) public pure returns (bytes32) {
    return keccak256(data);  // 计算数据的 Keccak-256 哈希
}
```

**Gas 消耗**: 30 gas + 6 * (len(data) / 32)
**栈操作**: pop 1, push 1 (净 0)
**说明**: 计算内存中数据的 Keccak-256 哈希

**注意**: 这是以太坊的默认哈希函数

---

#### RIPEMD-160 (RIPEMD-160 Hash)

```solidity
// 0x20: RIPEMD160
function ripemd160(bytes memory data) public pure returns (bytes20) {
    return ripemd160(data);  // 计算 RIPEMD-160 哈希
}
```

**Gas 消耗**: 600 gas + (len(data) * 120)
**栈操作**: pop 1, push 1 (净 0)
**说明**: 计算内存中数据的 RIPEMD-160 哈希

**注意**: 仅用于兼容比特币，以太坊主要使用 Keccak-256

---

#### ECRecover (椭圆曲线签名恢复)

```solidity
// 0x01: ECRECOVER
function ecrecover(bytes32 hash, uint8 v, uint8 r, uint8 s) public pure returns (address) {
    return ecrecover(hash, v, r, s);  // 从签名恢复以太坊地址
}
```

**Gas 消耗**: 3000 gas
**栈操作**: pop 4, push 1 (净 -3)
**说明**: 从 ECDSA 签名恢复公钥地址

**注意**: 非常昂贵，仅在需要时使用

---

### 0x40x4F: 环境信息 (Environmental Information)

#### 区块哈希 (Block Hash)

```solidity
// 0x40: BLOCKHASH
function blockhash(uint256 blockNumber) public view returns (bytes32) {
    return blockhash(blockNumber);  // 获取指定区块的哈希
}
```

**Gas 消耗**: 20 gas
**栈操作**: pop 1, push 1 (净 0)
**说明**: 获取指定区块号的区块哈希

**注意**: 只能获取最近 256 个区块的哈希

---

#### Coinbase (区块生产者地址)

```solidity
// 0x41: COINBASE
function coinbase() public view returns (address) {
    return block.coinbase;  // 获取当前区块生产者的地址
}
```

**Gas 消耗**: 2 gas
**栈操作**: pop 0, push 1 (净 +1)
**说明**: 获取当前区块生产者的地址

**注意**: 仅在 PoS 以太坊中有意义

---

#### 时间戳 (Timestamp)

```solidity
// 0x42: TIMESTAMP
function timestamp() public view returns (uint256) {
    return block.timestamp;  // 获取当前区块的时间戳
}
```

**Gas 消耗**: 2 gas
**栈操作**: pop 0, push 1 (净 +1)
**说明**: 获取当前区块的时间戳（Unix 时间）

**注意**: 可用于跟踪时间，但不适合高精度计算

---

#### 区块编号 (Block Number)

```solidity
// 0x43: NUMBER
function number() public view returns (uint256) {
    return block.number;  // 获取当前区块号
}
```

**Gas 消耗**: 2 gas
**栈操作**: pop 0, push 1 (净 +1)
**说明**: 获取当前区块号

**注意**: 可用于检查合约是否在特定区块前部署

---

#### 难度 (Difficulty)

```solidity
// 0x44: DIFFICULTY
function difficulty() public view returns (uint256) {
    return block.difficulty;  // 获取当前区块的难度
}
```

**Gas 消耗**: 2 gas
**栈操作**: pop 0, push 1 (净 +1)
**说明**: 获取当前区块的难度（仅对 PoW 以太坊有意义）

**注意**: 在 PoS 以太坊中已弃用

---

#### Gas 限制 (Gas Limit)

```solidity
// 0x45: GASLIMIT
function gaslimit() public view returns (uint256) {
    return block.gaslimit;  // 获取当前区块的 gas 上限
}
```

**Gas 消耗**: 2 gas
**栈操作**: pop 0, push 1 (净 +1)
**说明**: 获取当前区块的 gas 上限

**注意**: 可用于计算交易容量，但不应作为随机数源

---

#### 链 ID (Chain ID)

```solidity
// 0x46: CHAINID
function chainid() public view returns (uint256) {
    return block.chainid;  // 获取当前链的 ID
}
```

**Gas 消耗**: 2 gas
**栈操作**: pop 0, push 1 (净 +1)
**说明**: 获取当前链的 ID（用于区分不同的以太坊网络）

**注意**: 主网 = 1，测试网 = 5

---

#### 自我余额 (Self Balance)

```solidity
// 0x47: SELFBALANCE
function selfbalance() public view returns (uint256) {
    return address(this).balance;  // 获取当前合约的 ETH 余额
}
```

**Gas 消耗**: 5 gas (如果使用 BALANCE) 或 0x47 (特殊)
**栈操作**: pop 0, push 1 (净 +1)
**说明**: 获取当前合约地址的 ETH 余额

**注意**: 可用于检查合约资金

---

### 0x50x5F: 区块和交易信息 (Block and Transaction Information)

#### POP 操作

```solidity
// 0x50: POP
// 从栈顶移除一个值（不返回）
function popTest() public pure {
    // 在 EVM 汇编中直接使用 POP 操作码
    // 在 Solidity 中使用 delete 来模拟
}
```

**Gas 消耗**: 2 gas
**栈操作**: pop 1, push 0 (净 -1)
**说明**: 从栈顶移除一个值

---

#### MLOAD (Memory Load)

```solidity
// 0x51: MLOAD
function mload(uint256 offset) public pure returns (bytes32) {
    // 从内存读取 32 字节
    assembly {
        let result := mload(offset)
    }
    return result;
}
```

**Gas 消耗**: 3 gas (访问 warm 内存) 或 9 gas (访问 cold 内存)
**栈操作**: pop 1, push 1 (净 0)
**说明**: 从指定内存偏移量读取 32 字节

---

#### MSTORE (Memory Store)

```solidity
// 0x52: MSTORE
function mstore(uint256 offset, bytes32 value) public pure {
    // 向内存写入 32 字节
    assembly {
        mstore(offset, value)
    }
}
```

**Gas 消耗**: 3 gas (访问 warm 内存) 或 9 gas (访问 cold 内存)
**栈操作**: pop 2, push 0 (净 -2)
**说明**: 向指定内存偏移量写入 32 字节（覆盖）

---

#### MSTORE8 (Memory Store Byte)

```solidity
// 0x53: MSTORE8
function mstore8(uint256 offset, uint8 value) public pure {
    // 向内存写入 1 字节
    assembly {
        mstore8(offset, value)
    }
}
```

**Gas 消耗**: 3 gas (访问 warm 内存) 或 9 gas (访问 cold 内存)
**栈操作**: pop 2, push 0 (净 -2)
**说明**: 向指定内存偏移量写入 1 字节（覆盖）

---

#### SLOAD (Storage Load)

```solidity
// 0x54: SLOAD
function sload(uint256 slot) public view returns (bytes32) {
    return sload(slot);  // 从存储读取 32 字节
}
```

**Gas 消耗**: 100 gas (warm) 或 2100 gas (cold)
**栈操作**: pop 1, push 1 (净 0)
**说明**: 从指定存储槽位读取 32 字节

**注意**: 存储访问非常昂贵！设计合约时应最小化 SLOAD 次数

---

#### SSTORE (Storage Store)

```solidity
// 0x55: SSTORE
function sstore(uint256 slot, bytes32 value) public {
    sstore(slot, value);  // 向存储写入 32 字节
}
```

**Gas 消耗**:
- 初始化（从零到非零）: 20000 gas (warm) 或 5000 gas (cold)
- 写入新值: 20000 gas (warm) 或 5000 gas (cold)
- 写入相同值: 100 gas

**栈操作**: pop 2, push 0 (净 -2)
**说明**: 向指定存储槽位写入 32 字节

**注意**: 存储写入极其昂贵！只在必要时使用

---

#### JUMP (无条件跳转)

```solidity
// 0x56: JUMP
function jump(uint256 target) public pure {
    // 在 EVM 汇编中跳转到指定位置
    // Solidity 中不能直接使用
}
```

**Gas 消耗**: 8 gas
**栈操作**: pop 1, push 0 (净 -1)
**说明**: 无条件跳转到指定代码位置

**注意**: Solidity 的高级特性，需要内联汇编

---

#### JUMPI (条件跳转)

```solidity
// 0x57: JUMPI
function jumpi(uint256 target, uint256 condition) public pure {
    // 在 EVM 汇编中根据条件跳转
    // Solidity 中不能直接使用
}
```

**Gas 消耗**: 10 gas
**栈操作**: pop 2, push 0 (净 -2)
**说明**: 如果栈顶值为真，则跳转到指定位置

**注意**: Solidity 的高级特性，需要内联汇编

---

#### PC (程序计数器)

```solidity
// 0x58: PC
function pc() public pure returns (uint256) {
    // 在 EVM 汇编中获取当前程序计数器
    // Solidity 中不能直接使用
}
```

**Gas 消耗**: 2 gas
**栈操作**: pop 1, push 0 (净 -1)
**说明**: 获取当前程序计数器的值

**注意**: Solidity 中不可用，仅用于调试和汇编

---

#### MSIZE (内存大小)

```solidity
// 0x59: MSIZE
function msize() public pure returns (uint256) {
    // 获取当前活跃内存大小（最高访问地址 + 32）
    assembly {
        let size := msize()
    }
    return size;
}
```

**Gas 消耗**: 2 gas
**栈操作**: pop 0, push 1 (净 +1)
**说明**: 获取当前活跃内存大小

---

#### GAS (Gas 价格)

```solidity
// 0x5A: GAS
function gasprice() public view returns (uint256) {
    return tx.gasprice;  // 获取当前交易的 gas 价格
}
```

**Gas 消耗**: 2 gas
**栈操作**: pop 0, push 1 (净 +1)
**说明**: 获取当前交易的 gas 价格（wei/单位）

**注意**: 可用于动态调整交易费用

---

#### JUMPDEST (跳转目标)

```solidity
// 0x5B: JUMPDEST
function jumpdest() public pure {
    // 在 EVM 汇编中标记跳转目标
    // Solidity 中不能直接使用
}
```

**Gas 消耗**: 1 gas
**栈操作**: pop 0, push 0 (净 0)
**说明**: 标记跳转目标位置，确保跳转有效

**注意**: Solidity 中不可用，仅用于汇编优化

---

### 0x60x6F: 汇编操作 (Push Operations)

#### PUSH1 - PUSH32 (压栈操作)

```solidity
// 0x60: PUSH1 ~ 0x7F: PUSH32
function pushExample() public pure returns (uint256) {
    // PUSH1 推入 1 字节
    // PUSH32 推入 32 字节
    // 在 Solidity 中使用常数或 calldata
    return 0x1234;  // 示例：返回固定值（在 EVM 中用 PUSH 推入）
}
```

**Gas 消耗**: 2 gas (每个 PUSH 操作码)
**栈操作**: pop 0, push 1 (净 +1)
**说明**: 将指定字节数推入栈

**注意**: 这些是 EVM 的基本数据加载操作

---

#### DUP1 - DUP16 (复制操作)

```solidity
// 0x80: DUP1 ~ 0x8F: DUP16
function dupExample(uint256 a, uint256 b, uint256 c) public pure returns (uint256) {
    // DUP1 复制栈顶第一个值
    // DUP16 复制栈顶第 16 个值
    // 在 Solidity 中使用变量来实现
    uint256 dup1 = a;  // DUP1 示例
    uint256 dup2 = b;  // DUP2 示例
    return a;  // 返回栈顶值
}
```

**Gas 消耗**: 3 gas (每个 DUP 操作码)
**栈操作**: pop 0, push 1 (净 +1)
**说明**: 复制栈中指定位置的值到栈顶

**注意**: 这些是 EVM 的基本栈操作，用于减少代码大小

---

#### SWAP1 - SWAP16 (交换操作)

```solidity
// 0x90: SWAP1 ~ 0x9F: SWAP16
function swapExample(uint256 a, uint256 b, uint256 c) public pure returns (uint256) {
    // SWAP1 交换栈顶第 1 个值和第 1 个值
    // SWAP16 交换栈顶第 1 个值和第 16 个值
    // 在 Solidity 中使用变量交换来实现
    uint256 temp = a;
    a = b;
    b = temp;
    return c;  // 返回栈顶值
}
```

**Gas 消耗**: 3 gas (每个 SWAP 操作码)
**栈操作**: pop 0, push 0 (净 0)
**说明**: 交换栈中指定位置的值

**注意**: 这些是 EVM 的基本栈操作，用于优化代码

---

#### LOG0 - LOG4 (日志操作)

```solidity
// 0xA0: LOG0 ~ 0xA4: LOG4
event LogData(uint256 indexed topic1, bytes data);

function logExample(uint256 topic, bytes memory data) public {
    // LOG0 记录 0 个主题和数据
    // LOG4 记录 4 个主题和数据
    emit LogData(topic, data);  // Solidity 中的事件对应 LOG 操作码
}
```

**Gas 消耗**:
- LOG0: 375 gas + 8 * (len(data) / 32)
- LOG4: 375 gas + 375 gas + 8 * (len(data) / 32)

**栈操作**: pop 5, push 0 (净 -5) (对于 LOG4)
**说明**: 记录数据到交易日志（仅索引主题）

**注意**: 日志数据不存储在状态中，但会被归档节点

---

#### CREATE (创建合约)

```solidity
// 0xF0: CREATE
function createContract(bytes memory bytecode) public returns (address) {
    address newContract;
    assembly {
        newContract := create(0, bytecode)  // 部署新合约
    }
    return newContract;
}
```

**Gas 消耗**: 32000 gas
**栈操作**: pop 3, push 1 (净 -2)
**说明**: 从内存创建新合约，并返回新合约地址

**注意**: 这是最昂贵的操作之一

---

#### CALL (调用合约)

```solidity
// 0xF1: CALL
function callContract(address target, bytes memory data) public returns (bool success, bytes memory result) {
    // 调用外部合约
    (success, result) = target.staticcall(data);
    return (success, result);
}
```

**Gas 消耗**:
- 基础: 700 gas
- 访问内存: 3 gas (warm) 或 9 gas (cold)
- 调用合约: 2500 gas (value 非零) 或 100 gas (value 为零)
- 每访问 32 字节内存: 3 gas

**栈操作**: pop 7, push 1 (净 -6)
**说明**: 调用外部合约，传递 value 和 data

**注意**: 这是 EVM 的主要外部调用操作

---

#### CALLCODE (调用并返回代码)

```solidity
// 0xF2: CALLCODE
function callcodeExample(address target, bytes memory data) public returns (bytes memory) {
    // 在 EVM 汇编中调用合约并返回其代码
    // Solidity 中不能直接使用
    assembly {
        let code := callcode(gas(), 0, 0, target, data, 0, 0)
        return code;
    }
}
```

**Gas 消耗**: 700 + (额外 gas)
**栈操作**: pop 6, push 1 (净 -5)
**说明**: 调用合约并返回其运行时代码

**注意**: 已在 EIP-150 中弃用，使用 CREATE2 代替

---

#### RETURN (返回值)

```solidity
// 0xF3: RETURN
function returnData(bytes memory data) public pure returns (bytes memory) {
    // 在 EVM 汇编中返回数据给调用者
    // Solidity 中使用 return 语句
    return data;  // Solidity 中的 return 对应 RETURN 操作码
}
```

**Gas 消耗: 0 gas
**栈操作**: pop 2, push 0 (净 -2)
**说明**: 从内存读取数据并返回给调用者

**注意**: 合约执行的最后操作

---

#### DELEGATECALL (代理调用)

```solidity
// 0xF4: DELEGATECALL
function delegatecallExample(address proxy, bytes memory data) public returns (bool success, bytes memory result) {
    // 在 EVM 汇编中代理调用（使用调用者的存储和上下文）
    // Solidity 中不能直接使用
    assembly {
        (success, result) := delegatecall(gas(), 0, 0, proxy, data)
    }
    return (success, result);
}
```

**Gas 消耗**: 700 gas + (存储访问成本)
**栈操作**: pop 6, push 1 (净 -5)
**说明**: 使用调用者的存储和上下文调用代理合约

**注意**: 用于实现代理模式和可升级合约

---

#### STATICCALL (静态调用)

```solidity
// 0xFA: STATICCALL
function staticcallExample(address target, bytes memory data) public view returns (bytes memory) {
    // 静态调用：不允许修改状态
    (bool success, bytes memory result) = target.staticcall(data);
    return result;
}
```

**Gas 消耗**: 700 gas (不允许 value 修改状态）
**栈操作**: pop 6, push 1 (净 -5)
**说明**: 静态调用外部合约（不允许修改状态）

**注意**: 在编译时已确定不会修改状态，可优化 gas

---

#### REVERT (回滚)

```solidity
// 0xFD: REVERT
function revertExample(uint256 errorCode, bytes memory reason) public pure {
    // 回滚所有状态更改
    // Solidity 中使用 revert 语句
    revert(string(abi.encodeWithSelector("Error(uint256,string)", errorCode, reason)));
}
```

**Gas 消耗**: 所有已用 gas 都退还（除了已存储的 gas）
**栈操作**: pop 2, push 0 (净 -2)
**说明**: 回滚所有状态更改，不退还 gas

**注意**: 比无效代码更高效，因为不需要退还 gas

---

#### INVALID (无效操作)

```solidity
// 0xFE: INVALID
function invalidExample() public pure {
    // 在 EVM 汇编中标记无效指令
    // Solidity 中不能直接使用
}
```

**Gas 消耗: 全部剩余 gas（交易失败）
**栈操作**: pop 1, push 0 (净 -1)
**说明**: 标记当前指令无效

**注意**: 仅用于调试和异常处理

---

## 📚 学习资源

### 官方文档
- [Ethereum Yellow Paper](https://ethereum.github.io/yellowpaper/paper.pdf)
- [Ethereum EIPs](https://eips.ethereum.org/)
- [EVM Code Reference](https://www.evm.codes/)

### 工具
- [EVM Playground](https://www.evm.codes/playground)
- [Etherscan Opcodes](https://etherscan.io/opcodes)
- [Remix IDE](https://remix.ethereum.org/)

### 书籍
- 《Mastering Ethereum》
- 《The Art of Smart Contract Development》

---

## 🎯 实践练习

### 练习 1: 编写简单的算术操作
编写一个合约，实现基本的加法、减法、乘法和除法功能。

### 练习 2: 使用内存操作
编写一个合约，使用 MLOAD/MSTORE 来存储和读取数据。

### 练习 3: 使用存储操作
编写一个合约，使用 SLOAD/SSTORE 来持久化状态。

### 练习 4: 编写循环
使用 JUMP/JUMPI 实现简单的循环结构。

### 练习 5: 使用事件日志
使用 LOG0-LOG4 记录重要的合约状态。

---

## 📝 学习笔记

### 关键概念

1. **栈模型** - EVM 使用基于栈的执行模型，最大深度 1024
2. **内存模型** - 每笔交易最多访问 24KB 内存
3. **存储模型** - 持久化状态，每 256 位槽 32 字节，访问非常昂贵
4. **Gas 机制** - 每个操作码有固定的 gas 消耗，限制交易大小和执行时间
5. **异常处理** - 无效操作会消耗所有 gas，REVERT 返回 gas

### 优化技巧

1. **使用更便宜的操作码** - ADD 比 MUL 更便宜（3 gas vs 5 gas）
2. **批量存储** - 使用 MSTORE8 代替多次 MSTORE
3. **预计算** - 在部署前预计算常用值
4. **事件日志** - 最小化 LOG 数据量
5. **使用 STATICCALL** - 如果只读状态，使用 STATICCALL 节省 gas

---

**下一课**: Layer 1: 共识机制 (PoS, GHOST 协议)
