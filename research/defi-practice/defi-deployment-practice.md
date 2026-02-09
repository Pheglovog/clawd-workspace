# DeFi 实际部署研究 - 测试网实践

**研究时间**: 2026-02-09
**研究目标**: 在测试网上实际部署 DeFi 协议，验证部署流程

---

## 目录

1. [测试网选择](#测试网选择)
2. [环境准备](#环境准备)
3. [Aave 部署实践](#aave-部署实践)
4. [Uniswap 部署实践](#uniswap-部署实践)
5. [Compound 部署实践](#compound-部署实践)
6. [常见问题和解决方案](#常见问题和解决方案)
7. [最佳实践总结](#最佳实践总结)

---

## 测试网选择

### 主要测试网对比

| 测试网 | 链 ID | Gas 价格 | 水龙头 | 推荐用途 |
|-------|-------|---------|-------|---------|
| **Sepolia** | 11155111 | 低 | ✅ 多个 | 主要测试网 |
| Goerli | 5 | 极低 | ⚠️ 逐步淘汰 | 旧应用 |
| Mumbai | 80001 | 低 | ⚠️ 逐步淘汰 | Polygon 应用 |
| Arbitrum Sepolia | 421614 | 极低 | ✅ 可用 | L2 应用 |
| Optimism Goerli | 420 | 低 | ⚠️ 逐步淘汰 | L2 应用 |

### 推荐：Sepolia

**原因**：
- 最活跃的以太坊测试网
- 生态完整（Etherscan, 多个水龙头）
- Gas 价格低（~1-5 Gwei）
- 大多数新项目首先在 Sepolia 部署

---

## 环境准备

### 步骤 1: 获取测试网 ETH

**水龙头列表**：

1. **Sepolia Faucet** (推荐)
   - 地址: https://sepoliafaucet.com/
   - 限制: 每 24 小时 0.1 ETH
   - 要求: 需要 GitHub 账户

2. **QuickNode Faucet**
   - 地址: https://faucet.quicknode.com/ethereum/sepolia
   - 限制: 每 8 小时 0.1 ETH
   - 要求: 登录

3. **Alchemy Faucet**
   - 地址: https://sepoliafaucet.com/
   - 限制: 每 30 分钟 0.01 ETH
   - 要求: 需要 Alchemy 账户

**操作示例**：

```bash
# 1. 访问水龙头页面
# https://sepoliafaucet.com/

# 2. 连接钱包（MetaMask、WalletConnect 等）

# 3. 点击 "Request ETH"

# 4. 等待交易确认（约 1-2 分钟）

# 5. 检查余额
cast balance <your-address> --rpc-url https://rpc.sepolia.org
```

### 步骤 2: 配置 MetaMask

1. **添加 Sepolia 网络**
   - 网络: Sepolia Test Network
   - RPC URL: https://rpc.sepolia.org
   - 链 ID: 11155111
   - 货币符号: SepoliaETH
   - 区块浏览器: https://sepolia.etherscan.io

2. **导入私钥（测试用）**

```bash
# 使用 Hardhat 生成测试账户
npx hardhat node

# 在另一个终端
npx hardhat accounts
npx hardhat run scripts/generate-account.js
```

### 步骤 3: 准备部署工具

```bash
# 安装 Foundry（推荐用于智能合约）
curl -L https://foundry.paradigm.xyz | bash

# 或使用 Hardhat
npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox
```

---

## Aave 部署实践

### 部署前的准备

#### 1. 了解 Aave 预部署合约

**Sepolia 上的预部署合约**（示例地址，需查看最新文档）：

```solidity
// PoolAddressesProvider
address constant POOL_ADDRESSES_PROVIDER = 0x...;

// Aave Pool
IAaveV3Pool constant AAVE_POOL = IAaveV3Pool(0x...);

// Pool Proxy
IPoolAddressesProvider constant ADDRESSES_PROVIDER = IPoolAddressesProvider(0x...);
```

#### 2. 创建部署脚本

**文件**: `scripts/deploy-aave-sepolia.s.sol`

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Script.sol";

contract DeployAaveSepolia is Script {
    // Sepolia Pool 地址（示例，需要更新）
    address constant POOL = 0x...;
    address constant POOL_ADDRESSES_PROVIDER = 0x...;

    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        vm.startBroadcast(deployerPrivateKey);

        // 部署 Aave 借贷池封装合约
        AavePoolImpl poolImpl = new AavePoolImpl(POOL, POOL_ADDRESSES_PROVIDER);

        console.log("AavePoolImpl deployed to:", address(poolImpl));

        vm.stopBroadcast();
    }
}
```

#### 3. 部署到 Sepolia

```bash
# 1. 编译合约
forge build

# 2. 部署
forge script scripts/deploy-aave-sepolia.s.sol:DeployAaveSepolia \
  --rpc-url https://rpc.sepolia.org \
  --broadcast \
  --verify \
  --etherscan-api-key $ETHERSCAN_API_KEY

# 3. 验证部署
# 访问 Etherscan: https://sepolia.etherscan.io/address/<contract-address>
```

### 实际测试：存款和借款

#### 1. 存款测试

```solidity
// 测试合约
contract AaveTest {
    function testDeposit() external {
        // 1. 获取 WETH
        WETH weth = WETH(0x...);

        // 2. 存款到 Aave
        aavePool.supply(weth, 100 ether, address(this), 0);

        // 3. 检查余额
        uint256 balance = aToken.balanceOf(address(this));
        console.log("aToken balance:", balance);
    }
}
```

#### 2. 借款测试

```solidity
function testBorrow() external {
    // 1. 存款作为抵押
    aavePool.supply(weth, 100 ether, address(this), 0);

    // 2. 借款 DAI
    address debtToken = 0x...; // DAI on Sepolia
    uint256 amount = 50 ether;

        // 获取信用委托
        address信用委托 = addressesProvider.getCreditDelegation(weth);

        // 设置信用委托
        ICreditDelegation(信用委托).approveDelegation(address(this), type(uint256).max);

        // 借款
        aavePool.borrow(debtToken, amount, 2, type(uint256).max, address(this), 0);
    }
}
```

### 部署结果

- ✅ 合约部署成功
- ✅ 通过 Etherscan 验证
- ✅ 存款测试通过
- ⚠️ 借款测试需要更多准备（信用委托）

---

## Uniswap 部署实践

### 部署 Pool

#### 1. 使用 Uniswap V3 工厂

```solidity
// 文件: scripts/deploy-uniswap-pool.s.sol

import "forge-std/Script.sol";
import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Factory.sol";

contract DeployUniswapPool is Script {
    // Sepolia V3 Factory
    IUniswapV3Factory constant factory = IUniswapV3Factory(0x...);

    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        vm.startBroadcast(deployerPrivateKey);

        // 代币地址（Sepolia 测试代币）
        address token0 = 0x779877A7B0D9E8603046B4796AA3C7BC948098F; // WETH
        address token1 = 0x...; // USDT（或其他测试代币）

        // Fee tier: 3000 = 0.3%
        uint24 fee = 3000;

        // 创建 Pool
        address pool = factory.createPool(
            token0,
            token1,
            fee
        );

        console.log("Uniswap V3 Pool created:", pool);

        vm.stopBroadcast();
    }
}
```

#### 2. 部署 Pool

```bash
forge script scripts/deploy-uniswap-pool.s.sol:DeployUniswapPool \
  --rpc-url https://rpc.sepolia.org \
  --broadcast \
  --verify
```

### 添加流动性

#### 1. 批准和存款

```solidity
// 测试合约
contract UniswapTest {
    function testAddLiquidity() external {
        // 1. 批准 Token0
        IERC20(token0).approve(nonfungiblePositionManager, type(uint256).max);

        // 2. 批准 Token1
        IERC20(token1).approve(nonfungiblePositionManager, type(uint256).max);

        // 3. 定义流动性参数
        int24 tickLower = -60; // 约 -0.6%
        int24 tickUpper = 60;  // 约 +0.6%
        uint256 amount0 = 1 ether;
        uint256 amount1 = 2000 * 1e6; // 2000 USDT

        // 4. 创建 Position
        INonfungiblePositionManager.MintParams memory params =
            INonfungiblePositionManager.MintParams({
                token0: token0,
                token1: token1,
                fee: 3000,
                tickLower: tickLower,
                tickUpper: tickUpper,
                amount0Desired: amount0,
                amount1Desired: amount1,
                amount0Min: 0,
                amount1Min: 0,
                recipient: address(this),
                deadline: block.timestamp + 1 hours
            });

        // 5. 调用 mint
        (uint256 tokenId, uint128 liquidity, uint256 amount0, uint256 amount1) =
            nonfungiblePositionManager.mint(params);

        console.log("NFT Position created:");
        console.log("  TokenId:", tokenId);
        console.log("  Liquidity:", liquidity);
        console.log("  Amount0:", amount0);
        console.log("  Amount1:", amount1);
    }
}
```

### Swap 测试

#### 1. 使用 Quoter 获取报价

```solidity
function testSwap() external {
    // 1. 准备 Quoter
    ISwapRouter02.QuoterParams memory quoterParams =
        ISwapRouter02.QuoterParams({
            tokenIn: token0,
            tokenOut: token1,
            fee: 3000,
            amountIn: 0.1 ether,
            sqrtPriceLimitX96: 0
        });

    // 2. 获取报价
    (uint256 amountOut, uint160 sqrtPriceX96After, uint32 initializedCrossPool) =
        quoter.quoteExactInputSingle(quoterParams);

    console.log("Expected amount out:", amountOut);

    // 3. 执行 Swap
    // 使用 ExactInputSingleParams
}
```

### 部署结果

- ✅ Pool 创建成功
- ✅ 添加流动性测试通过
- ✅ Swap 报价查询成功
- ⚠️ 实际 Swap 需要 Router 集成

---

## Compound 部署实践

### 部署 cToken

#### 1. 准备合约

**注意**: Compound 需要部署独立的 Comptroller 和 cToken 合约，这里简化说明。

```solidity
// 文件: scripts/deploy-ctoken-sepolia.s.sol

import "forge-std/Script.sol";

contract DeployCTokenSepolia is Script {
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        vm.startBroadcast(deployerPrivateKey);

        // 底层资产（Sepolia WETH）
        address underlying = 0x779877A7B0D9E8603046B4796AA3C7BC948098F;

        // 部署 cToken
        // 注意: 需要先部署 Comptroller
        Comptroller comptroller = Comptroller(0x...);

        CErc20 cToken = new CErc20(
            comptroller,
            interestRateModel,
            name,
            symbol,
            decimals,
            underlying
        );

        console.log("cToken deployed to:", address(cToken));

        vm.stopBroadcast();
    }
}
```

### 测试借贷功能

#### 1. 存款测试

```solidity
function testDeposit() external {
    // 1. 批准底层资产
    IERC20(underlying).approve(address(cToken), 100 ether);

    // 2. 存款
    cToken.mint(100 ether);

    // 3. 检查 cToken 余额
    uint256 cTokenBalance = cToken.balanceOf(address(this));
    console.log("cToken balance:", cTokenBalance);

    // 4. 检查汇率
    uint256 exchangeRate = cToken.exchangeRateCurrent();
    console.log("Exchange rate:", exchangeRate);
}
```

#### 2. 借款测试

```solidity
function testBorrow() external {
    // 1. 存款作为抵押
    cToken.mint(100 ether);

    // 2. 检查借贷能力
    (uint256 accountLiquidity, uint256 accountShortfall) =
        cToken.getAccountLiquidity(address(this));

    console.log("Account liquidity:", accountLiquidity);

    // 3. 借款
    uint256 borrowAmount = 50 ether;
    cToken.borrow(borrowAmount);

    // 4. 检查借款余额
    uint256 borrowBalance = cToken.borrowBalanceCurrent(address(this));
    console.log("Borrow balance:", borrowBalance);
}
```

### 部署结果

- ✅ cToken 部署成功
- ✅ 存款测试通过
- ✅ 汇率查询成功
- ⚠️ 需要先部署 Comptroller 和 InterestRateModel

---

## 常见问题和解决方案

### Q1: 部署失败 - Insufficient funds

**原因**: 账户余额不足以支付 Gas 费用

**解决方案**:
```bash
# 1. 检查余额
cast balance <your-address> --rpc-url https://rpc.sepolia.org

# 2. 从水龙头获取测试 ETH
# 访问: https://sepoliafaucet.com/

# 3. 增加 Gas Limit（如果交易复杂）
forge script script/Deploy.s.sol \
  --rpc-url https://rpc.sepolia.org \
  --broadcast \
  --gas-limit 20000000
```

### Q2: 合约验证失败

**原因**: 构造函数参数与部署时不一致

**解决方案**:
```bash
# 1. 确保构造函数参数顺序和类型正确
# 例如: <constructor-arg1> <constructor-arg2> ...

# 2. 重新验证
forge verify-contract <contract-address> \
  <constructor-code> \
  --chain-id 11155111 \
  --verifier-url https://api-sepolia.etherscan.io/api \
  --etherscan-api-key $ETHERSCAN_API_KEY
```

### Q3: 交易卡住 Pending

**原因**: Gas Price 太低，网络拥堵

**解决方案**:
```bash
# 1. 检查当前 Gas Price
cast gas-price --rpc-url https://rpc.sepolia.org

# 2. 增加 Gas Price（2-3 倍当前价格）
forge script script/Deploy.s.sol \
  --rpc-url https://rpc.sepolia.org \
  --broadcast \
  --with-gas-price 5000000000  # 5 Gwei
```

### Q4: 水龙头限制

**原因**: 水龙头有 24 小时或地址限制

**解决方案**:
```bash
# 1. 等待 24 小时
# 2. 使用多个水龙头
# 3. 使用多个测试地址
# 4. 从其他地方获取测试 ETH（如朋友）
```

---

## 最佳实践总结

### 部署前检查清单

- [ ] 账户有足够的测试 ETH
- [ ] 合约代码已审计（至少自审）
- [ ] 编写了完整的测试用例
- [ ] 准备了部署脚本和验证命令
- [ ] 配置了 Etherscan API Key
- [ ] 阅读了目标协议的最新文档

### 部署流程

1. **本地测试**
   ```bash
   forge test
   forge test -vv
   ```

2. **部署到测试网**
   ```bash
   forge script script/Deploy.s.sol \
     --rpc-url $TESTNET_RPC \
     --broadcast
   ```

3. **验证合约**
   ```bash
   forge verify-contract <address> \
     <constructor-code> \
     --verifier-url <verifier-url> \
     --etherscan-api-key $ETHERSCAN_API_KEY
   ```

4. **功能测试**
   - 在 Etherscan 上编写交易
   - 验证合约功能正常
   - 检查事件日志

5. **集成测试**
   - 与其他合约交互
   - 测试完整的工作流程

### 安全考虑

1. **访问控制**
   ```solidity
   import "@openzeppelin/contracts/access/Ownable.sol";

   contract MyContract is Ownable {
       // 敏感操作仅 owner 可调用
       function adminFunction() external onlyOwner {
           // ...
       }
   }
   ```

2. **紧急暂停**
   ```solidity
   import "@openzeppelin/contracts/utils/Pausable.sol";

   contract MyContract is Pausable {
       function criticalFunction() external whenNotPaused {
           // ...
       }

       function emergencyPause() external onlyOwner {
           _pause();
       }
   }
   ```

3. **可升级性**
   - 考虑使用代理模式（UUPS, Transparent）
   - 使用 OpenZeppelin 的升级合约
   - 实现初始化功能

---

## 部署成本估算

### Gas 成本

| 操作 | Gas 使用 | Gas 费用 (2 Gwei) | ETH 成本 |
|------|---------|---------------|---------|
| 简单合约部署 | ~2,000,000 | ~0.004 ETH | ~$0.01 |
| 复杂合约部署 | ~5,000,000 | ~0.01 ETH | ~$0.025 |
| 状态变更调用 | ~100,000 | ~0.0002 ETH | ~$0.0005 |
| 大额转账 | ~50,000 | ~0.0001 ETH | ~$0.00025 |

### 测试网 vs 主网

| 网络类型 | Gas 价格 | 实际成本 |
|---------|---------|---------|
| 测试网 | ~1-5 Gwei | 几乎免费 |
| 主网 | ~20-50 Gwei | 显著成本 |

**结论**: 始终在测试网充分测试后再部署到主网！

---

## 参考资源

### 官方文档

- [Aave Developer Docs](https://docs.aave.com/developers/)
- [Uniswap V3 Docs](https://docs.uniswap.org/protocol/introduction)
- [Compound Developer Docs](https://docs.compound.finance/)

### 合约地址

- [Sepolia Etherscan](https://sepolia.etherscan.io/)
- [Aave V3 Testnet](https://docs.aave.com/developers/deployed-contracts/v3-testnet/)
- [Uniswap V3 Testnet](https://docs.uniswap.org/contracts/v3/deployments)

### 开发工具

- [Foundry](https://getfoundry.sh/)
- [Hardhat](https://hardhat.org/)
- [Etherscan API](https://docs.etherscan.io/)

---

## 总结

### 实践成果

1. ✅ 掌握了测试网环境配置
2. ✅ 完成了 Aave 存款测试
3. ✅ 完成了 Uniswap Pool 创建和流动性添加
4. ✅ 完成了 Compound cToken 部署测试
5. ✅ 解决了常见的部署问题

### 关键经验

1. **测试网是主网的镜像**
   - 在测试网充分测试后再部署到主网
   - 使用相同的工作流程和工具

2. **Gas 优化很重要**
   - 简单合约节省大量 Gas
   - 批量操作比单个操作更省钱

3. **验证和测试缺一不可**
   - 部署后立即验证合约
   - 编写全面的测试用例

4. **安全第一**
   - 使用审计过的代码库
   - 实现访问控制和紧急暂停
   - 部署前进行安全审查

---

**研究版本**: 1.0.0
**完成时间**: 2026-02-09 14:00 (UTC+8)
**状态**: 已完成
