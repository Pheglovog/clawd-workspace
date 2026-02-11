# EIP-712 Typed Structured Data Hashing and Signing 研究文档

> 研究时间：2026-02-12
> 预计字数：20K+
> EIP 状态：Final（2021年9月）

---

## 目录

1. [什么是 EIP-712](#什么是-eip-712)
2. [EIP-712 核心概念](#eip-712-核心概念)
3. [EIP-712 vs 传统签名](#eip-712-vs-传统签名)
4. [Domain Separator](#domain-separator)
5. [Type Hash 计算](#type-hash-计算)
6. [前端集成](#前端集成)
7. [智能合约集成](#智能合约集成)
8. [最佳实践](#最佳实践)
9. [安全考虑](#安全考虑)
10. [常见问题](#常见问题)

---

## 什么是 EIP-712

### 问题背景

在 EIP-712 之前，以太坊签名（eth_sign）有以下问题：

#### 1. 用户无法理解签名内容

```javascript
// 用户看到的是一串十六进制
const signature = await provider.getSigner().signMessage("0x...");

// 用户不知道自己在签名什么
```

#### 2. 容易受到钓鱼攻击

攻击者可以构造恶意交易数据，用户签名后无法及时发现。

#### 3. 签名难以验证

```solidity
// 验证签名复杂且易出错
bytes32 hash = keccak256(abi.encodePacked(
    "\x19Ethereum Signed Message:\n32",
    keccak256(data)
));
```

### EIP-712 的解决方案

EIP-712 引入了**类型化结构化数据签名**，让用户能够看到和验证他们签名的内容。

**关键特性：**
- ✅ 人类可读的签名数据
- ✅ 类型化数据结构
- ✅ 防止重放攻击
- ✅ 易于验证
- ✅ 支持 dApp 域名

---

## EIP-712 核心概念

### 消息结构

EIP-712 消息由以下部分组成：

```javascript
{
    types: {
        // 类型定义
        EIP712Domain: [
            { name: "name", type: "string" },
            { name: "version", type: "string" },
            { name: "chainId", type: "uint256" },
            { name: "verifyingContract", type: "address" },
            { name: "salt", type: "bytes32" }
        ],
        Permit: [
            { name: "owner", type: "address" },
            { name: "spender", type: "address" },
            { name: "value", type: "uint256" },
            { name: "nonce", type: "uint256" },
            { name: "deadline", type: "uint256" }
        ]
    },
    primaryType: "Permit",
    domain: {
        name: "MyDapp",
        version: "1",
        chainId: 1,
        verifyingContract: "0x...",
        salt: "0x..."
    },
    message: {
        owner: "0x...",
        spender: "0x...",
        value: 1000000000000000000,
        nonce: 0,
        deadline: 1640000000
    }
}
```

### 1. types（类型定义）

定义消息的结构和类型。

```javascript
types: {
    // EIP712Domain 是必需的
    EIP712Domain: [
        { name: "name", type: "string" },              // dApp 名称
        { name: "version", type: "string" },           // 版本号
        { name: "chainId", type: "uint256" },           // 链 ID
        { name: "verifyingContract", type: "address" }, // 验证合约地址
        { name: "salt", type: "bytes32" }             // 随机盐
    ],
    
    // 自定义类型
    Person: [
        { name: "name", type: "string" },
        { name: "wallet", type: "address" }
    ],
    
    // 引用其他类型
    Mail: [
        { name: "from", type: "Person" },
        { name: "to", type: "Person" },
        { name: "contents", type: "string" }
    ]
}
```

**支持的类型：**
- `string`: UTF-8 字符串
- `bool`: 布尔值
- `address`: 20 字节地址
- `bytes`: 字节数组
- `bytesNN`: 固定长度字节数组（如 bytes32）
- `uintNN`: 无符号整数（uint8, uint16, uint256）
- `intNN`: 有符号整数（int8, int16, int256）
- 自定义类型（引用）

### 2. primaryType（主要类型）

要签名的消息类型名称。

```javascript
primaryType: "Permit"
```

### 3. domain（域分隔符）

防止跨链和跨合约重放攻击。

```javascript
domain: {
    name: "MyDapp",                           // dApp 名称
    version: "1",                            // 版本
    chainId: 1,                              // 链 ID（1 = 以太坊主网）
    verifyingContract: "0x...",              // 验证合约（可选）
    salt: "0x..."                            // 随机盐（可选）
}
```

**为什么需要 domain？**
- 防止在不同链上重放签名
- 防止在不同合约间重放签名
- 防止同一合约的不同版本间重放签名

### 4. message（消息数据）

要签名的实际数据。

```javascript
message: {
    owner: "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9",
    spender: "0x4bF16773B7bBd38Bc8E9e1e1b8A23a4a6C5A5B0",
    value: ethers.parseEther("1.0"),
    nonce: 0,
    deadline: 1640000000
}
```

---

## EIP-712 vs 传统签名

### 传统签名（eth_sign）

```javascript
// 1. 数据序列化
const data = {
    from: "0x...",
    to: "0x...",
    value: "1000000000000000000"
};
const dataHash = web3.utils.sha3(JSON.stringify(data));

// 2. 添加前缀
const prefixedHash = web3.utils.sha3(
    "\x19Ethereum Signed Message:\n32" + dataHash.slice(2)
);

// 3. 签名
const signature = await signer.signMessage(prefixedHash);

// 问题：用户看到的是一串十六进制，不知道自己在签名什么
```

**缺点：**
- ❌ 用户无法理解签名内容
- ❌ 容易受到钓鱼攻击
- ❌ 类型不安全
- ❌ 容易出现序列化不一致

### EIP-712 签名

```javascript
// 1. 定义类型化数据
const domain = {
    name: "MyDapp",
    version: "1",
    chainId: 1,
    verifyingContract: "0x..."
};

const types = {
    Permit: [
        { name: "owner", type: "address" },
        { name: "spender", type: "address" },
        { name: "value", type: "uint256" },
        { name: "nonce", type: "uint256" },
        { name: "deadline", type: "uint256" }
    ]
};

const value = {
    owner: "0x...",
    spender: "0x...",
    value: "1000000000000000000",
    nonce: 0,
    deadline: 1640000000
};

// 2. 签名（钱包会显示可读的内容）
const signature = await signer._signTypedData(domain, types, value);

// 优点：用户可以清楚地看到自己在签名什么
```

**优点：**
- ✅ 用户可以看到人类可读的签名内容
- ✅ 类型安全
- ✅ 防止重放攻击
- ✅ 跨链/跨合约隔离
- ✅ 支持嵌套类型

---

## Domain Separator

### 什么是 Domain Separator？

Domain Separator 是一个唯一标识符，用于隔离不同 dApp、不同链、不同合约的签名。

### 计算方法

```javascript
const domainSeparator = keccak256(
    keccak256("EIP712Domain(string name,string version,uint256 chainId,address verifyingContract,bytes32 salt)")
    + keccak256(name)
    + keccak256(version)
    + chainId
    + verifyingContract
    + salt
);
```

### Solidity 实现

```solidity
function calculateDomainSeparator(
    string memory name,
    string memory version,
    uint256 chainId,
    address verifyingContract,
    bytes32 salt
) internal pure returns (bytes32) {
    return keccak256(
        abi.encode(
            keccak256(
                "EIP712Domain(string name,string version,uint256 chainId,address verifyingContract,bytes32 salt)"
            ),
            keccak256(bytes(name)),
            keccak256(bytes(version)),
            chainId,
            verifyingContract,
            salt
        )
    );
}
```

### 使用场景

#### 1. 跨链隔离

```javascript
// 主网签名
const domainMainnet = {
    name: "MyDapp",
    version: "1",
    chainId: 1  // 主网
};

// 测试网签名
const domainTestnet = {
    name: "MyDapp",
    version: "1",
    chainId: 5  // Goerli
};

// 主网签名不能在测试网使用，反之亦然
```

#### 2. 跨合约隔离

```javascript
// 合约 A
const domainA = {
    name: "MyDapp",
    version: "1",
    chainId: 1,
    verifyingContract: "0x123..."  // 合约 A 的地址
};

// 合约 B
const domainB = {
    name: "MyDapp",
    version: "1",
    chainId: 1,
    verifyingContract: "0x456..."  // 合约 B 的地址
};

// 合约 A 的签名不能在合约 B 上使用
```

#### 3. 版本隔离

```javascript
// 版本 1
const domainV1 = {
    name: "MyDapp",
    version: "1",
    chainId: 1
};

// 版本 2
const domainV2 = {
    name: "MyDapp",
    version: "2",
    chainId: 1
};

// 版本 1 的签名不能在版本 2 上使用
```

---

## Type Hash 计算

### 什么是 Type Hash？

Type Hash 是类型定义的哈希，用于编码消息结构。

### 计算步骤

#### 1. 编码类型定义

```javascript
function encodeType(type) {
    const parts = [];
    const dependencies = findDependencies(type);
    
    // 按字母顺序排列
    dependencies.sort();
    
    // 编码每个类型
    for (const dep of dependencies) {
        parts.push(dep.name + "(" + dep.fields.map(f => f.type + " " + f.name).join(",") + ")");
    }
    
    return keccak256(parts.join(""));
}

function findDependencies(type, visited = {}) {
    if (visited[type.name]) return [];
    visited[type.name] = true;
    
    const dependencies = [type];
    for (const field of type.fields) {
        if (field.type in types) {
            dependencies.push(...findDependencies(types[field.type], visited));
        }
    }
    
    return dependencies;
}
```

#### 2. 编码消息数据

```javascript
function encodeData(primaryType, types, data) {
    const encodedTypes = [];
    
    // 编码所有类型
    for (const type of Object.values(types)) {
        encodedTypes.push(keccak256(encodeType(type)));
    }
    
    // 编码数据
    const encoded = [];
    const type = types[primaryType];
    
    for (const field of type.fields) {
        if (field.type in types) {
            // 嵌套类型
            encoded.push(encodeData(field.type, types, data[field.name]));
        } else {
            // 基础类型
            encoded.push(encodeValue(field.type, data[field.name]));
        }
    }
    
    return keccak256(encoded.join(""));
}
```

### 完整示例

```javascript
const types = {
    EIP712Domain: [
        { name: "name", type: "string" },
        { name: "version", type: "string" },
        { name: "chainId", type: "uint256" }
    ],
    Mail: [
        { name: "from", type: "Person" },
        { name: "to", type: "Person" },
        { name: "contents", type: "string" }
    ],
    Person: [
        { name: "name", type: "string" },
        { name: "wallet", type: "address" }
    ]
};

// Type Hash 计算
const mailTypeHash = keccak256(
    "Mail(Person from,Person to,string contents)Person(string name,address wallet)"
);

// Data Hash 计算
const mailData = {
    from: { name: "Alice", wallet: "0x..." },
    to: { name: "Bob", wallet: "0x..." },
    contents: "Hello Bob!"
};

const mailDataHash = keccak256(
    encodeData("Mail", types, mailData)
);
```

---

## 前端集成

### 使用 ethers.js v6+

```javascript
import { ethers } from "ethers";

// 1. 定义 Domain
const domain = {
    name: "MyDapp",
    version: "1",
    chainId: 1,
    verifyingContract: "0x..."
};

// 2. 定义 Types
const types = {
    Permit: [
        { name: "owner", type: "address" },
        { name: "spender", type: "address" },
        { name: "value", type: "uint256" },
        { name: "nonce", type: "uint256" },
        { name: "deadline", type: "uint256" }
    ]
};

// 3. 定义 Message
const value = {
    owner: "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9",
    spender: "0x4bF16773B7bBd38Bc8E9e1e1b8A23a4a6C5A5B0",
    value: ethers.parseEther("1.0"),
    nonce: 0,
    deadline: Math.floor(Date.now() / 1000) + 3600  // 1 小时后过期
};

// 4. 签名
const signer = await provider.getSigner();
const signature = await signer.signTypedData(domain, types, value);

console.log("Signature:", signature);
// 输出: "0x..."
```

### 使用 Web3.js

```javascript
import Web3 from "web3";

const web3 = new Web3(provider);

const domain = {
    name: "MyDapp",
    version: "1",
    chainId: await web3.eth.getChainId(),
    verifyingContract: "0x..."
};

const types = {
    Permit: [
        { name: "owner", type: "address" },
        { name: "spender", type: "address" },
        { name: "value", type: "uint256" },
        { name: "nonce", type: "uint256" },
        { name: "deadline", type: "uint256" }
    ]
};

const value = {
    owner: "0x...",
    spender: "0x...",
    value: "1000000000000000000",
    nonce: 0,
    deadline: Math.floor(Date.now() / 1000) + 3600
};

const signature = await web3.eth.signTypedData(domain, types, value);
```

### 使用 viem

```javascript
import { createWalletClient, http } from "viem";

const walletClient = createWalletClient({
    account: privateKey,
    chain: mainnet,
    transport: http()
});

const signature = await walletClient.signTypedData({
    domain: {
        name: "MyDapp",
        version: "1",
        chainId: 1,
        verifyingContract: "0x..."
    },
    types: {
        Permit: [
            { name: "owner", type: "address" },
            { name: "spender", type: "address" },
            { name: "value", type: "uint256" },
            { name: "nonce", type: "uint256" },
            { name: "deadline", type: "uint256" }
        ]
    },
    primaryType: "Permit",
    message: {
        owner: "0x...",
        spender: "0x...",
        value: 1000000000000000000n,
        nonce: 0n,
        deadline: BigInt(Math.floor(Date.now() / 1000) + 3600)
    }
});
```

---

## 智能合约集成

### 简单的签名验证合约

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.23;

contract EIP712Verifier {
    bytes32 private constant EIP712_DOMAIN_TYPEHASH = keccak256(
        "EIP712Domain(string name,string version,uint256 chainId,address verifyingContract,bytes32 salt)"
    );

    bytes32 private DOMAIN_SEPARATOR;

    constructor() {
        DOMAIN_SEPARATOR = keccak256(
            abi.encode(
                EIP712_DOMAIN_TYPEHASH,
                keccak256("EIP712Verifier"),
                keccak256("1"),
                block.chainid,
                address(this),
                bytes32(0)
            )
        );
    }

    function verifySignature(
        address signer,
        bytes32 dataHash,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) public pure returns (bool) {
        bytes32 digest = keccak256(
            abi.encodePacked("\x19\x01", DOMAIN_SEPARATOR, dataHash)
        );

        return ecrecover(digest, v, r, s) == signer;
    }
}
```

### Permit2 实现

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.23;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

contract TokenPermit is ECDSA {
    using SafeERC20 for IERC20;

    bytes32 private immutable DOMAIN_SEPARATOR;
    bytes32 private constant PERMIT_TYPEHASH = keccak256(
        "Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)"
    );

    IERC20 public token;

    mapping(address => uint256) public nonces;

    event PermitUsed(address indexed owner, address indexed spender, uint256 value, uint256 nonce);

    constructor(IERC20 _token) {
        token = _token;

        DOMAIN_SEPARATOR = keccak256(
            abi.encode(
                keccak256("EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"),
                keccak256(bytes(token.name())),
                keccak256(bytes("1")),
                block.chainid,
                address(this)
            )
        );
    }

    function permit(
        address owner,
        address spender,
        uint256 value,
        uint256 deadline,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) public {
        require(block.timestamp <= deadline, "Permit expired");

        bytes32 digest = keccak256(
            abi.encodePacked(
                "\x19\x01",
                DOMAIN_SEPARATOR,
                keccak256(
                    abi.encode(
                        PERMIT_TYPEHASH,
                        owner,
                        spender,
                        value,
                        nonces[owner],
                        deadline
                    )
                )
            )
        );

        address recovered = ECDSA.recover(digest, v, r, s);
        require(recovered == owner, "Invalid signature");

        nonces[owner]++;

        emit PermitUsed(owner, spender, value, nonces[owner] - 1);
    }

    function transferWithPermit(
        address owner,
        address spender,
        uint256 value,
        uint256 deadline,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) public {
        permit(owner, spender, value, deadline, v, r, s);
        token.safeTransferFrom(owner, spender, value);
    }
}
```

### Meta-Transactions（Gasless 交易）

```solidity
contract MetaTransactions {
    address public owner;
    mapping(address => uint256) public nonces;

    event MetaTransactionExecuted(
        address indexed signer,
        address indexed target,
        uint256 value,
        bytes data,
        uint256 nonce
    );

    constructor() {
        owner = msg.sender;
    }

    struct MetaTransaction {
        address to;
        uint256 value;
        bytes data;
        uint256 nonce;
        uint256 deadline;
    }

    bytes32 private immutable DOMAIN_SEPARATOR;
    bytes32 private constant METATX_TYPEHASH = keccak256(
        "MetaTransaction(address to,uint256 value,bytes data,uint256 nonce,uint256 deadline)"
    );

    constructor() {
        DOMAIN_SEPARATOR = keccak256(
            abi.encode(
                keccak256("EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"),
                keccak256(bytes("MetaTransactions")),
                keccak256(bytes("1")),
                block.chainid,
                address(this)
            )
        );
    }

    function executeMetaTransaction(
        MetaTransaction calldata tx,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) public {
        require(block.timestamp <= tx.deadline, "Transaction expired");
        require(tx.nonce == nonces[msg.sender], "Invalid nonce");

        bytes32 digest = keccak256(
            abi.encodePacked(
                "\x19\x01",
                DOMAIN_SEPARATOR,
                keccak256(
                    abi.encode(
                        METATX_TYPEHASH,
                        tx.to,
                        tx.value,
                        keccak256(tx.data),
                        tx.nonce,
                        tx.deadline
                    )
                )
            )
        );

        address signer = ECDSA.recover(digest, v, r, s);
        nonces[signer]++;

        (bool success, ) = tx.to.call{value: tx.value}(tx.data);
        require(success, "Transaction failed");

        emit MetaTransactionExecuted(signer, tx.to, tx.value, tx.data, tx.nonce);
    }

    function getNonce(address account) public view returns (uint256) {
        return nonces[account];
    }
}
```

---

## 最佳实践

### 1. 使用合理的 Deadline

```javascript
// ❌ 不好：过长的 deadline
const deadline = Math.floor(Date.now() / 1000) + 86400 * 365;  // 1 年

// ✅ 好：合理的 deadline（几小时到几天）
const deadline = Math.floor(Date.now() / 1000) + 3600;  // 1 小时
```

### 2. 添加 Nonce 机制

```solidity
// 状态变量
mapping(address => uint256) public nonces;

// 验证 nonce
require(nonce == nonces[signer], "Invalid nonce");
nonces[signer]++;

// 查询 nonce
function getNonce(address account) public view returns (uint256) {
    return nonces[account];
}
```

### 3. 使用 EIP-191 Message

```solidity
// 区分 EIP-712 和 EIP-191 签名
function verifyWithPrefix(
    address signer,
    bytes32 message,
    bytes memory signature
) public pure returns (bool) {
    bytes32 digest = keccak256(
        abi.encodePacked("\x19\x01", DOMAIN_SEPARATOR, message)
    );
    
    return recoverSigner(digest, signature) == signer;
}
```

### 4. 类型安全

```typescript
// 使用 TypeScript 定义类型
interface Permit {
    owner: string;
    spender: string;
    value: bigint;
    nonce: bigint;
    deadline: bigint;
}

interface Domain {
    name: string;
    version: string;
    chainId: number;
    verifyingContract?: string;
    salt?: string;
}

// 使用类型
async function signPermit(domain: Domain, types: Record<string, any>, message: Permit) {
    return await signer.signTypedData(domain, types, message);
}
```

### 5. 错误处理

```javascript
try {
    const signature = await signer.signTypedData(domain, types, value);
} catch (error) {
    if (error.code === 4001) {
        // 用户拒绝
        console.log("User rejected signature");
    } else if (error.message.includes("user rejected")) {
        // 用户拒绝（不同钱包）
        console.log("User rejected signature");
    } else {
        // 其他错误
        console.error("Sign error:", error);
    }
}
```

### 6. 前端验证

```javascript
// 签名前验证数据
function validatePermit(permit) {
    // 检查地址格式
    if (!ethers.isAddress(permit.owner)) {
        throw new Error("Invalid owner address");
    }
    
    // 检查 deadline
    if (permit.deadline <= Math.floor(Date.now() / 1000)) {
        throw new Error("Deadline must be in the future");
    }
    
    // 检查 nonce
    if (permit.nonce < 0) {
        throw new Error("Nonce must be non-negative");
    }
    
    // 检查 value
    if (permit.value < 0) {
        throw new Error("Value must be non-negative");
    }
}

// 签名前验证
validatePermit(permit);
const signature = await signer.signTypedData(domain, types, permit);
```

---

## 安全考虑

### 1. 重放攻击防护

#### ChainId 隔离

```javascript
const domain = {
    name: "MyDapp",
    version: "1",
    chainId: await provider.getNetwork().then(n => n.chainId)  // 动态获取
};
```

#### Nonce 机制

```solidity
mapping(address => uint256) public nonces;

function executeWithNonce(address signer, uint256 nonce, ...) {
    require(nonce == nonces[signer], "Invalid nonce");
    nonces[signer]++;
    // 执行操作
}
```

#### Deadline 机制

```solidity
function executeWithDeadline(uint256 deadline, ...) {
    require(block.timestamp <= deadline, "Transaction expired");
    // 执行操作
}
```

### 2. 签名混淆攻击

**问题：** 攻击者可以交换相同类型的字段值。

**防护：** 使用不同的类型或添加额外的验证。

```javascript
// ❌ 容易混淆
const types = {
    Swap: [
        { name: "tokenIn", type: "address" },
        { name: "tokenOut", type: "address" },
        { name: "amountIn", type: "uint256" },
        { name: "amountOut", type: "uint256" }
    ]
};

// ✅ 添加额外验证
const types = {
    Swap: [
        { name: "tokenIn", type: "address" },
        { name: "tokenOut", type: "address" },
        { name: "amountIn", type: "uint256" },
        { name: "amountOut", type: "uint256" },
        { name: "salt", type: "bytes32" }  // 随机盐
    ]
};
```

### 3. 签名重用

**问题：** 用户可能多次使用相同的签名。

**防护：** 使用唯一标识符或时间戳。

```javascript
const message = {
    ...permit,
    timestamp: Math.floor(Date.now() / 1000)  // 时间戳
};
```

### 4. Domain 伪造

**问题：** 攻击者可能伪造 domain。

**防护：** 验证 domain 参数。

```solidity
function verifyDomain(bytes32 domainSeparator) public view returns (bool) {
    return domainSeparator == DOMAIN_SEPARATOR;
}
```

### 5. 前端安全

```javascript
// ✅ 使用 HTTPS
const provider = new ethers.providers.JsonRpcProvider("https://...");

// ✅ 验证网络
const network = await provider.getNetwork();
if (network.chainId !== 1) {
    throw new Error("Please switch to Mainnet");
}

// ✅ 使用安全的随机数
const salt = ethers.keccak256(ethers.randomBytes(32));

// ✅ 不暴露私钥
const signer = await provider.getSigner();  // 使用钱包签名器
// 不要这样做：const wallet = new ethers.Wallet(privateKey);
```

---

## 常见问题

### Q1: EIP-712 vs EIP-191？

**A:** EIP-712 用于类型化数据，EIP-191 用于简单的文本消息。

```javascript
// EIP-712
const signature = await signer.signTypedData(domain, types, value);

// EIP-191
const signature = await signer.signMessage("Hello");
```

### Q2: 如何处理跨链签名？

**A:** 使用不同的 chainId 在 domain 中。

```javascript
// 主网
const domainMainnet = { name: "MyDapp", version: "1", chainId: 1 };

// Polygon
const domainPolygon = { name: "MyDapp", version: "1", chainId: 137 };

// 每个链使用不同的签名
```

### Q3: 如何验证签名？

**A:** 使用 OpenZeppelin 的 ECDSA 库。

```solidity
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

function verifySignature(
    bytes32 digest,
    bytes memory signature,
    address signer
) public pure returns (bool) {
    (uint8 v, bytes32 r, bytes32 s) = splitSignature(signature);
    return ECDSA.recover(digest, v, r, s) == signer;
}
```

### Q4: 如何在合约中重算 digest？

**A:** 使用 keccak256 和 abi.encodePacked。

```solidity
bytes32 digest = keccak256(
    abi.encodePacked(
        "\x19\x01",
        DOMAIN_SEPARATOR,
        keccak256(abi.encode(TYPE_HASH, ...))
    )
);
```

### Q5: 如何处理大量签名？

**A:** 使用批处理或链下验证。

```javascript
// 链下验证
const isValid = verifySignature(digest, signature, expectedSigner);

// 批量验证
const signatures = [sig1, sig2, sig3];
const isValid = signatures.every(sig => verify(...));
```

### Q6: 如何在钱包中正确显示？

**A:** 确保类型定义正确且数据完整。

```javascript
// ✅ 完整的类型和 domain
const domain = {
    name: "MyDapp",           // dApp 名称
    version: "1",             // 版本
    chainId: 1,              // 链 ID
    verifyingContract: "0x..."  // 验证合约
};

const types = {
    Permit: [                // 类型名称
        { name: "owner", type: "address" },      // 字段名和类型
        { name: "spender", type: "address" },
        { name: "value", type: "uint256" },
        { name: "nonce", type: "uint256" },
        { name: "deadline", type: "uint256" }
    ]
};

const message = {            // 完整的消息
    owner: "0x...",
    spender: "0x...",
    value: ethers.parseEther("1.0"),  // 使用正确的单位
    nonce: 0,
    deadline: Math.floor(Date.now() / 1000) + 3600
};
```

---

## 总结

### 关键要点

1. **EIP-712 的优势**
   - 人类可读的签名内容
   - 类型安全
   - 防止重放攻击
   - 跨链/跨合约隔离

2. **核心组件**
   - Domain Separator：隔离不同的签名上下文
   - Type Hash：编码类型定义
   - Message Hash：编码消息数据

3. **最佳实践**
   - 使用合理的 deadline
   - 添加 nonce 机制
   - 使用 TypeScript 类型安全
   - 添加前端验证

4. **安全考虑**
   - 防止重放攻击
   - 防止签名混淆
   - 防止签名重用
   - 验证 domain 参数

### 下一步

- 在 CarLife 中集成 EIP-712
- 实现 Permit2 功能
- 研究 EIP-2612 (Permit)
- 研究 EIP-4494 (Batches)

---

*文档字数：约 20K 字*
*创建时间：2026-02-12*
*作者：吕布（上等兵•甘的AI助手）*
