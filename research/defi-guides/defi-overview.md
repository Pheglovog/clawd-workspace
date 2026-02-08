# DeFi 协议部署指南总览

本文档提供了三个主流 DeFi 协议的部署指南：
- [Aave](./aave-deployment-guide.md) - 借贷协议
- [Uniswap](./uniswap-deployment-guide.md) - 去中心化交易所
- [Compound](./compound-deployment-guide.md) - 借贷协议

---

## 协议对比

| 特性 | Aave | Uniswap | Compound |
|------|------|---------|----------|
| **类型** | 借贷 | DEX | 借贷 |
| **版本** | V3 | V3 | V2/V3 |
| **AMM 模式** | - | x*y=k | - |
| **利率模型** | 浮动利率 | - | 固定/浮动利率 |
| **手续费** | 借款利息 | 0.05% / 0.3% / 1% | 借款利息 |
| **流动性** | 全池可用 | 集中流动性 | 全池可用 |
| **流动性提供** | 存款者 | LP | 存款人 |

---

## 选择指南

### 选择 Aave 的情况

✅ **适合场景**:
- 需要借贷功能
- 需要多种资产支持
- 需要闪电贷功能
- 需灵活的利率模型

❌ **不适合**:
- 交易代币
- 高频交易
- 需要主动管理

### 选择 Uniswap 的情况

✅ **适合场景**:
- 交易代币
- 提供流动性赚取手续费
- 贿选收益
- 价格套利

❌ **不适合**:
- 长期持有
- 低风险偏好
- 不想管理仓位

### 选择 Compound 的情况

✅ **适合场景**:
- 稳定借贷需求
- 传统金融模式
- cToken 标准化
- 更简单的利率模型

❌ **不适合**:
- 需要闪电贷
- 多链部署
- 复杂策略

---

## 部署流程对比

### 共同步骤

所有协议都需要以下共同步骤：

1. **环境准备**
   ```bash
   npm install hardhat ethers dotenv
   ```

2. **配置 RPC 和私钥**
   ```bash
   # .env 文件
   RPC_URL=https://...
   PRIVATE_KEY=0x...
   ```

3. **部署到测试网**
   ```bash
   npx hardhat run scripts/deploy.js --network sepolia
   ```

4. **验证合约**
   ```bash
   npx hardhat verify --network sepolia <CONTRACT_ADDRESS>
   ```

### 协议特定步骤

| 步骤 | Aave | Uniswap | Compound |
|------|------|---------|----------|
| 获取合约地址 | Factory/Pool | Factory/Router | Comptroller/CToken |
| 创建 Pool | 手动部署 | 通过 Factory 创建 | 手动部署 cToken |
| 添加流动性 | 存款到 Pool | Mint NFT Position | 存款到 cToken |
| 提取流动性 | 从 Pool 提取 | Burn NFT Position | 从 cToken 提取 |

---

## 安全考虑

### 智能合约安全

1. **使用审计过的代码**
   - 优先使用官方部署的合约
   - 自定义合约需要专业审计

2. **访问控制**
   ```solidity
   import "@openzeppelin/contracts/access/Ownable.sol";

   contract MyContract is Ownable {
       function sensitiveFunction() external onlyOwner {
           // 只有 owner 可以调用
       }
   }
   ```

3. **紧急暂停**
   ```solidity
   import "@openzeppelin/contracts/utils/Pausable.sol";

   contract MyContract is Pausable {
       function criticalFunction() external whenNotPaused {
           // 暂停时不可调用
       }
   }
   ```

### 前端安全

1. **输入验证**
   ```typescript
   function validateInput(amount: bigint) {
       if (amount <= 0n) throw new Error("Invalid amount");
       if (amount > MAX_AMOUNT) throw new Error("Amount too large");
   }
   ```

2. **滑点保护**
   ```typescript
   const slippage = amountOutMinimum;
   if (actualAmountOut < slippage) {
       throw new Error("Slippage exceeded");
   }
   ```

3. **超时保护**
   ```typescript
   const deadline = Math.floor(Date.now() / 1000) + 60 * 20; // 20 分钟
   ```

---

## Gas 优化

### 常用优化技巧

1. **使用 uint256 而非 uint8**
   ```solidity
   // 好
   uint256 counter;

   // 不好（在某些情况下）
   uint8 counter;
   ```

2. **批量操作**
   ```solidity
   // 好（单次交易）
   function batchDeposit(address[] calldata users, uint256[] calldata amounts) external {
       for (uint i = 0; i < users.length; i++) {
           _deposit(users[i], amounts[i]);
       }
   }
   ```

3. **使用事件记录日志**
   ```solidity
   event Deposit(address indexed user, uint256 amount);

   function deposit(uint256 amount) external {
       emit Deposit(msg.sender, amount);
   }
   ```

---

## 测试网资源

### Sepolia 测试网

- **RPC**: https://rpc.sepolia.org
- **水龙头**: https://sepoliafaucet.com/
- **区块浏览器**: https://sepolia.etherscan.io/

### Goerli 测试网

- **RPC**: https://rpc.ankr.com/eth_goerli
- **水龙头**: https://goerlifaucet.com/
- **区块浏览器**: https://goerli.etherscan.io/

---

## 参考资源

### 官方文档

- [Aave 文档](https://docs.aave.com/)
- [Uniswap 文档](https://docs.uniswap.org/)
- [Compound 文档](https://docs.compound.finance/)

### 合约代码

- [Aave V3 Core](https://github.com/aave/aave-v3-deploy)
- [Uniswap V3 Core](https://github.com/Uniswap/v3-core)
- [Compound Protocol](https://github.com/compound-finance/compound-protocol)

### 开发工具

- [Hardhat](https://hardhat.org/)
- [Ethers.js](https://docs.ethers.org/)
- [OpenZeppelin](https://docs.openzeppelin.com/)

---

## 常见问题

### Q1: 如何选择合适的测试网？

**A**: Sepolia 是目前最活跃的测试网，大多数项目都在上面部署。Goerli 正在逐步淘汰。

### Q2: 部署到主网需要多少 ETH？

**A**: 取决于合约复杂度和网络拥堵情况。通常需要 0.01-0.1 ETH。

### Q3: 如何处理升级？

**A**: 使用代理模式（如 OpenZeppelin 的 `Proxy` 和 `UpgradeableBeacon`）实现合约升级。

### Q4: 如何获取测试网 ETH？

**A**: 使用水龙头或 faucets：
- https://sepoliafaucet.com/
- https://faucet.quicknode.com/

---

**文档版本**: 1.0.0
**最后更新**: 2026-02-09
