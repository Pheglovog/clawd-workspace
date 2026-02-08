# Uniswap DeFi 协议部署指南

**协议简介**: Uniswap 是去中心化交易协议，也是最大的去中心化交易所（DEX）。

**官方文档**: https://docs.uniswap.org/

---

## 目录

1. [环境准备](#环境准备)
2. [部署 Uniswap V3 Pool](#部署-uniswap-v3-pool)
3. [添加流动性](#添加流动性)
4. [创建 Swap 交易](#创建-swap-交易)
5. [常见问题](#常见问题)

---

## 环境准备

### 前置要求

```bash
# Node.js >= 18
node --version
```

### 安装依赖

```bash
# 创建项目目录
mkdir uniswap-deployment && cd uniswap-deployment

# 初始化项目
npm init -y

# 安装 Hardhat
npm install --save-dev hardhat

# 安装 Uniswap SDK
npm install @uniswap/sdk-core
npm install @uniswap/v3-sdk

# 安装 ethers
npm install ethers

# 安装 dotenv
npm install dotenv
```

### 配置环境变量

创建 `.env` 文件:

```bash
# RPC 端点
SEPOLIA_RPC_URL=https://rpc.sepolia.org
MAINNET_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_ALCHEMY_KEY

# 部署账户私钥
PRIVATE_KEY=your_private_key_here

# Etherscan API Key
ETHERSCAN_API_KEY=your_etherscan_api_key
```

---

## 部署 Uniswap V3 Pool

### 步骤 1: 获取预部署合约地址

在 Sepolia 测试网，以下合约已经预部署:

```typescript
// Uniswap V3 Core
const V3_CORE_ADDRESSES = {
  factory: "0x0227628f3F023bb0B980b67D528571c95c6DaC1",
  router: "0x3bFA4769FB09eefC5a80d6E87c3B9C650f7Ae48",
  nftManager: "0x1238536071E1c677A632429e3655c799b22cDAa",
} as const;
```

### 步骤 2: 创建 Pool 部署脚本

创建 `scripts/create-pool.ts`:

```typescript
import { ethers } from "hardhat";
import { Pool, Position, nearestUsableTick, TICK_SPACINGS, FeeAmount } from "@uniswap/v3-sdk";
import { Token } from "@uniswap/sdk-core";

async function main() {
  const [deployer] = await ethers.getSigners();

  console.log("Creating Uniswap V3 Pool with account:", deployer.address);

  // 定义代币（使用 Sepolia 测试代币）
  const token0 = new Token(
    11155111, // Chain ID (Sepolia)
    "0x779877A7B0D9E8603046B4796AA3C7BC948098F", // WETH 地址
    18,
    "WETH",
    "Wrapped Ether"
  );

  const token1 = new Token(
    11155111,
    "0x5FbDB2315678afecb367f032d93F642f64180aa3", // USDT 地址（示例）
    6,
    "USDT",
    "Tether USD"
  );

  // 获取 Factory 合约
  const factoryAbi = [
    "function createPool(address tokenA, address tokenB, uint24 fee) external returns (address pool)",
  ];

  const factory = new ethers.Contract(
    V3_CORE_ADDRESSES.factory,
    factoryAbi,
    deployer
  );

  // 创建 Pool（3000 = 0.3% 手续费）
  const tx = await factory.createPool(
    token0.address,
    token1.address,
    FeeAmount.MEDIUM // 3000 = 0.3%
  );

  const receipt = await tx.wait();
  console.log("Pool creation transaction:", receipt.hash);

  // 获取 Pool 地址（事件日志）
  const poolCreatedEvent = receipt?.logs.find(
    log => log.topics.includes(ethers.id("PoolCreated(address,address,uint24,int24,uint160)"))
  );

  if (poolCreatedEvent) {
    const poolAddress = ethers.AbiCoder.defaultAbiCoder().decode(
      ["address"],
      poolCreatedEvent.topics[1]
    );
    console.log("Pool created at:", poolAddress);
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
```

### 步骤 3: 部署 Pool

```bash
# 编译（如果需要）
npx hardhat compile

# 部署 Pool
npx hardhat run scripts/create-pool.ts --network sepolia
```

---

## 添加流动性

### 步骤 1: 创建添加流动性脚本

创建 `scripts/add-liquidity.ts`:

```typescript
import { ethers } from "hardhat";
import { Pool, Position, nearestUsableTick, TICK_SPACINGS, FeeAmount } from "@uniswap/v3-sdk";
import { Token } from "@uniswap/sdk-core";

async function main() {
  const [deployer] = await ethers.getSigners();

  // Pool 地址
  const poolAddress = "0xYourPoolAddressHere";

  // Pool ABI
  const poolAbi = [
    "function slot0() external view returns (uint160 sqrtPriceX96, int24 tick, uint16 observationIndex, uint16 observationCardinality, uint16 observationCardinalityNext, uint8 feeProtocol, bool unlocked)",
    "function mint(address recipient, int24 tickLower, int24 tickUpper, uint128 amount, bytes calldata data) external returns (uint256 amount0, uint256 amount1)",
  ];

  const pool = new ethers.Contract(poolAddress, poolAbi, deployer);

  // 获取当前价格和 tick
  const slot0 = await pool.slot0();
  const currentTick = slot0.tick;

  // 计算价格范围（上下 1000 ticks）
  const tickSpacing = TICK_SPACINGS[FeeAmount.MEDIUM];
  const tickLower = nearestUsableTick(currentTick - 1000, tickSpacing);
  const tickUpper = nearestUsableTick(currentTick + 1000, tickSpacing);

  // 计算需要添加的流动性
  const amount0 = ethers.parseEther("0.1"); // 0.1 WETH
  const amount1 = ethers.parseUnits("100", 6); // 100 USDT

  // 添加流动性（需要先授权）
  console.log("Approving tokens...");
  // ... 授权逻辑 ...

  console.log("Adding liquidity...");
  const tx = await pool.mint(
    deployer.address,
    tickLower,
    tickUpper,
    ethers.parseUnits("1000000", 18), // 流动性数量
    "0x"
  );

  const receipt = await tx.wait();
  console.log("Liquidity added:", receipt.hash);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
```

---

## 创建 Swap 交易

### 步骤 1: 创建 Swap 脚本

创建 `scripts/swap.ts`:

```typescript
import { ethers } from "hardhat";
import { Pool, Trade, Route, SwapQuoter, TradeType } from "@uniswap/v3-sdk";
import { Token } from "@uniswap/sdk-core";

async function main() {
  const [deployer] = await ethers.getSigners();

  // Pool 地址
  const poolAddress = "0xYourPoolAddressHere";

  // 定义代币
  const token0 = new Token(11155111, "0x...", 18, "WETH", "Wrapped Ether");
  const token1 = new Token(11155111, "0x...", 6, "USDT", "Tether USD");

  // Router ABI
  const routerAbi = [
    "function exactInputSingle((address tokenIn, address tokenOut, uint24 fee, address recipient, uint256 deadline, uint256 amountIn, uint256 amountOutMinimum, uint160 sqrtPriceLimitX96)) external payable returns (uint256 amountOut)",
  ];

  const router = new ethers.Contract(
    V3_CORE_ADDRESSES.router,
    routerAbi,
    deployer
  );

  // Swap 参数
  const amountIn = ethers.parseEther("0.01"); // 0.01 WETH
  const amountOutMinimum = 0; // 允许滑点
  const deadline = Math.floor(Date.now() / 1000) + 60 * 20; // 20 分钟后过期

  // 执行 Swap
  console.log("Swapping 0.01 WETH for USDT...");
  const tx = await router.exactInputSingle({
    tokenIn: token0.address,
    tokenOut: token1.address,
    fee: FeeAmount.MEDIUM,
    recipient: deployer.address,
    deadline: deadline,
    amountIn: amountIn,
    amountOutMinimum: amountOutMinimum,
    sqrtPriceLimitX96: 0,
  });

  const receipt = await tx.wait();
  console.log("Swap completed:", receipt.hash);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
```

### 步骤 2: 执行 Swap

```bash
npx hardhat run scripts/swap.ts --network sepolia
```

---

## 常见问题

### Q1: 创建 Pool 时提示 "Pool already exists"

**A**: 使用 Uniswap SDK 的 Pool 类连接到现有 Pool，而不是创建新的。

### Q2: 添加流动性失败

**A**: 确保:
1. 已授权 Router 合约使用代币
2. 有足够的代币余额
3. 价格范围合理（包含当前价格）

### Q3: Swap 时滑点太大

**A**:
1. 增加 `amountOutMinimum` 允许的滑点
2. 减少交易金额
3. 在价格波动较小的时段执行

---

## 参考资源

- [Uniswap V3 文档](https://docs.uniswap.org/protocol/introduction)
- [Uniswap SDK](https://github.com/Uniswap/v3-sdk)
- [Uniswap V3 Core 合约](https://github.com/Uniswap/v3-core)
- [Hardhat 文档](https://hardhat.org/docs)

---

**文档版本**: 1.0.0
**最后更新**: 2026-02-09
