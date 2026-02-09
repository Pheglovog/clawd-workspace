# Chainlink CCIP 跨链桥开发指南

**协议简介**: Chainlink CCIP 是去中心化跨链互操作协议，支持代币转移和跨链智能合约调用。

**官方文档**: https://docs.chain.link/ccip

---

## 目录

1. [架构概述](#架构概述)
2. [核心概念](#核心概念)
3. [快速开始](#快速开始)
4. [跨链代币转账](#跨链代币转账)
5. [跨链消息传递](#跨链消息传递)
6. [风险管理](#风险管理)
7. [常见问题](#常见问题)

---

## 架构概述

### 组件

1. **Router (路由器)**
   - 跨链消息的路由器
   - 每个链上的入口点
   - 地址：链特定

2. **OnRamp / OffRamp**
   - OnRamp: 发送消息到其他链
   - OffRamp: 接收来自其他链的消息

3. **Risk Management Module (RMM)**
   - 风险管理模块
   - 控制支持的链和代币
   - 可自定义

4. **Price Feed**
   - Chainlink 价格预言机
   - 用于跨链汇率计算

### 消息流程

```
链 A (发送端)                Router                链 B (接收端)
┌─────────────┐              ┌──────┐            ┌─────────────┐
│    CCIP     │              │      │            │    CCIP     │
│             │              │      │            │             │
│  ccipSend() │──Message────>│      │──Relay──>│ccipReceive()│
│             │              │      │            │             │
└─────────────┘              └──────┘            └─────────────┘
      ↑                                                  ↑
      │                                                  │
   用户触发                                         处理消息
```

---

## 核心概念

### 1. Chain ID

每条链都有唯一的 Chain ID：

| 网络 | Chain ID |
|------|----------|
| Ethereum Sepolia | 11155111 |
| Arbitrum Sepolia | 421614 |
| Optimism Goerli | 420 |
| Polygon Mumbai | 80001 |
| Avalanche Fuji | 43113 |

### 2. Supported Chains

CCIP 支持的链列表（持续更新）：

| 链 | 状态 | Router 地址 |
|----|------|-----------|
| Ethereum Mainnet | ✅ | 0x... |
| Arbitrum One | ✅ | 0x... |
| Optimism | ✅ | 0x... |
| Polygon | ✅ | 0x... |
| Base | ✅ | 0x... |

### 3. Token Pool

每个支持的代币都有一个 Pool，用于锁定/铸造跨链代币。

---

## 快速开始

### 步骤 1: 环境准备

```bash
# 创建项目
mkdir ccip-bridge && cd ccip-bridge

# 初始化 Foundry 项目
forge init

# 安装依赖
forge install OpenZeppelin/openzeppelin-contracts
forge install smartcontractkit/chainlink-brownie-contracts
```

### 步骤 2: 配置 `.env`

```bash
# RPC 端点
SEPOLIA_RPC_URL=https://rpc.sepolia.org
ARBITRUM_SEPOLIA_RPC_URL=https://sepolia-rollup.arbitrum.io/rpc

# 部署账户私钥
PRIVATE_KEY=your_private_key_here

# Etherscan API Key
ETHERSCAN_API_KEY=your_etherscan_api_key

# Chainlink CCIP 配置
SEPOLIA_ROUTER=0x...
ARB_SEPOLIA_ROUTER=0x...
```

---

## 跨链代币转账

### 步骤 1: 创建代币桥合约

创建 `src/CCIPTokenBridge.sol`:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts-ccip/src/v0.8/ccip/applications/CCIPReceiver.sol";

/**
 * @title CCIPTokenBridge
 * @notice 使用 Chainlink CCIP 实现的跨链代币桥
 */
contract CCIPTokenBridge is CCIPReceiver, ERC20, Ownable {
    using SafeERC20 for IERC20;

    // 事件
    event CrossChainTransfer(
        uint64 indexed destChainSelector,
        address indexed sender,
        address indexed receiver,
        uint256 amount
    );

    event CrossChainReceived(
        uint64 indexed srcChainSelector,
        address indexed sender,
        uint256 amount
    );

    /**
     * @notice 构造函数
     * @param _router CCIP Router 地址
     * @param _owner 合约 owner
     * @param _name 代币名称
     * @param _symbol 代币符号
     */
    constructor(
        address _router,
        address _owner,
        string memory _name,
        string memory _symbol
    ) CCIPReceiver(_router) ERC20(_name, _symbol) Ownable(_owner) {}

    /**
     * @notice 发送跨链代币
     * @param _destChainSelector 目标链 selector
     * @param _receiver 目标链上的接收者
     * @param _amount 转账金额
     * @param _feeToken 支付费用的代币地址（address(0) = native）
     */
    function sendToken(
        uint64 _destChainSelector,
        address _receiver,
        uint256 _amount,
        address _feeToken
    ) external onlyOwner returns (bytes memory) {
        require(balanceOf(owner()) >= _amount, "Insufficient balance");

        // 从 owner 销毁代币
        _burn(owner(), _amount);

        // 创建 CCIP 消息
        Client.EVM2AnyMessage memory evm2AnyMessage = Client.EVM2AnyMessage({
            receiver: abi.encode(_receiver),
            data: abi.encode(_amount),
            tokenAmounts: new Client.EVMTokenAmount[](0),
            extraArgs: Client._argsToBytes(
                Client.EVMExtraArgsV1({gasLimit: 200_000, strict: false})
            ),
            feeToken: _feeToken
        });

        // 发送消息
        bytes memory messageId = _router.ccipSend(_destChainSelector, evm2AnyMessage);

        emit CrossChainTransfer(_destChainSelector, owner(), _receiver, _amount);
        return messageId;
    }

    /**
     * @notice 接收跨链消息（CCIPReceiver 回调）
     */
    function _ccipReceive(
        Client.Any2EVMMessage calldata any2EvmMessage
    ) internal override {
        // 解码消息
        (address receiver, uint256 amount) = abi.decode(
            any2EvmMessage.data,
            (address, uint256)
        );

        // 铸造代币给接收者
        _mint(receiver, amount);

        emit CrossChainReceived(any2EvmMessage.sourceChainSelector, receiver, amount);
    }

    /**
     * @notice 获取 CCIP 费用
     * @param _destChainSelector 目标链 selector
     * @param _amount 转账金额
     * @param _feeToken 支付费用的代币
     * @return fee CCIP 费用
     */
    function getFee(
        uint64 _destChainSelector,
        uint256 _amount,
        address _feeToken
    ) external view returns (uint256 fee) {
        Client.EVM2AnyMessage memory evm2AnyMessage = Client.EVM2AnyMessage({
            receiver: abi.encode(address(this)),
            data: abi.encode(_amount),
            tokenAmounts: new Client.EVMTokenAmount[](0),
            extraArgs: Client._argsToBytes(
                Client.EVMExtraArgsV1({gasLimit: 200_000, strict: false})
            ),
            feeToken: _feeToken
        });

        return _router.getFee(_destChainSelector, evm2AnyMessage);
    }
}
```

---

## 跨链消息传递

### 通用消息桥

创建 `src/CCIPMessageBridge.sol`:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@chainlink/contracts-ccip/src/v0.8/ccip/applications/CCIPReceiver.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title CCIPMessageBridge
 * @notice 使用 Chainlink CCIP 实现的跨链消息桥
 */
contract CCIPMessageBridge is CCIPReceiver, Ownable {
    // 存储的消息
    mapping(bytes32 => string) public messages;
    mapping(bytes32 => address) public senders;

    // 事件
    event MessageSent(
        uint64 indexed destChainSelector,
        bytes32 indexed messageId,
        address indexed sender,
        string message
    );

    event MessageReceived(
        uint64 indexed srcChainSelector,
        address indexed sender,
        string message
    );

    /**
     * @notice 构造函数
     * @param _router CCIP Router 地址
     * @param _owner 合约 owner
     */
    constructor(address _router, address _owner) CCIPReceiver(_router) Ownable(_owner) {}

    /**
     * @notice 发送跨链消息
     * @param _destChainSelector 目标链 selector
     * @param _message 消息内容
     * @param _feeToken 支付费用的代币
     */
    function sendMessage(
        uint64 _destChainSelector,
        string calldata _message,
        address _feeToken
    ) external payable onlyOwner returns (bytes memory) {
        Client.EVM2AnyMessage memory evm2AnyMessage = Client.EVM2AnyMessage({
            receiver: abi.encode(address(this)),
            data: abi.encode(msg.sender, _message),
            tokenAmounts: new Client.EVMTokenAmount[](0),
            extraArgs: Client._argsToBytes(
                Client.EVMExtraArgsV1({gasLimit: 200_000, strict: false})
            ),
            feeToken: _feeToken
        });

        bytes memory messageId = _router.ccipSend(_destChainSelector, evm2AnyMessage);
        emit MessageSent(_destChainSelector, messageId, msg.sender, _message);
        return messageId;
    }

    /**
     * @notice 接收跨链消息
     */
    function _ccipReceive(
        Client.Any2EVMMessage calldata any2EvmMessage
    ) internal override {
        (address sender, string memory message) = abi.decode(
            any2EvmMessage.data,
            (address, string)
        );

        bytes32 messageId = keccak256(any2EvmMessage.sender);
        messages[messageId] = message;
        senders[messageId] = sender;

        emit MessageReceived(any2EvmMessage.sourceChainSelector, sender, message);
    }

    /**
     * @notice 获取消息
     */
    function getMessage(bytes32 _messageId) external view returns (address sender, string memory message) {
        sender = senders[_messageId];
        message = messages[_messageId];
    }
}
```

---

## 风险管理

### 风险管理模块 (RMM)

CCIP 提供了风险管理功能，可以控制：

1. **支持的链**
2. **支持的代币**
3. **转账限额**
4. **Gas 限制**

### 配置 RMM

```solidity
// 通过 Chainlink Registry 获取 RMM 地址
address rmm = IRegistry(registry).getRiskManagementModule();

// 检查是否支持
bool isChainSupported = IRiskManagementModule(rmm).isChainSupported(chainSelector);
bool isTokenSupported = IRiskManagementModule(rmm).isTokenSupported(tokenAddress);
```

---

## 常见问题

### Q1: 如何获取测试网 Token？

**A**: 使用 Chainlink Faucet:
- https://faucets.chain.link/

### Q2: CCIP 费用如何计算？

**A**:
1. 基础费用：固定费用
2. Gas 费用：基于目标链的 Gas 价格
3. 代币费用：基于转账金额

使用 `getFee()` 函数查询费用。

### Q3: 消息发送失败怎么办？

**A**: 检查：
1. 目标链是否被 RMM 支持
2. 代币是否被 RMM 支持
3. 支付的费用是否足够
4. 查看区块浏览器

### Q4: 如何查看 CCIP 交易状态？

**A**: 使用 Chainlink Explorer:
https://ccip.chain.link/

---

## 参考资源

### 官方文档

- [Chainlink CCIP 文档](https://docs.chain.link/ccip)
- [CCIP 开发者指南](https://docs.chain.link/ccip/developer-guide)
- [支持的链和代币](https://docs.chain.link/ccip/supported-networks)

### 合约代码

- [Chainlink CCIP 合约](https://github.com/smartcontractkit/chainlink-brownie-contracts)

### 开发工具

- [Foundry](https://getfoundry.sh/)
- [Chainlink Explorer](https://ccip.chain.link/)
- [Chainlink Faucet](https://faucets.chain.link/)

---

**文档版本**: 1.0.0
**最后更新**: 2026-02-09
