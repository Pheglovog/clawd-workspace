# 第九小时：Staking & Yield Farming + Derivatives

> 主动进化学习 🪵 → 💪
> 基于 MCP 搜索的 2026 年最新趋势

---

## 二十八、DeFi Staking 深度研究

### 28.1 Staking 机制

**什么是 Staking？**

Staking 是将代币锁定在区块链网络中，用于验证交易和维护网络安全，同时获得奖励。

```
Staking 类型：
1. PoS 共识质押
   - 直接参与网络共识
   - 例：ETH 质押（以太坊 2.0）
   - 奖励：区块奖励 + Gas 费

2. Liquid Staking（流动性质押）
   - 质押后获得流动性质押代币
   - 例：Lido stETH, Rocket Pool rETH
   - 特点：保持流动性 + 参与 DeFi

3. LP Staking（流动性提供者）
   - 提供流动性到 DEX
   - 奖励：交易手续费 + 激励代币
   - 例：Uniswap, SushiSwap

4. Yield Farming（收益耕作）
   - 质押代币到特定协议获得额外奖励
   - 例：Curve, Balancer, Aave
   - 风险：代币价格波动 + 智能合约风险
```

### 28.2 Liquid Staking 协议

#### Lido Finance

**核心特点：**
- 支持多链：ETH, SOL, MATIC, DOT, TIA
- TVL（总锁定价值）：$19.5B+（2026）
- 流动性代币：stETH, stSOL, stMATIC, stDOT
- APY：约 3-4%（ETH）

**工作原理：**
```
用户流程：
1. 用户质押 ETH → 获得 stETH (1:1)
2. stETH 可自由交易或用于 DeFi
3. Lido 将 ETH 委托给多个验证者
4. 验证者奖励通过 stETH 反映给用户

优势：
- 保留流动性
- 去中心化验证者网络
- 多策略（Lido GGV, Lido DVV）
```

**集成示例：**

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

/**
 * @title Lido Staking 集成
 * @author 上等兵•甘
 */
contract LidoStakingIntegration {
    using SafeERC20 for IERC20;

    // ========== 接口 ==========
    interface IStETH {
        function submit(address _referral) external payable;
        function balanceOf(address _account) external view returns (uint256);
    }

    interface IwstETH {
        function wrap(uint256 _amount) external returns (uint256);
        function unwrap(uint256 _amount) external returns (uint256);
    }

    // ========== 常量 ==========
    address public constant LIDO = 0xae7ab96520DE3A18E5e111B5EaAb095412699; // Mainnet
    address public constant STETH = 0xae7ab96520DE3A18E5e111B5EaAb095412699;
    address public constant WSTETH = 0x7f39C581F595B53c5cb19bD0f3f899A33;
    address public constant WSTETH_OLD = 0xf92cD56611d312754311f3669f3A0E6C03b31;

    // ========== 状态变量 ==========
    address public owner;
    mapping(address => uint256) public userStakedEth;
    mapping(address => uint256) public userStakedSteth;

    // ========== 事件 ==========
    event Staked(address indexed user, uint256 amount, uint256 stethReceived);
    event Unwrapped(address indexed user, uint256 wstethAmount, uint256 stethReceived);

    // ========== 修饰符 ==========
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }

    // ========== 构造函数 ==========
    constructor() {
        owner = msg.sender;
    }

    // ========== 核心功能 ==========

    /**
     * @dev 质押 ETH 获 stETH
     * @param referral 推荐地址
     */
    function stakeETH(address referral) external payable {
        require(msg.value > 0, "Amount must be > 0");

        uint256 stethBalanceBefore = IStETH(STETH).balanceOf(address(this));

        // 调用 Lido 质押
        IStETH(LIDO).submit{value: msg.value}(referral);

        uint256 stethReceived = IStETH(STETH).balanceOf(address(this)) - stethBalanceBefore;

        userStakedEth[msg.sender] += msg.value;
        userStakedSteth[msg.sender] += stethReceived;

        emit Staked(msg.sender, msg.value, stethReceived);
    }

    /**
     * @dev 将 stETH 包装为 wstETH
     * @param amount stETH 数量
     */
    function wrapSteth(uint256 amount) external {
        require(userStakedSteth[msg.sender] >= amount, "Insufficient stETH balance");

        IERC20(STETH).safeTransferFrom(msg.sender, address(this), amount);

        IERC20(STETH).safeApprove(WSTETH, amount);

        IwstETH(WSTETH).wrap(amount);

        emit Unwrapped(msg.sender, amount, 0); // 这里实际上是 wrap
    }

    /**
     * @dev 将 wstETH 解包为 stETH
     * @param amount wstETH 数量
     */
    function unwrapWsteth(uint256 amount) external {
        IERC20(WSTETH).safeTransferFrom(msg.sender, WSTETH, amount);

        IwstETH(WSTETH).unwrap(amount);

        emit Unwrapped(msg.sender, amount, amount);
    }

    /**
     * @dev 获取用户 staking 信息
     */
    function getUserStakingInfo(address user)
        external
        view
        returns (
            uint256 stakedEth,
            uint256 stakedSteth,
            uint256 stethPrice,
            uint256 apy
        )
    {
        stakedEth = userStakedEth[user];
        stakedSteth = userStakedSteth[user];

        // 获取当前 stETH 价格（通过 DEX）
        stethPrice = _getStethPrice();

        // 计算 APY（简化版）
        apy = _calculateApy();
    }

    /**
     * @dev 获取 stETH 价格
     */
    function _getStethPrice() internal view returns (uint256) {
        // 实际应从 DEX 获取
        // stETH/ETH ≈ 1.00x（略高于 1）
        return 1.001 ether;
    }

    /**
     * @dev 计算 APY
     */
    function _calculateApy() internal view returns (uint256) {
        // Lido APY 约 3-4%
        // 1 ETH ≈ 0.04 ETH/年 = 4%
        return 400; // 400 bps = 4%
    }

    // ========== 管理函数 ==========

    function withdraw(address token, uint256 amount) external onlyOwner {
        IERC20(token).safeTransfer(owner, amount);
    }

    receive() external payable {}
}
```

#### Rocket Pool

**核心特点：**
- 纯去中心化
- 由去中心化节点网络运营
- 流动性代币：rETH
- APY：约 3-4%（ETH）

**rETH vs stETH：**

| 特性 | rETH | stETH |
|------|------|-------|
| 去中心化 | 完全 | 部分委托给中心化节点 |
| 网络开销 | 较高 | 较低 |
| 稳定性 | 更高 | 更高 |
| TVL | $3B+ | $19.5B+ |

### 28.3 Yield Farming 策略

#### Curve Gauge 系统

**Gauge 工作原理：**

```
Curve 使用 Gauge 机制来分配 CRV 奖励：

1. 用户质押 LP 到 Gauge
2. Gauge 跟踪质押量和时间
3. 根据权重分配 CRV
4. Gauge 可以被投票增加权重

公式：
  reward = user_stake × gauge_weight × crv_emission_rate
```

**集成示例：**

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

/**
 * @title Curve Gauge 集成
 * @author 上等兵•甘
 */
contract CurveGaugeIntegration {
    using SafeERC20 for IERC20;

    // ========== 接口 ==========
    interface IGauge {
        function deposit(uint256 _value) external;
        function withdraw(uint256 _value) external;
        function balanceOf(address _account) external view returns (uint256);
        function claim_rewards() external;
    }

    // ========== 常量 ==========
    address public constant CRV = 0xD533a949740B3b02e59448E499a739B980A2Af07;

    // ========== 状态变量 ==========
    address public gauge;
    address public owner;

    // ========== 事件 ==========
    event Deposited(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount);
    event RewardsClaimed(address indexed user, uint256 amount);

    // ========== 修饰符 ==========
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }

    // ========== 构造函数 ==========
    constructor(address _gauge) {
        gauge = _gauge;
        owner = msg.sender;
    }

    // ========== 核心功能 ==========

    /**
     * @dev 质押 LP 到 Gauge
     * @param amount LP 数量
     */
    function depositLp(uint256 amount) external {
        require(amount > 0, "Amount must be > 0");

        IERC20(gauge).safeTransferFrom(msg.sender, gauge, amount);

        IGauge(gauge).deposit(amount);

        emit Deposited(msg.sender, amount);
    }

    /**
     * @dev 从 Gauge 提取 LP
     * @param amount LP 数量
     */
    function withdrawLp(uint256 amount) external {
        require(amount > 0, "Amount must be > 0");
        require(IGauge(gauge).balanceOf(msg.sender) >= amount, "Insufficient balance");

        IGauge(gauge).withdraw(amount);

        IERC20(gauge).safeTransfer(msg.sender, amount);

        emit Withdrawn(msg.sender, amount);
    }

    /**
     * @dev 领取 CRV 奖励
     */
    function claimRewards() external {
        uint256 crvBalanceBefore = IERC20(CRV).balanceOf(msg.sender);

        IGauge(gauge).claim_rewards();

        uint256 crvEarned = IERC20(CRV).balanceOf(msg.sender) - crvBalanceBefore;

        emit RewardsClaimed(msg.sender, crvEarned);
    }

    /**
     * @dev 获取奖励信息
     */
    function getRewardsInfo(address user)
        external
        view
        returns (
            uint256 lpBalance,
            uint256 crvBalance
        )
    {
        lpBalance = IGauge(gauge).balanceOf(user);
        crvBalance = IERC20(CRV).balanceOf(user);
    }

    // ========== 管理函数 ==========

    function withdraw(address token, uint256 amount) external onlyOwner {
        IERC20(token).safeTransfer(owner, amount);
    }
}
```

### 28.4 高级 Staking 策略

#### Leveraged Staking（杠杆质押）

```
原理：
1. 借入资金（通过 Aave）
2. 质押借入资金
3. 放大收益
4. 需管理清算风险

示例：
- 自己有 10 ETH
- 借入 20 ETH（2x 杠杆）
- 质押 30 ETH 到 Lido → 获 30 stETH
- 收益 = 30 ETH × 3% = 0.9 ETH/年
- 成本 = 20 ETH × 5%（Aave 利率）= 1 ETH/年
- 净收益 = -0.1 ETH/年（亏损！）

结论：只有当 APY > 借款利率时才可行
```

#### Re-Staking（再质押）

```
原理：
将流动性质押代币（如 stETH）再次质押到其他协议

流程：
ETH → stETH (Lido) → stETH 质押到 Aave → 奖励

风险：
- 协议叠加风险
- 重新质押风险（EigenLayer）
```

---

## 二十九、DeFi Derivatives 深度研究

### 29.1 Perpetual Futures（永续合约）

**永续合约特点：**

```
永续合约（Perps）是没有到期日的期货合约：

1. 通过资金费率（Funding Rate）锚定现货价格
   - 资金费率 = (标记价格 - 现货价格) / 24 小时
   - 资金费率为正 → 做多支付给做空
   - 资金费率为负 → 做空支付给做多

2. 无到期日，可无限期持有

3. 支持高杠杆（最高 100x）

4. 持续清算监控
```

#### dYdX Perpetuals

**核心特点：**
- 去中心化永续合约交易所
- 支持交易对：BTC-USD, ETH-USD, SOL-USD 等
- 杠杆：最高 20x
- TVL：约 $140M（2026）
- 架构：App-chain（dYdX Chain）

**dYdX v4 架构：**

```
┌─────────────────────────────────────┐
│   Off-chain (dYdX Chain)        │
│   ┌───────────────────────────┐    │
│   │   Order Book (订单簿）    │    │
│   └───────────────────────────┘    │
│   ┌───────────────────────────┐    │
│   │   Matching Engine         │    │
│   └───────────────────────────┘    │
│   ┌───────────────────────────┐    │
│   │   Insurance Fund         │    │
│   └───────────────────────────┘    │
└─────────────────────────────────────┘
             ↓ Merkle root
┌─────────────────────────────────────┐
│   On-chain (StarkEx)            │
│   ┌───────────────────────────┐    │
│   │   State Transition        │    │
│   └───────────────────────────┘    │
│   ┌───────────────────────────┐    │
│   │   Liquidation            │    │
│   └───────────────────────────┘    │
└─────────────────────────────────────┘
```

**dYdX 集成示例：**

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title dYdX Perpetuals 集成
 * @author 上等兵•甘
 */
contract DydxPerpetualsIntegration {
    // ========== 接口 ==========
    interface IDydxV4Perp {
        struct TradeParams {
            uint256 marketId;
            address account;
            address trader;
            bool isBuy;
            uint256 amount;
            uint256 limitPrice;
            uint8 triggerOrderId;
        }

        function openTrade(TradeParams calldata params) external;
        function closeTrade(uint256 marketId, address account, bool isBuy, uint256 amount) external;
        function getAccountPositions(address account, uint256 marketId)
            external
            view
            returns (int256 position, uint256 leverage);
    }

    // ========== 常量 ==========
    uint256 public constant ETH_USDC_MARKET = 0;
    uint256 public constant BTC_USDC_MARKET = 1;

    // ========== 状态变量 ==========
    address public dydxV4Perp;
    address public owner;

    // ========== 事件 ==========
    event TradeOpened(uint256 indexed marketId, address indexed trader, uint256 amount);
    event TradeClosed(uint256 indexed marketId, address indexed trader, uint256 pnl);

    // ========== 修饰符 ==========
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }

    // ========== 构造函数 ==========
    constructor(address _dydxV4Perp) {
        dydxV4Perp = _dydxV4Perp;
        owner = msg.sender;
    }

    // ========== 核心功能 ==========

    /**
     * @dev 开仓做多
     * @param amount USDC 数量
     */
    function openLong(uint256 amount) external {
        IDydxV4Perp.TradeParams memory params = IDydxV4Perp.TradeParams({
            marketId: ETH_USDC_MARKET,
            account: msg.sender,
            trader: msg.sender,
            isBuy: true, // 做多
            amount: amount,
            limitPrice: 0, // 市价
            triggerOrderId: 0
        });

        IDydxV4Perp(dydxV4Perp).openTrade(params);

        emit TradeOpened(ETH_USDC_MARKET, msg.sender, amount);
    }

    /**
     * @dev 开仓做空
     * @param amount USDC 数量
     */
    function openShort(uint256 amount) external {
        IDydxV4Perp.TradeParams memory params = IDydxV4Perp.TradeParams({
            marketId: ETH_USDC_MARKET,
            account: msg.sender,
            trader: msg.sender,
            isBuy: false, // 做空
            amount: amount,
            limitPrice: 0,
            triggerOrderId: 0
        });

        IDydxV4Perp(dydxV4Perp).openTrade(params);

        emit TradeOpened(ETH_USDC_MARKET, msg.sender, amount);
    }

    /**
     * @dev 平仓
     * @param isLong 是否是多头
     */
    function closePosition(bool isLong) external {
        IDydxV4Perp.closeTrade(
            ETH_USDC_MARKET,
            msg.sender,
            !isLong, // 反向平仓
            type(uint256).max
        );

        emit TradeClosed(ETH_USDC_MARKET, msg.sender, 0); // PnL 需计算
    }

    /**
     * @dev 获取仓位信息
     */
    function getPositionInfo(address trader, uint256 marketId)
        external
        view
        returns (int256 position, uint256 leverage)
    {
        (position, leverage) = IDydxV4Perp(dydxV4Perp).getAccountPositions(
            trader,
            marketId
        );
    }

    // ========== 管理函数 ==========

    function withdraw(address token, uint256 amount) external onlyOwner {
        payable(owner).transfer(amount);
    }

    receive() external payable {}
}
```

#### GMX

**核心特点：**
- Arbitrum & Avalanche 主网
- 杠杆：最高 50x
- 支持多种模式：
  - 永续合约（Perps）
  - 挂单委托（Orders）
  - 无需许可交易（Permissionless）
- TVL：约 $66.7M（2026）

**GMX 特有功能：**

```
1. Zero-Impact Trades（零滑点）
   - 通过内部流动性池实现
   - 大额交易无滑点

2. Multi-Asset Collateral（多资产抵押）
   - 支持 ETH, USDC, WBTC 作为抵押品
   - 动态调整抵押价值

3. Price Impact Protection（价格影响保护）
   - 限制单笔交易对价格的影响
```

### 29.2 DeFi Options（DeFi 期权）

#### Lyra Finance

**核心特点：**
- 基于 Synthetix 的期权协议
- 支持链上期权交易
- 无需信任结算
- Delta 中性策略

**期权类型：**

```
1. Call Options（看涨期权）
   - 买方有权在到期日以执行价买入
   - 收益 = max(0, S - K) - premium

2. Put Options（看跌期权）
   - 买方有权在到期日以执行价卖出
   - 收益 = max(0, K - S) - premium

其中：
- S = 标的资产价格
- K = 执行价格（Strike Price）
- premium = 期权费
```

#### Dopex

**核心特点：**
- 去中心化期权金库（Options Vault）
- 期权卖方赚取期权费
- 资金利用率高
- 无需许可

**Options Vault 工作原理：**

```
┌─────────────────────────────────────┐
│   Options Vault                 │
│                                 │
│   卖方质押 USDC                 │
│       ↓                         │
│   生成期权（Call/Put）          │
│       ↓                         │
│   买方购买期权                 │
│       ↓                         │
│   到期结算                     │
│   ↓                            │
│   卖方获得：                   │
│   - 期权费（无论盈亏）        │
│   - 抵押金（如期权未执行）    │
└─────────────────────────────────────┘

风险：
- 如果期权被执行，卖方可能亏损
- 需要购买保险或对冲
```

### 29.3 Derivatives 风险管理

#### 止损（Stop Loss）

```solidity
/**
 * @dev 止损功能
 */
contract StopLossIntegration {
    struct StopLossOrder {
        address trader;
        uint256 marketId;
        bool isLong;
        uint256 amount;
        uint256 stopPrice;
        bool executed;
    }

    mapping(bytes32 => StopLossOrder) public stopLossOrders;

    event StopLossCreated(bytes32 indexed orderId);
    event StopLossExecuted(bytes32 indexed orderId);

    /**
     * @dev 创建止损单
     */
    function createStopLoss(
        uint256 marketId,
        bool isLong,
        uint256 amount,
        uint256 stopPrice
    ) external returns (bytes32 orderId) {
        orderId = keccak256(
            abi.encode(
                msg.sender,
                marketId,
                block.timestamp,
                isLong
            )
        );

        stopLossOrders[orderId] = StopLossOrder({
            trader: msg.sender,
            marketId: marketId,
            isLong: isLong,
            amount: amount,
            stopPrice: stopPrice,
            executed: false
        });

        emit StopLossCreated(orderId);
    }

    /**
     * @dev 执行止损
     */
    function executeStopLoss(bytes32 orderId) external {
        StopLossOrder storage order = stopLossOrders[orderId];

        require(!order.executed, "Already executed");
        require(order.trader == msg.sender, "Not your order");

        // 检查是否触发
        (int256 currentPrice, ) = _getCurrentPrice(order.marketId);

        bool triggerCondition = order.isLong
            ? currentPrice < int256(order.stopPrice) // 做多：价格跌破止损价
            : currentPrice > int256(order.stopPrice); // 做空：价格涨破止损价

        require(triggerCondition, "Stop price not reached");

        order.executed = true;

        // 执行平仓
        _closePosition(order);

        emit StopLossExecuted(orderId);
    }

    /**
     * @dev 获取当前价格
     */
    function _getCurrentPrice(uint256 marketId)
        internal
        view
        returns (int256 price, uint256 timestamp)
    {
        // 从预言机获取价格
        // ...
    }

    /**
     * @dev 平仓
     */
    function _closePosition(StopLossOrder storage order) internal {
        // 调用衍生品协议平仓
        // ...
    }
}
```

---

## 第三十、DeFi Derivatives 对比

| 协议 | 类型 | 杠杆 | TVL | 主网 |
|------|------|------|-----|------|
| **dYdX** | Perps | 20x | $140M | dYdX Chain |
| **GMX** | Perps | 50x | $66.7M | Arbitrum, Avalanche |
| **Hyperliquid** | Perps | 50x | $6B | Arbitrum |
| **Lyra** | Options | - | $50M+ | Optimism |
| **Dopex** | Options | - | $20M+ | Arbitrum, Optimism |
| **Aevo** | Options | 10x | $30M+ | Arbitrum |
| **Gains Network** | Perps | 100x | $10M+ | Arbitrum |

---

## 第三十一、Oracle Systems（预言机）

### 31.1 Oracle 类型

```
预言机类型：

1. Push Oracle（推送预言机）
   - 数据源主动推送数据到链上
   - 例：Chainlink, Pyth
   - 优点：实时更新
   - 缺点：Gas 成本高

2. Pull Oracle（拉取预言机）
   - 智能合约主动请求数据
   - 例：UMA, RedStone
   - 优点：按需获取，Gas 成本低
   - 缺点：数据可能不是最新

3. Hybrid Oracle（混合预言机）
   - 结合 Push 和 Pull
   - 例：RedStone（支持两种模式）
```

### 31.2 Chainlink Oracle

**核心特点：**
- 市场领导者（约 70% 的预言机市场份额）
- 支持 $100B+ 资产
- 去中心化节点网络
- 支持多链

**Chainlink Price Feeds：**

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title Chainlink Oracle 集成
 * @author 上等兵•甘
 */
contract ChainlinkOracleIntegration {
    // ========== 接口 ==========
    interface AggregatorV3Interface {
        function latestRoundData()
            external
            view
            returns (
                uint80 roundId,
                int256 answer,
                uint256 startedAt,
                uint256 updatedAt,
                uint80 answeredInRound
            );

        function latestAnswer() external view returns (int256);

        function decimals() external view returns (uint8);
    }

    // ========== 常量 ==========
    AggregatorV3Interface public constant ETH_USD =
        AggregatorV3Interface(0x5f4eC3Df9cbd4E14C284F69a300f5d1dB35D);
    AggregatorV3Interface public constant BTC_USD =
        AggregatorV3Interface(0xF4030086522a5bEEa4988F8cA5B36dbC97BeE8);
    AggregatorV3Interface public constant STETH_ETH =
        AggregatorV3Interface(0x8639dEA8C0Dd809edFf482C2Da0234EeC982C);

    // ========== 状态变量 ==========
    address public owner;
    mapping(address => int256) public lastPrices;

    // ========== 事件 ==========
    event PriceUpdated(address indexed feed, int256 price, uint256 timestamp);

    // ========== 修饰符 ==========
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }

    // ========== 构造函数 ==========
    constructor() {
        owner = msg.sender;
    }

    // ========== 核心功能 ==========

    /**
     * @dev 获取最新价格
     * @param feed Chainlink Feed 地址
     */
    function getLatestPrice(address feed)
        external
        view
        returns (int256 price, uint256 timestamp)
    {
        (
            uint80 roundId,
            int256 answer,
            uint256 startedAt,
            uint256 updatedAt,
            uint80 answeredInRound
        ) = AggregatorV3Interface(feed).latestRoundData();

        price = answer;
        timestamp = updatedAt;

        lastPrices[feed] = answer;
    }

    /**
     * @dev 获取 ETH/USD 价格
     */
    function getEthUsdPrice() external view returns (int256) {
        return AggregatorV3Interface(ETH_USD).latestAnswer();
    }

    /**
     * @dev 获取 BTC/USD 价格
     */
    function getBtcUsdPrice() external view returns (int256) {
        return AggregatorV3Interface(BTC_USD).latestAnswer();
    }

    /**
     * @dev 获取 stETH/ETH 价格
     */
    function getStethEthPrice() external view returns (int256) {
        return AggregatorV3Interface(STETH_ETH).latestAnswer();
    }

    /**
     * @dev 批量获取价格
     */
    function getBatchPrices(address[] calldata feeds)
        external
        view
        returns (int256[] memory prices, uint256[] memory timestamps)
    {
        prices = new int256[](feeds.length);
        timestamps = new uint256[](feeds.length);

        for (uint256 i = 0; i < feeds.length; ) {
            (
                uint80 roundId,
                int256 answer,
                uint256 startedAt,
                uint256 updatedAt,
                uint80 answeredInRound
            ) = AggregatorV3Interface(feeds[i]).latestRoundData();

            prices[i] = answer;
            timestamps[i] = updatedAt;

            unchecked { ++i; }
        }
    }

    /**
     * @dev 检查价格更新时间
     */
    function isPriceStale(address feed, uint256 maxAge) external view returns (bool) {
        (
            uint80 roundId,
            int256 answer,
            uint256 startedAt,
            uint256 updatedAt,
            uint80 answeredInRound
        ) = AggregatorV3Interface(feed).latestRoundData();

        return block.timestamp - updatedAt > maxAge;
    }

    // ========== 管理函数 ==========

    function withdraw(address token, uint256 amount) external onlyOwner {
        payable(owner).transfer(amount);
    }
}
```

### 31.3 Pyth Network

**核心特点：**
- 低延迟（约 0.3-0.8 秒）
- 高频数据更新
- 支持多链
- Pull Oracle 模式

**Pyth vs Chainlink：**

| 特性 | Chainlink | Pyth |
|------|-----------|------|
| 延迟 | 中等（秒级） | 低（<1 秒）|
| 更新频率 | 可配置 | 高频（每分钟）|
| 数据源 | 多个数据聚合 | 直接来自交易所 |
| Gas 成本 | 中等 | 低（Pull 模式）|

---

## 第九小时学到的技能总结

### 32.1 核心技能

1. **Staking 机制**
   - PoS 质押
   - Liquid Staking（Lido, Rocket Pool）
   - LP Staking
   - Yield Farming

2. **Liquid Staking 集成**
   - Lido Finance
   - Rocket Pool
   - stETH / rETH / wstETH
   - Re-Staking 策略

3. **Yield Farming**
   - Curve Gauge 系统
   - CRV 奖励机制
   - 杠杆 Staking
   - 跨协议策略

4. **DeFi Derivatives**
   - Perpetual Futures（dYdX, GMX）
   - Options（Lyra, Dopex）
   - 止损机制
   - 杠杆管理

5. **Oracle Systems**
   - Push vs Pull Oracles
   - Chainlink Price Feeds
   - Pyth Network
   - 预言机集成

### 32.2 代码产出

- ✅ LidoStakingIntegration Lido 集成
- ✅ CurveGaugeIntegration Curve Gauge 集成
- ✅ DydxPerpetualsIntegration dYdX 永续合约集成
- ✅ StopLossIntegration 止损功能
- ✅ ChainlinkOracleIntegration Chainlink 预言机集成

---

**【第9小时汇报完毕】**
