# LayerZero 跨链桥开发指南

**协议简介**: LayerZero 是一个全链互操作协议，支持轻量级消息传递和跨链智能合约调用。

**官方文档**: https://layerzero.gitbook.io/

---

## 目录

1. [架构概述](#架构概述)
2. [核心概念](#核心概念)
3. [快速开始](#快速开始)
4. [跨链代币转账](#跨链代币转账)
5. [跨链消息传递](#跨链消息传递)
6. [部署到测试网](#部署到测试网)
7. [常见问题](#常见问题)

---

## 架构概述

### 组件

LayerZero 由以下组件组成：

1. **Endpoint (端点)**
   - 每个链上的入口点
   - 处理跨链消息的发送和接收
   - 地址：链特定（见文档）

2. **ULN (Ultra Light Node)**
   - 验证跨链消息
   - 去中心化验证器网络
   - 链下运行

3. **OApp (Omnichain App)**
   - 用户构建的跨链应用
   - 实现发送和接收逻辑
   - 可以是代币、NFT、DeFi 协议等

### 消息流程

```
链 A (发送端)                ULN                 链 B (接收端)
┌─────────────┐              ┌──────┐            ┌─────────────┐
│    OApp    │              │      │            │    OApp    │
│             │              │      │            │             │
│  lzSend()  │──Message────>│      │──Relayer──>│  lzReceive()│
│             │              │      │            │             │
└─────────────┘              └──────┘            └─────────────┘
      ↑                                                  ↑
      │                                                  │
   用户触发                                         处理消息
```

---

## 核心概念

### 1. Eid (Endpoint ID)

每条链的 Endpoint 都有唯一 ID：

| 网络 | Eid |
|------|-----|
| Ethereum Sepolia | 40161 |
| Ethereum Goerli | 40162 |
| Arbitrum Sepolia | 40231 |
| Optimism Goerli | 40232 |
| Polygon Mumbai | 40109 |
| BSC Testnet | 40102 |

### 2. Channel (通道)

OApp 和 Endpoint 之间的通道，用于发送和接收消息。

### 3. Relayer (中继器)

将消息从源链中继到目标链的服务。可以自定义中继器或使用默认中继器。

### 4. SendParam (发送参数)

发送消息时的参数：

```solidity
struct SendParam {
    uint32 dstEid;        // 目标链 Eid
    bytes32 receiver;       // 接收者地址（20 字节）
    bytes message;          // 消息内容
    bytes extraArgs;       // 额外参数
    bool payInLzToken;     // 是否用 LayerZero Token 支付
}
```

---

## 快速开始

### 步骤 1: 环境准备

```bash
# 安装 Foundry
curl -L https://foundry.paradigm.xyz | bash

# 创建项目
forge init layerzero-bridge

# 进入项目目录
cd layerzero-bridge

# 安装依赖
forge install OpenZeppelin/openzeppelin-contracts
forge install LayerZero-Labs/LayerZero-v2
```

### 步骤 2: 配置 Foundry

编辑 `foundry.toml`:

```toml
[profile.default]
src = "src"
out = "out"
libs = ["lib"]
solc_version = "0.8.20"

[rpc_endpoints]
sepolia = "${SEPOLIA_RPC_URL}"
arbitrum_sepolia = "${ARBITRUM_SEPOLIA_RPC_URL}"
```

### 步骤 3: 创建 `.env` 文件

```bash
# RPC 端点
SEPOLIA_RPC_URL=https://rpc.sepolia.org
ARBITRUM_SEPOLIA_RPC_URL=https://sepolia-rollup.arbitrum.io/rpc

# 部署账户私钥
PRIVATE_KEY=your_private_key_here

# Etherscan API Key
ETHERSCAN_API_KEY=your_etherscan_api_key
```

---

## 跨链代币转账

### 步骤 1: 创建代币桥合约

创建 `src/TokenBridge.sol`:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@layerzerolabs/oapp-evm/contracts/oapp/OApp.sol";

/**
 * @title TokenBridge
 * @notice 使用 LayerZero 实现的跨链代币桥
 */
contract TokenBridge is ERC20, OApp {
    using SafeERC20 for IERC20;

    // 锁定的代币（用于提款）
    mapping(address => uint256) public lockedTokens;

    // 事件
    event CrossChainTransfer(
        uint32 indexed dstEid,
        address indexed from,
        address indexed to,
        uint256 amount
    );

    event CrossChainReceived(
        uint32 indexed srcEid,
        address indexed from,
        address indexed to,
        uint256 amount
    );

    /**
     * @notice 构造函数
     * @param _endpoint LayerZero Endpoint 地址
     * @param _owner 合约 owner
     * @param _name 代币名称
     * @param _symbol 代币符号
     */
    constructor(
        address _endpoint,
        address _owner,
        string memory _name,
        string memory _symbol
    ) ERC20(_name, _symbol) OApp(_endpoint, _owner) {}

    /**
     * @notice 存款并跨链转账
     * @param _dstEid 目标链 Eid
     * @param _to 目标链上的接收者
     * @param _amount 转账金额
     * @param _options LayerZero 选项
     */
    function sendToken(
        uint32 _dstEid,
        address _to,
        uint256 _amount,
        bytes calldata _options
    ) external payable {
        // 检查余额
        require(balanceOf(msg.sender) >= _amount, "Insufficient balance");

        // 销毁源链上的代币
        _burn(msg.sender, _amount);

        // 编码消息
        bytes memory message = abi.encode(msg.sender, _to, _amount);

        // 创建 LayerZero 发送参数
        SendParam memory sendParam = SendParam({
            dstEid: _dstEid,
            receiver: bytes32(uint256(uint160(_to))), // 20 字节地址 -> 32 字节
            message: message,
            extraArgs: _options,
            payInLzToken: false
        });

        // 计算 LayerZero 费用
        MessagingFee memory messagingFee = _quoteSend(sendParam, _to, _options);

        // 发送跨链消息
        _lzSend(sendParam, messagingFee);

        emit CrossChainTransfer(_dstEid, msg.sender, _to, _amount);
    }

    /**
     * @notice 接收跨链消息
     * @param _origin 消息来源
     * @param _guid 消息 GUID
     * @param _payload 消息内容
     * @param _executor 执行者
     * @param _extraData 额外数据
     */
    function _lzReceive(
        Origin calldata _origin,
        bytes32 _guid,
        bytes calldata _payload,
        address _executor,
        bytes calldata _extraData
    ) internal override {
        // 解码消息
        (address from, address to, uint256 amount) = abi.decode(_payload, (address, address, uint256));

        // 铸造代币给接收者
        _mint(to, amount);

        emit CrossChainReceived(_origin.srcEid, from, to, amount);
    }

    /**
     * @notice 提款（紧急情况）
     * @param _token 代币地址
     * @param _amount 提款金额
     */
    function emergencyWithdraw(address _token, uint256 _amount) external onlyOwner {
        if (_token == address(this)) {
            // 提取原生代币
            payable(owner()).transfer(_amount);
        } else {
            // 提取 ERC20 代币
            IERC20(_token).safeTransfer(owner(), _amount);
        }
    }
}
```

### 步骤 2: 创建部署脚本

创建 `script/Deploy.s.sol`:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Script.sol";
import "../src/TokenBridge.sol";

contract DeployScript is Script {
    // Sepolia Endpoint
    address constant SEPOLIA_ENDPOINT = 0x6EDCE65403992e310A62460808c48b846cec7e1;

    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        vm.startBroadcast(deployerPrivateKey);

        // 部署 TokenBridge
        TokenBridge bridge = new TokenBridge(
            SEPOLIA_ENDPOINT,
            vm.addr(deployerPrivateKey), // owner = deployer
            "Cross Chain Token",
            "cCCT"
        );

        console.log("TokenBridge deployed to:", address(bridge));

        vm.stopBroadcast();
    }
}
```

---

## 跨链消息传递

### 通用消息桥

创建 `src/MessageBridge.sol`:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@layerzerolabs/oapp-evm/contracts/oapp/OApp.sol";

/**
 * @title MessageBridge
 * @notice 使用 LayerZero 实现的跨链消息桥
 */
contract MessageBridge is OApp {
    // 存储的消息
    mapping(bytes32 => string) public messages;
    mapping(bytes32 => address) public senders;

    // 事件
    event MessageSent(
        uint32 indexed dstEid,
        bytes32 indexed guid,
        address indexed sender,
        string message
    );

    event MessageReceived(
        uint32 indexed srcEid,
        bytes32 indexed guid,
        address indexed sender,
        string message
    );

    /**
     * @notice 发送跨链消息
     * @param _dstEid 目标链 Eid
     * @param _message 消息内容
     * @param _options LayerZero 选项
     */
    function sendMessage(
        uint32 _dstEid,
        string calldata _message,
        bytes calldata _options
    ) external payable {
        bytes memory message = abi.encode(msg.sender, _message);

        SendParam memory sendParam = SendParam({
            dstEid: _dstEid,
            receiver: bytes32(uint256(uint160(address(this)))), // 发送到自己
            message: message,
            extraArgs: _options,
            payInLzToken: false
        });

        MessagingFee memory messagingFee = _quoteSend(sendParam, address(this), _options);
        _lzSend(sendParam, messagingFee);

        emit MessageSent(_dstEid, bytes32(0), msg.sender, _message);
    }

    /**
     * @notice 接收跨链消息
     */
    function _lzReceive(
        Origin calldata _origin,
        bytes32 _guid,
        bytes calldata _payload,
        address _executor,
        bytes calldata _extraData
    ) internal override {
        (address sender, string memory message) = abi.decode(_payload, (address, string));

        messages[_guid] = message;
        senders[_guid] = sender;

        emit MessageReceived(_origin.srcEid, _guid, sender, message);
    }

    /**
     * @notice 获取消息
     * @param _guid 消息 GUID
     * @return sender 发送者
     * @return message 消息内容
     */
    function getMessage(bytes32 _guid) external view returns (address sender, string memory message) {
        sender = senders[_guid];
        message = messages[_guid];
    }
}
```

---

## 部署到测试网

### 步骤 1: 编译合约

```bash
forge build
```

### 步骤 2: 部署到 Sepolia

```bash
forge script script/Deploy.s.sol:DeployScript \
  --rpc-url $SEPOLIA_RPC_URL \
  --broadcast \
  --verify \
  --etherscan-api-key $ETHERSCAN_API_KEY
```

### 步骤 3: 部署到 Arbitrum Sepolia

创建 `script/DeployArb.s.sol`:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Script.sol";
import "../src/TokenBridge.sol";

contract DeployArbScript is Script {
    // Arbitrum Sepolia Endpoint
    address constant ARB_SEPOLIA_ENDPOINT = 0x6EDCE65403992e310A62460808c48b846cec7e1;

    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        vm.startBroadcast(deployerPrivateKey);

        TokenBridge bridge = new TokenBridge(
            ARB_SEPOLIA_ENDPOINT,
            vm.addr(deployerPrivateKey),
            "Cross Chain Token",
            "cCCT"
        );

        console.log("TokenBridge deployed to:", address(bridge));

        vm.stopBroadcast();
    }
}
```

部署：

```bash
forge script script/DeployArb.s.sol:DeployArbScript \
  --rpc-url $ARBITRUM_SEPOLIA_RPC_URL \
  --broadcast
```

### 步骤 4: 测试跨链转账

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/TokenBridge.sol";

contract TokenBridgeTest is Test {
    TokenBridge public sepoliaBridge;
    TokenBridge public arbBridge;

    uint32 constant SEPOLIA_EID = 40161;
    uint32 constant ARB_SEPOLIA_EID = 40231;

    address public user = address(0x1);

    function setUp() public {
        // 模拟部署的合约地址
        sepoliaBridge = TokenBridge(address(0x1234));
        arbBridge = TokenBridge(address(0x5678));
    }

    function testCrossChainTransfer() public {
        uint256 amount = 100 ether;
        address receiver = address(0x2);

        // 在 Sepolia 上授权和发送
        vm.prank(user);
        sepoliaBridge.sendToken(ARB_SEPOLIA_EID, receiver, amount, bytes(""));

        // 模拟接收消息
        bytes memory message = abi.encode(user, receiver, amount);

        Origin memory origin = Origin({
            srcEid: SEPOLIA_EID,
            sender: bytes32(uint256(uint160(address(sepoliaBridge)))),
            nonce: 0
        });

        arbBridge._lzReceive(origin, bytes32(0), message, address(0), bytes(""));

        // 验证代币已铸造
        assertEq(arbBridge.balanceOf(receiver), amount);
    }
}
```

运行测试：

```bash
forge test
```

---

## 常见问题

### Q1: Gas 费用太高

**A**: 可以优化：
1. 压缩消息内容
2. 调整 Gas 参数
3. 使用 LayerZero Token 支付（如果可用）

### Q2: 消息没有到达

**A**: 检查：
1. Eid 是否正确
2. Endpoint 地址是否正确
3. 支付的 LayerZero 费用是否足够
4. 查看区块浏览器的交易状态

### Q3: 如何获取测试网 Token？

**A**: 使用水龙头：
- Sepolia: https://sepoliafaucet.com/
- Arbitrum Sepolia: https://faucet.quicknode.com/arbitrum/sepolia

### Q4: 如何调试跨链消息？

**A**: 使用 LayerZero Explorer：
https://testnet.layerzeroscan.com/

---

## 参考资源

### 官方文档

- [LayerZero V2 文档](https://layerzero.gitbook.io/layerzero-v2)
- [OApp 开发指南](https://layerzero.gitbook.io/layerzero-v2/evm-guides)
- [Endpoint 地址](https://layerzero.gitbook.io/layerzero-v2/technical-documents/mainnet/supported-chains)

### 合约代码

- [LayerZero V2 合约](https://github.com/LayerZero-Labs/LayerZero-v2)
- [OApp 模板](https://github.com/LayerZero-Labs/LayerZero-v2-examples)

### 开发工具

- [Foundry](https://getfoundry.sh/)
- [LayerZero Explorer](https://testnet.layerzeroscan.com/)

---

**文档版本**: 1.0.0
**最后更新**: 2026-02-09
