# Aave DeFi 协议部署指南

**协议简介**: Aave 是一个去中心化非托管流动性市场协议，用户可以作为存款人或借款人参与。

**官方文档**: https://docs.aave.com/

---

## 目录

1. [环境准备](#环境准备)
2. [部署到测试网](#部署到测试网)
3. [合约验证](#合约验证)
4. [常见问题](#常见问题)

---

## 环境准备

### 前置要求

```bash
# Node.js >= 16
node --version

# Python >= 3.8（用于某些脚本）
python3 --version
```

### 安装依赖

```bash
# 创建项目目录
mkdir aave-deployment && cd aave-deployment

# 初始化项目
npm init -y

# 安装 Hardhat
npm install --save-dev hardhat

# 安装 OpenZeppelin
npm install @openzeppelin/contracts

# 安装 Aave 依赖
npm install @aave/aave-stake-v2
npm install @aave/core-v3

# 安装 dotenv
npm install dotenv
```

### 配置环境变量

创建 `.env` 文件：

```bash
# RPC 端点
SEPOLIA_RPC_URL=https://rpc.sepolia.org
MAINNET_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_ALCHEMY_KEY

# 部署账户私钥（不要提交到 Git）
PRIVATE_KEY=your_private_key_here

# Etherscan API Key（用于验证合约）
ETHERSCAN_API_KEY=your_etherscan_api_key
```

---

## 部署到测试网

### 步骤 1: 初始化 Hardhat 项目

```bash
npx hardhat init
```

选择:
- "Create a TypeScript project"
- "Create a .gitignore"
- "Install this sample project's dependencies with npm"

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

### 步骤 3: 创建 Pool 合约

创建 `contracts/AavePool.sol`:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title AavePool
 * @notice 简化的 Aave Pool 实现
 */
contract AavePool is ERC20, Ownable {
    // 状态变量
    address public aToken;
    uint256 public totalDeposited;
    uint256 public constant RESERVE_FACTOR = 0.1e18; // 10%

    // 事件
    event Deposit(address indexed user, uint256 amount);
    event Withdraw(address indexed user, uint256 amount);
    event Borrow(address indexed user, uint256 amount);

    /**
     * @notice 构造函数
     * @param _name Pool 名称
     * @param _symbol Pool 符号
     */
    constructor(
        string memory _name,
        string memory _symbol,
        address _underlyingAsset
    ) ERC20(_name, _symbol) Ownable(msg.sender) {
        // 在实际部署中，这里会引用 Aave 的 aToken 合约
        aToken = _underlyingAsset;
    }

    /**
     * @notice 存款
     * @param amount 存款金额
     */
    function deposit(uint256 amount) external {
        require(amount > 0, "Amount must be greater than 0");

        // 转入底层资产
        IERC20(aToken).transferFrom(msg.sender, address(this), amount);

        // 铸造 aToken
        _mint(msg.sender, amount);

        totalDeposited += amount;

        emit Deposit(msg.sender, amount);
    }

    /**
     * @notice 取款
     * @param amount 取款金额
     */
    function withdraw(uint256 amount) external {
        require(amount > 0, "Amount must be greater than 0");
        require(balanceOf(msg.sender) >= amount, "Insufficient balance");

        // 销毁 aToken
        _burn(msg.sender, amount);

        // 转出底层资产
        IERC20(aToken).transfer(msg.sender, amount);

        totalDeposited -= amount;

        emit Withdraw(msg.sender, amount);
    }

    /**
     * @notice 获取存款余额
     * @param user 用户地址
     * @return 存款余额
     */
    function getDepositBalance(address user) external view returns (uint256) {
        return balanceOf(user);
    }
}
```

### 步骤 4: 创建部署脚本

创建 `scripts/deploy-aave.ts`:

```typescript
import { ethers } from "hardhat";

async function main() {
  const [deployer] = await ethers.getSigners();

  console.log("Deploying AavePool with account:", deployer.address);
  console.log("Account balance:", (await deployer.provider.getBalance(deployer.address)).toString());

  // 部署 AavePool
  const AavePool = await ethers.getContractFactory("AavePool");
  const aavePool = await AavePool.deploy(
    "Aave Test Pool",
    "aTEST",
    "0x0000000000000000000000000000000000000000" // 替换为实际的底层资产地址
  );

  await aavePool.waitForDeployment();

  console.log("AavePool deployed to:", await aavePool.getAddress());

  // 验证合约
  if (process.env.ETHERSCAN_API_KEY) {
    console.log("Waiting for block confirmations...");
    await aavePool.deploymentTransaction()?.wait(6);

    console.log("Verifying contract on Etherscan...");
    try {
      await hre.run("verify:verify", {
        address: await aavePool.getAddress(),
        constructorArguments: [
          "Aave Test Pool",
          "aTEST",
          "0x0000000000000000000000000000000000000"
        ],
      });
      console.log("Contract verified!");
    } catch (error) {
      console.error("Verification failed:", error);
    }
  }
}

main()
  .then(() => process.exit(0))
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
npx hardhat run scripts/deploy-aave.ts --network sepolia
```

---

## 合约验证

### 自动验证

部署脚本会自动验证合约（如果配置了 `ETHERSCAN_API_KEY`）。

### 手动验证

```bash
npx hardhat verify --network sepolia <CONTRACT_ADDRESS> \
  "Aave Test Pool" \
  "aTEST" \
  "0x0000000000000000000000000000000000000"
```

---

## 常见问题

### Q1: 部署失败提示 "insufficient funds"

**A**: 确保账户有足够的 ETH 支付 Gas 费用。

```bash
# 检查账户余额
cast balance <YOUR_ADDRESS> --rpc-url $SEPOLIA_RPC_URL
```

### Q2: 验证失败

**A**: 确保构造函数参数与部署时完全一致，包括空格和引号。

### Q3: 如何获取测试网 ETH？

**A**: 使用 Sepolia 水龙头:
- https://sepoliafaucet.com/
- https://faucet.quicknode.com/ethereum/sepolia

---

## 参考资源

- [Aave 官方文档](https://docs.aave.com/)
- [Aave V3 合约地址](https://docs.aave.com/developers/deployed-contracts/v3-mainnet)
- [Hardhat 文档](https://hardhat.org/docs)
- [OpenZeppelin 文档](https://docs.openzeppelin.com/)

---

**文档版本**: 1.0.0
**最后更新**: 2026-02-09
