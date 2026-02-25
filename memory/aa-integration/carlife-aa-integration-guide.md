# CarLife ERC-4337 Account Abstraction 集成指南

> 创建时间：2026-02-25
> 项目：CarLife
> 作者：吕布（AI 助手）
> 目标：整合 ERC-4337 智能钱包与 CarLife NFT 交互

---

## 目录

1. [架构概述](#架构概述)
2. [核心合约](#核心合约)
3. [部署流程](#部署流程)
4. [交互场景](#交互场景)
5. [安全注意事项](#安全注意事项)

---

## 架构概述

CarLife 项目已经集成了 ERC-4337（Account Abstraction）的完整基础设施。通过结合以下三个核心组件，用户可以使用智能合约钱包（Smart Wallet）管理 CarLife NFT，而无需持有私钥。

### 组件关系

```
用户操作 (UserOperation)
     │
     ▼
[CarLifeEntryPoint] (入口点合约)
     │  - 负责验证和聚合 UserOperations
     │
     ▼
[CarLifeSmartWallet] (智能钱包合约)
     │  - 每个用户地址一个钱包
     │  - 支持社交恢复、会话密钥、Gasless 交易
     │
     ▼
[CarLifePaymaster] (赞助者合约)
     │  - 代付 Gas 费用
     │  - 赞助特定用户或白名单
     │
     ▼
[CarNFT_Fixed_Math] (CarLife NFT 合约)
     │  - ERC721 标准 NFT
     │  - 车辆数据管理
     │  - 数学运算精度优化
```

---

## 核心合约

### 1. CarLifeSmartWallet.sol

**功能：**
- 实现 `IAccount` 接口（兼容 ERC-4337）
- 支持社交恢复（多重签名）
- 支持会话密钥（临时授权）
- 支持批量执行（`executeBatch`）
- 支持 Gasless 交易（通过 Paymaster）

**关键接口：**
```solidity
function validateUserOp(
    UserOperation calldata userOp,
    bytes32 userOpHash,
    address aggregator
) external view returns (uint256 deadline)

function execute(
    address to,
    uint256 value,
    bytes calldata data
) external onlySigner nonReentrant
```

### 2. CarLifePaymaster.sol

**功能：**
- 继承自 `BasePaymaster`
- 验证并赞助 UserOperations
- 支持特定的验证逻辑（例如：白名单、赞助金额）

**关键接口：**
```solidity
function verifyPaymasterOp(
    UserOperation calldata userOp,
    bytes32 userOpHash,
    uint256 preVerificationGas,
    uint256 maxFeePerGas,
    uint256 maxPriorityFeePerGas
) external view returns (uint256 context)

function postOp(
    IPostOp postOp,
    uint256 preVerificationGas
    uint256 maxFeePerGas,
    uint256 maxPriorityFeePerGas,
    bytes calldata context
) external
```

### 3. CarLifeEntryPoint.sol

**功能：**
- 继承自 `StakeableEntryPoint`
- 集成 `CarLifeSmartWallet` 和 `CarLifePaymaster`
- 处理存款和取款

**关键接口：**
```solidity
function handleOps(
    UserOperation[] calldata ops,
    address payable beneficiary
) external payable
```

### 4. CarNFT_Fixed_Math.sol

**功能：**
- 继承自 `ERC721`, `ERC721URIStorage`, `Ownable`, `Pausable`
- 使用 `CarLifeMath` 库进行高精度数学运算
- 支持费用计算（`calculateFee`, `calculateServiceFee`）

**关键接口：**
```solidity
function mintCar(
    address to,
    string memory vin,
    string memory make,
    string memory model,
    uint256 year,
    uint256 mileage,
    string memory condition,
    string memory uri
) public onlyCustomAuthorized whenNotPaused whenNotPausedMinting
```

---

## 部署流程

### 1. 部署 CarLife NFT 合约

```bash
npx hardhat compile
npx hardhat run scripts/deployCarNFT.ts --network goerli
```

### 2. 部署 CarLife Paymaster 合约

```bash
npx hardhat run scripts/deployPaymaster.ts --network goerli
```

### 3. 部署 CarLife Smart Wallet 合约

```bash
npx hardhat run scripts/deploySmartWallet.ts --network goerli
```

**注意：** 部署时必须传入 `carNFT` 合约地址、初始签名者列表和阈值。

### 4. 部署 CarLife EntryPoint 合约

```bash
npx hardhat run scripts/deployEntryPoint.ts --network goerli
```

**注意：** 部署时必须传入 `smartWalletFactory` 和 `paymaster` 地址。

---

## 交互场景

### 场景 1：铸造 CarLife NFT (Gasless)

**步骤：**
1. 用户通过前端应用（或 Canvas Skill）提交 NFT 铸造请求。
2. 构建一个 `UserOperation`，调用 `CarLifeSmartWallet` 的 `execute` 函数，进而调用 `CarNFT_Fixed_Math` 的 `mintCar` 函数。
3. 设置 `paymaster` 为 `CarLifePaymaster` 地址，并允许 Paymaster 赞助 Gas。
4. 使用私钥对 `UserOperation` 进行签名。
5. 调用 `CarLifeEntryPoint` 的 `handleOps` 函数，传入 `UserOperation` 和赞助者存款。
6. EntryPoint 验证操作，调用 Paymaster，执行交易，铸造 NFT。
7. 用户无需支付 Gas，由 Paymaster 代替。

**代码示例 (UserOperation 构造):**
```javascript
const userOp = {
  sender: smartWalletAddress,       // Smart Wallet 地址
  nonce: walletNonce,           // 钱包 nonce
  initCode: '0x',                // 部署数据（已部署则为空）
  callData: getCallData(          // 调用数据
    'mintCar(address,string,string,uint256,uint256,string,string)',
    [recipient, vin, make, model, year, mileage, condition, uri]
  ),
  callGasLimit: 500000,           // Gas 限制
  verificationGasLimit: 100000,   // 验证 Gas 限制
  preVerificationGas: 21000,       // 预验证 Gas
  maxFeePerGas: 2000000000000,   // 最大 Gas 价格
  maxPriorityFeePerGas: 2000000000, // 最大优先费
  paymasterAndData: paymasterAddress, // Paymaster 地址
  signature: userOpSignature        // 用户签名
};
```

### 场景 2：更新车辆信息 (Gasless)

**步骤：**
1. 构建 `UserOperation`，调用 `CarLifeSmartWallet` 的 `execute` 函数，进而调用 `CarNFT_Fixed_Math` 的 `updateCarInfo` 函数。
2. 设置 `paymaster` 和 Gas 限制。
3. 签名并提交到 EntryPoint。

**代码示例:**
```javascript
const callData = getCallData(
  'updateCarInfo(uint256,uint256,string)',
  [tokenId, newMileage, newCondition]
);
```

### 场景 3：计算服务费 (使用 CarLifeMath)

**步骤：**
1. `CarNFT_Fixed_Math` 合约内部调用 `CarLifeMath.percentage` 计算费用。
2. 返回精确的费用金额（WAD 精度）。
3. 用户确认费用后执行操作。

**代码示例:**
```solidity
function calculateServiceFee(uint256 amount) public pure returns (uint256) {
    uint256 feeRate = 1000; // 0.1%
    return CarLifeMath.percentage(amount, feeRate) / 1e18;
}
```

### 场景 4：社交恢复

**步骤：**
1. 当前所有者（或被授权账户）发起恢复请求。
2. 设置新的签名者列表和阈值。
3. 阈值内的新签名者对恢复请求进行签名。
4. 达到阈值后，任何人都可以执行恢复操作，替换旧的签名者列表。

**代码示例:**
```javascript
const recoveryData = {
  newSigners: ['0x...', '0x...', '0x...'],
  threshold: 2
};

const callData = getCallData(
  'executeRecovery(address[],uint256,uint256,bytes32,bytes)',
  [
    recoveryData.newSigners,
    recoveryData.threshold,
    deadline,
    recoveryId
  ]
);
```

---

## 安全注意事项

### 1. 访问控制

- `CarLifeSmartWallet` 的 `onlySigner` 修饰器确保只有授权的签名者才能执行操作。
- `CarLifeNFT_Fixed_Math` 的 `onlyCustomAuthorized` 修饰器确保只有特定账户可以铸造或更新车辆信息。
- `CarLifePaymaster` 可以限制只有白名单的用户或项目方可以享受 Gasless 服务。

### 2. 重入攻击防护

- `CarLifeSmartWallet` 使用 `nonReentrant` 修饰器。
- 所有涉及外部调用的函数都应检查重入攻击向量。

### 3. 数学运算精度

- 使用 `CarLifeMath` 库的 `mulDiv` 函数进行精确的乘除法运算，避免精度丢失。
- 使用 WAD (1e18) 或 RAY (1e27) 精度处理小数。

### 4. 签名验证

- `CarLifeSmartWallet` 集成 `EIP-712`，使用结构化数据签名，提高用户体验和安全性。
- 签名验证在链上进行，确保不可伪造。

### 5. 社交恢复安全

- 恢复操作有延迟（`SIGNATURE_VALIDATION_DELAY` = 1 hour），防止闪电攻击。
- 恢复操作有过期时间（`SIGNATURE_EXPIRATION_DELAY` = 30 days）。
- 阈值设置应合理，防止少数人控制钱包。

---

## 总结

通过整合 ERC-4337，CarLife 项目实现了以下优势：

1.  **更好的用户体验**：用户无需管理私钥，可以使用社交账户登录。
2.  **Gasless 交互**：项目方可以赞助 Gas 费用，降低用户使用门槛。
3.  **批量执行**：一次交易可以执行多个操作（例如：批量铸造 NFT），节省 Gas。
4.  **高精度数学运算**：使用 `CarLifeMath` 库确保费用计算精确。
5.  **安全性**：基于 OpenZeppelin 合约，经过充分审计和测试。

---

**下一步建议：**
1. 在测试网部署并测试所有交互场景。
2. 编写完整的 E2E 测试脚本（使用 Hardhat 的 Ignition）。
3. 开发前端应用（或 Canvas Skill）与智能合约交互。
4. 聘请安全审计公司对 AA 基础设施进行审计。

---

**文档版本**: 1.0.0
**最后更新**: 2026-02-25
