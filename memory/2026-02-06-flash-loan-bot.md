# 第五小时：Flash Loan Arbitrage Bot 完整实现

---

## 十三、完整套利机器人架构

### 13.1 系统架构图

```
┌─────────────────────────────────────────────────────────┐
│                    监控层 (Monitor)                       │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│   │ Price        │  │ Opportunity  │  │ Gas          │  │
│   │ Monitor      │  │ Detector     │  │ Oracle       │  │
│   └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                    ↓ (WebSocket/HTTP)
┌─────────────────────────────────────────────────────────┐
│                   决策层 (Decision)                       │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│   │ Profit       │  │ Risk         │  │ Queue        │  │
│   │ Calculator   │  │ Manager      │  │ Manager      │  │
│   └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                    ↓ (RPC Call)
┌─────────────────────────────────────────────────────────┐
│                   执行层 (Execution)                       │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│   │ Transaction │  │ Flash Loan   │  │ MEV          │  │
│   │ Builder     │  │ Executor     │  │ Protection   │  │
│   └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                    ↓ (Direct Contract Call)
┌─────────────────────────────────────────────────────────┐
│                 智能合约层 (Contract)                      │
│   ┌──────────────────────────────────────────────────┐   │
│   │      GasOptimizedFlashLoanBot                     │   │
│   │      - Flash Loan Executor                         │   │
│   │      - DEX Swapper                                 │   │
│   │      - Profit Calculator                           │   │
│   └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 13.2 智能合约实现

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@aave/v3-core/contracts/interfaces/IPool.sol";
import "@aave/v3-core/contracts/interfaces/IPoolAddressesProvider.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@uniswap/v2-periphery/contracts/interfaces/IUniswapV2Router02.sol";

/**
 * @title FlashLoanArbitrageBot
 * @dev 完整的闪电贷套利机器人
 * @author 上等兵•甘
 */
contract FlashLoanArbitrageBot {
    using SafeERC20 for IERC20;

    // ========== 常量 ==========
    address public constant WETH = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
    address public constant USDC = 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48;
    address public constant UNISWAP_V2_ROUTER =
        0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D;
    address public constant SUSHISWAP_ROUTER =
        0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F;

    // ========== 状态变量 ==========
    IPool public immutable pool;
    address public immutable owner;

    // 紧凑存储
    struct BotState {
        uint128 totalBorrowed;
        uint128 totalProfit;
        address owner;
        bool paused;
    }
    BotState public state;

    // ========== 修饰符 ==========
    modifier onlyOwner() {
        require(msg.sender == state.owner, "Only owner");
        _;
    }

    modifier whenNotPaused() {
        require(!state.paused, "Paused");
        _;
    }

    // ========== 事件 ==========
    event ArbitrageExecuted(
        address indexed asset,
        uint256 amount,
        uint256 profit,
        string indexed strategy
    );

    event ArbitrageFailed(
        address indexed asset,
        uint256 amount,
        string reason
    );

    // ========== 构造函数 ==========
    constructor(address _poolAddressProvider) {
        IPoolAddressesProvider provider =
            IPoolAddressesProvider(_poolAddressProvider);
        pool = IPool(provider.getPool());

        state = BotState({
            totalBorrowed: 0,
            totalProfit: 0,
            owner: msg.sender,
            paused: false
        });

        owner = msg.sender;
    }

    // ========== 核心功能 ==========

    /**
     * @dev 简单套利：在两个 DEX 之间套利
     * @param asset 借入资产
     * @param amount 借入金额
     * @param buyRouter 买入 DEX Router
     * @param sellRouter 卖出 DEX Router
     */
    function executeSimpleArbitrage(
        address asset,
        uint256 amount,
        address buyRouter,
        address sellRouter
    ) external onlyOwner whenNotPaused {
        // 准备参数
        bytes memory params = abi.encode(
            asset,
            amount,
            buyRouter,
            sellRouter
        );

        // 执行闪电贷
        _executeFlashLoan(asset, amount, params);
    }

    /**
     * @dev 三角套利：A → B → C → A
     * @param asset 借入资产
     * @param amount 借入金额
     * @param router DEX Router
     * @param pathAtoB A→B 路径
     * @param pathBtoC B→C 路径
     * @param pathCtoA C→A 路径
     */
    function executeTriangularArbitrage(
        address asset,
        uint256 amount,
        address router,
        address[] calldata pathAtoB,
        address[] calldata pathBtoC,
        address[] calldata pathCtoA
    ) external onlyOwner whenNotPaused {
        bytes memory params = abi.encode(
            asset,
            amount,
            router,
            pathAtoB,
            pathBtoC,
            pathCtoA
        );

        _executeFlashLoan(asset, amount, params);
    }

    /**
     * @dev 执行闪电贷
     */
    function _executeFlashLoan(
        address asset,
        uint256 amount,
        bytes memory params
    ) internal {
        address[] memory assets = new address[](1);
        assets[0] = asset;

        uint256[] memory amounts = new uint256[](1);
        amounts[0] = amount;

        uint256[] memory modes = new uint256[](1);
        modes[0] = 0;

        pool.flashLoan(
            address(this),
            assets,
            amounts,
            modes,
            address(this),
            params,
            0
        );
    }

    /**
     * @dev 闪电贷回调函数
     */
    function executeOperation(
        address[] calldata assets,
        uint256[] calldata amounts,
        uint256[] calldata premiums,
        address initiator,
        bytes calldata params
    ) external returns (bool) {
        require(msg.sender == address(pool), "Invalid caller");
        require(initiator == state.owner, "Invalid initiator");

        address asset = assets[0];
        uint256 amount = amounts[0];
        uint256 premium = premiums[0];
        uint256 totalRepay = amount + premium;

        // 解析策略类型
        bytes4 strategySelector = bytes4(params);

        uint256 finalAmount;

        // 根据选择器执行不同策略
        if (strategySelector == bytes4(keccak256("SimpleArbitrage"))) {
            finalAmount = _executeSimpleArbitrage(
                asset,
                amount,
                params
            );
        } else if (strategySelector == bytes4(keccak256("TriangularArbitrage"))) {
            finalAmount = _executeTriangularArbitrage(
                asset,
                amount,
                params
            );
        } else {
            revert("Unknown strategy");
        }

        // 检查是否有足够的资金偿还
        require(finalAmount >= totalRepay, "Insufficient profit");

        uint256 profit = finalAmount - totalRepay;

        // 更新状态
        unchecked {
            state.totalBorrowed += uint128(amount);
            state.totalProfit += uint128(profit);
        }

        emit ArbitrageExecuted(asset, amount, profit, "Arbitrage");

        // 批准 Pool
        IERC20(asset).safeApprove(address(pool), totalRepay);

        return keccak256("IERC3156FlashBorrower.onFlashLoan") ==
            keccak256("IERC3156FlashBorrower.onFlashLoan");
    }

    /**
     * @dev 执行简单套利
     */
    function _executeSimpleArbitrage(
        address asset,
        uint256 amount,
        bytes calldata params
    ) internal returns (uint256 finalAmount) {
        (
            , // asset
            , // amount
            address buyRouter,
            address sellRouter
        ) = abi.decode(params, (address, uint256, address, address));

        // 在 buyRouter 买入代币
        address[] memory buyPath = new address[](2);
        buyPath[0] = asset;        // USDC
        buyPath[1] = WETH;        // WETH

        // 检查并批准
        IERC20(asset).safeApprove(buyRouter, amount);

        // 执行买入
        uint[] memory amountsBuy = IUniswapV2Router02(buyRouter)
            .swapExactTokensForTokens(
                amount,
                0, // 最小输出
                buyPath,
                address(this),
                block.timestamp
            );

        uint256 tokenAmount = amountsBuy[1]; // 获得的 WETH

        // 在 sellRouter 卖出代币
        address[] memory sellPath = new address[](2);
        sellPath[0] = WETH;
        sellPath[1] = asset;       // USDC

        // 检查并批准
        IERC20(WETH).safeApprove(sellRouter, tokenAmount);

        // 执行卖出
        uint[] memory amountsSell = IUniswapV2Router02(sellRouter)
            .swapExactTokensForTokens(
                tokenAmount,
                0, // 最小输出
                sellPath,
                address(this),
                block.timestamp
            );

        finalAmount = amountsSell[1]; // 最终获得的 USDC
    }

    /**
     * @dev 执行三角套利
     */
    function _executeTriangularArbitrage(
        address asset,
        uint256 amount,
        bytes calldata params
    ) internal returns (uint256 finalAmount) {
        (
            , // asset
            , // amount
            address router,
            address[] memory pathAtoB,
            address[] memory pathBtoC,
            address[] memory pathCtoA
        ) = abi.decode(params, (
            address,
            uint256,
            address,
            address[],
            address[],
            address[]
        ));

        // A → B
        IERC20(asset).safeApprove(router, amount);
        uint[] memory amounts1 = IUniswapV2Router02(router)
            .swapExactTokensForTokens(
                amount,
                0,
                pathAtoB,
                address(this),
                block.timestamp
            );

        // B → C
        IERC20(pathAtoB[1]).safeApprove(router, amounts1[1]);
        uint[] memory amounts2 = IUniswapV2Router02(router)
            .swapExactTokensForTokens(
                amounts1[1],
                0,
                pathBtoC,
                address(this),
                block.timestamp
            );

        // C → A
        IERC20(pathBtoC[1]).safeApprove(router, amounts2[1]);
        uint[] memory amounts3 = IUniswapV2Router02(router)
            .swapExactTokensForTokens(
                amounts2[1],
                0,
                pathCtoA,
                address(this),
                block.timestamp
            );

        finalAmount = amounts3[1];
    }

    // ========== 管理函数 ==========

    /**
     * @dev 获取统计数据
     */
    function getStats()
        external
        view
        returns (
            uint128 totalBorrowed,
            uint128 totalProfit,
            uint256 profitRate
        )
    {
        totalBorrowed = state.totalBorrowed;
        totalProfit = state.totalProfit;

        if (totalBorrowed > 0) {
            profitRate = (uint256(totalProfit) * 1e18) / totalBorrowed;
        }
    }

    /**
     * @dev 暂停
     */
    function pause() external onlyOwner {
        state.paused = true;
    }

    /**
     * @dev 恢复
     */
    function unpause() external onlyOwner {
        state.paused = false;
    }

    /**
     * @dev 紧急提取
     */
    function emergencyWithdraw(
        address token,
        uint256 amount
    ) external onlyOwner {
        IERC20(token).safeTransfer(owner, amount);
    }

    /**
     * @dev 接收 ETH
     */
    receive() external payable {}
}
```

---

## 十四、链下机器人控制器

```typescript
/**
 * Flash Loan Bot 控制器
 */
import { ethers } from 'ethers';
import { FlashLoanArbitrageBotAbi } from './abis/FlashLoanArbitrageBot.json';
import { PriceMonitor } from './PriceMonitor';
import { ArbitrageDetector } from './ArbitrageDetector';

class FlashLoanBotController {
  private provider: ethers.Provider;
  private wallet: ethers.Wallet;
  private botContract: ethers.Contract;
  private priceMonitor: PriceMonitor;
  private arbitrageDetector: ArbitrageDetector;

  /**
   * 初始化
   */
  async initialize(
    rpcUrl: string,
    privateKey: string,
    botContractAddress: string
  ) {
    this.provider = new ethers.JsonRpcProvider(rpcUrl);
    this.wallet = new ethers.Wallet(privateKey, this.provider);
    this.botContract = new ethers.Contract(
      botContractAddress,
      FlashLoanArbitrageBotAbi,
      this.wallet
    );

    this.priceMonitor = new PriceMonitor();
    this.arbitrageDetector = new ArbitrageDetector(this.priceMonitor);

    // 添加监控的交易对
    this.priceMonitor.addWatchedPair(
      'uniswap-v2',
      '0xB4e16d0168e52d35CACd2c6185b44281Ec28c9Dc',
      'USDC',
      'WETH'
    );
    this.priceMonitor.addWatchedPair(
      'sushiswap',
      '0x397FF1542f962076d0Bfe58eA045Ffa2d347ACA0',
      'USDC',
      'WETH'
    );

    // 启动价格监控
    await this.priceMonitor.start(2000);
  }

  /**
   * 运行套利循环
   */
  async runArbitrageLoop() {
    console.log('Starting arbitrage loop...');

    setInterval(async () => {
      await this.checkAndExecuteArbitrage();
    }, 5000); // 每 5 秒检查一次
  }

  /**
   * 检查并执行套利
   */
  async checkAndExecuteArbitrage() {
    try {
      // 检测简单套利机会
      const opportunity = this.arbitrageDetector.detectSimpleArbitrage(
        '0xB4e16d0168e52d35CACd2c6185b44281Ec28c9Dc',
        'USDC',
        'WETH',
        0.5 // 最小利润率 0.5%
      );

      if (opportunity) {
        console.log('Found arbitrage opportunity:', opportunity);

        // 检查 Gas 价格
        const gasPrice = await this.provider.getGasPrice();
        const maxGasPrice = ethers.parseUnits('30', 'gwei');

        if (gasPrice > maxGasPrice) {
          console.log('Gas price too high, skipping...');
          return;
        }

        // 执行套利
        await this.executeSimpleArbitrage(opportunity);
      }
    } catch (error) {
      console.error('Error in arbitrage loop:', error);
    }
  }

  /**
   * 执行简单套利
   */
  async executeSimpleArbitrage(opportunity: any) {
    try {
      const USDC_ADDRESS = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48';
      const UNISWAP_V2_ROUTER = '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D';
      const SUSHISWAP_ROUTER = '0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F';

      // 决定买卖方向
      let buyRouter: string;
      let sellRouter: string;

      if (opportunity.buyDex === 'uniswap-v2') {
        buyRouter = UNISWAP_V2_ROUTER;
        sellRouter = SUSHISWAP_ROUTER;
      } else {
        buyRouter = SUSHISWAP_ROUTER;
        sellRouter = UNISWAP_V2_ROUTER;
      }

      // 借入金额（估算）
      const borrowAmount = ethers.parseUnits('10000', 6); // 10,000 USDC

      // 估算 Gas
      const gasEstimate = await this.botContract.executeSimpleArbitrage.estimateGas(
        USDC_ADDRESS,
        borrowAmount,
        buyRouter,
        sellRouter
      );

      const gasPrice = await this.provider.getGasPrice();
      const gasCostWei = gasEstimate * gasPrice;

      console.log(`Estimated gas cost: ${ethers.formatEther(gasCostWei)} ETH`);

      // 检查是否有足够利润
      const estimatedProfitWei = ethers.parseUnits(
        opportunity.estimatedProfit.toFixed(6),
        6
      );

      if (estimatedProfitWei < gasCostWei) {
        console.log('Profit less than gas cost, skipping...');
        return;
      }

      // 执行交易
      console.log('Executing arbitrage...');
      const tx = await this.botContract.executeSimpleArbitrage(
        USDC_ADDRESS,
        borrowAmount,
        buyRouter,
        sellRouter,
        {
          gasLimit: gasEstimate * 12 / 10, // 增加 20% 缓冲
          gasPrice
        }
      );

      console.log('Transaction sent:', tx.hash);

      // 等待确认
      const receipt = await tx.wait();
      console.log('Transaction confirmed:', receipt.status === 1 ? 'Success' : 'Failed');

      // 记录统计
      this.logArbitrageResult(opportunity, receipt);
    } catch (error) {
      console.error('Error executing arbitrage:', error);
    }
  }

  /**
   * 记录套利结果
   */
  private logArbitrageResult(opportunity: any, receipt: any) {
    console.log('Arbitrage Result:');
    console.log('  Opportunity:', opportunity);
    console.log('  Tx Hash:', receipt.hash);
    console.log('  Gas Used:', receipt.gasUsed.toString());
    console.log('  Effective Gas Price:', ethers.formatUnits(receipt.effectiveGasPrice, 'gwei'));
  }

  /**
   * 获取机器人统计
   */
  async getBotStats() {
    const stats = await this.botContract.getStats();
    console.log('Bot Statistics:');
    console.log('  Total Borrowed:', ethers.formatUnits(stats.totalBorrowed, 6));
    console.log('  Total Profit:', ethers.formatUnits(stats.totalProfit, 6));
    console.log('  Profit Rate:', (Number(stats.profitRate) / 1e18).toFixed(4));
  }

  /**
   * 紧急暂停
   */
  async pauseBot() {
    await this.botContract.pause();
    console.log('Bot paused');
  }

  /**
   * 恢复运行
   */
  async unpauseBot() {
    await this.botContract.unpause();
    console.log('Bot unpaused');
  }
}

/**
 * 使用示例
 */
async function main() {
  const bot = new FlashLoanBotController();

  await bot.initialize(
    'https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY',
    'YOUR_PRIVATE_KEY',
    'YOUR_BOT_CONTRACT_ADDRESS'
  );

  // 运行套利循环
  bot.runArbitrageLoop();

  // 定期获取统计
  setInterval(async () => {
    await bot.getBotStats();
  }, 60000); // 每分钟
}

main().catch(console.error);
```

---

## 十五、第五小时学到的技能总结

### 15.1 核心技能

1. **完整合约架构**
   - 闪电贷接收器设计
   - 多策略支持
   - Gas 优化实现

2. **套利策略实现**
   - 简单套利执行
   - 三角套利执行
   - Uniswap V2 Router 集成

3. **链下控制器**
   - TypeScript/ethers.js
   - 价格监控集成
   - 自动化执行循环

4. **风险管理**
   - Gas 价格检查
   - 利润率验证
   - 暂停机制

5. **生产级代码**
   - 紧凑存储布局
   - 事件日志记录
   - 错误处理

### 15.2 代码产出

- ✅ FlashLoanArbitrageBot 完整套利合约
- ✅ FlashLoanBotController 链下控制器
- ✅ 自动化套利循环

---

**【第5小时汇报完毕】**

- ✅ 已完成：完整套利机器人实现、链下控制器、自动化执行
- ⏳ 下一步：MEV 保护与高级策略
