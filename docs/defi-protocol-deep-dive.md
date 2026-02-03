# DeFi 协议深度解析

## 📋 概述

去中心化金融（DeFi）是区块链应用的核心领域。本文将深入分析 DeFi 协议的核心机制、数学模型和实际应用。

---

## 🏦️ AMM（自动做市商）机制

### Uniswap V2 恒定乘积做市商

**核心公式**：
```
x * y = k
```

其中：
- x = 代币 A 的数量
- y = 代币 B 的数量
- k = 常数乘积

**流动性提供**：
```solidity
// Uniswap V2 Router
function addLiquidity(
    address tokenA,
    address tokenB,
    uint amountADesired,
    uint amountBDesired,
    uint amountAMin,
    uint amountBMin,
    address to,
    uint deadline
) external returns (uint amountA, uint amountB) {
    // 计算最优代币数量
    uint amountBOptimal = UniswapV2Library.quote(
        amountADesired, reserveA, reserveB
    );

    // 转账到池子
    TransferHelper.safeTransferFrom(
        tokenA,
        msg.sender,
        uniswapV2Pair,
        amountA,
        amountBMin
    );

    TransferHelper.safeTransferFrom(
        tokenB,
        msg.sender,
        uniswapV2Pair,
        amountBOptimal,
        amountAMin
    );

    // 铸造 LP 代币
    IUniswapV2Pair(uniswapV2Pair).mint(to, liquidity);
}
```

**价格计算**：
```python
# 计算代币价格
def calculate_price(reserve_a, reserve_b):
    return reserve_b / reserve_a  # B/A 价格

# 计算滑点
def calculate_slippage(input_amount, current_price, slippage_tolerance=0.003):
    expected_output = input_amount / current_price
    min_output = expected_output * (1 - slippage_tolerance)
    return min_output

# 计算无常损失
def calculate_impermanent_loss(
    initial_price_a,
    initial_price_b,
    final_price_a,
    final_price_b,
    initial_liquidity_a,
    initial_liquidity_b
):
    # 价格波动导致的损失
    price_ratio_change = (final_price_b / final_price_a) / (initial_price_b / initial_price_a)
    return (price_ratio_change - 1) * initial_liquidity_a
```

### Uniswap V3 集中流动性

**核心改进**：
- **资本效率**：集中流动性，减少无常损失
- **费用分级**：根据价格范围调整手续费
- **多跳交易**：支持跨多个价格池的复杂交易

**Position NFT**：
```solidity
// Uniswap V3 Position NFT
contract NonfungiblePositionManager is IERC721 {
    struct Position {
        uint96 nonce;
        address operator;
        address token0;
        address token1;
        uint24 fee;
        int24 tickLower;
        int24 tickUpper;
        uint128 liquidity;
        uint256 feeGrowthInside0LastX128;
        uint256 feeGrowthInside1LastX128;
        uint128 tokensOwed0;
        uint128 tokensOwed1;
    }

    mapping(uint256 => Position) public positions;
    mapping(address => uint256) public nextNonce;
    mapping(address => mapping(uint256 => Position)) public positions;

    function mint(
        address recipient,
        int24 tickLower,
        int24 tickUpper,
        uint128 amount0,
        uint128 amount1,
        uint24 fee,
        int256 amount0Min,
        int256 amount1Min,
        address recipient
    ) external returns (uint256 tokenId, uint128 liquidity, uint256 amount0, uint256 amount1);
}
```

**价格范围计算**：
```solidity
function getTickAtSqrtRatio(uint160 sqrtPriceX96) public pure returns (int24 tick) {
    uint160 ratioX128 = sqrtPriceX96 >>> 64;
    // 对数计算
    uint160 log2 = Math.log2(ratioX128);

    // 价格每 0.01% 变化一个 tick
    int24 tickLow = int24((log2 * 1e18) >> 64) - 887220;
    int24 tickHi = int24((log2 * 1e18) >> 128) + 887220;

    return tickLow < tickHi ? tickLow : tickHi;
}
```

---

## 💰 借贷协议

### Compound

**核心机制**：
- **cToken**：代表存入资产的 ERC20 代币
- **利率**：动态计算的借贷利率
- **清算**：抵押品价值低于阈值时自动清算

**利息计算**：
```solidity
// Compound 利率模型
contract CompoundInterestRateModel {
    function getBorrowRate(
        uint cash,
        uint borrows,
        uint reserves
    ) public view returns (uint) {
        // 利用率模型
        uint utilization = (borrows * 1e18) / (cash + borrows);

        // 分段利率计算
        if (utilization < 0.2e18) {
            return kink0 * utilization / 1e18;
        } else if (utilization < 0.8e18) {
            // kink0 到 kink1 之间线性插值
            uint slope1 = (kink1 - kink0) / 0.6e18;
            return kink0 + slope1 * (utilization - 0.2e18) / 1e18;
        } else {
            // kink1 之后斜率增加
            uint slope2 = (maxRate - kink1) / 0.2e18;
            return kink1 + slope2 * (utilization - 0.8e18) / 1e18;
        }
    }

    function getSupplyRate(uint cash, uint borrows, uint reserves) public view returns (uint) {
        uint borrowRate = getBorrowRate(cash, borrows, reserves);
        uint spread = borrowRate - 0.02e18;
        return borrowRate * (cash - reserves) / (cash + borrows);
    }
}
```

**抵押品计算**：
```solidity
// 抵押品价值计算
function calculateCollateralValue(
    address asset,
    uint amount,
    address priceFeed
) public view returns (uint) {
    // 从价格预言机获取资产价格
    uint price = AggregatorV3Interface(priceFeed).latestAnswer(asset, asset);

    // 计算抵押品价值（以 ETH 为单位）
    return price * amount;
}

// 最大可借额度
function getMaxBorrowAmount(
    uint collateralValue,
    uint collateralFactor,  // 例如 0.75 (75%）
    uint price
) public pure returns (uint) {
    return (collateralValue * collateralFactor * 1e18) / price;
}
```

**清算机制**：
```solidity
// 清算人激励
function liquidate(
    address borrower,
    address[] calldata collateralTokens,
    uint[] calldata collateralAmounts,
    address debtToken,
    uint debtAmount,
    address liquidator,
    address recipient
) public {
    // 计算未偿还债务
    uint debtOwed = cTokens[debtToken].borrowBalanceCurrent(borrower);

    // 检查抵押品价值是否充足
    uint collateralValue = calculateCollateralValue(collateralTokens[0], collateralAmounts[0], priceFeed);
    uint borrowLimit = getMaxBorrowAmount(collateralValue, collateralFactor, price);

    require(collateralValue >= borrowLimit * 1e18, "Collateral not sufficient");

    // 清算抵押品
    for (uint i = 0; i < collateralTokens.length; i++) {
        ERC20(collateralTokens[i]).safeTransfer(borrower, msg.sender, collateralAmounts[i]);
    }

    // 偿还债务
    cTokens[debtToken].borrowBalanceCurrent(liquidator) += debtOwed;

    // 清算激励（通常 0.5% 抵押品价值）
    uint incentiveAmount = collateralValue / 200;

    if (msg.sender != borrower) {
        cTokens[debtToken].transfer(liquidator, incentiveAmount);
    }
}
```

### Aave V3

**核心改进**：
- **Portal**: 集成借贷和 AMM，减少滑点
- **隔离模式**: 支持 Uniswap V3 集中流动性
- **风险参数**: 多档利率模型

**Portal 合约**：
```solidity
// Aave V3 Portal
contract AaveV3Portal is IPoolAddressesProvider {
    function getPool(
        address market,
        address reserve
    ) external view returns (address) {
        // 返回对应的 AMM 池
        IPoolAddressesProvider.PoolAddresses memory poolAddresses = poolAddressesProvider.getPoolAddresses(market, reserve);

        // 返回 Uniswap V3 池地址
        return poolAddresses.uniswapV3DexPool;
    }
}
```

---

## 🔮 衍生品

### 永续合约（Perpetuals）

**核心机制**：
- **无清算**：通过资金池和标记价格机制
- **多空双向**：支持做多和做空
- **杠杆交易**：通过保证金增加头寸

**订单簿**：
```solidity
// 简化的订单簿
contract OrderBook {
    struct Order {
        address trader;
        bool isBuy;
        uint128 price;
        uint128 amount;
        uint32 time;
    }

    mapping(bytes32 => Order) public orders;

    // 提交订单
    function placeLimitOrder(
        uint128 price,
        uint128 amount,
        bool isBuy
    ) external returns (bytes32 orderId) {
        // 创建订单
        Order memory order = Order({
            trader: msg.sender,
            isBuy: isBuy,
            price: price,
            amount: amount,
            time: uint32(block.timestamp)
        });

        bytes32 orderIdHash = keccak256(abi.encode(order));
        orders[orderIdHash] = order;

        // 匹配订单
        _matchOrders();

        return orderIdHash;
    }

    // 匹配订单
    function _matchOrders() internal {
        // 简化的撮合逻辑
        Order[] memory bestBid = _getBestBid();
        Order[] memory bestAsk = _getBestAsk();

        if (bestBid.price >= bestAsk.price) {
            // 订单匹配
            _executeTrade(bestBid, bestAsk);
        }
    }

    function _getBestBid() internal view returns (Order[] memory) {
        // 获取最高买单
        // 实现省略
    }

    function _getBestAsk() internal view returns (Option[] memory) {
        // 获取最低卖单
        // 实现省略
    }

    function _executeTrade(Order memory bid, Option memory ask) internal {
        // 执行交易
        require(bid.trader != ask.trader, "Self-match not allowed");

        // 转账
        ERC20(bidToken).transferFrom(bid.trader, ask.trader, bid.amount);
        ERC20(askToken).transferFrom(ask.trader, bid.trader, ask.amount);
    }
}
```

**资金池和标记价格**：
```solidity
// 资金池
contract Vault {
    mapping(address => uint256) public userBalances;

    function deposit(uint256 amount) external {
        ERC20(token).transferFrom(msg.sender, address(this), amount);
        userBalances[msg.sender] += amount;
    }

    function withdraw(uint256 amount) external {
        require(userBalances[msg.sender] >= amount, "Insufficient balance");
        userBalances[msg.sender] -= amount;
        ERC20(token).transfer(msg.sender, amount);
    }
}

// 标记价格
contract Oracle is AggregatorV3Interface {
    function latestRoundData(
        bytes[] calldata tokens
    ) external view returns (
        uint80[] memory roundIds,
        int256[] memory answers,
        uint256[] memory startedAts,
        uint256[] memory updatedAts,
        uint80[] memory answeredInRounds
    );
}
```

---

## 📊 稳定币协议

### DSR（Dai Savings Rate）

**核心机制**：
- **自动再投资**：将 DAI 借入协议中
- **利息累积**：基于当前利率动态调整
- **即时提取**：用户可以随时提取

**利息计算**：
```solidity
// DSR 合约
contract Pot {
    mapping(address => uint256) public chi;  // 存款指数

    uint public RAY = 10 ** 27;  // 每秒 1e27 单位的利息增长
    uint256 internal constant _chi = 10 ** 27;

    function _chiAccumulated(uint256 _timestamp) internal view returns (uint256) {
        // 计算自最后一次 rho 更新以来累积的 chi
        return _chi.mul(block.timestamp - _timestamp);
    }

    function dsr() external view returns (uint256) {
        // 计算年化收益率
        uint256 _chiAccumulated = _chiAccumulated(block.timestamp - _rho);
        uint256 _pie = _pie.add(_chiAccumulated);
        return _pie.mul(RAY) / _pie.sub(_chiAccumulated) - 1;
    }

    function join(uint256 wad) external {
        // 存款到 DSR
        uint256 _chiAccumulated = _chiAccumulated(block.timestamp - _rho);
        uint256 _pie = _pie.add(_chiAccumulated);

        uint256 pie = _pie.sub(_chiAccumulated); // 转换为 pie
        uint256 chi = pie.mul(_chiAccumulated).div(_pie);  // 转换为 chi

        ERC20(dai).transferFrom(msg.sender, address(this), wad);

        // 更新用户余额
        pie[msg.sender] = pie.add(chi);
    }

    function exit(uint256 wad) external {
        // 从 DSR 提款
        uint256 _chiAccumulated = _chiAccumulated(block.timestamp - _rho);
        uint256 _pie = _pie.add(_chiAccumulated);

        uint256 pie = pie[msg.sender];
        uint256 chi = chi.mul(_chiAccumulated).div(_pie);

        // 更新用户余额
        pie[msg.sender] = pie.sub(chi);

        // 转回 DAI
        uint256 _pie = pie.sub(_chiAccumulated); // 转换为 pie
        uint256 _wad = _pie.mul(_chiAccumulated).div(_pie);  // 转换为 wad

        require(_wad >= wad, "Insufficient balance");
        ERC20(dai).transfer(msg.sender, wad);
    }
}
```

---

## 🎯 学习路径

### 初级阶段
- [ ] 理解 AMM 基本原理
- [ ] 学习简单的借贷协议逻辑
- [ ] 理解价格预言机的作用

### 中级阶段
- [ ] 深入研究 Uniswap V2/V3 数学模型
- [ ] 学习 Compound 利率模型
- [ ] 理解清算机制和风险参数

### 高级阶段
- [ ] 研究复杂的衍生品策略
- [ ] 学习做市商算法和订单簿
- [ ] 理解风险管理和对冲策略

### 实践阶段
- [ ] 使用 Foundry 测试 AMM 合约
- [ ] 部署简单的借贷协议
- [ ] 集成多个 DeFi 协议

---

## 📚 参考资源

### Uniswap V2
- [ ] Whitepaper: https://uniswap.org/whitepaper-v2.pdf
- [ ] Documentation: https://docs.uniswap.org/protocol/V2/introduction

### Uniswap V3
- [ ] Whitepaper: https://uniswap.org/whitepaper-v3.pdf
- [ ] Documentation: https://docs.uniswap.org/protocol/V3/introduction

### Compound
- [ ] Whitepaper: https://compound.finance/documents/Compound.Whitepaper.pdf
- [ ] Documentation: https://docs.compound.finance/

### Aave
- [ ] Whitepaper: https://github.com/aave/aave-v3-whitepaper
- [ ] Documentation: https://docs.aave.com/

---

**创建时间**: 2026-02-03
**学习目标**: 深入理解 DeFi 协议
**难度级别**: 中级到高级
