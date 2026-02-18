# EIP-712 实战开发

> 研究时间：2026-02-18
> 深度学习第 34 小时

---

## 目录

1. [EIP-712 概述](#eip-712-概述)
2. [技术原理](#技术原理)
3. [开发环境搭建](#开发环境搭建)
4. [Solidity 实战](#solidity-实战)
5. [TypeScript/JavaScript 实战](#typescriptjavascript-实战)
6. [CarLife 项目集成](#carlife-项目集成)
7. [最佳实践](#最佳实践)
8. [常见问题](#常见问题)

---

## EIP-712 概述

### 什么是 EIP-712？

**EIP-712** 是以太坊改进提案，全称为 "Typed Structured Data Hashing and Signing"，即类型化结构化数据哈希和签名。它允许用户通过结构化数据（而非原始十六进制字符串）对交易进行签名，大大改善了用户体验。

### EIP-712 的核心价值

1. **用户体验优化**
   - 用户看到可读的交易数据（如 "Swap 1 ETH for 2000 USDC"）
   - 减少签名错误
   - 支持离线签名（冷钱包）

2. **安全性增强**
   - 类型化数据防止签名错误
   - 清晰的签名域边界
   - 防止钓鱼攻击

3. **智能合约集成**
   - 智能合约验证类型化签名
   - 减少复杂的参数解析
   - 提高代码可读性

### EIP-712 的组成部分

1. **域分隔符（Domain Separator）**
   - 用于隔离不同智能合约的签名域
   - 防止重放攻击
   - 包含合约地址和链 ID

2. **类型数据（Type Data）**
   - 描述数据结构的类型
   - 使用递归哈希编码
   - 支持嵌套结构

3. **消息数据（Message Data）**
   - 实际要签名的数据
   - 结构化、类型化
   - 包含所有签名域

---

## 技术原理

### 域分隔符（Domain Separator）

**定义：**
域分隔符是一个唯一的标识符，用于隔离不同智能合约或链的签名空间。它包含：

- 合约名称（可选）
- 合约版本（可选）
- 链 ID
- 合约地址

**计算方法：**
```solidity
bytes32 private DOMAIN_SEPARATOR;

constructor() {
    DOMAIN_SEPARATOR = keccak256(
        abi.encode(
            keccak256("EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"),
            keccak256("MyContract"),
            keccak256("1"),
            block.chainid,
            address(this)
        )
    );
}
```

**为什么需要域分隔符？**
- **链隔离**：在以太坊主网和测试网上使用相同的签名域
- **合约隔离**：不同合约使用不同的签名域
- **版本隔离**：同一合约的不同版本使用不同的签名域
- **重放保护**：防止在不同链上重复使用签名

### 类型数据（Type Data）

**定义：**
类型数据是一个递归的数据结构，用于描述消息数据的类型。它支持：

- 基本类型：`address`, `address[]`, `uint256`, `uint256[]`, `bytes`, `bytes32`, `bool`
- 复杂类型：自定义类型
- 嵌套类型：数组、结构体

**示例：**
```typescript
// EIP-712 类型数据
const types = {
    // 域分隔符类型
    EIP712Domain: [
        { name: "name", type: "string" },
        { name: "version", type: "string" },
        { name: "chainId", type: "uint256" },
        { name: "verifyingContract", type: "address" },
    ],
    // 自定义类型
    Permit: [
        { name: "owner", type: "address" },
        { name: "spender", type: "address" },
        { name: "value", type: "uint256" },
        { name: "nonce", type: "uint256" },
        { name: "deadline", type: "uint256" },
    ],
    // 嵌套类型
    Swap: [
        { name: "tokenIn", type: "address" },
        { name: "tokenOut", type: "address" },
        { name: "amountIn", type: "uint256" },
        { name: "amountOutMin", type: "uint256" },
        { name: "recipient", type: "address" },
        { name: "deadline", type: "uint256" },
        { name: "v", type: "bytes32" },
        { name: "r", type: "bytes32" },
        { name: "s", type: "bytes8" },
    ],
};
```

**类型哈希计算：**
```typescript
// 计算类型哈希
const typesHash = ethers.utils.keccak256(
    ethers.AbiCoder.encode(
        ["bytes32", "bytes32"],
        [
            keccak256("Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)"),
            keccak256("EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)")
        ]
    )
);
```

### 消息数据（Message Data）

**定义：**
消息数据是实际要签名的数据，它必须与类型数据匹配。

**示例：**
```typescript
// 消息数据
const message = {
    owner: "0x...",
    spender: "0x...",
    value: 1000000000000000000, // 1 ETH
    nonce: 0,
    deadline: Math.floor(Date.now() / 1000) + 3600, // 1 小时后
};
```

**消息哈希计算：**
```typescript
// 计算消息哈希
const messageHash = ethers.utils.keccak256(
    ethers.AbiCoder.encode(
        ["bytes32", "bytes32", "address", "address", "uint256", "uint256", "uint256"],
        [
            typesHash,
            domainHash,
            message.owner,
            message.spender,
            message.value,
            message.nonce,
            message.deadline,
        ]
    )
);
```

**最终签名：**
```typescript
// 对消息哈希进行签名
const signature = await signer.signMessage(ethers.utils.arrayify(messageHash));

// 分离签名
const { v, r, s } = ethers.utils.splitSignature(signature);
```

---

## 开发环境搭建

### 1. 安装依赖

**TypeScript/JavaScript 项目：**
```bash
# 初始化项目
npm init -y

# 安装 ethers.js
npm install ethers@6

# 或者安装 viem
npm install viem
```

**Solidity 项目：**
```bash
# 安装 Hardhat
npm install --save-dev hardhat

# 安装 OpenZeppelin 合约
npm install @openzeppelin/contracts

# 安装 EIP-712 库（可选）
npm install @openzeppelin/contracts/utils/cryptography/ECDSA.sol
```

### 2. 配置环境

**TypeScript 配置（tsconfig.json）：**
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "moduleResolution": "node"
  }
}
```

**Hardhat 配置（hardhat.config.js）：**
```javascript
require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

module.exports = {
  solidity: {
    version: "0.8.20",
    settings: {
        optimizer: {
          enabled: true,
          runs: 200,
        },
    },
  },
  networks: {
    sepolia: {
      url: process.env.SEPOLIA_RPC_URL,
      accounts: [process.env.PRIVATE_KEY],
    },
    mainnet: {
      url: process.env.MAINNET_RPC_URL,
      accounts: [process.env.PRIVATE_KEY],
    },
  },
};
```

---

## Solidity 实战

### 1. 实现 Permit 功能

**合约代码：**
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/cryptography/draft-EIP712.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title TokenPermit
 * @dev 实现 EIP-712 的 Permit 功能
 */
contract TokenPermit is EIP712 {
    using Counters for Counters.Counter;
    using SafeERC20 for IERC20;

    bytes32 private immutable DOMAIN_SEPARATOR;
    bytes32 private constant PERMIT_TYPEHASH =
        keccak256("Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)");

    // 映射 nonce
    mapping(address => Counters.Counter) private _nonces;

    // 事件
    event PermitUsed(address indexed owner, address indexed spender, uint256 value, uint256 nonce, uint256 deadline);

    constructor(address token) EIP712("TokenPermit", "1") {
        DOMAIN_SEPARATOR = _calculateDomainSeparator();
    }

    /**
     * @notice 使用 Permit 进行转账
     * @param owner 所有者地址
     * @param spender 授权的地址
     * @param value 转账金额
     * @param deadline 过期时间
     * @param v 签名的 v 值
     * @param r 签名的 r 值
     * @param s 签名的 s 值
     */
    function permit(
        address owner,
        address spender,
        uint256 value,
        uint256 deadline,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) external {
        // 检查签名
        _verifyPermit(owner, spender, value, deadline, v, r, s);

        // 使用 nonce
        _nonces[owner].increment();

        // 执行转账
        IERC20(token).safeTransferFrom(owner, spender, value);

        emit PermitUsed(owner, spender, value, _nonces[owner].current() - 1, deadline);
    }

    /**
     * @notice 验证 Permit 签名
     * @param owner 所有者地址
     * @param spender 授权的地址
     * @param value 转账金额
     * @param deadline 过期时间
     * @param v 签名的 v 值
     * @param r 签名的 r 值
     * @param s 签名的 s 值
     */
    function _verifyPermit(
        address owner,
        address spender,
        uint256 value,
        uint256 deadline,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) private view {
        // 检查过期
        require(block.timestamp <= deadline, "Permit expired");

        // 获取 nonce
        uint256 nonce = _nonces[owner].current();

        // 构建数据结构
        bytes32 structHash = keccak256(
            abi.encode(PERMIT_TYPEHASH, owner, spender, value, nonce, deadline)
        );

        bytes32 digest = keccak256(
            abi.encodePacked("\x19\x01", DOMAIN_SEPARATOR, structHash)
        );

        // 恢复签名者
        address signer = ECDSA.recover(digest, v, r, s);
        require(signer == owner, "Invalid signature");
    }

    /**
     * @notice 计算 Domain Separator
     * @return domainSeparator 域分隔符哈希
     */
    function _calculateDomainSeparator() private view returns (bytes32) {
        return keccak256(
            abi.encode(
                keccak256("EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"),
                keccak256("TokenPermit"),
                keccak256("1"),
                block.chainid,
                address(this)
            )
        );
    }

    /**
     * @notice 获取 nonce
     * @param owner 所有者地址
     * @return nonce 当前 nonce
     */
    function nonces(address owner) external view returns (uint256) {
        return _nonces[owner].current();
    }
}
```

### 2. 实现 Permit2 批量授权

**Permit2 是 EIP-712 的升级版，支持批量授权和 nonce 管理。**

**合约代码：**
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/IERC20Permit.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/draft-IERC20PermitAllowed.sol";
import "@openzeppelin/contracts/utils/cryptography/draft-EIP712.sol";
import "@openzeppelin/contracts/utils/Nonces.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

/**
 * @title TokenPermit2
 * @dev 实现 EIP-712 的 Permit2 功能
 */
contract TokenPermit2 is IERC20PermitAllowed, EIP712, Nonces {
    bytes32 private immutable DOMAIN_SEPARATOR;
    bytes32 private constant PERMIT_TYPEHASH =
        keccak256("Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)");

    // 允许的授权
    address private immutable _permit2;

    constructor(address token, address permit2) EIP712("TokenPermit2", "1") {
        DOMAIN_SEPARATOR = _calculateDomainSeparator();
        _permit2 = permit2;
    }

    /**
     * @notice 使用 Permit2 进行授权
     * @param owner 所有者地址
     * @param spender 授权的地址
     * @param value 授权金额
     * @param deadline 过期时间
     * @param v 签名的 v 值
     * @param r 签名的 r 值
     * @param s 签名的 s 值
     */
    function permit(
        address owner,
        address spender,
        uint256 value,
        uint256 deadline,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) external {
        // 检查签名
        _verifyPermit(owner, spender, value, deadline, v, r, s);

        // 使用 Permit2
        IERC20PermitAllowed(_permit2).permit(owner, type(IERC20Permit).interfaceId, owner, spender, value, deadline, v, r, s);
    }

    /**
     * @notice 验证 Permit2 签名
     * @param owner 所有者地址
     * @param spender 授权的地址
     * @param value 授权金额
     * @param deadline 过期时间
     * @param v 签名的 v 值
     * @param r 签名的 r 值
     * @param s 签名的 s 值
     */
    function _verifyPermit(
        address owner,
        address spender,
        uint256 value,
        uint256 deadline,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) private view {
        // 检查过期
        require(block.timestamp <= deadline, "Permit expired");

        // 获取 nonce
        uint256 nonce = _nonces(owner);

        // 构建数据结构
        bytes32 structHash = keccak256(
            abi.encode(PERMIT_TYPEHASH, owner, spender, value, nonce, deadline)
        );

        bytes32 digest = keccak256(
            abi.encodePacked("\x19\x01", DOMAIN_SEPARATOR, structHash)
        );

        // 恢复签名者
        address signer = ECDSA.recover(digest, v, r, s);
        require(signer == owner, "Invalid signature");
    }

    /**
     * @notice 检查是否允许 Permit2
     * @param owner 所有者地址
     * @param spender 授权的地址
     * @param value 授权金额
     * @param deadline 过期时间
     * @param v 签名的 v 值
     * @param r 签名的 r 值
     * @param s 签名的 s 值
     * @return 是否允许
     */
    function permit(
        address owner,
        address, // token
        address spender,
        uint256 value,
        uint256 deadline,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) external view override returns (bool) {
        _verifyPermit(owner, spender, value, deadline, v, r, s);
        return true;
    }

    /**
     * @notice 计算 Domain Separator
     * @return domainSeparator 域分隔符哈希
     */
    function _calculateDomainSeparator() private view returns (bytes32) {
        return keccak256(
            abi.encode(
                keccak256("EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"),
                keccak256("TokenPermit2"),
                keccak256("1"),
                block.chainid,
                address(this)
            )
        );
    }
}
```

### 3. 实现 Meta-Transaction

**Meta-Transaction 是 EIP-712 的一个重要应用，允许用户授权第三方代表他们执行交易。**

**合约代码：**
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/utils/cryptography/draft-EIP712.sol";
import "@openzeppelin/contracts/utils/Nonces.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title MetaTransaction
 * @dev 实现 EIP-712 的 Meta-Transaction 功能
 */
contract MetaTransaction is Ownable, EIP712, Nonces {
    bytes32 private immutable DOMAIN_SEPARATOR;
    bytes32 private constant META_TRANSACTION_TYPEHASH =
        keccak256("MetaTransaction(uint256 nonce,address from,bytes data)");

    // 转发器映射
    mapping(address => bool) public isForwarder;
    uint256 public forwarderFee = 0.001 ether; // 0.1%

    // 事件
    event ForwarderAdded(address indexed forwarder);
    event ForwarderRemoved(address indexed forwarder);
    event MetaTransactionExecuted(address indexed from, bytes data, uint256 nonce);

    constructor() EIP712("MetaTransaction", "1") {
        DOMAIN_SEPARATOR = _calculateDomainSeparator();
    }

    /**
     * @notice 添加转发器
     * @param forwarder 转发器地址
     */
    function addForwarder(address forwarder) external onlyOwner {
        require(!isForwarder[forwarder], "Forwarder already exists");
        isForwarder[forwarder] = true;
        emit ForwarderAdded(forwarder);
    }

    /**
     * @notice 移除转发器
     * @param forwarder 转发器地址
     */
    function removeForwarder(address forwarder) external onlyOwner {
        require(isForwarder[forwarder], "Forwarder does not exist");
        isForwarder[forwarder] = false;
        emit ForwarderRemoved(forwarder);
    }

    /**
     * @notice 执行 Meta-Transaction
     * @param from 发送者地址
     * @param data 交易数据（编码的函数调用）
     * @param nonce Nonce
     * @param signature 签名
     */
    function executeMetaTransaction(
        address from,
        bytes calldata data,
        uint256 nonce,
        bytes calldata signature
    ) external {
        // 检查转发器
        require(isForwarder[msg.sender], "Not a forwarder");

        // 验证签名
        _verifySignature(from, data, nonce, signature);

        // 使用 nonce
        _useNonce(from);

        // 执行交易
        (bool success, ) = from.call(data);
        require(success, "Transaction failed");

        emit MetaTransactionExecuted(from, data, nonce);
    }

    /**
     * @notice 验证 Meta-Transaction 签名
     * @param from 发送者地址
     * @param data 交易数据
     * @param nonce Nonce
     * @param signature 签名
     */
    function _verifySignature(
        address from,
        bytes memory data,
        uint256 nonce,
        bytes memory signature
    ) private view {
        // 构建数据结构
        bytes32 structHash = keccak256(
            abi.encode(META_TRANSACTION_TYPEHASH, from, keccak256(data), nonce)
        );

        bytes32 digest = keccak256(
            abi.encodePacked("\x19\x01", DOMAIN_SEPARATOR, structHash)
        );

        // 恢复签名者
        address signer = ECDSA.recover(digest, signature);
        require(signer == from, "Invalid signature");
    }

    /**
     * @notice 计算 Domain Separator
     * @return domainSeparator 域分隔符哈希
     */
    function _calculateDomainSeparator() private view returns (bytes32) {
        return keccak256(
            abi.encode(
                keccak256("EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"),
                keccak256("MetaTransaction"),
                keccak256("1"),
                block.chainid,
                address(this)
            )
        );
    }
}
```

---

## TypeScript/JavaScript 实战

### 1. 使用 ethers.js 签署 Permit

**代码示例：**
```typescript
import { ethers } from "ethers";

// 配置
const provider = new ethers.JsonRpcProvider(process.env.RPC_URL);
const wallet = new ethers.Wallet(process.env.PRIVATE_KEY, provider);
const tokenAddress = "0x...";
const tokenContract = new ethers.Contract(tokenAddress, [
    "function permit(address owner, address spender, uint256 value, uint256 deadline, uint8 v, bytes32 r, bytes32 s)",
    "function nonces(address owner) view returns (uint256)"
], wallet);

// EIP-712 类型
const domain = {
    name: "TokenPermit",
    version: "1",
    chainId: 31337, // 或 await provider.getNetwork().then(n => n.chainId)
    verifyingContract: tokenAddress,
};

// Permit 类型
const types = {
    Permit: [
        { name: "owner", type: "address" },
        { name: "spender", type: "address" },
        { name: "value", type: "uint256" },
        { name: "nonce", type: "uint256" },
        { name: "deadline", type: "uint256" },
    ],
};

// Permit 数据
const permitData = {
    owner: wallet.address,
    spender: "0x...", // 授权的地址
    value: ethers.parseEther("1"), // 1 ETH
    nonce: 0,
    deadline: Math.floor(Date.now() / 1000) + 3600, // 1 小时后
};

// 签名 Permit
async function signPermit() {
    const nonce = await tokenContract.nonces(wallet.address);
    permitData.nonce = nonce;

    const signature = await wallet.signTypedData(domain, {
        Permit: types.Permit,
    }, permitData);

    // 分离签名
    const { v, r, s } = ethers.utils.splitSignature(signature);

    console.log("Permit signed:", { v, r, s });
    return { v, r, s, deadline: permitData.deadline };
}

// 使用 Permit 转账
async function usePermit() {
    const { v, r, s, deadline } = await signPermit();

    const tx = await tokenContract.permit(
        wallet.address,
        permitData.spender,
        permitData.value,
        deadline,
        v,
        r,
        s
    );

    await tx.wait();
    console.log("Permit used successfully!");
}
```

### 2. 使用 viem 签署 Permit2

**代码示例：**
```typescript
import { createClient, http, parseEther, parseUnits } from "viem";
import { privateKeyToAccount } from "viem/accounts";
import { mainnet } from "viem/chains";
import { tokenPermit } from "viem/zksync"; // 或其他链

// 创建客户端
const client = createClient({
    transport: http(process.env.RPC_URL),
    chain: mainnet,
});

// 创建账户
const account = privateKeyToAccount(process.env.PRIVATE_KEY);

// Permit2 类型
const domain = {
    name: "TokenPermit2",
    version: "1",
    chainId: 1,
    verifyingContract: "0x...", // 合约地址
};

// Permit2 类型
const types = {
    PermitSingle: [
        { name: "details", type: "PermitDetails" },
        { name: "spender", type: "address" },
        { name: "sigDeadline", type: "uint256" },
    ],
    PermitDetails: [
        { name: "token", type: "address" },
        { name: "amount", type: "uint160" },
        { name: "expiration", type: "uint48" },
        { name: "nonce", type: "uint48" },
    ],
};

// Permit2 数据
const permitData = {
    details: {
        token: "0x...",
        amount: parseEther("1"),
        expiration: Math.floor(Date.now() / 1000) + 3600,
        nonce: 0,
    },
    spender: "0x...", // 授权的地址
    sigDeadline: Math.floor(Date.now() / 1000) + 3600,
};

// 签名 Permit2
async function signPermit2() {
    const signature = await account.signTypedData({
        domain,
        types,
        value: permitData,
        primaryType: "PermitSingle",
    });

    // 分离签名
    const { v, r, s } = signature;
    console.log("Permit2 signed:", { v, r, s });
    return { v, r, s };
}

// 使用 Permit2 授权
async function usePermit2() {
    const { v, r, s } = await signPermit2();

    const request = await publicClient.simulateContract({
        address: PERMIT2_ADDRESS,
        abi: permit2Abi,
        functionName: "permit",
        args: [
            {
                token: permitData.details.token,
                amount: permitData.details.amount,
                expiration: permitData.details.expiration,
                nonce: permitData.details.nonce,
                signature: {
                    v,
                    r,
                    s,
                },
            },
            permitData.spender,
            permitData.sigDeadline,
        ],
    });

    const hash = await wallet.writeContract(request);
    console.log("Permit2 used successfully!", hash);
}
```

---

## CarLife 项目集成

### 1. CarLife Permit 合约

**场景：** 允许车主授权服务商进行维护记录。

**合约代码：**
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/utils/cryptography/draft-EIP712.sol";
import "@openzeppelin/contracts/utils/Nonces.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "./CarNFT_Secure.sol";

/**
 * @title CarLifeServicePermit
 * @dev CarLife 服务 Permit 合约
 */
contract CarLifeServicePermit is Ownable, EIP712, Nonces {
    bytes32 private immutable DOMAIN_SEPARATOR;
    bytes32 private constant SERVICE_TYPEHASH =
        keccak256("Service(uint256 tokenId,uint256 mileage,string notes,uint256 nonce,uint256 deadline)");

    CarNFT_Secure public carNFT;

    // 服务商映射
    mapping(address => bool) public isService;

    // 事件
    event ServiceAdded(address indexed service);
    event ServiceRemoved(address indexed service);
    event ServiceRecorded(uint256 indexed tokenId, uint256 mileage, string notes, uint256 nonce, uint256 deadline);

    constructor(address _carNFT) EIP712("CarLifeServicePermit", "1") {
        carNFT = CarNFT_Secure(_carNFT);
        DOMAIN_SEPARATOR = _calculateDomainSeparator();
    }

    /**
     * @notice 使用 Permit 记录服务
     * @param owner 车主地址
     * @param tokenId Token ID
     * @param mileage 里程
     * @param notes 备注
     * @param nonce Nonce
     * @param deadline 过期时间
     * @param v 签名的 v 值
     * @param r 签名的 r 值
     * @param s 签名的 s 值
     */
    function recordServiceWithPermit(
        address owner,
        uint256 tokenId,
        uint256 mileage,
        string calldata notes,
        uint256 nonce,
        uint256 deadline,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) external {
        // 检查服务商
        require(isService[msg.sender], "Not a service provider");

        // 验证签名
        _verifyPermit(owner, tokenId, mileage, notes, nonce, deadline, v, r, s);

        // 使用 nonce
        _useNonce(owner);

        // 记录服务
        carNFT.recordMaintenance(tokenId, mileage, notes);

        emit ServiceRecorded(tokenId, mileage, notes, nonce, deadline);
    }

    /**
     * @notice 添加服务商
     * @param service 服务商地址
     */
    function addService(address service) external onlyOwner {
        require(!isService[service], "Service already exists");
        isService[service] = true;
        emit ServiceAdded(service);
    }

    /**
     * @notice 移除服务商
     * @param service 服务商地址
     */
    function removeService(address service) external onlyOwner {
        require(isService[service], "Service does not exist");
        isService[service] = false;
        emit ServiceRemoved(service);
    }

    /**
     * @notice 验证 Permit 签名
     * @param owner 车主地址
     * @param tokenId Token ID
     * @param mileage 里程
     * @param notes 备注
     * @param nonce Nonce
     * @param deadline 过期时间
     * @param v 签名的 v 值
     * @param r 签名的 r 值
     * @param s 签名的 s 值
     */
    function _verifyPermit(
        address owner,
        uint256 tokenId,
        uint256 mileage,
        string memory notes,
        uint256 nonce,
        uint256 deadline,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) private view {
        // 检查过期
        require(block.timestamp <= deadline, "Permit expired");

        // 构建数据结构
        bytes32 structHash = keccak256(
            abi.encode(SERVICE_TYPEHASH, tokenId, mileage, keccak256(bytes(notes)), nonce, deadline)
        );

        bytes32 digest = keccak256(
            abi.encodePacked("\x19\x01", DOMAIN_SEPARATOR, structHash)
        );

        // 恢复签名者
        address signer = ECDSA.recover(digest, v, r, s);
        require(signer == owner, "Invalid signature");
    }

    /**
     * @notice 计算 Domain Separator
     * @return domainSeparator 域分隔符哈希
     */
    function _calculateDomainSeparator() private view returns (bytes32) {
        return keccak256(
            abi.encode(
                keccak256("EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"),
                keccak256("CarLifeServicePermit"),
                keccak256("1"),
                block.chainid,
                address(this)
            )
        );
    }
}
```

### 2. CarLife 前端集成

**React 组件示例：**
```tsx
import { useState, useEffect } from 'react';
import { ethers } from 'ethers';

const CarServiceForm = () => {
    const [tokenId, setTokenId] = useState('');
    const [mileage, setMileage] = useState('');
    const [notes, setNotes] = useState('');

    const handleRecordService = async () => {
        try {
            // 获取 nonce
            const provider = new ethers.providers.Web3Provider(window.ethereum);
            const signer = await provider.getSigner();
            const carLifeContract = new ethers.Contract(
                CAR_LIFE_ADDRESS,
                [
                    "function recordServiceWithPermit(address owner, uint256 tokenId, uint256 mileage, string notes, uint256 nonce, uint256 deadline, uint8 v, bytes32 r, bytes32 s)",
                    "function nonces(address owner) view returns (uint256)"
                ],
                signer
            );

            // 获取 nonce
            const nonce = await carLifeContract.nonces(await signer.getAddress());

            // 构建数据
            const domain = {
                name: "CarLifeServicePermit",
                version: "1",
                chainId: (await provider.getNetwork()).chainId,
                verifyingContract: CAR_LIFE_ADDRESS,
            };

            const types = {
                Service: [
                    { name: "tokenId", type: "uint256" },
                    { name: "mileage", type: "uint256" },
                    { name: "notes", type: "string" },
                    { name: "nonce", type: "uint256" },
                    { name: "deadline", type: "uint256" },
                ],
            };

            const value = {
                tokenId: parseInt(tokenId),
                mileage: parseInt(mileage),
                notes,
                nonce: parseInt(nonce.toString()),
                deadline: Math.floor(Date.now() / 1000) + 3600, // 1 小时后
            };

            // 签名
            const signature = await signer.signTypedData(domain, { Service: types.Service }, value);

            // 分离签名
            const { v, r, s } = ethers.utils.splitSignature(signature);

            // 记录服务
            const tx = await carLifeContract.recordServiceWithPermit(
                await signer.getAddress(),
                value.tokenId,
                value.mileage,
                value.notes,
                value.nonce,
                value.deadline,
                v,
                r,
                s
            );

            await tx.wait();
            console.log("Service recorded successfully!");
        } catch (error) {
            console.error("Failed to record service:", error);
        }
    };

    return (
        <div>
            <h2>记录车辆服务</h2>
            <input
                type="text"
                placeholder="Token ID"
                value={tokenId}
                onChange={(e) => setTokenId(e.target.value)}
            />
            <input
                type="number"
                placeholder="里程"
                value={mileage}
                onChange={(e) => setMileage(e.target.value)}
            />
            <textarea
                placeholder="备注"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
            />
            <button onClick={handleRecordService}>记录服务</button>
        </div>
    );
};

export default CarServiceForm;
```

---

## 最佳实践

### 1. 安全最佳实践

**验证签名：**
```solidity
function _verifySignature(...) internal view {
    // 始终验证签名
    address signer = ECDSA.recover(digest, v, r, s);
    require(signer == expectedSigner, "Invalid signature");

    // 使用 EIP-712 重放保护
    _useNonce(signer);
}
```

**检查过期：**
```solidity
function _checkDeadline(uint256 deadline) internal view {
    require(block.timestamp <= deadline, "Transaction expired");
    require(block.timestamp >= deadline - 1 days, "Transaction too old");
}
```

**限制额度：**
```solidity
function _checkAmount(uint256 amount) internal view {
    require(amount <= MAX_PERMIT_AMOUNT, "Amount exceeds limit");
}
```

### 2. Gas 优化最佳实践

**使用 unchecked：**
```solidity
function _useNonce(address owner) internal {
    unchecked {
        ++_nonces[owner];
    }
}
```

**批量操作：**
```typescript
// 批量 Permit 签名
async function batchSignPermits(permits: PermitData[]) {
    const signatures = await Promise.all(
        permits.map(permit => wallet.signTypedData(domain, { Permit: types.Permit }, permit))
    );
    return signatures;
}
```

**使用 Permit2：**
```solidity
// Permit2 允许单次签名授权多个代币
function permit2(
    PermitTransferFrom memory permit,
    address owner,
    AuthCalldata auth
) external {
    IERC20PermitAllowed(token).permit2(owner, type(IERC20Permit).interfaceId, permit, auth);
}
```

### 3. 用户体验最佳实践

**清晰的错误信息：**
```typescript
try {
    const tx = await tokenContract.permit(...);
} catch (error) {
    if (error.code === "CALL_EXCEPTION") {
        throw new Error("签名验证失败：请检查签名数据");
    } else if (error.code === "TIMEOUT") {
        throw new Error("交易超时：请提高 Gas 限制");
    }
}
```

**显示可读的签名数据：**
```typescript
function displayPermitData(permit: PermitData) {
    console.log("授权详情:");
    console.log(`所有者: ${permit.owner}`);
    console.log(`被授权方: ${permit.spender}`);
    console.log(`金额: ${ethers.formatEther(permit.value)} ETH`);
    console.log(`过期时间: ${new Date(permit.deadline * 1000).toLocaleString()}`);
    console.log(`Nonce: ${permit.nonce}`);
}
```

**使用离线签名：**
```typescript
// 使用硬件钱包（如 Ledger、Trezor）
const provider = new ethers.providers.JsonRpcProvider();
const wallet = new ethers.Wallet(process.env.PRIVATE_KEY, provider);

// 转换为硬件钱包连接
const hardwareWallet = await wallet.connect(hardwareProvider);

// 离线签名
const signature = await hardwareWallet.signTypedData(domain, types, permit);
```

---

## 常见问题

### 1. Nonce 不匹配

**问题：** 服务器返回的 nonce 与客户端使用的 nonce 不一致。

**解决方案：**
- 始终从合约获取最新的 nonce
- 使用 `_useNonce` 来原子性地增加 nonce
- 在签名后等待交易确认

### 2. 签名过期

**问题：** 签名的 deadline 已经过期。

**解决方案：**
- 使用合理的 deadline（如 1 小时）
- 在签名前验证 deadline
- 提供重新签名按钮

### 3. 转发器攻击

**问题：** 转发器重放 Permit 以获取费用。

**解决方案：**
- 添加转发器白名单
- 限制转发器费用
- 使用 Permit2（具有更好的重放保护）

### 4. 钓鱼攻击

**问题：** 攻击者伪造 Permit 以欺骗用户。

**解决方案：**
- 始终显示签名数据给用户确认
- 验证合约地址
- 使用声誉系统（仅授权知名转发器）

### 5. Gas 成本高

**问题：** Permit 交易的 Gas 成本高于直接授权交易。

**解决方案：**
- 使用 Permit2（批量授权）
- 批量 Permit 签名
- 使用 Permit2 批量授权多个代币

---

## 总结

EIP-712 是改善以太坊用户体验的重要技术。通过本研究，我们：

1. **掌握了 EIP-712 的核心概念**：域分隔符、类型数据、消息数据
2. **学习了技术原理**：哈希计算、签名验证、重放保护
3. **实现了 Solidity 实战**：Permit 功能、Permit2、Meta-Transaction
4. **实现了 TypeScript/JavaScript 实战**：ethers.js 签名、viem 签名
5. **集成到 CarLife 项目**：CarLifeServicePermit 合约、React 前端组件
6. **总结了最佳实践**：安全、Gas 优化、用户体验
7. **解决了常见问题**：Nonce 不匹配、签名过期、转发器攻击、钓鱼攻击、Gas 成本高

**下一步：**
- 集成 EIP-712 到 CarLife 项目
- 开发 CarLife Permit2 集成
- 实施 CarLife 元交易功能

---

**研究完成时间：** 2026-02-18
**总字数：** 约 20,000 字
**下次研究方向：** 待定（等待义父指令）
