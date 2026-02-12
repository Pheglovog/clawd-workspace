# DeFi 协议部署指南

**作者**: 上等兵•甘
**日期**: 2026-02-11
**版本**: 1.0.0

---

## 目录

1. [环境准备](#环境准备)
2. [Aave 部署](#aave-部署)
3. [Uniswap V2 部署](#uniswap-v2-部署)
4. [Uniswap V3 部署](#uniswap-v3-部署)
5. [Compound 部署](#compound-部署)
6. [最佳实践](#最佳实践)
7. [故障排除](#故障排除)

---

## 环境准备

### 1. 安装开发工具

```bash
# 安装 Node.js 和 npm (如果尚未安装)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# 验证安装
node --version  # 应显示 v20.x.x
npm --version   # 应显示 10.x.x
```

### 2. 安装 Hardhat

```bash
npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox

# 初始化 Hardhat 项目
npx hardhat init
# 选择 "Create a JavaScript project"
```

### 3. 安装常用依赖

```bash
npm install @openzeppelin/contracts
npm install @aave/core-v3
npm install @uniswap/v2-core
npm install @uniswap/v3-core
npm install @compound-finance/compound-protocol
npm install dotenv
npm install ethers
```

### 4. 配置环境变量

创建 `.env` 文件：

```env
# 私钥（谨慎保管！）
PRIVATE_KEY=your_private_key_here

# RPC 端点（以太坊主网或测试网）
RPC_URL=https://eth-mainnet.g.alchemy.com/v2/your_api_key

# Etherscan API 密钥（用于合约验证）
ETHERSCAN_API_KEY=your_etherscan_api_key

# 测试网 RPC（Sepolia）
SEPOLIA_RPC_URL=https://eth-sepolia.g.alchemy.com/v2/your_api_key
```

**⚠️ 重要提示**: 永远不要提交 `.env` 文件到 Git！

### 5. 配置 Hardhat

更新 `hardhat.config.js`:

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
    hardhat: {
      chainId: 31337,
    },
    sepolia: {
      url: process.env.SEPOLIA_RPC_URL,
      accounts: [process.env.PRIVATE_KEY],
      chainId: 11155111,
    },
    mainnet: {
      url: process.env.RPC_URL,
      accounts: [process.env.PRIVATE_KEY],
      chainId: 1,
    },
  },
  etherscan: {
    apiKey: process.env.ETHERSCAN_API_KEY,
  },
  paths: {
    sources: "./contracts",
    tests: "./test",
    cache: "./cache",
    artifacts: "./artifacts",
  },
};
```

---

## Aave 部署

### 概述

Aave 是一个去中心化借贷协议，支持多种加密资产的借贷和存款。

### 部署步骤

#### 1. 创建 Aave 集成合约

创建 `contracts/AaveIntegration.sol`:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@aave/core-v3/contracts/flashloan/base/FlashLoanSimpleReceiverBase.sol";
import "@aave/core-v3/contracts/interfaces/IPoolAddressesProvider.sol";

/**
 * @title AaveIntegration
 * @notice Aave 协议集成示例合约
 * @dev 实现闪电贷功能
 */
contract AaveIntegration is FlashLoanSimpleReceiverBase {
    address public owner;

    event FlashLoanReceived(
        address indexed asset,
        uint256 amount,
        uint256 premium,
        address indexed initiator
    );

    constructor(address _addressProvider)
        FlashLoanSimpleReceiverBase(IPoolAddressesProvider(_addressProvider))
    {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    /**
     * @notice 请求闪电贷
     * @param asset 借贷资产地址
     * @param amount 借贷金额
     */
    function requestFlashLoan(address asset, uint256 amount)
        external
        onlyOwner
    {
        POOL.flashLoanSimple(
            address(this),
            asset,
            amount,
            "", // params
            0    // referral code
        );
    }

    /**
     * @notice 闪电贷回调函数
     * @dev Aave 闪电贷收到后调用此函数执行业务逻辑
     */
    function executeOperation(
        address asset,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata params
    )
        external
        override
        returns (bool)
    {
        require(msg.sender == address(POOL), "Invalid caller");
        require(initiator == address(this), "Invalid initiator");

        // 计算需要偿还的总金额（本金 + 手续费）
        uint256 amountOwed = amount + premium;

        // 这里执行业务逻辑
        // 例如：套利交易、资金池再平衡等

        // 确保有足够的资产偿还
        require(
            IERC20(asset).balanceOf(address(this)) >= amountOwed,
            "Insufficient balance to repay"
        );

        emit FlashLoanReceived(asset, amount, premium, initiator);

        return true;
    }

    /**
     * @notice 提取合约资金
     */
    function withdraw(address asset, uint256 amount)
        external
        onlyOwner
    {
        IERC20(asset).transfer(msg.sender, amount);
    }

    /**
     * @notice 接收 ETH
     */
    receive() external payable {}
}
```

#### 2. 创建部署脚本

创建 `scripts/deployAave.js`:

```javascript
const hre = require("hardhat");

async function main() {
  console.log("Deploying Aave Integration...");

  // Aave PoolAddressesProvider 地址（Sepolia 测试网）
  const addressProvider = "0x012bAC54348C0E635dCAc9D5FB99f06F24136C9A";

  const AaveIntegration = await hre.ethers.getContractFactory(
    "AaveIntegration"
  );
  const aaveIntegration = await AaveIntegration.deploy(addressProvider);

  await aaveIntegration.waitForDeployment();
  const address = await aaveIntegration.getAddress();

  console.log(`AaveIntegration deployed to: ${address}`);

  // 验证合约（可选）
  if (hre.network.name !== "hardhat" && hre.network.name !== "localhost") {
    console.log("Waiting for block confirmations...");
    await aaveIntegration.deploymentTransaction().wait(6);

    console.log("Verifying contract...");
    await hre.run("verify:verify", {
      address: address,
      constructorArguments: [addressProvider],
    });
  }

  return address;
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
```

#### 3. 部署到测试网

```bash
# 部署到 Sepolia 测试网
npx hardhat run scripts/deployAave.js --network sepolia
```

#### 4. 创建测试用例

创建 `test/AaveIntegration.test.js`:

```javascript
const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("AaveIntegration", function () {
  let aaveIntegration;
  let owner;
  let dai;
  let daiAddress;

  beforeEach(async function () {
    [owner] = await ethers.getSigners();

    // Aave PoolAddressesProvider (Sepolia)
    const addressProvider =
      "0x012bAC54348C0E635dCAc9D5FB99f06F24136C9A";

    // 部署合约
    const AaveIntegration = await ethers.getContractFactory(
      "AaveIntegration"
    );
    aaveIntegration = await AaveIntegration.deploy(addressProvider);
    await aaveIntegration.waitForDeployment();

    // DAI 地址 (Sepolia)
    daiAddress = "0xff795577d9ac8bd7d90ee22b6c1703490b6512fd";
    dai = await ethers.getContractAt("IERC20", daiAddress);
  });

  describe("Deployment", function () {
    it("Should set the right owner", async function () {
      expect(await aaveIntegration.owner()).to.equal(owner.address);
    });

    it("Should have the correct address provider", async function () {
      expect(await aaveIntegration.ADDRESSES_PROVIDER()).to.not.equal(
        ethers.ZeroAddress
      );
    });
  });

  describe("Flash Loan", function () {
    it("Should fail to request flash loan from non-owner", async function () {
      const [_, attacker] = await ethers.getSigners();
      await expect(
        aaveIntegration.connect(attacker).requestFlashLoan(daiAddress, 1000)
      ).to.be.revertedWith("Not owner");
    });
  });

  describe("Withdraw", function () {
    it("Should withdraw tokens from owner", async function () {
      // 转移一些 DAI 到合约
      const amount = ethers.parseEther("1");

      // 注意：测试时需要先铸造或转移 DAI 给合约
      // 这里仅演示测试结构

      await expect(
        aaveIntegration.withdraw(daiAddress, amount)
      ).not.to.be.reverted;
    });

    it("Should fail to withdraw from non-owner", async function () {
      const [_, attacker] = await ethers.getSigners();
      await expect(
        aaveIntegration.connect(attacker).withdraw(daiAddress, 1000)
      ).to.be.revertedWith("Not owner");
    });
  });
});
```

#### 5. 运行测试

```bash
npx hardhat test
```

---

## Uniswap V2 部署

### 概述

Uniswap V2 是一个去中心化交易协议，使用自动做市商（AMM）模型。

### 部署步骤

#### 1. 创建 Uniswap V2 集成合约

创建 `contracts/UniswapV2Integration.sol`:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@uniswap/v2-core/contracts/interfaces/IUniswapV2Factory.sol";
import "@uniswap/v2-core/contracts/interfaces/IUniswapV2Router02.sol";
import "@uniswap/v2-periphery/contracts/interfaces/IWETH.sol";

/**
 * @title UniswapV2Integration
 * @notice Uniswap V2 协议集成示例合约
 * @dev 实现代币交换和流动性添加功能
 */
contract UniswapV2Integration {
    IUniswapV2Factory public factory;
    IUniswapV2Router02 public router;
    IWETH public weth;

    address public owner;

    event Swapped(
        address indexed tokenIn,
        address indexed tokenOut,
        uint256 amountIn,
        uint256 amountOut,
        address indexed recipient
    );

    event LiquidityAdded(
        address indexed tokenA,
        address indexed tokenB,
        uint256 amountA,
        uint256 amountB,
        uint256 liquidity
    );

    constructor(address _router, address _weth) {
        router = IUniswapV2Router02(_router);
        factory = IUniswapV2Factory(router.factory());
        weth = IWETH(_weth);
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    /**
     * @notice 交换代币
     * @param tokenIn 输入代币地址
     * @param tokenOut 输出代币地址
     * @param amountIn 输入金额
     * @param amountOutMin 最小输出金额（滑点保护）
     * @param recipient 接收地址
     */
    function swapTokens(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 amountOutMin,
        address recipient
    )
        external
        onlyOwner
        returns (uint256 amountOut)
    {
        // 批准路由器使用代币
        IERC20(tokenIn).approve(address(router), amountIn);

        // 定义路径
        address[] memory path;
        if (tokenIn == address(weth) || tokenOut == address(weth)) {
            path = new address[](2);
            path[0] = tokenIn;
            path[1] = tokenOut;
        } else {
            path = new address[](3);
            path[0] = tokenIn;
            path[1] = address(weth);
            path[2] = tokenOut;
        }

        // 执行交换
        uint256[] memory amounts = router.swapExactTokensForTokens(
            amountIn,
            amountOutMin,
            path,
            recipient,
            block.timestamp + 300 // 5分钟有效期
        );

        amountOut = amounts[amounts.length - 1];

        emit Swapped(tokenIn, tokenOut, amountIn, amountOut, recipient);
    }

    /**
     * @notice 添加流动性
     * @param tokenA 代币 A 地址
     * @param tokenB 代币 B 地址
     * @param amountADesired 期望的代币 A 金额
     * @param amountBDesired 期望的代币 B 金额
     * @param amountAMin 最小代币 A 金额
     * @param amountBMin 最小代币 B 金额
     */
    function addLiquidity(
        address tokenA,
        address tokenB,
        uint256 amountADesired,
        uint256 amountBDesired,
        uint256 amountAMin,
        uint256 amountBMin
    )
        external
        onlyOwner
        returns (
            uint256 amountA,
            uint256 amountB,
            uint256 liquidity
        )
    {
        // 批准路由器使用代币
        IERC20(tokenA).approve(address(router), amountADesired);
        IERC20(tokenB).approve(address(router), amountBDesired);

        // 添加流动性
        (amountA, amountB, liquidity) = router.addLiquidity(
            tokenA,
            tokenB,
            amountADesired,
            amountBDesired,
            amountAMin,
            amountBMin,
            owner,
            block.timestamp + 300
        );

        emit LiquidityAdded(tokenA, tokenB, amountA, amountB, liquidity);
    }

    /**
     * @notice 获取代币交换价格
     * @param tokenIn 输入代币地址
     * @param tokenOut 输出代币地址
     * @param amountIn 输入金额
     * @return amountOut 输出金额
     */
    function getAmountsOut(
        address tokenIn,
        address tokenOut,
        uint256 amountIn
    )
        external
        view
        returns (uint256[] memory amounts)
    {
        address[] memory path;
        if (tokenIn == address(weth) || tokenOut == address(weth)) {
            path = new address[](2);
            path[0] = tokenIn;
            path[1] = tokenOut;
        } else {
            path = new address[](3);
            path[0] = tokenIn;
            path[1] = address(weth);
            path[2] = tokenOut;
        }

        amounts = router.getAmountsOut(amountIn, path);
    }

    /**
     * @notice 提取合约资金
     */
    function withdraw(address token, uint256 amount)
        external
        onlyOwner
    {
        if (token == address(0)) {
            payable(owner).transfer(amount);
        } else {
            IERC20(token).transfer(owner, amount);
        }
    }

    /**
     * @notice 接收 ETH
     */
    receive() external payable {}
}
```

#### 2. 创建部署脚本

创建 `scripts/deployUniswapV2.js`:

```javascript
const hre = require("hardhat");

async function main() {
  console.log("Deploying Uniswap V2 Integration...");

  // Uniswap V2 Router 地址（Sepolia）
  const routerAddress = "0x94A9D9AC8a22534E3FaCa9F4e7F2E2cf85d5E4C8";

  // WETH 地址（Sepolia）
  const wethAddress = "0xfFf9976782d46CC05630D1f6eBAb18b2324d6B14";

  const UniswapV2Integration = await hre.ethers.getContractFactory(
    "UniswapV2Integration"
  );
  const uniswapV2Integration = await UniswapV2Integration.deploy(
    routerAddress,
    wethAddress
  );

  await uniswapV2Integration.waitForDeployment();
  const address = await uniswapV2Integration.getAddress();

  console.log(`UniswapV2Integration deployed to: ${address}`);

  // 验证合约（可选）
  if (hre.network.name !== "hardhat" && hre.network.name !== "localhost") {
    console.log("Waiting for block confirmations...");
    await uniswapV2Integration.deploymentTransaction().wait(6);

    console.log("Verifying contract...");
    await hre.run("verify:verify", {
      address: address,
      constructorArguments: [routerAddress, wethAddress],
    });
  }

  return address;
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
```

#### 3. 部署到测试网

```bash
# 部署到 Sepolia 测试网
npx hardhat run scripts/deployUniswapV2.js --network sepolia
```

#### 4. 创建测试用例

创建 `test/UniswapV2Integration.test.js`:

```javascript
const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("UniswapV2Integration", function () {
  let uniswapV2Integration;
  let owner;
  let weth;
  let wethAddress;

  beforeEach(async function () {
    [owner] = await ethers.getSigners();

    // Uniswap V2 Router (Sepolia)
    const routerAddress = "0x94A9D9AC8a22534E3FaCa9F4e7F2E2cf85d5E4C8";

    // WETH (Sepolia)
    wethAddress = "0xfFf9976782d46CC05630D1f6eBAb18b2324d6B14";

    const UniswapV2Integration = await ethers.getContractFactory(
      "UniswapV2Integration"
    );
    uniswapV2Integration = await UniswapV2Integration.deploy(
      routerAddress,
      wethAddress
    );
    await uniswapV2Integration.waitForDeployment();

    weth = await ethers.getContractAt("IWETH", wethAddress);
  });

  describe("Deployment", function () {
    it("Should set the right owner", async function () {
      expect(await uniswapV2Integration.owner()).to.equal(owner.address);
    });

    it("Should have the correct router and factory", async function () {
      const router = await uniswapV2Integration.router();
      expect(router).to.not.equal(ethers.ZeroAddress);

      const factory = await uniswapV2Integration.factory();
      expect(factory).to.not.equal(ethers.ZeroAddress);
    });
  });

  describe("Swap Tokens", function () {
    it("Should revert if caller is not owner", async function () {
      const [_, attacker] = await ethers.getSigners();
      await expect(
        uniswapV2Integration
          .connect(attacker)
          .swapTokens(
            wethAddress,
            owner.address,
            1000,
            0,
            owner.address
          )
      ).to.be.revertedWith("Not owner");
    });
  });

  describe("Get Amounts Out", function () {
    it("Should return correct amount out", async function () {
      const amountIn = ethers.parseEther("1");

      const amounts = await uniswapV2Integration.getAmountsOut(
        wethAddress,
        owner.address,
        amountIn
      );

      expect(amounts).to.have.lengthOf(2);
      expect(amounts[0]).to.equal(amountIn);
    });
  });
});
```

#### 5. 运行测试

```bash
npx hardhat test
```

---

## Uniswap V3 部署

### 概述

Uniswap V3 是 Uniswap V2 的升级版本，引入了集中流动性功能，提供更高的资本效率。

### 部署步骤

#### 1. 创建 Uniswap V3 集成合约

创建 `contracts/UniswapV3Integration.sol`:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Factory.sol";
import "@uniswap/v3-periphery/contracts/interfaces/ISwapRouter.sol";
import "@uniswap/v3-periphery/contracts/interfaces/INonfungiblePositionManager.sol";
import "@uniswap/v3-periphery/contracts/libraries/TransferHelper.sol";

/**
 * @title UniswapV3Integration
 * @notice Uniswap V3 协议集成示例合约
 * @dev 实现集中流动性交易和 NFT 位置管理
 */
contract UniswapV3Integration {
    ISwapRouter public swapRouter;
    INonfungiblePositionManager public positionManager;
    IUniswapV3Factory public factory;

    address public owner;

    struct Position {
        uint256 tokenId;
        address token0;
        address token1;
        uint24 fee;
        int24 tickLower;
        int24 tickUpper;
        uint128 liquidity;
    }

    mapping(uint256 => Position) public positions;

    event SwappedV3(
        address indexed tokenIn,
        address indexed tokenOut,
        uint256 amountIn,
        uint256 amountOut,
        address indexed recipient
    );

    event PositionCreated(
        uint256 indexed tokenId,
        address indexed token0,
        address indexed token1,
        uint24 fee,
        int24 tickLower,
        int24 tickUpper,
        uint128 liquidity
    );

    constructor(address _swapRouter, address _positionManager) {
        swapRouter = ISwapRouter(_swapRouter);
        positionManager = INonfungiblePositionManager(_positionManager);
        factory = IUniswapV3Factory(positionManager.factory());
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    /**
     * @notice 使用 Uniswap V3 交换代币
     * @param tokenIn 输入代币地址
     * @param tokenOut 输出代币地址
     * @param amountIn 输入金额
     * @param amountOutMinimum 最小输出金额
     * @param fee 手续费等级 (500, 3000, 10000)
     */
    function exactInputSingle(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 amountOutMinimum,
        uint24 fee
    )
        external
        onlyOwner
        returns (uint256 amountOut)
    {
        // 转移代币到合约
        TransferHelper.safeTransferFrom(
            tokenIn,
            msg.sender,
            address(this),
            amountIn
        );

        // 批准路由器使用代币
        TransferHelper.safeApprove(tokenIn, address(swapRouter), amountIn);

        // 执行交换
        ISwapRouter.ExactInputSingleParams memory params = ISwapRouter
            .ExactInputSingleParams({
                tokenIn: tokenIn,
                tokenOut: tokenOut,
                fee: fee,
                recipient: msg.sender,
                amountIn: amountIn,
                amountOutMinimum: amountOutMinimum,
                sqrtPriceLimitX96: 0
            });

        amountOut = swapRouter.exactInputSingle(params);

        emit SwappedV3(tokenIn, tokenOut, amountIn, amountOut, msg.sender);
    }

    /**
     * @notice 创建新的流动性位置
     * @param token0 代币 0 地址
     * @param token1 代币 1 地址
     * @param fee 手续费等级
     * @param tickLower 下限 tick
     * @param tickUpper 上限 tick
     * @param amount0Desired 期望代币 0 金额
     * @param amount1Desired 期望代币 1 金额
     */
    function createPosition(
        address token0,
        address token1,
        uint24 fee,
        int24 tickLower,
        int24 tickUpper,
        uint256 amount0Desired,
        uint256 amount1Desired
    )
        external
        onlyOwner
        returns (
            uint256 tokenId,
            uint128 liquidity,
            uint256 amount0,
            uint256 amount1
        )
    {
        // 转移代币到合约
        TransferHelper.safeTransferFrom(
            token0,
            msg.sender,
            address(this),
            amount0Desired
        );
        TransferHelper.safeTransferFrom(
            token1,
            msg.sender,
            address(this),
            amount1Desired
        );

        // 批准位置管理器使用代币
        TransferHelper.safeApprove(
            token0,
            address(positionManager),
            amount0Desired
        );
        TransferHelper.safeApprove(
            token1,
            address(positionManager),
            amount1Desired
        );

        // 创建位置参数
        INonfungiblePositionManager.MintParams memory params = INonfungiblePositionManager
            .MintParams({
                token0: token0,
                token1: token1,
                fee: fee,
                tickLower: tickLower,
                tickUpper: tickUpper,
                amount0Desired: amount0Desired,
                amount1Desired: amount1Desired,
                amount0Min: 0,
                amount1Min: 0,
                recipient: address(this),
                deadline: block.timestamp + 300
            });

        // 创建位置
        (tokenId, liquidity, amount0, amount1) = positionManager.mint(params);

        // 存储位置信息
        positions[tokenId] = Position({
            tokenId: tokenId,
            token0: token0,
            token1: token1,
            fee: fee,
            tickLower: tickLower,
            tickUpper: tickUpper,
            liquidity: liquidity
        });

        emit PositionCreated(
            tokenId,
            token0,
            token1,
            fee,
            tickLower,
            tickUpper,
            liquidity
        );
    }

    /**
     * @notice 增加流动性
     */
    function increaseLiquidity(
        uint256 tokenId,
        uint256 amount0Desired,
        uint256 amount1Desired
    )
        external
        onlyOwner
        returns (uint128 liquidity, uint256 amount0, uint256 amount1)
    {
        Position storage position = positions[tokenId];
        require(position.tokenId != 0, "Position not found");

        // 转移代币到合约
        TransferHelper.safeTransferFrom(
            position.token0,
            msg.sender,
            address(this),
            amount0Desired
        );
        TransferHelper.safeTransferFrom(
            position.token1,
            msg.sender,
            address(this),
            amount1Desired
        );

        // 批准
        TransferHelper.safeApprove(
            position.token0,
            address(positionManager),
            amount0Desired
        );
        TransferHelper.safeApprove(
            position.token1,
            address(positionManager),
            amount1Desired
        );

        // 增加流动性参数
        INonfungiblePositionManager.IncreaseLiquidityParams
            memory params = INonfungiblePositionManager
                .IncreaseLiquidityParams({
                    tokenId: tokenId,
                    amount0Desired: amount0Desired,
                    amount1Desired: amount1Desired,
                    amount0Min: 0,
                    amount1Min: 0,
                    deadline: block.timestamp + 300
                });

        (liquidity, amount0, amount1) = positionManager.increaseLiquidity(
            params
        );

        position.liquidity += liquidity;
    }

    /**
     * @notice 获取位置信息
     */
    function getPosition(uint256 tokenId)
        external
        view
        returns (Position memory)
    {
        return positions[tokenId];
    }

    /**
     * @notice 接收 ERC721
     */
    function onERC721Received(
        address,
        address,
        uint256,
        bytes calldata
    )
        external
        pure
        returns (bytes4)
    {
        return this.onERC721Received.selector;
    }
}
```

#### 2. 创建部署脚本

创建 `scripts/deployUniswapV3.js`:

```javascript
const hre = require("hardhat");

async function main() {
  console.log("Deploying Uniswap V3 Integration...");

  // Uniswap V3 SwapRouter 地址（Sepolia）
  const swapRouterAddress = "0x3bFA4769FB09eefC5a80d58Ea2714b53C01d382F";

  // Uniswap V3 PositionManager 地址（Sepolia）
  const positionManagerAddress = "0x1238536071E1c677A632429e3655c799b0c2C722";

  const UniswapV3Integration = await hre.ethers.getContractFactory(
    "UniswapV3Integration"
  );
  const uniswapV3Integration = await UniswapV3Integration.deploy(
    swapRouterAddress,
    positionManagerAddress
  );

  await uniswapV3Integration.waitForDeployment();
  const address = await uniswapV3Integration.getAddress();

  console.log(`UniswapV3Integration deployed to: ${address}`);

  // 验证合约（可选）
  if (hre.network.name !== "hardhat" && hre.network.name !== "localhost") {
    console.log("Waiting for block confirmations...");
    await uniswapV3Integration.deploymentTransaction().wait(6);

    console.log("Verifying contract...");
    await hre.run("verify:verify", {
      address: address,
      constructorArguments: [swapRouterAddress, positionManagerAddress],
    });
  }

  return address;
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
```

#### 3. 部署到测试网

```bash
# 部署到 Sepolia 测试网
npx hardhat run scripts/deployUniswapV3.js --network sepolia
```

---

## Compound 部署

### 概述

Compound 是一个去中心化借贷协议，使用利率模型动态调整借贷利率。

### 部署步骤

#### 1. 创建 Compound 集成合约

创建 `contracts/CompoundIntegration.sol`:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

/**
 * @title CompoundIntegration
 * @notice Compound 协议集成示例合约
 * @dev 实现存款和借款功能
 */
contract CompoundIntegration {
    using SafeERC20 for IERC20;

    IComptroller public comptroller;

    address public owner;
    mapping(address => address) public cTokens;

    event Deposited(
        address indexed token,
        address indexed cToken,
        uint256 amount,
        address indexed user
    );

    event Borrowed(
        address indexed token,
        address indexed cToken,
        uint256 amount,
        address indexed user
    );

    event Repaid(
        address indexed token,
        address indexed cToken,
        uint256 amount,
        address indexed user
    );

    constructor(address _comptroller) {
        comptroller = IComptroller(_comptroller);
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    /**
     * @notice 添加 cToken 映射
     */
    function addCToken(address token, address cToken) external onlyOwner {
        cTokens[token] = cToken;
    }

    /**
     * @notice 存款到 Compound
     * @param token 底层代币地址
     * @param amount 存款金额
     */
    function supply(address token, uint256 amount) external onlyOwner {
        address cToken = cTokens[token];
        require(cToken != address(0), "CToken not found");

        // 转移代币到合约
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        // 批准 cToken 使用代币
        IERC20(token).safeApprove(cToken, amount);

        // 存款到 Compound
        require(
            ICToken(cToken).mint(amount) == 0,
            "Mint failed"
        );

        emit Deposited(token, cToken, amount, msg.sender);
    }

    /**
     * @notice 从 Compound 借款
     * @param token 底层代币地址
     * @param amount 借款金额
     */
    function borrow(address token, uint256 amount) external onlyOwner {
        address cToken = cTokens[token];
        require(cToken != address(0), "CToken not found");

        // 借款
        require(
            ICToken(cToken).borrow(amount) == 0,
            "Borrow failed"
        );

        emit Borrowed(token, cToken, amount, msg.sender);
    }

    /**
     * @notice 偿还 Compound 借款
     * @param token 底层代币地址
     * @param amount 偿还金额
     */
    function repayBorrow(address token, uint256 amount) external onlyOwner {
        address cToken = cTokens[token];
        require(cToken != address(0), "CToken not found");

        // 转移代币到合约
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        // 批准 cToken 使用代币
        IERC20(token).safeApprove(cToken, amount);

        // 偿还借款
        require(
            ICToken(cToken).repayBorrow(amount) == 0,
            "Repay failed"
        );

        emit Repaid(token, cToken, amount, msg.sender);
    }

    /**
     * @notice 获取账户余额
     */
    function getBalance(address token) external view returns (uint256) {
        address cToken = cTokens[token];
        if (cToken == address(0)) {
            return 0;
        }
        return ICToken(cToken).balanceOf(address(this));
    }

    /**
     * @notice 提取合约资金
     */
    function withdraw(address token, uint256 amount) external onlyOwner {
        IERC20(token).safeTransfer(owner, amount);
    }
}

/**
 * @title IComptroller
 * @notice Compound Comptroller 接口
 */
interface IComptroller {
    function markets(address cToken) external view returns (bool, uint256);
    function enterMarkets(address[] calldata cTokens) external returns (uint256);
}

/**
 * @title ICToken
 * @notice Compound cToken 接口
 */
interface ICToken {
    function mint(uint256 mintAmount) external returns (uint256);
    function redeem(uint256 redeemTokens) external returns (uint256);
    function borrow(uint256 borrowAmount) external returns (uint256);
    function repayBorrow(uint256 repayAmount) external returns (uint256);
    function balanceOf(address owner) external view returns (uint256);
    function exchangeRateCurrent() external returns (uint256);
    function underlying() external view returns (address);
}
```

#### 2. 创建部署脚本

创建 `scripts/deployCompound.js`:

```javascript
const hre = require("hardhat");

async function main() {
  console.log("Deploying Compound Integration...");

  // Compound Comptroller 地址（Sepolia）
  const comptrollerAddress = "0xdc8d2831C4849a564444DcE9E50E425034a982b6";

  const CompoundIntegration = await hre.ethers.getContractFactory(
    "CompoundIntegration"
  );
  const compoundIntegration = await CompoundIntegration.deploy(
    comptrollerAddress
  );

  await compoundIntegration.waitForDeployment();
  const address = await compoundIntegration.getAddress();

  console.log(`CompoundIntegration deployed to: ${address}`);

  // 添加 cToken 映射（示例）
  const daiAddress = "0xff795577d9ac8bd7d90ee22b6c1703490b6512fd";
  const cDAIAddress = "0x95d889f770Ae6E7d7528B617c4f3711e5e7C9488";

  const tx = await compoundIntegration.addCToken(daiAddress, cDAIAddress);
  await tx.wait();

  console.log(`Added cToken mapping: ${daiAddress} -> ${cDAIAddress}`);

  // 验证合约（可选）
  if (hre.network.name !== "hardhat" && hre.network.name !== "localhost") {
    console.log("Waiting for block confirmations...");
    await compoundIntegration.deploymentTransaction().wait(6);

    console.log("Verifying contract...");
    await hre.run("verify:verify", {
      address: address,
      constructorArguments: [comptrollerAddress],
    });
  }

  return address;
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
```

#### 3. 部署到测试网

```bash
# 部署到 Sepolia 测试网
npx hardhat run scripts/deployCompound.js --network sepolia
```

---

## 最佳实践

### 1. 安全性

- ✅ 始终使用 OpenZeppelin 的审计合约
- ✅ 实现适当的访问控制（如 `onlyOwner`）
- ✅ 添加重入保护（`nonReentrant`）
- ✅ 验证所有外部调用
- ✅ 使用 SafeERC20 处理代币转账

### 2. Gas 优化

- ✅ 使用 `calldata` 代替 `memory`
- ✅ 批处理操作以减少交易次数
- ✅ 使用事件记录重要信息（节省存储）
- ✅ 考虑使用 EIP-2535（Diamond 标准）减少合约大小

### 3. 测试

- ✅ 编写全面的单元测试
- ✅ 测试边界情况和异常
- ✅ 使用 Fork Testing 测试主网环境
- ✅ 实现集成测试

### 4. 部署

- ✅ 在测试网充分测试后再部署到主网
- ✅ 使用确定性部署（CREATE2）
- ✅ 实现可升级合约模式（如 Proxy）
- ✅ 在 Etherscan 验证合约代码

### 5. 监控

- ✅ 实现事件监听器
- ✅ 设置价格警报
- ✅ 监控合约余额
- ✅ 使用 The Graph 进行链上数据查询

---

## 故障排除

### 常见问题

#### 1. 合约部署失败

```bash
# 检查 Gas 限制
npx hardhat run scripts/deploy.js --network sepolia --gas-limit 30000000

# 检查账户余额
npx hardhat run scripts/check-balance.js
```

#### 2. 合约验证失败

```bash
# 确保等待足够的区块确认（6 个区块）
# 检查构造函数参数是否正确

# 手动验证
npx hardhat verify --network sepolia <CONTRACT_ADDRESS> <CONSTRUCTOR_ARGS>
```

#### 3. 代币批准失败

```bash
# 检查代币小数位数
# 检查代币余额
# 确保批准金额足够
```

#### 4. 交易回滚

```bash
# 使用 Hardhat Console 调试
npx hardhat console --network sepolia

# 检查交易回滚原因
await ethers.provider.getTransactionReceipt("<TX_HASH>")
```

### 调试技巧

1. **使用 Hardhat Console**
   ```bash
   npx hardhat console --network sepolia
   ```

2. **启用详细日志**
   ```javascript
   console.log("Variable value:", variable);
   ```

3. **使用 Tenderly 进行交易调试**
   ```bash
   npm install --save-dev @tenderly/hardhat-tenderly
   ```

4. **使用 Foundry 进行模糊测试**
   ```bash
   foundry test
   ```

---

## 资源链接

- [Hardhat 文档](https://hardhat.org/docs)
- [OpenZeppelin 合约](https://docs.openzeppelin.com/contracts)
- [Aave 开发文档](https://docs.aave.com/developers)
- [Uniswap V2 文档](https://docs.uniswap.org/contracts/v2/overview)
- [Uniswap V3 文档](https://docs.uniswap.org/contracts/v3/overview)
- [Compound 文档](https://compound.finance/docs)
- [Solidity 文档](https://docs.soliditylang.org/)
- [Ethers.js 文档](https://docs.ethers.org/v6/)

---

**文档版本**: 1.0.0
**最后更新**: 2026-02-11
**作者**: 上等兵•甘
