# 第三小时：套利策略理论基础

---

## 七、套利数学模型

### 7.1 套利基础理论

**套利（Arbitrage）**是指在不同市场之间利用价格差异获取无风险利润的行为。

**核心公式：**
```
利润 = (卖出价格 - 买入价格) × 数量 - 手续费 - Gas成本

P = (P_sell - P_buy) × Q - F - G

其中：
- P: 利润
- P_sell: 卖出价格
- P_buy: 买入价格
- Q: 数量
- F: 手续费
- G: Gas 成本
```

### 7.2 简单套利模型

**场景：在两个 DEX 之间进行套利**

```
DEX A: ETH/USDC = $1,850
DEX B: ETH/USDC = $1,860

价差: $10 (0.54%)

套利流程：
1. 在 DEX A 用 10,000 USDC 买入 5.4054 ETH
2. 在 DEX B 卖出 5.4054 ETH 获得 10,054 USDC
3. 毛利: 54 USDC

考虑成本：
- 闪电贷手续费: 9 USDC (0.09%)
- DEX A 手续费: 30 USDC (0.3%)
- DEX B 手续费: 30 USDC (0.3%)
- Gas 成本: 15 USDC
- 总成本: 84 USDC

净利润: 54 - 84 = -30 USDC ❌ 亏损！
```

**结论：需要更大价差或更优化策略！**

### 7.3 三角套利（Triangular Arbitrage）

**三角套利**利用三种代币之间的价格差异进行套利。

**数学模型：**
```
路径: A → B → C → A

条件判断：
Price_AB × Price_BC × Price_CA > 1

其中：
- Price_AB: A 换 B 的价格
- Price_BC: B 换 C 的价格
- Price_CA: C 换 A 的价格

如果乘积 > 1，则存在套利机会。
```

**示例：**
```
DEX 上的价格对：
- ETH/USDC: $1,850 (1 ETH = 1,850 USDC)
- WBTC/ETH: 0.0568 (1 WBTC = 0.0568 ETH)
- USDC/WBTC: $32,500 (1 WBTC = 32,500 USDC)

三角路径：
1. 1 ETH → 17,652 USDC (在 DEX A)
   计算: 1 / 0.0568 × 32,500 = 17,652.11 USDC

2. 17,652 USDC → 9.54 ETH (在 DEX B)
   计算: 17,652 / 1,850 = 9.5411 ETH

3. 检查: 9.5411 > 1 ETH! ✅

利润率: (9.5411 - 1) / 1 = 854.11% 😱

实际情况（考虑手续费）：
- DEX A 手续费: 0.3%
- DEX B 手续费: 0.3%
- 闪电贷手续费: 0.09%
- Gas 成本: ~$15

实际利润率计算...
```

### 7.4 滑点模型

**滑点（Slippage）**是预期价格与实际执行价格之间的差异。

**滑点公式：**
```
滑点% = |预期价格 - 实际价格| / 预期价格 × 100%

Slippage = |P_expected - P_actual| / P_expected × 100%
```

**恒定乘积做市商（CPMM）滑点公式：**

对于 Uniswap V2：
```
x × y = k (常数)

输入 amountIn 时，输出 amountOut：
amountOut = y - k / (x + amountIn)

滑点：
Slippage% = (P_theoretical - P_actual) / P_theoretical × 100%
         = (y/x - amountOut/amountIn) / (y/x) × 100%
```

**代码实现：**

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title 套利数学库
 */
library ArbitrageMath {
    /**
     * @dev 计算简单套利利润
     * @param priceBuy 买入价格
     * @param priceSell 卖出价格
     * @param amount 交易数量
     * @param feeRate 手续费率（bps，10000 = 100%）
     * @return profit 利润
     */
    function calculateSimpleArbitrage(
        uint256 priceBuy,
        uint256 priceSell,
        uint256 amount,
        uint256 feeRate
    ) internal pure returns (int256 profit) {
        // 收入
        uint256 revenue = (amount * priceSell) / 1e18;

        // 成本（本金 + 手续费）
        uint256 cost = (amount * priceBuy) / 1e18;
        uint256 fee = (cost * feeRate) / 10000;
        uint256 totalCost = cost + fee;

        // 利润
        profit = int256(revenue) - int256(totalCost);
    }

    /**
     * @dev 计算三角套利是否可行
     * @param priceAB A → B 的价格
     * @param priceBC B → C 的价格
     * @param priceCA C → A 的价格
     * @param feeRate 手续费率
     * @return profitable 是否盈利
     * @return profitRate 利润率
     */
    function checkTriangularArbitrage(
        uint256 priceAB,
        uint256 priceBC,
        uint256 priceCA,
        uint256 feeRate
    ) internal pure returns (
        bool profitable,
        uint256 profitRate
    ) {
        // 计算乘积（使用高精度）
        uint256 product = (priceAB * priceBC * priceCA) / 1e36;

        // 考虑手续费后的阈值
        uint256 threshold = (1e18 * (10000 + feeRate * 3)) / 10000;

        // 判断是否盈利
        if (product > threshold) {
            profitable = true;
            profitRate = ((product - threshold) * 1e18) / threshold;
        } else {
            profitable = false;
            profitRate = 0;
        }
    }

    /**
     * @dev 计算 Uniswap V2 的输出金额（考虑滑点）
     * @param reserveIn 储备量（输入代币）
     * @param reserveOut 储备量（输出代币）
     * @param amountIn 输入金额
     * @param feeRate 手续费率
     * @return amountOut 输出金额
     */
    function calculateUniswapV2Output(
        uint256 reserveIn,
        uint256 reserveOut,
        uint256 amountIn,
        uint256 feeRate
    ) internal pure returns (uint256 amountOut) {
        // 手续费调整
        uint256 amountInWithFee = amountIn * (10000 - feeRate);

        // 恒定乘积公式
        uint256 numerator = amountInWithFee * reserveOut;
        uint256 denominator = reserveIn * 10000 + amountInWithFee;

        amountOut = numerator / denominator;
    }

    /**
     * @dev 计算滑点百分比
     * @param expectedAmount 预期输出金额
     * @param actualAmount 实际输出金额
     * @return slippageBps 滑点（bps，10000 = 100%）
     */
    function calculateSlippage(
        uint256 expectedAmount,
        uint256 actualAmount
    ) internal pure returns (uint256 slippageBps) {
        require(expectedAmount > 0, "Expected amount must be > 0");

        uint256 diff;
        if (actualAmount > expectedAmount) {
            diff = actualAmount - expectedAmount;
        } else {
            diff = expectedAmount - actualAmount;
        }

        slippageBps = (diff * 10000) / expectedAmount;
    }

    /**
     * @dev 检查滑点是否可接受
     * @param amountIn 输入金额
     * @param reserveIn 输入代币储备
     * @param reserveOut 输出代币储备
     * @param amountOut 预期输出金额
     * @param maxSlippageBps 最大可接受滑点（bps）
     * @return acceptable 是否可接受
     * @return actualOutput 实际输出金额
     */
    function checkSlippage(
        uint256 amountIn,
        uint256 reserveIn,
        uint256 reserveOut,
        uint256 amountOut,
        uint256 maxSlippageBps
    ) internal pure returns (
        bool acceptable,
        uint256 actualOutput
    ) {
        // Uniswap V2 默认手续费 0.3% = 30 bps
        uint256 feeRate = 30;

        // 计算实际输出
        actualOutput = calculateUniswapV2Output(
            reserveIn,
            reserveOut,
            amountIn,
            feeRate
        );

        // 计算滑点
        uint256 slippage = calculateSlippage(amountOut, actualOutput);

        // 检查是否可接受
        acceptable = slippage <= maxSlippageBps;
    }

    /**
     * @dev 计算最优交易数量（考虑价格影响）
     * @param reserveIn 输入代币储备
     * @param reserveOut 输出代币储备
     * @param feeRate 手续费率
     * @param maxSlippageBps 最大滑点
     * @return optimalAmount 最优输入金额
     */
    function calculateOptimalAmount(
        uint256 reserveIn,
        uint256 reserveOut,
        uint256 feeRate,
        uint256 maxSlippageBps
    ) internal pure returns (uint256 optimalAmount) {
        // 二分法求解
        uint256 low = 0;
        uint256 high = reserveIn;

        for (uint256 i = 0; i < 32; i++) {
            uint256 mid = (low + high) / 2;

            uint256 output = calculateUniswapV2Output(
                reserveIn,
                reserveOut,
                mid,
                feeRate
            );

            // 预期价格（瞬时价格）
            uint256 expectedOutput = (mid * reserveOut) / reserveIn;

            uint256 slippage = calculateSlippage(expectedOutput, output);

            if (slippage <= maxSlippageBps) {
                low = mid;
            } else {
                high = mid;
            }
        }

        optimalAmount = low;
    }

    /**
     * @dev 计算套利的盈亏平衡点
     * @param borrowAmount 借入金额
     * @param flashLoanFee 闪电贷手续费（bps）
     * @param gasCostWei Gas 成本
     * @param dexFees DEX 手续费率（bps）
     * @return breakevenPriceDiff 盈亏平衡所需价差
     */
    function calculateArbitrageBreakeven(
        uint256 borrowAmount,
        uint256 flashLoanFee,
        uint256 gasCostWei,
        uint256 dexFees
    ) internal pure returns (uint256 breakevenPriceDiff) {
        // 闪电贷手续费
        uint256 flashLoanCost = (borrowAmount * flashLoanFee) / 10000;

        // DEX 手续费（假设两次交易）
        uint256 dexFeeTotal = (borrowAmount * dexFees * 2) / 10000;

        // 总成本
        uint256 totalCost = flashLoanCost + dexFeeTotal + gasCostWei;

        // 盈亏平衡价差（百分比）
        breakevenPriceDiff = (totalCost * 1e18) / borrowAmount;
    }

    /**
     * @dev 完整的套利利润计算
     * @param borrowAmount 借入金额
     * @param priceBuy 买入价格
     * @param priceSell 卖出价格
     * @param flashLoanFee 闪电贷手续费（bps）
     * @param dexFees DEX 手续费率（bps）
     * @param gasCostWei Gas 成本
     * @return profitWei 净利润
     * @return profitRate 利润率
     */
    function calculateTotalProfit(
        uint256 borrowAmount,
        uint256 priceBuy,
        uint256 priceSell,
        uint256 flashLoanFee,
        uint256 dexFees,
        uint256 gasCostWei
    ) internal pure returns (
        int256 profitWei,
        uint256 profitRate
    ) {
        // 买入数量
        uint256 amount = borrowAmount;

        // 收入
        uint256 revenue = (amount * priceSell) / 1e18;

        // 成本
        uint256 cost = (amount * priceBuy) / 1e18;
        uint256 flashLoanCost = (cost * flashLoanFee) / 10000;
        uint256 dexFeeTotal = (cost * dexFees * 2) / 10000;

        // 净利润
        int256 netProfit = int256(revenue) - int256(cost) -
            int256(flashLoanCost) - int256(dexFeeTotal) -
            int256(gasCostWei);

        profitWei = netProfit;

        // 利润率
        if (netProfit > 0) {
            profitRate = (uint256(netProfit) * 1e18) / cost;
        } else {
            profitRate = 0;
        }
    }
}

/**
 * @title 套利计算器合约
 */
contract ArbitrageCalculator {
    using ArbitrageMath for *;

    /**
     * @dev 计算套利机会
     * @param borrowAmount 借入金额
     * @param priceBuy 买入价格
     * @param priceSell 卖出价格
     * @param flashLoanFee 闪电贷手续费（bps）
     * @param dexFees DEX 手续费率（bps）
     * @param gasCostWei Gas 成本
     * @return profitable 是否盈利
     * @return profitWei 利润
     * @return profitRate 利润率
     */
    function checkArbitrageOpportunity(
        uint256 borrowAmount,
        uint256 priceBuy,
        uint256 priceSell,
        uint256 flashLoanFee,
        uint256 dexFees,
        uint256 gasCostWei
    ) external pure returns (
        bool profitable,
        int256 profitWei,
        uint256 profitRate
    ) {
        (profitWei, profitRate) = ArbitrageMath.calculateTotalProfit(
            borrowAmount,
            priceBuy,
            priceSell,
            flashLoanFee,
            dexFees,
            gasCostWei
        );

        profitable = profitWei > 0;
    }

    /**
     * @dev 计算三角套利机会
     * @param priceAB A→B 价格
     * @param priceBC B→C 价格
     * @param priceCA C→A 价格
     * @param feeRate 手续费率
     * @return profitable 是否盈利
     * @return profitRate 利润率
     */
    function checkTriangularArbitrageOpportunity(
        uint256 priceAB,
        uint256 priceBC,
        uint256 priceCA,
        uint256 feeRate
    ) external pure returns (
        bool profitable,
        uint256 profitRate
    ) {
        return ArbitrageMath.checkTriangularArbitrage(
            priceAB,
            priceBC,
            priceCA,
            feeRate
        );
    }

    /**
     * @dev 计算 Uniswap V2 输出
     * @param reserveIn 输入储备
     * @param reserveOut 输出储备
     * @param amountIn 输入金额
     * @return amountOut 输出金额
     * @return priceImpact 价格影响
     */
    function calculateUniswapV2OutputWithImpact(
        uint256 reserveIn,
        uint256 reserveOut,
        uint256 amountIn
    ) external pure returns (
        uint256 amountOut,
        uint256 priceImpactBps
    ) {
        // Uniswap V2 手续费
        uint256 feeRate = 30;

        // 计算输出
        amountOut = ArbitrageMath.calculateUniswapV2Output(
            reserveIn,
            reserveOut,
            amountIn,
            feeRate
        );

        // 瞬时价格
        uint256 expectedOut = (amountIn * reserveOut) / reserveIn;

        // 价格影响
        priceImpactBps = ArbitrageMath.calculateSlippage(
            expectedOut,
            amountOut
        );
    }
}
```

---

## 八、套利策略类型

### 8.1 简单套利（Simple Arbitrage）

**定义：** 在两个不同市场之间进行买入和卖出。

**流程：**
```
1. 在 DEX A 买入代币（价格较低）
2. 在 DEX B 卖出代币（价格较高）
3. 赚取价差
```

**适用场景：**
- 同一资产在不同 DEX 价格差异明显
- 价格差异 > 手续费 + Gas 成本

**代码框架：**

```solidity
function simpleArbitrage(
    address token,
    uint256 amount,
    address dexA,
    address dexB
) external {
    // 1. 借入闪电贷
    // ...

    // 2. 在 DEX A 买入
    _swap(dexA, amount, token);

    // 3. 在 DEX B 卖出
    uint256 finalAmount = _swap(dexB, token, USDC);

    // 4. 偿还闪电贷
    // ...
}
```

### 8.2 三角套利（Triangular Arbitrage）

**定义：** 利用三种代币之间的价格差异进行套利。

**常见路径：**
```
ETH → USDC → WBTC → ETH
USDC → ETH → DAI → USDC
WBTC → ETH → USDC → WBTC
```

**代码框架：**

```solidity
function triangularArbitrage(
    uint256 amount,
    address router1,
    address router2,
    address router3
) external {
    // 1. ETH → USDC
    uint256 amount1 = _swap(router1, amount, ETH, USDC);

    // 2. USDC → WBTC
    uint256 amount2 = _swap(router2, amount1, USDC, WBTC);

    // 3. WBTC → ETH
    uint256 finalAmount = _swap(router3, amount2, WBTC, ETH);

    // 4. 检查利润
    require(finalAmount > amount, "No profit");
}
```

### 8.3 多跳套利（Multi-hop Arbitrage）

**定义：** 跨越多个 DEX 进行套利，以获取更大价差。

**示例路径：**
```
Uniswap V2 → SushiSwap → Uniswap V3 → Balancer
```

**优势：**
- 可以发现更复杂的价格差异
- 组合多个小价差获得利润

**劣势：**
- Gas 成本高
- 执行复杂

### 8.4 清算套利（Liquidation Arbitrage）

**定义：** 通过清算抵押品不足的借款人获取清算奖励。

**清算条件：**
```
健康因子 < 1

Health Factor = (总抵押品价值 × 清算阈值) / 总债务

示例：
- 抵押品：10 ETH @ $1,850 = $18,500
- 债务：15,000 USDC @ $1 = $15,000
- 清算阈值：0.85
- 健康因子 = (18,500 × 0.85) / 15,000 = 1.048 > 1 ❌ 健康

如果 ETH 跌至 $1,700：
- 抵押品：10 ETH @ $1,700 = $17,000
- 健康因子 = (17,000 × 0.85) / 15,000 = 0.963 < 1 ✅ 可清算
```

**清算奖励：**
```
Aave: 额外 0.5% 奖励
Compound: 额外 0.5% 奖励

使用闪电贷清算：
1. 借入 USDC
2. 清算借款人的抵押品（获得 ETH）
3. 在 DEX 卖出 ETH
4. 偿还 USDC + 获利
```

### 8.5 空间套利（Spatial Arbitrage）

**定义：** 在不同 Layer2 之间进行套利。

**场景：**
```
Arbitrum: ETH/USDC = $1,840
Optimism: ETH/USDC = $1,860

策略：
1. 在 Arbitrum 买入 ETH
2. 跨桥到 Optimism
3. 在 Optimism 卖出 ETH
4. 跨桥回 Arbitrum
```

**考虑因素：**
- 跨桥费用
- 跨桥时间
- Gas 成本差异

---

## 九、第三小时学到的技能总结

### 9.1 核心技能

1. **套利数学模型**
   - 简单套利公式
   - 三角套利数学证明
   - 滑点计算公式

2. **高级数学计算**
   - Uniswap V2 恒定乘积公式
   - 价格影响计算
   - 最优交易量求解

3. **套利策略分析**
   - 5 种套利策略类型
   - 各策略的适用场景
   - 策略优劣势分析

4. **Solidity 数学库**
   - 高精度计算
   - 二分法求解
   - 防溢出处理

5. **盈亏平衡分析**
   - 完整成本计算
   - 盈亏平衡点求解
   - 利润率计算

### 9.2 代码产出

- ✅ ArbitrageMath 完整数学库
- ✅ ArbitrageCalculator 计算器合约
- ✅ 套利策略框架代码

---

**【第3小时汇报完毕】**

- ✅ 已完成：套利数学模型、策略类型、盈亏平衡分析
- ⏳ 下一步：DEX 价格监控与套利机会识别（链下 + 链上）
