# Layer 0: EVM 深入解析 - 执行流程、状态转换、Gas 精确计算

> **目标**: 真正理解 EVM 的核心机制，不仅仅是列举操作码，而是深入理解执行流程、栈/内存/存储交互、Gas 消耗计算

---

## 📋 学习目标

1. ✅ 理解 EVM 的完整执行流程（从交易到最终状态）
2. ✅ 掌握栈、内存、存储的精确交互机制
3. ✅ 深入理解 Gas 消耗的每个组成部分
4. ✅ 理解 EVM 字节码结构和汇编转换
5. ✅ 掌握异常处理和回滚机制

---

## 🏗️ EVM 执行流程

### 1. 交易生命周期

```python
class EVMTransactionExecution:
    def __init__(self):
        self.tx = None         # 原始交易对象
        self.env = Environment()  # 执行环境（区块信息等）
        self.substate = Substate()  # 子状态（临时状态）
        self.result = None     # 执行结果

    def execute(self, tx):
        """执行交易"""
        # =============================================
        # 阶段 1: 交易验证
        # =============================================
        self.validate_transaction(tx)

        # =============================================
        # 阶段 2: 转换到消息调用
        # =============================================
        self.message_call = self.convert_to_message_call(tx)

        # =============================================
        # 阶段 3: 执行消息调用
        # =============================================
        self.result = self.execute_message_call(self.message_call)

        # =============================================
        # 阶段 4: 计算交易收据
        # =============================================
        self.receipt = self.create_receipt(self.result)

        # =============================================
        # 阶段 5: 更新状态
        # =============================================
        self.apply_state_updates(self.result)

        return self.receipt
```

**关键概念**:
- ✅ **交易验证** - nonce、gas limit、签名、RLP 编码
- ✅ **消息调用** - 将交易转换为 EVM 可执行的消息
- ✅ **子状态** - 执行过程中的临时状态（可能被回滚）
- ✅ **收据创建** - 日志、状态根、gas used

---

### 2. EVM 环境模型

```python
class Environment:
    def __init__(self):
        # 区块信息
        self.block = Block(
            number=0,
            timestamp=0,
            coinbase=address(0),
            difficulty=0,
            gaslimit=30000000,
            chainid=1,
            basefee=0x1234  # EIP-1559: EIP-1559 Base Fee
        )

        # 交易信息
        self.tx = Transaction(
            origin=address(0),
            gasprice=0x1234,
            value=0
        )

        # 区块链状态
        self.state = StateDB()

        # 账户抽象
        self.accounts = Accounts(self.state)
```

**环境提供的操作码**:
- ✅ `0x40: BLOCKHASH` - 获取区块哈希
- ✅ `0x41: COINBASE` - 获取区块生产者
- ✅ `0x42: TIMESTAMP` - 获取区块时间戳
- ✅ `0x43: NUMBER` - 获取区块号
- ✅ `0x44: DIFFICULTY` - 获取区块难度（已弃用）
- ✅ `0x45: GASLIMIT` - 获取区块 gas 上限
- ✅ `0x46: CHAINID` - 获取链 ID
- ✅ `0x47: SELFBALANCE` - 获取当前合约余额
- ✅ `0x48: PUSH0` - 当前调用者地址
- ✅ `0x49: PUSH1` - 父区块哈希

---

## 💻 EVM 核心架构

### 1. 栈模型 (Stack Model)

#### 栈结构
```python
class Stack:
    def __init__(self, max_depth=1024):
        self.max_depth = max_depth
        self.stack = []  # 数组实现，支持随机访问

    def push(self, value):
        """压栈"""
        if len(self.stack) >= self.max_depth:
            raise StackOverflow("Stack limit exceeded")
        self.stack.append(value)

    def pop(self):
        """弹栈"""
        if len(self.stack) == 0:
            raise StackUnderflow("Stack underflow")
        return self.stack.pop()

    def peek(self, index):
        """查看栈元素（不弹栈）"""
        if index < 0 or index >= len(self.stack):
            raise StackOutOfBounds("Stack index out of bounds")
        return self.stack[-(index + 1)]

    def swap(self, n):
        """交换栈顶和第 n 个元素"""
        if n >= len(self.stack):
            raise StackOutOfBounds("Swap index out of bounds")
        depth = len(self.stack)
        self.stack[-1], self.stack[-(n + 1)] = \
            self.stack[-(n + 1)], self.stack[-1]

    def dup(self, n):
        """复制第 n 个元素到栈顶"""
        if n >= len(self.stack):
            raise StackOutOfBounds("Dup index out of bounds")
        self.stack.append(self.stack[-(n + 1)])
```

**栈操作 Gas 消耗**:
- ✅ **PUSH1-PUSH32**: 2 gas（无栈变化，只压栈）
- ✅ **DUP1-DUP16**: 3 gas（复制操作）
- ✅ **SWAP1-SWAP16**: 3 gas（交换操作）
- ✅ **POP**: 2 gas（弹栈）

---

### 2. 内存模型 (Memory Model)

#### 内存分配
```python
class Memory:
    def __init__(self):
        self.data = bytearray()  # 初始为空
        self.active_words = 0    # 活跃的字数（用于 gas 计算）

    def allocate(self, size):
        """分配内存"""
        # 计算需要的 32 字节对齐
        aligned_size = (size + 31) // 32 * 32

        # 计算新的活跃字数
        new_active_words = (len(self.data) + aligned_size) // 32

        # 计算 gas 消耗
        if new_active_words > self.active_words:
            # 扩容：每个新 word 3 gas
            gas_cost = (new_active_words - self.active_words) * 3
            self.active_words = new_active_words

        # 分配空间
        self.data.extend(bytes(aligned_size - size))

        return len(self.data) - size

    def load(self, offset, size):
        """从内存加载"""
        if offset + size > len(self.data):
            raise MemoryAccessError("Memory access out of bounds")

        # 如果访问未初始化的内存，视为 0
        if offset >= len(self.data):
            return bytes(size)
        elif offset + size > len(self.data):
            return self.data[offset:] + bytes((offset + size) - len(self.data))
        else:
            return self.data[offset:offset + size]

    def store(self, offset, data):
        """向内存存储"""
        size = len(data)
        self.allocate(offset + size)  # 确保内存已分配

        # 存储数据（覆盖）
        for i, byte in enumerate(data):
            self.data[offset + i] = byte
```

**内存 Gas 消耗**:
- ✅ **MLOAD**: 3 gas (warm) / 9 gas (cold)
- ✅ **MSTORE**: 3 gas (warm) / 9 gas (cold)
- ✅ **MSTORE8**: 3 gas (warm) / 9 gas (cold)
- ✅ **扩展内存**: 每 32 字节新 word 3 gas

**warm/cold 概念**:
- ✅ **warm**: 最近访问过 20 个 slot
- ✅ **cold**: 超过 20 个 slot 未访问
- ✅ **访问模式**: 基于最近访问的地址（slot alignment）

---

### 3. 存储模型 (Storage Model)

#### 存储结构
```python
class Storage:
    def __init__(self):
        self.slots = {}  # 存储槽映射（32 字节对齐）
        self.access_list = []  # 最近访问的地址列表

    def load(self, address, slot):
        """从存储加载"""
        # 计算存储键
        key = self._calculate_storage_key(address, slot)

        # 检查是否为 warm
        is_warm = self._is_warm_storage(key)

        # 计算 gas 消耗
        if is_warm:
            gas_cost = 100  # warm access
        else:
            gas_cost = 2100  # cold access

        # 记录访问
        self.access_list.append(key)
        if len(self.access_list) > 20:
            self.access_list.pop(0)

        # 返回数据
        if key not in self.slots:
            return bytes32(0)
        return self.slots[key]

    def store(self, address, slot, value):
        """向存储写入"""
        key = self._calculate_storage_key(address, slot)

        # 检查是否为 warm
        is_warm = self._is_warm_storage(key)

        # 检查是否为第一次写入（初始化）
        is_first_write = key not in self.slots

        # 计算 gas 消耗
        if is_first_write:
            gas_cost = 20000  # 初始化
        elif is_warm:
            gas_cost = 2900   # warm write
        else:
            gas_cost = 21000  # cold write

        # 检查是否写入相同值
        if key in self.slots and self.slots[key] == value:
            gas_cost = 100  # 重写相同值最便宜

        # 记录访问
        self.access_list.append(key)
        if len(self.access_list) > 20:
            self.access_list.pop(0)

        # 写入数据
        self.slots[key] = value

    def _calculate_storage_key(self, address, slot):
        """计算存储键"""
        # keccak256(abi.encodePacked(address, slot))
        return keccak256(abi.encodePacked(address, slot))

    def _is_warm_storage(self, key):
        """检查存储是否为 warm"""
        return key in self.access_list
```

**存储 Gas 消耗总结**:
| 操作 | 条件 | Gas |
|------|------|-----|
| SLOAD | warm | 100 |
| SLOAD | cold | 2100 |
| SSTORE | 第一次写入 | 20000 |
| SSTORE | warm write | 2900 |
| SSTORE | cold write | 21000 |
| SSTORE | 重写相同值 | 100 |

**存储设计最佳实践**:
- ✅ **最小化 SLOAD/SSTORE** - 存储访问非常昂贵
- ✅ **打包存储** - 将多个小值打包到一个槽
- ✅ **使用内存缓存** - 将频繁访问的值放在内存中
- ✅ **避免空检查** - 使用 `unchecked` 块

---

### 4. Gas 精确计算模型

#### Gas 计算公式

```python
class GasCalculator:
    def __init__(self):
        self.static_gas = 21000   # 交易基础 gas
        self.zero_byte_cost = 4      # 每个 0 字节 4 gas
        self.nonzero_byte_cost = 16  # 每个非 0 字节 16 gas
        self.zero_word_cost = 4     # 每个 0 word 4 gas
        self.nonzero_word_cost = 16  # 每个非 0 word 16 gas

    def calculate_intrinsic_gas(self, tx):
        """计算交易的内在 gas"""
        # 1. 基础 gas (21000)
        gas = self.static_gas

        # 2. 交易数据成本
        data = tx.data
        for i in range(0, len(data), 32):
            chunk = data[i:i+32]

            # 检查是否为 zero word (32 字节全为 0)
            if int.from_bytes(chunk, 'big') == 0:
                gas += self.zero_word_cost
            else:
                # 非 zero word，每个非 0 字节 16 gas
                nonzero_bytes = 0
                for byte in chunk:
                    if byte != 0:
                        nonzero_bytes += 1
                gas += self.nonzero_word_cost * 32 + \
                       (32 - nonzero_bytes) * self.zero_byte_cost + \
                       nonzero_bytes * self.nonzero_byte_cost

        # 3. 访问列表成本 (EIP-2930)
        for addr in tx.access_list:
            if not addr.is_warm:
                gas += 2400  # 冷地址访问 2400 gas
            # 热地址访问无额外成本

        return gas

    def calculate_message_call_gas(self, env, msg):
        """计算消息调用的 gas"""
        gas = 0

        # 1. 交易数据成本（已在上一步计算）
        gas += env.calculate_intrinsic_gas(msg.tx)

        # 2. 访问列表成本 (EIP-2930)
        for addr in msg.tx.access_list:
            if not env.accounts.is_warm(addr):
                gas += 2400

        # 3. 创建成本 (EIP-3860)
        if msg.kind == "CREATE":
            gas += 32000  # 创建账户成本
        elif msg.kind == "CREATE2":
            gas += 32000  # 创建账户成本

        return gas

    def calculate_gas_used(self, env, msg):
        """计算实际使用的 gas"""
        # 1. 计算内在 gas
        gas = self.calculate_message_call_gas(env, msg)

        # 2. 执行操作码消耗的 gas
        for op in msg.ops:
            gas += self.get_opcode_gas(env, op)

        # 3. 扩展内存消耗的 gas
        gas += env.memory.expansion_cost

        # 4. 存储访问消耗的 gas
        gas += self.storage.access_cost

        return gas
```

**EIP-2930 访问列表优化**:
- ✅ **warm 地址**: 账户有 nonce 或代码（最近使用过）
- ✅ **cold 地址**: 新账户，无 nonce 和代码
- ✅ **成本**: warm 免费，cold 2400 gas
- ✅ **好处**: 鼓励重用账户，减少垃圾账户

**EIP-3860 空账户成本**:
- ✅ **CREATE**: 32000 gas（创建新账户）
- ✅ **CREATE2**: 32000 gas（创建新账户）
- ✅ **奖励**: 如果账户为空，退还 15000 gas

---

## 📊 EVM 字节码结构

### 1. EVM 字节码格式

#### 完整交易结构
```python
class EVMBytecode:
    def __init__(self, tx):
        self.nonce = tx.nonce        # 1-9 字节
        self.gasPrice = tx.gasPrice  # 1-9 字节
        self.gasLimit = tx.gasLimit  # 1-9 字节
        self.to = tx.to                # 20 字节（可以是空）
        self.value = tx.value          # 0-32 字节
        self.data = tx.data            # 0-1074951 字节

    def encode(self):
        """RLP 编码交易"""
        # 1. RLP 编码 nonce, gasPrice, gasLimit, to, value, data
        items = [
            self.nonce,
            self.gasPrice,
            self.gasLimit,
            self.to,
            self.value,
            self.data
        ]

        # 2. 计算 RLP 编码
        encoded_tx = self._rlp_encode(items)

        # 3. 计算哈希
        tx_hash = keccak256(encoded_tx)

        # 4. 生成签名
        v, r, s = self.sign(tx_hash, self.private_key)

        # 5. 编码完整交易
        signed_tx = self._rlp_encode([
            self.nonce,
            self.gasPrice,
            self.gasLimit,
            self.to,
            self.value,
            self.data,
            v, r, s
        ])

        return signed_tx
```

**RLP (Recursive Length Prefix) 编码**:
- ✅ **递归前缀长度编码**：`[length, data]` 格式
- ✅ **单字节长度**: < 0x80，直接编码长度
- ✅ **多字节长度**: >= 0x80，`0x80 + length` 格式
- ✅ **列表编码**: `[length_1, length_2, ..., data]` 格式

---

### 2. EVM 汇编 (Assembly)

#### 汇编到字节码转换

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract AssemblyExample {
    // 汇编示例：加法函数
    function add(uint256 a, uint256 b) public pure returns (uint256) {
        assembly {
            // 手动写入字节码：0x01 = ADD
            mstore(0, 0x01)  // 将 ADD 操作码写入内存位置 0

            // 加载参数到栈
            // 假设 a 和 b 已经在栈顶

            // 执行操作码
            let result := mload(0)  // 从内存加载操作码

            // 实际上，EVM 会直接执行操作码
            // 这里只是展示汇编结构
        }

        return a + b;  // 编译器生成正确字节码
    }
}
```

**字节码示例**:
```solidity
// 示例：简单的加法函数
function add(uint256 a, uint256 b) public pure returns (uint256) {
    // 编译后的字节码：
    // PUSH1 0x00      // 0x60 0x00 (入栈 0)
    // PUSH1 0x01      // 0x61 0x01 (入栈 1)
    // ADD               // 0x01       (相加)
    // PUSH1 0x00      // 0x60 0x00 (入栈 0x20 - 内存地址)
    // MSTORE            // 0x52       (存入内存)
    // PUSH1 0x20      // 0x60 0x20 (入栈 0x20)
    // PUSH1 0x00      // 0x60 0x00 (入栈 0x20 - 内存地址)
    // RETURN            // 0xf3       (返回内存中的数据)

    // 实际编译：
    {
        0x60, 0x00,     // PUSH1 0
        0x60, 0x01,     // PUSH1 1
        0x01,           // ADD
        0x60, 0x00,     // PUSH1 0
        0x60, 0x20,     // PUSH1 32
        0x52,           // MSTORE
        0x60, 0x20,     // PUSH1 32
        0x60, 0x00,     // PUSH1 0
        0xf3            // RETURN
    }
}
```

**字节码解读**:
1. `0x60 0x00` - 将 0 压栈
2. `0x60 0x01` - 将 1 压栈
3. `0x01` - 栈顶两数相加
4. `0x60 0x00` - 将 0 压栈（内存偏移量）
5. `0x60 0x20` - 将 32 压栈（值大小）
6. `0x52` - 从栈弹出（地址, 值）存入内存
7. `0x60 0x20` - 将 32 压栈（内存偏移量）
8. `0x60 0x00` - 将 0 压栈（返回大小）
9. `0xf3` - 返回内存中的数据

---

## 🔍 执行流程详解

### 1. 交易执行步骤

```python
def execute_transaction(evm, tx):
    """执行交易的完整流程"""

    # ===========================================
    # 步骤 1: 验证交易签名
    # ===========================================
    if not verify_signature(tx):
        revert("Invalid signature")

    # ===========================================
    # 步骤 2: 检查 nonce
    # ===========================================
    if tx.nonce != get_nonce(tx.origin):
        revert("Invalid nonce")

    # ===========================================
    # 步骤 3: 检查 gas limit
    # ===========================================
    gas_limit = tx.gasLimit
    if gas_limit < 21000:
        revert("Gas limit too low")

    # ===========================================
    # 步骤 4: 计算内在 gas
    # ===========================================
    intrinsic_gas = calculate_intrinsic_gas(tx)

    # ===========================================
    # 步骤 5: 创建执行环境
    # ===========================================
    env = create_environment(tx, block_info)
    substate = create_substate()  # 临时状态

    # ===========================================
    # 步骤 6: 执行消息调用
    # ===========================================
    try:
        # 递归执行所有调用
        result = execute_message_call(env, tx)

        # 计算实际使用的 gas
        gas_used = intrinsic_gas + result.opcode_gas + \
                   result.memory_expansion + result.storage_access

        # 检查 gas limit
        if gas_used > gas_limit:
            revert("Out of gas")

    except Exception as e:
        # 执行失败，回滚所有状态更改
        revert(str(e))

    # ===========================================
    # 步骤 7: 创建收据
    # ===========================================
    receipt = Receipt(
        status=1,  # 成功
        cumulative_gas_used=get_cumulative_gas() + gas_used,
        logs=result.logs,
        contract_address=result.contract_address,
        gas_used=gas_used
    )

    # ===========================================
    # 步骤 8: 更新状态
    # ===========================================
    apply_state_updates(substate, result)

    # ===========================================
    # 步骤 9: 退还未使用的 gas
    # ===========================================
    gas_refund = gas_limit - gas_used
    if gas_refund > 0:
        refund(tx.origin, gas_refund * tx.gasPrice)

    return receipt
```

**状态更新包括**:
- ✅ **账户 nonce**: 如果调用了合约，增加 nonce
- ✅ **账户余额**: 扣除 gas 费用，转移 value
- ✅ **合约代码**: 如果是 CREATE，存储字节码
- ✅ **合约存储**: 更新合约的存储
- ✅ **日志**: 添加到交易收据中

---

### 2. 异常处理与回滚

#### 异常类型

```python
class EVMException(Exception):
    pass

class StackOverflow(EVMException):
    """栈溢出"""
    pass

class StackUnderflow(EVMException):
    """栈下溢出"""
    pass

class OutOfGas(EVMException):
    """gas 耗尽"""
    pass

class InvalidJump(EVMException):
    """无效跳转"""
    pass

class Revert(EVMException):
    """显式回滚"""
    pass

class InvalidOpcode(EVMException):
    """无效操作码"""
    pass
```

#### 回滚机制

```python
def execute_with_rollback(evm, code, data):
    """执行代码，失败时回滚所有状态更改"""

    # 1. 创建子状态（快照）
    substate = create_substate()

    try:
        # 2. 执行代码
        result = evm.execute(code, data)

        # 3. 应用状态更改
        apply_substate(substate)

        return result

    except EVMException as e:
        # 4. 执行失败，丢弃子状态（自动回滚）

        # REVERT 的情况特殊处理
        if isinstance(e, Revert):
            # REVERT 不退还 gas（除了存储访问成本）
            return Receipt(
                status=0,
                gas_used=calculate_gas_used(),
                output=e.output
            )

        # 其他异常情况
        return Receipt(
            status=0,
            gas_used=calculate_gas_used()
        )
```

**回滚机制**:
- ✅ **子状态隔离**: 每个消息调用都在独立的子状态中执行
- ✅ **快照机制**: 执行前记录状态，失败时恢复
- ✅ **REVERT vs INVALID**: REVERT 保留存储访问成本，INVALID 全部退款 gas
- ✅ **日志保留**: REVERT 保留日志，INVALID 清除日志

---

## 📊 Gas 优化策略

### 1. 存储优化

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract StorageOptimization {
    // ===========================================
    // 优化 1: 打包存储
    // ===========================================
    // 将多个小值打包到一个 slot
    struct PackedData {
        uint128 a;  // 128 位
        uint64 b;   // 64 位
        uint32 c;   // 32 位
        bool d;     // 8 位
        bool e;     // 8 位
        bool f;     // 8 位
        bool g;     // 8 位
        bool h;     // 8 位
        // 总共 256 位
    }

    PackedData public packedData;

    function setPackedData(uint128 _a, uint64 _b, bool _c) external {
        packedData = PackedData({
            a: _a,
            b: _b,
            c: _c,
            d: false,
            e: false,
            f: false,
            g: false,
            h: false
        });
    }

    // ===========================================
    // 优化 2: 映射缓存
    // ===========================================
    mapping(address => uint256) private _cache;
    address private _cacheAddress;

    function getCached(address key) public view returns (uint256) {
        // 使用临时变量减少存储访问
        uint256 cached = _cache[key];
        return cached;
    }

    function setCached(address key, uint256 value) external {
        _cache[key] = value;
    }

    // ===========================================
    // 优化 3: 内存缓存
    // ===========================================
    function batchRead(address[] calldata keys) external view returns (uint256[] memory) {
        uint256[] memory results = new uint256[](keys.length);
        for (uint256 i = 0; i < keys.length; i++) {
            results[i] = _cache[keys[i]];
        }
        return results;
    }
}
```

**存储优化技巧**:
- ✅ **打包存储**: 将多个小值打包到一个 256 位槽
- ✅ **映射缓存**: 使用临时变量减少重复的 SLOAD
- ✅ **内存批量操作**: 在内存中操作，最后才存储
- ✅ **使用 calldata**: 如果数据已提供，不要复制到内存

---

### 2. 内存优化

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract MemoryOptimization {
    // ===========================================
    // 优化 1: 使用 calldata 而不是 memory
    // ===========================================
    function processCalldata(bytes calldata data) external pure returns (bytes32) {
        // 直接访问 calldata，不需要复制到内存
        return keccak256(data);  // calldata hash 不消耗内存
    }

    function processMemory(bytes memory data) external pure returns (bytes32) {
        // 复制到内存会消耗 gas
        return keccak256(data);  // 内存 hash 消耗 gas
    }

    // ===========================================
    // 优化 2: 使用数组而不是映射
    // ===========================================
    uint256[] private _array;
    uint256 private _length;

    function addToArray(uint256 value) external {
        // 数组访问比映射访问便宜（无存储访问）
        _array.push(value);
        _length = _array.length;
    }

    function getFromArray(uint256 index) external view returns (uint256) {
        return _array[index];
    }
}
```

**内存优化技巧**:
- ✅ **使用 calldata**: 如果数据已提供，直接访问
- ✅ **使用数组**: 数组访问比映射访问便宜（无存储）
- ✅ **避免动态内存分配**: 预先计算大小
- ✅ **使用固定大小数组**: 避免动态扩容

---

### 3. 循环优化

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopOptimization {
    // ===========================================
    // 优化 1: 使用 unchecked 块
    // ===========================================
    function uncheckedLoop(uint256 n) external pure returns (uint256) {
        uint256 sum;
        assembly {
            // 使用 unchecked 不检查溢出
            for { let i := 0 } lt(i, n) { i := add(i, 1) } {
                sum := add(sum, i)  // 求和
            }
        }
        return sum;
    }

    // ===========================================
    // 优化 2: 预计算循环边界
    // ===========================================
    function precomputeLoop(uint256[] calldata arr) external pure returns (uint256) {
        uint256 length = arr.length;
        uint256 sum;
        assembly {
            for { let i := 0 } lt(i, length) { i := add(i, 1) } {
                sum := add(sum, mload(add(mul(i, 0x20), arr.slot)))
            }
        }
        return sum;
    }

    // ===========================================
    // 优化 3: 使用 while 代替 for
    // ===========================================
    function whileLoop(uint256 n) external pure returns (uint256) {
        uint256 sum;
        uint256 i;
        assembly {
            // while 循环通常比 for 循环便宜
            for { } iszero(eq(i, n)) { i := add(i, 1) } {
                sum := add(sum, i)
            }
        }
        return sum;
    }
}
```

**循环优化技巧**:
- ✅ **使用 unchecked**: 算术运算不检查溢出
- ✅ **预计算边界**: 提前计算数组长度
- ✅ **使用 while**: 有时比 for 便宜
- ✅ **避免重复计算**: 缓存不变量

---

## 🚀 下一步

**完成度**: Layer 0 (EVM) 已深度研究 ✅

**下一步**: 继续其他层级或实践开发

---

**正在准备下一个主题...** 🧠
