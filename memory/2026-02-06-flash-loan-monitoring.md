# 第四小时：DEX 价格监控与套利机会识别

---

## 十、DEX 价格监控架构

### 10.1 监控系统架构

```
┌─────────────────────────────────────┐
│   数据源层                           │
│   - Uniswap V2 Subgraph              │
│   - Uniswap V3 Subgraph              │
│   - SushiSwap Subgraph               │
│   - Curve Subgraph                  │
│   - Balancer GraphQL                 │
│   - Chainlink Price Feeds           │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│   价格聚合层                         │
│   - 价格数据标准化                   │
│   - 实时价格更新                     │
│   - 历史价格存储                     │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│   机会识别层                         │
│   - 价差计算引擎                     │
│   - 三角套利检测                     │
│   - 盈利性分析                       │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│   执行层                             │
│   - 交易队列                         │
│   - Gas 优化器                       │
│   - Flash Loan 调用                  │
└─────────────────────────────────────┘
```

### 10.2 GraphQL 查询设计

#### Uniswap V2 Subgraph 查询

```typescript
// TypeScript/Javascript 监控器
import { gql, request } from 'graphql-request';

/**
 * Uniswap V2 价格查询
 */
const UNISWAP_V2_SUBGRAPH = 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2';

/**
 * 获取交易对价格
 */
async function getUniswapV2Price(pairAddress: string): Promise<{
  token0Price: string;
  token1Price: string;
  reserve0: string;
  reserve1: string;
}> {
  const query = gql`
    {
      pair(id: "${pairAddress.toLowerCase()}") {
        token0Price
        token1Price
        reserve0
        reserve1
        reserveUSD
      }
    }
  `;

  const result = await request(UNISWAP_V2_SUBGRAPH, query);
  return result.pair;
}

/**
 * 获取多个交易对价格
 */
async function getBatchUniswapV2Prices(pairAddresses: string[]): Promise<any[]> {
  const query = gql`
    {
      pairs(where: { id_in: ${JSON.stringify(pairAddresses.map(a => a.toLowerCase()))} }) {
        id
        token0 { symbol, decimals }
        token1 { symbol, decimals }
        token0Price
        token1Price
        reserve0
        reserve1
        reserveUSD
      }
    }
  `;

  const result = await request(UNISWAP_V2_SUBGRAPH, query);
  return result.pairs;
}
```

#### Uniswap V3 Subgraph 查询

```typescript
const UNISWAP_V3_SUBGRAPH = 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3';

/**
 * 获取 Uniswap V3 池价格
 */
async function getUniswapV3PoolPrice(poolAddress: string): Promise<{
  token0Price: string;
  token1Price: string;
  liquidity: string;
  sqrtPriceX96: string;
  tick: string;
}> {
  const query = gql`
    {
      pool(id: "${poolAddress.toLowerCase()}") {
        token0 { symbol, decimals }
        token1 { symbol, decimals }
        token0Price
        token1Price
        liquidity
        sqrtPriceX96
        tick
      }
    }
  `;

  const result = await request(UNISWAP_V3_SUBGRAPH, query);
  return result.pool;
}

/**
 * 获取 Uniswap V3 池的当前tick和价格
 */
async function getUniswapV3PoolTicks(
  poolAddress: string,
  numTicks: number = 100
): Promise<any> {
  const query = gql`
    {
      pool(id: "${poolAddress.toLowerCase()}") {
        ticks(first: ${numTicks}, orderBy: tickIdx, orderDirection: desc) {
          tickIdx
          liquidityNet
          price0
          price1
          liquidityGross
        }
      }
    }
  `;

  const result = await request(UNISWAP_V3_SUBGRAPH, query);
  return result.pool.ticks;
}
```

### 10.3 价格监控器实现

```typescript
/**
 * DEX 价格监控器
 */
class PriceMonitor {
  private prices: Map<string, number> = new Map();
  private reserves: Map<string, { reserve0: bigint; reserve1: bigint }> = new Map();
  private listeners: Array<(event: PriceEvent) => void> = [];

  /**
   * 价格事件
   */
  interface PriceEvent {
    dex: string;
    pair: string;
    price0: number;
    price1: number;
    timestamp: number;
  }

  /**
   * 监控的交易对
   */
  private watchedPairs: Array<{
    dex: string;
    pair: string;
    token0: string;
    token1: string;
  }> = [];

  /**
   * 添加监控的交易对
   */
  addWatchedPair(dex: string, pair: string, token0: string, token1: string) {
    this.watchedPairs.push({ dex, pair, token0, token1 });
  }

  /**
   * 订阅价格事件
   */
  onPriceUpdate(listener: (event: PriceEvent) => void) {
    this.listeners.push(listener);
  }

  /**
   * 更新价格
   */
  private async updatePrices() {
    for (const pair of this.watchedPairs) {
      try {
        let priceData: any;

        switch (pair.dex) {
          case 'uniswap-v2':
            priceData = await getUniswapV2Price(pair.pair);
            break;
          case 'uniswap-v3':
            priceData = await getUniswapV3PoolPrice(pair.pair);
            break;
          default:
            continue;
        }

        const key = `${pair.dex}:${pair.pair}`;
        const price0 = parseFloat(priceData.token0Price);
        const price1 = parseFloat(priceData.token1Price);

        this.prices.set(key + ':price0', price0);
        this.prices.set(key + ':price1', price1);

        // 触发事件
        const event: PriceEvent = {
          dex: pair.dex,
          pair: pair.pair,
          price0,
          price1,
          timestamp: Date.now()
        };

        this.listeners.forEach(listener => listener(event));
      } catch (error) {
        console.error(`Error updating price for ${pair.dex}:${pair.pair}:`, error);
      }
    }
  }

  /**
   * 获取价格
   */
  getPrice(dex: string, pair: string, tokenIndex: 0 | 1): number | undefined {
    const key = `${dex}:${pair}:price${tokenIndex}`;
    return this.prices.get(key);
  }

  /**
   * 获取储备量
   */
  getReserves(dex: string, pair: string): { reserve0: bigint; reserve1: bigint } | undefined {
    const key = `${dex}:${pair}`;
    return this.reserves.get(key);
  }

  /**
   * 启动监控
   */
  async start(intervalMs: number = 5000) {
    console.log('Starting price monitor...');

    // 立即更新一次
    await this.updatePrices();

    // 定期更新
    setInterval(() => {
      this.updatePrices();
    }, intervalMs);
  }

  /**
   * 停止监控
   */
  stop() {
    // 清理定时器（实际实现需要保存定时器引用）
    console.log('Stopping price monitor...');
  }
}

/**
 * 使用示例
 */
async function exampleUsage() {
  const monitor = new PriceMonitor();

  // 添加监控的交易对
  monitor.addWatchedPair(
    'uniswap-v2',
    '0xa478c2975ab1ea89e8196811f51a7b7ade33eb11', // WBTC/ETH
    'WBTC',
    'WETH'
  );
  monitor.addWatchedPair(
    'sushiswap',
    '0x397ff1542f962076d0bfe58ea045ffa2d347aca0', // WBTC/ETH
    'WBTC',
    'WETH'
  );

  // 订阅价格更新
  monitor.onPriceUpdate((event) => {
    console.log(`Price update: ${event.dex}:${event.pair}`);
    console.log(`  Token0: ${event.price0}`);
    console.log(`  Token1: ${event.price1}`);
  });

  // 启动监控（每 2 秒更新一次）
  await monitor.start(2000);
}
```

---

## 十一、套利机会识别引擎

### 11.1 简单套利检测

```typescript
/**
 * 套利机会检测器
 */
class ArbitrageDetector {
  private priceMonitor: PriceMonitor;

  constructor(priceMonitor: PriceMonitor) {
    this.priceMonitor = priceMonitor;
  }

  /**
   * 简单套利机会
   */
  interface SimpleArbitrageOpportunity {
    buyDex: string;
    sellDex: string;
    pair: string;
    token0: string;
    token1: string;
    buyPrice: number;
    sellPrice: number;
    priceDiff: number;
    priceDiffPercent: number;
    estimatedProfit: number;
    timestamp: number;
  }

  /**
   * 检测简单套利机会
   */
  detectSimpleArbitrage(
    pair: string,
    token0: string,
    token1: string,
    minProfitPercent: number = 0.5
  ): SimpleArbitrageOpportunity | null {
    // 获取各 DEX 的价格
    const dexes = ['uniswap-v2', 'sushiswap', 'uniswap-v3'];
    const prices: Map<string, number> = new Map();

    for (const dex of dexes) {
      const price = this.priceMonitor.getPrice(dex, pair, 0);
      if (price !== undefined) {
        prices.set(dex, price);
      }
    }

    if (prices.size < 2) {
      return null; // 需要至少两个 DEX 的价格
    }

    // 找出最高价和最低价
    let buyDex = '';
    let sellDex = '';
    let buyPrice = Infinity;
    let sellPrice = 0;

    for (const [dex, price] of prices) {
      if (price < buyPrice) {
        buyPrice = price;
        buyDex = dex;
      }
      if (price > sellPrice) {
        sellPrice = price;
        sellDex = dex;
      }
    }

    // 计算价差
    const priceDiff = sellPrice - buyPrice;
    const priceDiffPercent = (priceDiff / buyPrice) * 100;

    // 检查是否盈利
    if (priceDiffPercent >= minProfitPercent && buyDex !== sellDex) {
      // 估算利润（假设交易 1 ETH）
      const tradeAmount = 1;
      const estimatedProfit = priceDiff * tradeAmount;

      return {
        buyDex,
        sellDex,
        pair,
        token0,
        token1,
        buyPrice,
        sellPrice,
        priceDiff,
        priceDiffPercent,
        estimatedProfit,
        timestamp: Date.now()
      };
    }

    return null;
  }

  /**
   * 批量检测简单套利
   */
  detectAllSimpleArbitrage(
    pairs: Array<{ pair: string; token0: string; token1: string }>,
    minProfitPercent: number = 0.5
  ): SimpleArbitrageOpportunity[] {
    const opportunities: SimpleArbitrageOpportunity[] = [];

    for (const { pair, token0, token1 } of pairs) {
      const opportunity = this.detectSimpleArbitrage(
        pair,
        token0,
        token1,
        minProfitPercent
      );

      if (opportunity) {
        opportunities.push(opportunity);
      }
    }

    return opportunities;
  }
}
```

### 11.2 三角套利检测

```typescript
/**
 * 三角套利检测器
 */
class TriangularArbitrageDetector {
  private priceMonitor: PriceMonitor;

  constructor(priceMonitor: PriceMonitor) {
    this.priceMonitor = priceMonitor;
  }

  /**
   * 三角套利路径
   */
  interface TriangularPath {
    tokenA: string;
    tokenB: string;
    tokenC: string;
    dex: string;
    pairAB: string;
    pairBC: string;
    pairCA: string;
  }

  /**
   * 三角套利机会
   */
  interface TriangularArbitrageOpportunity {
    path: TriangularPath;
    priceAB: number;
    priceBC: number;
    priceCA: number;
    product: number;
    profitPercent: number;
    estimatedProfit: number;
    timestamp: number;
  }

  /**
   * 预定义的三角路径
   */
  private predefinedPaths: TriangularPath[] = [
    {
      tokenA: 'WETH',
      tokenB: 'USDC',
      tokenC: 'WBTC',
      dex: 'uniswap-v2',
      pairAB: '0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc',
      pairBC: '0xb4fbf271143f4fbf7b91a5ded31805e42b2208d6',
      pairCA: '0xa478c2975ab1ea89e8196811f51a7b7ade33eb11'
    },
    // 可以添加更多路径...
  ];

  /**
   * 检测三角套利
   */
  detectTriangularArbitrage(
    path: TriangularPath,
    minProfitPercent: number = 1.0
  ): TriangularArbitrageOpportunity | null {
    // 获取各段价格
    const priceAB = this.priceMonitor.getPrice(path.dex, path.pairAB, 0);
    const priceBC = this.priceMonitor.getPrice(path.dex, path.pairBC, 0);
    const priceCA = this.priceMonitor.getPrice(path.dex, path.pairCA, 0);

    if (!priceAB || !priceBC || !priceCA) {
      return null;
    }

    // 计算乘积
    const product = priceAB * priceBC * priceCA;

    // 计算利润率
    const profitPercent = (product - 1) * 100;

    // 检查是否盈利
    if (profitPercent >= minProfitPercent) {
      // 估算利润（假设交易 1 ETH）
      const tradeAmount = 1;
      const estimatedProfit = product - 1;

      return {
        path,
        priceAB,
        priceBC,
        priceCA,
        product,
        profitPercent,
        estimatedProfit: estimatedProfit * tradeAmount,
        timestamp: Date.now()
      };
    }

    return null;
  }

  /**
   * 批量检测三角套利
   */
  detectAllTriangularArbitrage(
    minProfitPercent: number = 1.0
  ): TriangularArbitrageOpportunity[] {
    const opportunities: TriangularArbitrageOpportunity[] = [];

    for (const path of this.predefinedPaths) {
      const opportunity = this.detectTriangularArbitrage(
        path,
        minProfitPercent
      );

      if (opportunity) {
        opportunities.push(opportunity);
      }
    }

    return opportunities;
  }
}
```

### 11.3 智能合约价格查询

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title 链上价格查询合约
 */
contract OnChainPriceQuery {
    /**
     * @dev Uniswap V2 Router 接口
     */
    interface IUniswapV2Router {
        function getAmountsOut(
            uint256 amountIn,
            address[] calldata path
        ) external view returns (uint256[] memory amounts);
    }

    /**
     * @dev Uniswap V2 Pair 接口
     */
    interface IUniswapV2Pair {
        function getReserves()
            external
            view
            returns (
                uint112 reserve0,
                uint112 reserve1,
                uint32 blockTimestampLast
            );
    }

    /**
     * @dev Uniswap V3 Pool 接口
     */
    interface IUniswapV3Pool {
        function slot0()
            external
            view
            returns (
                uint160 sqrtPriceX96,
                int24 tick,
                uint16 observationIndex,
                uint16 observationCardinality,
                uint16 observationCardinalityNext,
                uint8 feeProtocol,
                bool unlocked
            );

        function liquidity() external view returns (uint128);
    }

    // Router 地址
    IUniswapV2Router public constant UNISWAP_V2_ROUTER =
        IUniswapV2Router(0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D);

    /**
     * @dev 从 Uniswap V2 获取输出金额
     */
    function getUniswapV2AmountOut(
        uint256 amountIn,
        address[] calldata path
    ) external view returns (uint256 amountOut) {
        uint256[] memory amounts = UNISWAP_V2_ROUTER.getAmountsOut(
            amountIn,
            path
        );
        amountOut = amounts[amounts.length - 1];
    }

    /**
     * @dev 从 Uniswap V2 Pair 获取价格
     */
    function getUniswapV2Price(
        address pair
    ) external view returns (
        uint256 price0,
        uint256 price1
    ) {
        (uint112 reserve0, uint112 reserve1, ) = IUniswapV2Pair(pair)
            .getReserves();

        price0 = (uint256(reserve1) * 1e18) / uint256(reserve0);
        price1 = (uint256(reserve0) * 1e18) / uint256(reserve1);
    }

    /**
     * @dev 从 Uniswap V3 Pool 获取价格
     */
    function getUniswapV3Price(
        address pool
    ) external view returns (
        uint256 price0,
        uint256 price1
    ) {
        (uint160 sqrtPriceX96, , , , , , ) = IUniswapV3Pool(pool).slot0();

        // 计算 price0 = (sqrtPriceX96 / 2^96)^2
        uint256 price = (uint256(sqrtPriceX96) * uint256(sqrtPriceX96)) /
            (1 << 192);

        price0 = price;
        price1 = (1 << 192) / price;
    }

    /**
     * @dev 比较多个 DEX 的价格
     */
    function compareDexPrices(
        uint256 amountIn,
        address[] calldata path
    ) external view returns (
        uint256 uniswapV2Out,
        uint256 sushiswapOut
    ) {
        // Uniswap V2
        IUniswapV2Router uniswapRouter = IUniswapV2Router(
            0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D
        );
        uint256[] memory uniAmounts = uniswapRouter.getAmountsOut(
            amountIn,
            path
        );
        uniswapV2Out = uniAmounts[uniAmounts.length - 1];

        // SushiSwap
        IUniswapV2Router sushiRouter = IUniswapV2Router(
            0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F
        );
        uint256[] memory sushiAmounts = sushiRouter.getAmountsOut(
            amountIn,
            path
        );
        sushiswapOut = sushiAmounts[sushiAmounts.length - 1];
    }

    /**
     * @dev 检查简单套利机会
     */
    function checkSimpleArbitrage(
        uint256 amountIn,
        address[] calldata pathA,
        address[] calldata pathB
    ) external view returns (
        bool profitable,
        uint256 profitAmount,
        uint256 profitPercent
    ) {
        // 获取两个路径的输出
        uint256 outA = this.getUniswapV2AmountOut(amountIn, pathA);
        uint256 outB = this.getUniswapV2AmountOut(amountIn, pathB);

        // 假设在 A 买入，在 B 卖出
        uint256 revenue = outB;
        uint256 cost = outA;

        if (revenue > cost) {
            profitable = true;
            profitAmount = revenue - cost;
            profitPercent = ((revenue - cost) * 100) / cost;
        } else {
            profitable = false;
            profitAmount = 0;
            profitPercent = 0;
        }
    }
}
```

---

## 十二、第四小时学到的技能总结

### 12.1 核心技能

1. **GraphQL 查询技术**
   - Uniswap V2/V3 Subgraph 查询
   - 批量查询优化
   - 实时价格获取

2. **价格监控系统**
   - 多 DEX 价格聚合
   - 事件驱动架构
   - 实时更新机制

3. **套利检测算法**
   - 简单套利检测
   - 三角套利检测
   - 盈利性分析

4. **TypeScript 开发**
   - 类型安全的价格数据
   - 异步编程
   - 事件订阅模式

5. **链上价格查询**
   - Uniswap V2/V3 集成
   - 链上套利检测
   - Gas 优化查询

### 12.2 代码产出

- ✅ PriceMonitor 价格监控器
- ✅ ArbitrageDetector 套利检测器
- ✅ TriangularArbitrageDetector 三角套利检测
- ✅ OnChainPriceQuery 链上价格查询合约

---

**【第4小时汇报完毕】**

- ✅ 已完成：DEX 价格监控、GraphQL 查询、套利机会识别
- ⏳ 下一步：Flash Loan Arbitrage Bot 完整实现
