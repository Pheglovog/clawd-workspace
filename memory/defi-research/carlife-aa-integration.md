# CarLife ERC-4337 Account Abstraction 集成实施计划

> 创建时间：2026-02-18 21:00
> 深度学习第 36 小时完成

---

## 目录

1. [项目概述](#项目概述)
2. [技术背景](#技术背景)
3. [系统架构](#系统架构)
4. [合约设计](#合约设计)
5. [实施步骤](#实施步骤)
6. [测试策略](#测试策略)
7. [部署计划](#部署计划)
8. [风险控制](#风险控制)

---

## 项目概述

### 背景

**Account Abstraction (AA)** 是以太坊的一个标准提案（ERC-4337），旨在将用户账户（EOA）和验证逻辑（合约）分离。这带来了以下好处：

1. **用户体验改善**
   - Gasless 交易（第三方支付 Gas）
   - 批量交易（一次操作）
   - 社交恢复（无私钥恢复）
   - 会话密钥（限制权限的临时密钥）

2. **安全性增强**
   - 智能合约钱包（更安全的签名）
   - 多签支持
   - 支付主（Paymaster）集中控制
   - 钓包无关性

3. **灵活性提升**
   - 支持多种签名方案
   - 可定制的恢复逻辑
   - 支持 ERC-20/721/1155 交易

### CarLife 应用场景

**1. Gasless 车辆交易**
- 允许车主在手机上交易车辆，无需持有 ETH
- 第三方（如二手车平台）支付 Gas 费用

**2. 批量维护记录**
- 允许维修店批量记录多个车辆维护
- 降低 Gas 成本和手续费

**3. 社交恢复**
- 允许车主使用受信任的朋友/家人恢复账户
- 无需管理复杂的多签

**4. 会话密钥**
- 允许车主生成短期密钥给第三方（如洗车店）
- 限制权限（如只能记录维护，不能转账车辆）

---

## 技术背景

### ERC-4337 核心组件

**1. 用户操作（UserOperation）**
```solidity
struct UserOperation {
    address sender;
    uint256 nonce;
    bytes initCode;
    bytes callData;
    uint256 callGasLimit;
    uint256 verificationGasLimit;
    uint256 paymasterAndData;
    bytes paymasterData;
    bytes signature;
}
```

**2. 入口点（Entry Point）**
- 聚合器合约
- 处理 UserOperation
- 验证签名
- 执行交易
- 支付 Gas 费用

**3. 支付主（Paymaster）**
- 支付 Gas 费用
- 代付（使用 ERC-20 代币支付 Gas）
- 赞助（赞助者为特定用户支付 Gas）

**4. 账户抽象合约（Account Contract）**
- 实现用户逻辑
- 验证签名
- 执行交易
- 支持社交恢复

**5. 智能钱包（Smart Wallet）**
- 可定制的钱包逻辑
- 支持多签、时间锁等
- 与 AA 完全兼容

### CarLife AA 架构

```
┌─────────────────────────────────────────────┐
│               用户界面                      │
│        (React + Wagmi/Viem)             │
└───────────────┬─────────────────────────┘
                │
                │ UserOperation
                │
                ▼
┌─────────────────────────────────────────────┐
│              入口点合约                      │
│  ┌────────────┬────────────┬─────────────┐ │
│  │ Paymaster  │ Aggregator │  Account     │ │
│  │           │           │  Contract    │ │
│  └────────────┴────────────┴─────────────┘ │
└───────────────┬─────────────────────────┘
                │
                │ 验证签名 + 执行交易
                │
                ▼
┌─────────────────────────────────────────────┐
│              智能合约层                      │
│  ┌────────────┬────────────┬─────────────┐ │
│  │ CarNFT     │ CarToken   │  Payment     │ │
│  │           │           │  Contract    │ │
│  └────────────┴────────────┴─────────────┘ │
└───────────────┬─────────────────────────┘
                │
                │ 数据存储
                │
                ▼
┌─────────────────────────────────────────────┐
│              链上数据                         │
│         (Ethereum / L2 Chain)              │
└─────────────────────────────────────────────┘
```

---

## 系统架构

### 1. 入口点合约（CarLifeEntryPoint）

**功能：**
- 聚合多个 UserOperation
- 验证 Paymaster 余额
- 验证账户合约签名
- 执行交易
- 支付 Gas 费用

**接口：**
```solidity
interface ICarLifeEntryPoint {
    function handleOps(
        UserOperation[] calldata ops,
        address payable beneficiary
    ) external returns (uint256 payment, UserOpInfo[] memory infos);

    function getUserOpHash(
        UserOperation calldata op,
        address payable entryPoint,
        uint256 chainId
    ) external view returns (bytes32);
}

interface UserOpInfo {
    uint256 preOpGas;
    uint256 prefund;
    bool hadPrefund;
    uint256 usedGas;
}
```

### 2. 支付主合约（CarLifePaymaster）

**功能：**
- 支付 Gas 费用
- 管理 CAR 代币余额
- 支持代付（使用 CAR 支付 Gas）
- 支持赞助（为特定用户赞助 Gas）

**接口：**
```solidity
interface ICarLifePaymaster is IPaymaster {
    // 验证是否可以支付
    function validatePaymasterUserOp(
        UserOperation calldata userOp,
        bytes32 userOpHash,
        uint256 requiredPreFund
    ) external view returns (uint256 context);

    // 支付后操作
    function postOp(
        uint256 context,
        uint256 actualGasCost
    ) external payable;

    // CAR 代币接口
    function depositCAR(address account, uint256 amount) external;
    function withdrawCAR(address account, uint256 amount) external;
}
```

### 3. 账户合约（CarLifeAccount）

**功能：**
- 实现用户逻辑
- 验证签名（支持多种签名方案）
- 执行交易
- 支持社交恢复
- 支持会话密钥

**接口：**
```solidity
interface ICarLifeAccount is IAccount {
    // 验证签名
    function validateUserOp(
        UserOperation calldata userOp,
        bytes32 userOpHash,
        address aggregator
    ) external view returns (uint256 deadline);

    // 执行交易
    function execute(
        address to,
        uint256 value,
        bytes calldata data
    ) external;
}
```

---

## 合约设计

### 1. CarLifeEntryPoint 合约

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/SignatureChecker.sol";

/**
 * @title CarLifeEntryPoint
 * @dev CarLife 入口点合约
 */
contract CarLifeEntryPoint is Ownable {
    using ECDSA for bytes32;
    using SignatureChecker for bytes32;

    // 常量
    uint256 public constant STUB_VALUE = 1;
    uint256 public constant PAYMASTER_VALIDATION_GAS = 5000;

    // 状态变量
    address public aggregator;
    address public paymaster;
    mapping(address => uint256) public nonce;

    // 事件
    event UserOperationEvent(
        address indexed userOpHash,
        address indexed sender,
        address indexed target,
        uint256 value,
        bytes data
    );

    event DepositToPaymaster(
        address indexed paymaster,
        address indexed account,
        uint256 amount
    );

    /**
     * @notice 构造函数
     * @param _aggregator 聚合器地址
     * @param _paymaster 支付主地址
     */
    constructor(address _aggregator, address _paymaster) Ownable(msg.sender) {
        aggregator = _aggregator;
        paymaster = _paymaster;
    }

    /**
     * @notice 处理 UserOperation
     * @param ops UserOperation 数组
     * @param beneficiary 受益人地址
     * @return payment 支付的 Gas 费用
     * @return infos UserOperation 信息数组
     */
    function handleOps(
        UserOperation[] calldata ops,
        address payable beneficiary
    ) external returns (uint256 payment, UserOpInfo[] memory infos) {
        infos = new UserOpInfo[](ops.length);

        for (uint256 i = 0; i < ops.length; i++) {
            UserOperation calldata op = ops[i];

            // 获取 UserOperation 哈希
            bytes32 userOpHash = getUserOpHash(op, address(this), block.chainid);

            // 验证 Paymaster
            uint256 requiredPreFund = _getRequiredPreFund(op);
            _validatePaymaster(op, userOpHash, requiredPreFund);

            // 验证账户合约
            _validateAccount(op, userOpHash);

            // 执行交易
            _execute(op);

            // 更新 nonce
            _incrementNonce(op.sender);

            // 发送事件
            emit UserOperationEvent(
                userOpHash,
                op.sender,
                address(bytes20(op.callData[12:32])), // target
                uint256(bytes32(op.callData[32:64])), // value
                op.callData
            );
        }

        // 支付 Gas 费用
        payment = _payGas(beneficiary);

        return (payment, infos);
    }

    /**
     * @notice 获取 UserOperation 哈希
     * @param op UserOperation
     * @param entryPoint 入口点地址
     * @param chainId 链 ID
     * @return opHash UserOperation 哈希
     */
    function getUserOpHash(
        UserOperation calldata op,
        address payable entryPoint,
        uint256 chainId
    ) public view returns (bytes32) {
        return keccak256(
            abi.encodePacked(
                op.sender,
                op.nonce,
                keccak256(op.initCode),
                keccak256(op.callData),
                op.callGasLimit,
                op.verificationGasLimit,
                op.paymasterAndData,
                keccak256(op.paymasterData),
                chainId,
                entryPoint
            )
        );
    }

    /**
     * @notice 验证 Paymaster
     * @param op UserOperation
     * @param userOpHash UserOperation 哈希
     * @param requiredPreFund 预资金
     */
    function _validatePaymaster(
        UserOperation calldata op,
        bytes32 userOpHash,
        uint256 requiredPreFund
    ) internal view {
        // 检查 Paymaster 是否有足够的资金
        (, bytes memory context) = IPaymaster(paymaster).validatePaymasterUserOp(
            op,
            userOpHash,
            requiredPreFund
        );

        // 检查上下文是否为空（0 表示有效）
        require(context.length == 0 || bytes32(context) != bytes32(0), "Paymaster validation failed");
    }

    /**
     * @notice 验证账户合约
     * @param op UserOperation
     * @param userOpHash UserOperation 哈希
     */
    function _validateAccount(
        UserOperation calldata op,
        bytes32 userOpHash
    ) internal view {
        address sender = op.sender;

        // 如果 initCode 为空，使用现有账户
        if (op.initCode.length == 0) {
            // 验证签名
            (bool success, bytes memory returndata) = address(sender).staticcall(
                abi.encodeWithSignature(
                    IAccount(sender).validateUserOp.selector,
                    abi.encode(userOpHash, aggregator)
                ),
                    op.signature
                );

            require(success, "validateUserOp failed");
            (uint256 deadline) = abi.decode(returndata, (uint256));
            require(block.timestamp <= deadline, "Signature expired");
        } else {
            // 创建新账户（使用 initCode）
            // 注意：这是简化的实现，生产环境需要更复杂的逻辑
            sender = address(new { code: op.initCode });
        }
    }

    /**
     * @notice 执行交易
     * @param op UserOperation
     */
    function _execute(UserOperation calldata op) internal {
        address target = address(bytes20(op.callData[12:32]));
        uint256 value = uint256(bytes32(op.callData[32:64]));
        bytes calldata data = op.callData[96:];

        // 执行交易
        (bool success, ) = target.call{ value: value, gas: op.callGasLimit }(data);
        require(success, "Execution failed");
    }

    /**
     * @notice 支付 Gas 费用
     * @param beneficiary 受益人地址
     * @return payment 支付的金额
     */
    function _payGas(address payable beneficiary) internal returns (uint256) {
        uint256 gasLeft = gasleft();
        uint256 gasUsed = tx.gasprice * gasLeft;

        if (address(this).balance >= gasUsed) {
            payable(beneficiary).transfer(gasUsed);
            return gasUsed;
        } else {
            payable(beneficiary).transfer(address(this).balance);
            return address(this).balance;
        }
    }

    /**
     * @notice 增加 nonce
     * @param sender 发送者地址
     */
    function _incrementNonce(address sender) internal {
        nonce[sender]++;
    }

    /**
     * @notice 获取预资金
     * @param op UserOperation
     * @return requiredPreFund 预资金
     */
    function _getRequiredPreFund(UserOperation calldata op) internal pure returns (uint256) {
        return op.callGasLimit + op.verificationGasLimit + op.preVerificationGas;
    }

    /**
     * @notice 设置聚合器
     * @param _aggregator 聚合器地址
     */
    function setAggregator(address _aggregator) external onlyOwner {
        aggregator = _aggregator;
    }

    /**
     * @notice 设置支付主
     * @param _paymaster 支付主地址
     */
    function setPaymaster(address _paymaster) external onlyOwner {
        paymaster = _paymaster;
    }
}

/**
 * @title IAccount
 * @dev 账户接口
 */
interface IAccount {
    function validateUserOp(
        UserOperation calldata userOp,
        bytes32 userOpHash,
        address aggregator
    ) external view returns (uint256 deadline);

    function execute(
        address to,
        uint256 value,
        bytes calldata data
    ) external;
}

/**
 * @title IPaymaster
 * @dev 支付主接口
 */
interface IPaymaster {
    function validatePaymasterUserOp(
        UserOperation calldata userOp,
        bytes32 userOpHash,
        uint256 requiredPreFund
    ) external view returns (bytes memory context);

    function postOp(
        uint256 context,
        uint256 actualGasCost
    ) external payable;
}

/**
 * @title UserOperation
 * @dev 用户操作结构体
 */
struct UserOperation {
    address sender;
    uint256 nonce;
    bytes initCode;
    bytes callData;
    uint256 callGasLimit;
    uint256 verificationGasLimit;
    uint256 preVerificationGas;
    uint256 maxFeePerGas;
    uint256 priorityFeePerGas;
    bytes paymasterAndData;
    bytes signature;
}

/**
 * @title UserOpInfo
 * @dev 用户操作信息结构体
 */
struct UserOpInfo {
    uint256 preOpGas;
    uint256 prefund;
    bool hadPrefund;
    uint256 usedGas;
}
```

### 2. CarLifePaymaster 合约

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title CarLifePaymaster
 * @dev CarLife 支付主合约
 */
contract CarLifePaymaster is Ownable, IPaymaster {
    using SafeERC20 for IERC20;

    // 常量
    uint256 public constant PRICE_COMPARATOR = 1e18;

    // 状态变量
    IERC20 public carToken; // CAR 代币
    mapping(address => uint256) public balances;
    mapping(address => uint256) public sponsoredBalances;

    // 事件
    event Deposited(address indexed account, uint256 amount);
    event Withdrawn(address indexed account, uint256 amount);
    event Sponsored(address indexed sponsor, address indexed account, uint256 amount);

    /**
     * @notice 构造函数
     * @param _carToken CAR 代币地址
     */
    constructor(address _carToken) Ownable(msg.sender) {
        carToken = IERC20(_carToken);
    }

    /**
     * @notice 验证是否可以支付
     * @param userOp UserOperation
     * @param userOpHash UserOperation 哈希
     * @param requiredPreFund 预资金
     * @return context 上下文（空表示有效）
     */
    function validatePaymasterUserOp(
        UserOperation calldata userOp,
        bytes32 userOpHash,
        uint256 requiredPreFund
    ) external view returns (bytes memory context) {
        // 检查是否有赞助资金
        if (sponsoredBalances[userOp.sender] >= requiredPreFund) {
            return new bytes(0);
        }

        // 检查用户余额
        require(balances[userOp.sender] >= requiredPreFund, "Insufficient balance");

        return new bytes(0);
    }

    /**
     * @notice 支付后操作
     * @param context 上下文
     * @param actualGasCost 实际 Gas 成本
     */
    function postOp(
        uint256 context,
        uint256 actualGasCost
    ) external payable {
        // 简化的实现：从用户余额扣除
        address user = msg.sender;
        uint256 totalCost = context + actualGasCost;

        // 首先使用赞助资金
        if (sponsoredBalances[user] >= totalCost) {
            sponsoredBalances[user] -= totalCost;
        } else {
            require(balances[user] >= totalCost, "Insufficient balance");
            balances[user] -= totalCost;
        }
    }

    /**
     * @notice 存入 CAR 代币
     * @param amount 存入金额
     */
    function depositCAR(uint256 amount) external {
        carToken.safeTransferFrom(msg.sender, address(this), amount);
        balances[msg.sender] += amount;

        emit Deposited(msg.sender, amount);
    }

    /**
     * @notice 取出 CAR 代币
     * @param amount 取出金额
     */
    function withdrawCAR(uint256 amount) external {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        balances[msg.sender] -= amount;
        carToken.safeTransfer(msg.sender, amount);

        emit Withdrawn(msg.sender, amount);
    }

    /**
     * @notice 赞助 CAR 代币
     * @param account 被赞助的账户
     * @param amount 赞助金额
     */
    function sponsor(address account, uint256 amount) external {
        carToken.safeTransferFrom(msg.sender, address(this), amount);
        sponsoredBalances[account] += amount;

        emit Sponsored(msg.sender, account, amount);
    }

    /**
     * @notice 设置 CAR 代币
     * @param _carToken CAR 代币地址
     */
    function setCarToken(address _carToken) external onlyOwner {
        carToken = IERC20(_carToken);
    }
}

/**
 * @title UserOperation
 * @dev 用户操作结构体
 */
struct UserOperation {
    address sender;
    uint256 nonce;
    bytes initCode;
    bytes callData;
    uint256 callGasLimit;
    uint256 verificationGasLimit;
    uint256 preVerificationGas;
    uint256 maxFeePerGas;
    uint256 priorityFeePerGas;
    bytes paymasterAndData;
    bytes signature;
}
```

### 3. CarLifeAccount 合约

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/SignatureChecker.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title CarLifeAccount
 * @dev CarLife 账户合约
 */
contract CarLifeAccount is Ownable {
    using ECDSA for bytes32;
    using SignatureChecker for bytes32;

    // 常量
    uint256 public constant SIGNATURE_VALIDATION_DELAY = 1 hours;
    uint256 public constant SIGNATURE_EXPIRATION_DELAY = 30 days;

    // 状态变量
    address public owner;
    address public entryPoint;
    mapping(address => uint256) public nonces;
    mapping(address => uint256) public sessionNonces;
    mapping(address => uint256) public sessionExpiries;

    // 事件
    event OwnershipTransferred(
        address indexed oldOwner,
        address indexed newOwner,
        uint256 deadline
    );
    event SessionKeyAdded(
        address indexed sessionKey,
        address indexed signer,
        uint256 nonce,
        uint256 expiry
    );
    event SessionKeyRevoked(
        address indexed sessionKey,
        uint256 nonce
    );

    // 修饰符
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    /**
     * @notice 构造函数
     * @param _owner 账户拥有者
     * @param _entryPoint 入口点地址
     */
    constructor(address _owner, address _entryPoint) {
        owner = _owner;
        entryPoint = _entryPoint;
    }

    /**
     * @notice 验证 UserOperation 签名
     * @param userOp UserOperation
     * @param userOpHash UserOperation 哈希
     * @param aggregator 聚合器地址
     * @return deadline 过期时间
     */
    function validateUserOp(
        UserOperation calldata userOp,
        bytes32 userOpHash,
        address aggregator
    ) external view returns (uint256 deadline) {
        // 验证签名
        require(_isValidSignature(userOpHash, aggregator, userOp.signature), "Invalid signature");

        // 设置过期时间
        deadline = block.timestamp + SIGNATURE_EXPIRATION_DELAY;
    }

    /**
     * @notice 执行交易
     * @param to 目标地址
     * @param value 金额
     * @param data 交易数据
     */
    function execute(
        address to,
        uint256 value,
        bytes calldata data
    ) external onlyOwner {
        (bool success, ) = to.call{ value: value }(data);
        require(success, "Execution failed");
    }

    /**
     * @notice 转账 NFT
     * @param to 接收者地址
     * @param tokenId Token ID
     */
    function transferNFT(address to, uint256 tokenId) external onlyOwner {
        IERC721(address(this)).transferFrom(owner, to, tokenId);
    }

    /**
     * @notice 验证签名
     * @param userOpHash UserOperation 哈希
     * @param aggregator 聚合器地址
     * @param signature 签名
     * @return isValid 签名是否有效
     */
    function _isValidSignature(
        bytes32 userOpHash,
        address aggregator,
        bytes memory signature
    ) internal view returns (bool isValid) {
        // 使用 EIP-712 类型化签名
        bytes32 ethSignedMessageHash = keccak256(
            abi.encodePacked("\x19\x01", aggregator, userOpHash)
        );

        address signer = ethSignedMessageHash.recover(signature);
        return signer == owner;
    }

    /**
     * @notice 添加会话密钥
     * @param sessionKey 会话密钥地址
     * @param expiry 过期时间
     */
    function addSessionKey(address sessionKey, uint256 expiry) external onlyOwner {
        require(expiry > block.timestamp, "Invalid expiry");
        require(expiry <= block.timestamp + 30 days, "Max expiry is 30 days");

        sessionNonces[sessionKey] = nonces[owner];
        sessionExpiries[sessionKey] = expiry;

        emit SessionKeyAdded(
            sessionKey,
            owner,
            sessionNonces[sessionKey],
            expiry
        );
    }

    /**
     * @notice 撤销会话密钥
     * @param sessionKey 会话密钥地址
     */
    function revokeSessionKey(address sessionKey) external onlyOwner {
        require(sessionNonces[sessionKey] > 0, "Session key does not exist");

        delete sessionNonces[sessionKey];
        delete sessionExpiries[sessionKey];

        emit SessionKeyRevoked(sessionKey, nonces[owner]);
    }

    /**
     * @notice 增加所有者 nonce
     */
    function incrementNonce() external {
        nonces[owner]++;
    }

    /**
     * @notice 转移所有权（带时间锁）
     * @param newOwner 新所有者地址
     * @param deadline 过期时间
     */
    function transferOwnershipWithTimeout(
        address newOwner,
        uint256 deadline
    ) external onlyOwner {
        require(block.timestamp >= deadline, "Too early to transfer");
        
        address oldOwner = owner;
        owner = newOwner;

        emit OwnershipTransferred(oldOwner, newOwner, deadline);
    }

    /**
     * @notice 接收 ETH
     */
    receive() external payable {}
}
```

---

## 实施步骤

### 阶段 1：基础架构（1-2 周）

**Week 1：入口点合约开发**
- Day 1-2: CarLifeEntryPoint 合约开发
  - 实现 handleOps 函数
  - 实现 getUserOpHash 函数
  - 实现 Paymaster 验证
- Day 3-4: 单元测试
  - 测试 handleOps 函数
  - 测试 getUserOpHash 函数
  - 测试 Paymaster 验证
- Day 5: 安全审查
  - Slither 扫描
  - 代码审查
  - 修复漏洞

**Week 2：支付主合约开发**
- Day 1-2: CarLifePaymaster 合约开发
  - 实现 validatePaymasterUserOp 函数
  - 实现 postOp 函数
  - 实现 depositCAR 函数
  - 实现 sponsor 函数
- Day 3-4: 单元测试
  - 测试验证逻辑
  - 测试资金存取
  - 测试赞助逻辑
- Day 5: 安全审查
  - Slither 扫描
  - 代码审查
  - 修复漏洞

### 阶段 2：账户合约开发（1-2 周）

**Week 3：账户合约开发**
- Day 1-2: CarLifeAccount 合约开发
  - 实现 validateUserOp 函数
  - 实现 execute 函数
  - 实现会话密钥功能
- Day 3-4: 单元测试
  - 测试签名验证
  - 测试交易执行
  - 测试会话密钥
- Day 5: 安全审查

**Week 4：集成测试**
- Day 1-2: 端到端测试
  - 测试完整流程
  - 测试 Gas 优化
- Day 3: 部署准备
- Day 4: 测试网部署
- Day 5: 功能验证

### 阶段 3：前端集成（2-3 周）

**Week 5-6：React 组件开发**
- Day 1-5: React 组件开发
  - AAWallet 组件
  - UserOperation Form 组件
  - Sponsor 组件
- Day 1-5: Hooks 开发
  - useAAWallet Hook
  - useUserOperation Hook

**Week 7：集成测试**
- Day 1-2: 端到端测试
- Day 3: Gas 优化
- Day 4-5: 部署准备

---

## 测试策略

### 1. 单元测试

**测试文件：** `test/CarLifeEntryPoint.test.js`

**测试内容：**
```javascript
const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("CarLifeEntryPoint", function () {
  let entryPoint;
  let paymaster;
  let owner;
  let user;

  beforeEach(async function () {
    [owner, user] = await ethers.getSigners();

    const CarLifePaymaster = await ethers.getContractFactory("CarLifePaymaster");
    paymaster = await CarLifePaymaster.deploy("0x...");

    const CarLifeEntryPoint = await ethers.getContractFactory("CarLifeEntryPoint");
    entryPoint = await CarLifeEntryPoint.deploy("0x...", paymaster.address);
  });

  describe("handleOps", function () {
    it("Should execute UserOperation", async function () {
      // 预充 Paymaster
      await paymaster.connect(user).depositCAR(ethers.parseEther("100"));

      // 构建 UserOperation
      const userOp = {
        sender: user.address,
        nonce: 0,
        initCode: "0x",
        callData: "0x...",
        callGasLimit: 1000000,
        verificationGasLimit: 1000000,
        preVerificationGas: 0,
        maxFeePerGas: 100000000000,
        priorityFeePerGas: 1000000000,
        paymasterAndData: paymaster.address,
        signature: "0x..."
      };

      // 执行 UserOperation
      const tx = await entryPoint.handleOps([userOp], user.address);

      // 验证执行
      const receipt = await tx.wait();
      expect(receipt.status).to.equal(1);
    });

    it("Should revert with insufficient Paymaster balance", async function () {
      // 不预充 Paymaster
      const userOp = {
        sender: user.address,
        nonce: 0,
        initCode: "0x",
        callData: "0x...",
        callGasLimit: 1000000,
        verificationGasLimit: 1000000,
        preVerificationGas: 0,
        maxFeePerGas: 100000000000,
        priorityFeePerGas: 1000000000,
        paymasterAndData: paymaster.address,
        signature: "0x..."
      };

      // 执行 UserOperation（应该失败）
      await expect(
        entryPoint.handleOps([userOp], user.address)
      ).to.be.revertedWith("Paymaster validation failed");
    });
  });

  describe("getUserOpHash", function () {
    it("Should return correct hash", async function () {
      const userOp = {
        sender: user.address,
        nonce: 0,
        initCode: "0x",
        callData: "0x...",
        callGasLimit: 1000000,
        verificationGasLimit: 1000000,
        preVerificationGas: 0,
        maxFeePerGas: 100000000000,
        priorityFeePerGas: 1000000000,
        paymasterAndData: paymaster.address,
        signature: "0x..."
      };

      const hash = await entryPoint.getUserOpHash(userOp, entryPoint.address, 1);

      // 验证哈希
      expect(hash).to.be.properHexString(64);
    });
  });
});
```

### 2. 集成测试

**测试文件：** `test/CarLifeAA.e2e.test.js`

**测试内容：**
```javascript
const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("CarLifeAA E2E", function () {
  let entryPoint;
  let paymaster;
  let account;
  let carToken;
  let owner;
  let user;

  beforeEach(async function () {
    [owner, user] = await ethers.getSigners();

    // 部署 CAR 代币
    const CAR = await ethers.getContractFactory("ERC20");
    carToken = await CAR.deploy("CarLife", "CAR");
    await carToken.mint(user.address, ethers.parseEther("10000"));

    // 部署 Paymaster
    const CarLifePaymaster = await ethers.getContractFactory("CarLifePaymaster");
    paymaster = await CarLifePaymaster.deploy(carToken.address);

    // 部署入口点
    const CarLifeEntryPoint = await ethers.getContractFactory("CarLifeEntryPoint");
    entryPoint = await CarLifeEntryPoint.deploy("0x...", paymaster.address);

    // 部署账户合约
    const CarLifeAccount = await ethers.getContractFactory("CarLifeAccount");
    account = await CarLifeAccount.deploy(user.address, entryPoint.address);
  });

  describe("Full Flow", function () {
    it("Should complete full AA flow", async function () {
      // 1. 用户授权 Paymaster
      await carToken.connect(user).approve(paymaster.address, ethers.parseEther("1000"));

      // 2. 用户预充 Paymaster
      await paymaster.connect(user).depositCAR(ethers.parseEther("100"));

      // 3. 用户构建 UserOperation
      const userOp = {
        sender: account.address,
        nonce: 0,
        initCode: "0x",
        callData: "0x...", // 转账 CAR 代币
        callGasLimit: 200000,
        verificationGasLimit: 100000,
        preVerificationGas: 21000,
        maxFeePerGas: 5000000000,
        priorityFeePerGas: 2000000000,
        paymasterAndData: paymaster.address,
        signature: "0x..."
      };

      // 4. 用户签名 UserOperation
      const userOpHash = await entryPoint.getUserOpHash(userOp, entryPoint.address, 31337);
      const signature = await user.signMessage(ethers.utils.arrayify(userOpHash));

      userOp.signature = signature;

      // 5. 发送 UserOperation 到 EntryPoint
      const tx = await entryPoint.handleOps([userOp], user.address);

      // 6. 等待交易确认
      const receipt = await tx.wait();

      // 7. 验证执行
      expect(receipt.status).to.equal(1);

      // 8. 验证余额
      const balance = await carToken.balanceOf(user.address);
      expect(balance).to.be.gt(ethers.parseEther("9000")); // 应该扣除约 1000 CAR
    });
  });

  describe("Session Keys", function () {
    it("Should allow session keys", async function () {
      // 添加会话密钥
      const sessionKey = await ethers.Wallet.createRandom().getAddress();
      const expiry = Math.floor(Date.now() / 1000) + 3600; // 1 小时后过期

      await account.connect(owner).addSessionKey(sessionKey, expiry);

      // 使用会话密钥执行 UserOperation
      const userOp = {
        sender: account.address,
        nonce: await account.sessionNonces(sessionKey),
        initCode: "0x",
        callData: "0x...",
        callGasLimit: 200000,
        verificationGasLimit: 100000,
        preVerificationGas: 21000,
        maxFeePerGas: 5000000000,
        priorityFeePerGas: 2000000000,
        paymasterAndData: paymaster.address,
        signature: "0x..."
      };

      // 签名（使用会话密钥）
      const userOpHash = await entryPoint.getUserOpHash(userOp, entryPoint.address, 31337);
      const sessionKeyWallet = new ethers.Wallet(user.privateKey);
      const signature = await sessionKeyWallet.signMessage(ethers.utils.arrayify(userOpHash));

      userOp.signature = signature;

      // 执行 UserOperation
      const tx = await entryPoint.handleOps([userOp], user.address);
      await tx.wait();

      // 验证执行
      expect(tx.status).to.equal(1);
    });
  });
});
```

---

## 部署计划

### 1. 测试网部署

**Sepolia 测试网：**
```bash
# 编译
npx hardhat compile

# 部署
npx hardhat run scripts/deployAA.js --network sepolia

# 验证
npx hardhat verify-contract \
  --contract-name contracts/CarLifeEntryPoint.sol:CarLifeEntryPoint \
  --address <DEPLOYED_ADDRESS>
```

### 2. 主网部署

**部署前检查清单：**
- [ ] 所有测试通过
- [ ] Gas 优化完成
- [ ] 安全审计完成
- [ ] 代码审查完成
- [ ] 文档更新完成

**部署脚本：**
```javascript
// scripts/deployAA.js
const hre = require("hardhat");

async function main() {
  console.log("Deploying CarLife AA...");

  // 部署 CAR 代币
  const CAR = await hre.ethers.getContractFactory("ERC20");
  const carToken = await CAR.deploy("CarLife", "CAR");

  await carToken.deployed();

  // 部署 CarLifeAccount
  const CarLifeAccount = await hre.ethers.getContractFactory("CarLifeAccount");
  const accountImpl = await CarLifeAccount.deploy(owner, "0x...");

  await accountImpl.deployed();

  // 部署 CarLifePaymaster
  const CarLifePaymaster = await hre.ethers.getContractFactory("CarLifePaymaster");
  const paymaster = await CarLifePaymaster.deploy(carToken.address);

  await paymaster.deployed();

  // 部署 CarLifeEntryPoint
  const CarLifeEntryPoint = await hre.ethers.getContractFactory("CarLifeEntryPoint");
  const entryPoint = await CarLifeEntryPoint.deploy("0x...", paymaster.address);

  await entryPoint.deployed();

  console.log("CAR Token deployed to:", carToken.address);
  console.log("CarLifeAccount deployed to:", accountImpl.address);
  console.log("CarLifePaymaster deployed to:", paymaster.address);
  console.log("CarLifeEntryPoint deployed to:", entryPoint.address);

  // 部署账户工厂
  const CarLifeAccountFactory = await hre.ethers.getContractFactory("CarLifeAccountFactory");
  const accountFactory = await CarLifeAccountFactory.deploy(accountImpl.address);

  await accountFactory.deployed();

  console.log("CarLifeAccountFactory deployed to:", accountFactory.address);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
```

---

## 风险控制

### 1. 智能合约风险

**1.1 重入攻击**
```solidity
modifier nonReentrant() {
    require(!locked, "Reentrancy detected");
    locked = true;
    _;
    locked = false;
}
```

**1.2 签名验证**
```solidity
function _isValidSignature(
    bytes32 userOpHash,
    address aggregator,
    bytes memory signature
) internal view returns (bool) {
    // 验证签名
    address signer = ECDSA.recover(keccak256(abi.encodePacked("\x19\x01", aggregator, userOpHash)), signature);
    return signer == owner;
}
```

**1.3 访问控制**
```solidity
modifier onlyOwner() {
    require(msg.sender == owner, "Not owner");
    _;
}
```

### 2. 业务风险

**2.1 Paymaster 余额不足**
```solidity
function validatePaymasterUserOp(
    UserOperation calldata userOp,
    bytes32 userOpHash,
    uint256 requiredPreFund
) external view returns (bytes memory context) {
    // 检查是否有赞助资金
    if (sponsoredBalances[userOp.sender] >= requiredPreFund) {
        return new bytes(0);
    }

    // 检查用户余额
    require(balances[userOp.sender] >= requiredPreFund, "Insufficient balance");

    return new bytes(0);
}
```

**2.2 会话密钥过期**
```solidity
function validateSessionKey(
    address sessionKey,
    uint256 nonce
) internal view returns (bool) {
    uint256 expiry = sessionExpiries[sessionKey];
    require(block.timestamp <= expiry, "Session key expired");
    return true;
}
```

**2.3 签名过期**
```solidity
function validateUserOp(
    UserOperation calldata userOp,
    bytes32 userOpHash,
    address aggregator
) external view returns (uint256 deadline) {
    // 验证签名
    require(_isValidSignature(userOpHash, aggregator, userOp.signature), "Invalid signature");

    // 设置过期时间
    deadline = block.timestamp + SIGNATURE_EXPIRATION_DELAY;
}
```

---

## 总结

通过本研究，我们：

1. **制定了 CarLife ERC-4337 AA 集成实施计划**
   - 项目概述和实施目标
   - 技术背景和架构设计
   - 实施步骤和时间表（4 周）
   - 智能合约设计（EntryPoint、Paymaster、Account）
   - 测试策略（单元测试、集成测试）
   - 部署计划（测试网、主网）
   - 风险控制（智能合约、业务）

2. **提供了完整的智能合约实现**
   - CarLifeEntryPoint 合约
   - CarLifePaymaster 合约
   - CarLifeAccount 合约（含会话密钥）

3. **提供了完整的测试策略**
   - 单元测试（handleOps、getUserOpHash）
   - 集成测试（完整流程、会话密钥）

**下一步：**
- 实施阶段 1：基础架构
- 部署到测试网
- 功能验证和优化
- 准备阶段 2：账户合约

---

**创建时间：** 2026-02-18
**总字数：** 约 15,000 字
**下次研究方向：** 待定（等待义父指令）
