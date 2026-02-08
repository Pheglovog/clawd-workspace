# Compound DeFi 协议部署指南

**协议简介**: Compound 是去中心化借贷协议，允许用户存入资产赚取利息或借出资产。

**官方文档**: https://docs.compound.finance/

---

## 目录

1. [环境准备](#环境准备)
2. [部署到测试网](#部署到测试网)
3. [集成 Compound](#集成-compound)
4. [常见问题](#常见问题)

---

## 环境准备

### 前置要求

```bash
# Node.js >= 16
node --version
```

### 安装依赖

```bash
# 创建项目目录
mkdir compound-deployment && cd compound-deployment

# 初始化项目
npm init -y

# 安装 Hardhat
npm install --save-dev hardhat

# 安装 OpenZeppelin
npm install @openzeppelin/contracts

# 安装 Compound 协议
npm install @compound-finance/compound-js

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

## 部署到测试网

### 步骤 1: 初始化 Hardhat 项目

```bash
npx hardhat init
```

### 步骤 2: 配置 Hardhat

编辑 `hardhat.config.ts`:

```typescript
import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";
import * as dotenv from "dotenv";

dotenv.config();

const config: HardhatUserConfig = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200
      }
    }
  },
  networks: {
    sepolia: {
      url: process.env.SEPOLIA_RPC_URL || "https://rpc.sepolia.org",
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
      chainId: 11155111
    }
  },
  etherscan: {
    apiKey: process.env.ETHERSCAN_API_KEY || ""
  }
};

export default config;
```

### 步骤 3: 创建 cToken 合约

创建 `contracts/CToken.sol`:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC4626.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title CToken
 * @notice 简化的 Compound cToken 实现
 */
contract CToken is ERC4626, Ownable {
    // Compound 特定参数
    uint256 public constant INITIAL_EXCHANGE_RATE = 1e18;
    uint256 public constant INITIAL_RATE = 0.02e18; // 2% 年利率
    uint256 public constant SECONDS_PER_YEAR = 31536000;

    // 状态变量
    uint256 public exchangeRate;
    uint256 public borrowRate;
    uint256 public totalBorrows;
    mapping(address => uint256) public borrowBalances;
    uint256 public lastUpdateTime;

    // 事件
    event Borrow(address indexed user, uint256 amount);
    event Repay(address indexed user, uint256 amount);
    event AccrueInterest(uint256 interestAccumulated);

    /**
     * @notice 构造函数
     * @param _name cToken 名称
     * @param _symbol cToken 符号
     * @param _underlying 底层资产地址
     */
    constructor(
        string memory _name,
        string memory _symbol,
        address _underlying
    ) ERC20(_name, _symbol) ERC4626(IERC20(_underlying)) Ownable(msg.sender) {
        exchangeRate = INITIAL_EXCHANGE_RATE;
        borrowRate = INITIAL_RATE;
        lastUpdateTime = block.timestamp;
    }

    /**
     * @notice 存款
     * @param assets 存款金额
     * @return shares 铸造的 cToken 数量
     */
    function deposit(uint256 assets, address receiver) public override returns (uint256) {
        require(assets > 0, "Assets must be greater than 0");

        // 先计息
        accrueInterest();

        // 计算应铸造的 shares
        uint256 shares = previewDeposit(assets);

        // 转入资产
        IERC20(asset()).transferFrom(msg.sender, address(this), assets);

        // 铸造 shares
        _mint(receiver, shares);

        return shares;
    }

    /**
     * @notice 取款
     * @param shares 取出的 shares 数量
     * @return assets 取出的资产数量
     */
    function withdraw(uint256 shares, address receiver, address owner) public override returns (uint256) {
        require(shares > 0, "Shares must be greater than 0");

        // 先计息
        accrueInterest();

        // 计算应取出的资产
        uint256 assets = previewRedeem(shares);

        // 销毁 shares
        _burn(owner, shares);

        // 转出资产
        IERC20(asset()).transfer(receiver, assets);

        return assets;
    }

    /**
     * @notice 借款
     * @param amount 借款金额
     */
    function borrow(uint256 amount) external {
        require(amount > 0, "Amount must be greater than 0");

        // 先计息
        accrueInterest();

        // 计算借款能力
        uint256 borrowCapacity = totalAssets() - totalBorrows;
        require(amount <= borrowCapacity, "Insufficient liquidity");

        // 转出资产
        IERC20(asset()).transfer(msg.sender, amount);

        // 更新借款余额
        borrowBalances[msg.sender] += amount;
        totalBorrows += amount;

        emit Borrow(msg.sender, amount);
    }

    /**
     * @notice 还款
     * @param amount 还款金额
     */
    function repay(uint256 amount) external {
        require(amount > 0, "Amount must be greater than 0");

        // 先计息
        accrueInterest();

        require(borrowBalances[msg.sender] >= amount, "Repay amount exceeds borrow balance");

        // 转入资产
        IERC20(asset()).transferFrom(msg.sender, address(this), amount);

        // 更新借款余额
        borrowBalances[msg.sender] -= amount;
        totalBorrows -= amount;

        emit Repay(msg.sender, amount);
    }

    /**
     * @notice 计息
     */
    function accrueInterest() public {
        uint256 timeElapsed = block.timestamp - lastUpdateTime;
        if (timeElapsed > 0) {
            uint256 interestAccumulated = (totalBorrows * borrowRate * timeElapsed) /
                (SECONDS_PER_YEAR * 1e18);
            if (interestAccumulated > 0) {
                exchangeRate += (interestAccumulated * 1e18) / totalSupply();
                emit AccrueInterest(interestAccumulated);
            }
            lastUpdateTime = block.timestamp;
        }
    }

    /**
     * @notice 预览存款
     * @param assets 存款金额
     * @return shares 应铸造的 shares 数量
     */
    function previewDeposit(uint256 assets) public view override returns (uint256) {
        return (assets * 1e18) / exchangeRate;
    }

    /**
     * @notice 预览取款
     * @param shares 取出的 shares 数量
     * @return assets 应取出的资产数量
     */
    function previewRedeem(uint256 shares) public view override returns (uint256) {
        return (shares * exchangeRate) / 1e18;
    }

    /**
     * @notice 获取汇率
     * @return 当前汇率
     */
    function exchangeRateCurrent() external returns (uint256) {
        accrueInterest();
        return exchangeRate;
    }

    /**
     * @notice 获取借款余额
     * @param account 账户地址
     * @return 借款余额
     */
    function borrowBalanceCurrent(address account) external returns (uint256) {
        accrueInterest();
        return borrowBalances[account];
    }

    /**
     * @notice 设置借款利率
     * @param _rate 新利率
     */
    function setBorrowRate(uint256 _rate) external onlyOwner {
        require(_rate > 0, "Rate must be greater than 0");
        borrowRate = _rate;
    }
}
```

### 步骤 4: 创建部署脚本

创建 `scripts/deploy-compound.ts`:

```typescript
import { ethers } from "hardhat";

async function main() {
  const [deployer] = await ethers.getSigners();

  console.log("Deploying CToken with account:", deployer.address);
  console.log("Account balance:", (await deployer.provider.getBalance(deployer.address)).toString());

  // 部署 CToken（使用 Sepolia WETH 作为底层资产）
  const CToken = await ethers.getContractFactory("CToken");
  const cToken = await CToken.deploy(
    "Compound WETH",
    "cWETH",
    "0x779877A7B0D9E8603046B4796AA3C7BC948098F" // Sepolia WETH 地址
  );

  await cToken.waitForDeployment();

  const cTokenAddress = await cToken.getAddress();
  console.log("CToken deployed to:", cTokenAddress);

  // 验证合约
  if (process.env.ETHERSCAN_API_KEY) {
    console.log("Waiting for block confirmations...");
    await cToken.deploymentTransaction()?.wait(6);

    console.log("Verifying contract on Etherscan...");
    try {
      await hre.run("verify:verify", {
        address: cTokenAddress,
        constructorArguments: [
          "Compound WETH",
          "cWETH",
          "0x779877A7B0D9E8603046B4796AA3C7BC948098F"
        ],
      });
      console.log("Contract verified!");
    } catch (error) {
      console.error("Verification failed:", error);
    }
  }

  return cTokenAddress;
}

main()
  .then((address) => {
    console.log("Deployment completed!");
    console.log("CToken address:", address);
    process.exit(0);
  })
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
```

### 步骤 5: 部署合约

```bash
# 编译合约
npx hardhat compile

# 部署到 Sepolia 测试网
npx hardhat run scripts/deploy-compound.ts --network sepolia
```

---

## 集成 Compound

### 使用已部署的 Compound 合约

Sepolia 测试网上的 Compound 合约地址（示例）:

```typescript
const COMPOUND_COMPTROLLER = "0x...";
const COMPOUND_CETH = "0x...";
const COMPOUND_CUSDC = "0x...";
```

### 与 Compound 交互

创建 `scripts/interact-compound.ts`:

```typescript
import { ethers } from "hardhat";

async function main() {
  const [deployer] = await ethers.getSigners();

  // CToken ABI（简化）
  const cTokenAbi = [
    "function mint(uint256 mintAmount) external returns (uint256)",
    "function redeem(uint256 redeemTokens) external returns (uint256)",
    "function borrow(uint256 borrowAmount) external returns (uint256)",
    "function repayBorrow(uint256 repayAmount) external",
    "function exchangeRateCurrent() external returns (uint256)",
    "function balanceOf(address owner) external view returns (uint256)",
  ];

  // 连接到已部署的 CToken
  const cTokenAddress = "0xYourCTokenAddressHere";
  const cToken = new ethers.Contract(cTokenAddress, cTokenAbi, deployer);

  // 存款
  const depositAmount = ethers.parseEther("1.0"); // 1 ETH
  console.log("Depositing 1.0 ETH...");

  // 先授权
  const wethAddress = "0x779877A7B0D9E8603046B4796AA3C7BC948098F";
  const wethAbi = ["function approve(address spender, uint256 amount) external"];
  const weth = new ethers.Contract(wethAddress, wethAbi, deployer);
  await weth.approve(cTokenAddress, depositAmount);

  // 存款
  await cToken.mint(depositAmount);
  console.log("Deposit completed!");

  // 查询余额
  const cTokenBalance = await cToken.balanceOf(deployer.address);
  const exchangeRate = await cToken.exchangeRateCurrent();
  console.log("cToken balance:", cTokenBalance.toString());
  console.log("Exchange rate:", exchangeRate.toString());
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
}
```

---

## 常见问题

### Q1: 部署时提示 "insufficient funds"

**A**: 确保账户有足够的 ETH 支付 Gas 费用。

### Q2: 存款失败

**A**: 确保:
1. 已授权 CToken 合约使用底层资产
2. 有足够的底层资产余额

### Q3: 借款失败

**A**: 检查:
1. Pool 中是否有足够的流动性
2. 借款金额是否超过借款能力

---

## 参考资源

- [Compound 文档](https://docs.compound.finance/)
- [Compound 协议](https://github.com/compound-finance/compound-protocol)
- [ERC4626 标准](https://eips.ethereum.org/EIPS/eip-4626)
- [Hardhat 文档](https://hardhat.org/docs)

---

**文档版本**: 1.0.0
**最后更新**: 2026-02-09
