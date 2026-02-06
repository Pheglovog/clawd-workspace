# 第八小时：DeFi DEX 协议深度研究

---

## 二十四、Uniswap V3 深度解析

### 24.1 核心创新：集中流动性

**Uniswap V2 vs V3 对比：**

| 特性 | Uniswap V2 | Uniswap V3 |
|------|------------|-------------|
| 流动性分布 | 均匀分布（0 → ∞） | 可自定义区间 |
| 资金效率 | ~0.01% | **x4000** (理论最大值） |
| 费用层级 | 固定 0.3% | 4 个层级（0.01%, 0.05%, 0.3%, 1%） |
| 流动性代币 | ERC-20 (LP Token) | ERC-721 (NFT Position) |
| Range Orders | 不支持 | 支持 |

**集中流动性原理：**

```
Uniswap V2：
|--------|--------|--------|--------|--------|--------|----|
  $1700    $1800    $1900    $2000    $2100    $2200
  ↑
  资金均匀分布在 $0 → ∞

Uniswap V3（在 $1900-$2000 之间提供流动性）：
              |████████|
              $1900    $2000
                ↑
  资金集中在 $1900-$2000 区间

结果：
- 同等资金下，V3 的有效深度是 V2 的 10 倍
- 在 $1900-$2000 区间内，滑点减少 90%
```

### 24.2 Tick 和区间机制

**Tick 系统原理：**

```
价格转换公式：
price = 1.0001^tick

反公式：
tick = floor(log(price) / log(1.0001))

示例：
tick = 0  →  price = 1.0001^0 = 1
tick = 1  →  price = 1.0001^1 = 1.0001
tick = -1 →  price = 1.0001^(-1) ≈ 0.9999
tick = 100 →  price = 1.0001^100 ≈ 1.01

ETH 价格 $1,850 的 tick：
tick = floor(log(1850) / log(1.0001)) ≈ 233,866

Tick 间距：
- 0.01% 费用池：tickSpacing = 1
- 0.05% 费用池：tickSpacing = 10
- 0.3% 费用池：tickSpacing = 60
- 1% 费用池：tickSpacing = 200
```

**价格区间：**

```solidity
/**
 * @dev Tick 价格计算库
 */
library TickMath {
    uint256 internal constant MIN_SQRT_RATIO = 4295128739;
    uint256 internal constant MAX_SQRT_RATIO = 146144670348521010928682265947820054505766274508752;

    /**
     * @dev 从 tick 获取 sqrt(P * Q)
     * @param tick Tick 值
     * @return sqrtPriceX96 sqrt(P * Q) * 2^96
     */
    function getSqrtRatioAtTick(
        int24 tick
    ) internal pure returns (uint160 sqrtPriceX96) {
        uint256 absTick = tick < 0 ? uint256(-int256(tick)) : uint256(int256(tick));

        uint256 ratio = absTick & 0x1 != 0
            ? 0xfffcb933bd6fad37aa2d162d1a594001
            : 0x100000000000000000000000000000000000;

        if (absTick & 0x2 != 0) ratio = (ratio * 0xfff97272373d413259a46990580e213a) >> 128;
        if (absTick & 0x4 != 0) ratio = (ratio * 0xfff2e50f5f656932ef12357cf3c7fdcc) >> 128;
        if (absTick & 0x8 != 0) ratio = (ratio * 0xffe5caca7e10e4e61c3624eaa0941cd0) >> 128;
        if (absTick & 0x10 != 0) ratio = (ratio * 0xffcb9843d60f6159c9db58835c926644) >> 128;
        if (absTick & 0x20 != 0) ratio = (ratio * 0xff973b41fa98c081472e6896dfb254c0) >> 128;
        if (absTick & 0x40 != 0) ratio = (ratio * 0xff9ea6e7f0a46c4a07b6e0f7d66a67c4) >> 128;
        if (absTick & 0x80 != 0) ratio = (ratio * 0xff68d8754545f5b471e2c7266c6e0b1e) >> 128;
        if (absTick & 0x100 != 0) ratio = (ratio * 0xff5757722c7f7b8e0819f7f8c5c6d3f4) >> 128;
        if (absTick & 0x200 != 0) ratio = (ratio * 0xff2a490e886f1f6b246a8f8a7241dc9) >> 128;
        if (absTick & 0x400 != 0) ratio = (ratio * 0xfef0506e6a4396645d60c5418388025c) >> 128;
        if (absTick & 0x800 != 0) ratio = (ratio * 0xfde5a4a8f5428b5900a766c709e6985) >> 128;
        if (absTick & 0x1000 != 0) ratio = (ratio * 0xfcba6dd2a702b22c4310708f5342c391) >> 128;
        if (absTick & 0x2000 != 0) ratio = (ratio * 0xf9c595878a40b7658c5e5038b062c5f3) >> 128;
        if (absTick & 0x4000 != 0) ratio = (ratio * 0xf4680900e906045d504d5571f606c0e1) >> 128;
        if (absTick & 0x8000 != 0) ratio = (ratio * 0xece538a9c68a0895b26a675e27f75d93) >> 128;
        if (absTick & 0x10000 != 0) ratio = (ratio * 0xe4d966c79f3cfb5e5459b0d289a7c2c7) >> 128;
        if (absTick & 0x20000 != 0) ratio = (ratio * 0xda7958237e5a8a7b3f60f40739a8178) >> 128;
        if (absTick & 0x40000 != 0) ratio = (ratio * 0xcf0f766f6b27f993b2373c569989f727) >> 128;
        if (absTick & 0x80000 != 0) ratio = (ratio * 0xc1e2ad657509061071e5f325c7264d1c) >> 128;
        if (absTick & 0x100000 != 0) ratio = (ratio * 0xb4895c3784b449481735c0579c596446) >> 128;
        if (absTick & 0x200000 != 0) ratio = (ratio * 0xa7a3d4d726d0b7a0116c422a25d8d2ee) >> 128;
        if (absTick & 0x400000 != 0) ratio = (ratio * 0x9b63c7d7e440e5076d5a69075d977616) >> 128;
        if (absTick & 0x800000 != 0) ratio = (ratio * 0x8f90e047a9a95541639f6485364653c36) >> 128;
        if (absTick & 0x1000000 != 0) ratio = (ratio * 0x846f0e7663856d5720455f953e2a4a5a) >> 128;
        if (absTick & 0x2000000 != 0) ratio = (ratio * 0x79b34440b5c972389093a41952778f0f9) >> 128;
        if (absTick & 0x4000000 != 0) ratio = (ratio * 0x6f8022d846a8c8725c424408024f0b63) >> 128;
        if (absTick & 0x8000000 != 0) ratio = (ratio * 0x664648f2838c8b802014c7d920758b04) >> 128;
        if (absTick & 0x10000000 != 0) ratio = (ratio * 0x5dbf86526c7394c8747764f9a56a90b8) >> 128;
        if (absTick & 0x20000000 != 0) ratio = (ratio * 0x557511d2b4b8365356b786a40f4951ca) >> 128;
        if (absTick & 0x40000000 != 0) ratio = (ratio * 0x4d7854404662660b07d3533e8e392918) >> 128;
        if (absTick & 0x80000000 != 0) ratio = (ratio * 0x4601d4829f5c1c3e1f6b2a7497e78a0d) >> 128;
        if (absTick & 0x100000000 != 0) ratio = (ratio * 0x3ea3d3a2e8c017312387c1c686c8f623) >> 128;
        if (absTick & 0x200000000 != 0) ratio = (ratio * 0x377d3a2c4d5496c6f7075a9e88d986f5) >> 128;
        if (absTick & 0x400000000 != 0) ratio = (ratio * 0x307535970904933738f4d9f5b930a787) >> 128;
        if (absTick & 0x800000000 != 0) ratio = (ratio * 0x29a6959b4b66c4478a4f998423b8776b) >> 128;
        if (absTick & 0x1000000000 != 0) ratio = (ratio * 0x236020453c742884d896a0b2cb7e669c6) >> 128;
        if (absTick & 0x2000000000 != 0) ratio = (ratio * 0x1d913c0e1b4c7c4e0c5847067b2b2538) >> 128;
        if (absTick & 0x4000000000 != 0) ratio = (ratio * 0x184942d818905dc057a7d8b7404570f97) >> 128;
        if (absTick & 0x8000000000 != 0) ratio = (ratio * 0x1323a052a621b5a50e86c2a710e89646) >> 128;
        if (absTick & 0x10000000000 != 0) ratio = (ratio * 0xe4c8d4c59679656a4735e9a56dc6c7975) >> 128;
        if (absTick & 0x20000000000 != 0) ratio = (ratio * 0xb6e080e04446894399b9d9d9e90e7575) >> 128;
        if (absTick & 0x40000000000 != 0) ratio = (ratio * 0x8c77e35e536748b625495e5689185521) >> 128;
        if (absTick & 0x80000000000 != 0) ratio = (ratio * 0x6504935118720f819a6db723a9d707c5) >> 128;
        if (absTick & 0x100000000000 != 0) ratio = (ratio * 0x40d0e088b9175c8e0689c8a7f725e8e2) >> 128;
        if (absTick & 0x200000000000 != 0) ratio = (ratio * 0x200d015829f91791835738e452d2af5f) >> 128;
        if (absTick & 0x400000000000 != 0) ratio = (ratio * 0x1085c6f7d0d032d0f766d3b7083cb86) >> 128;
        if (absTick & 0x800000000000 != 0) ratio = (ratio * 0x87a267f4a98c0b6c9b7b6c3c7266d7d) >> 128;
        if (absTick & 0x1000000000000 != 0) ratio = (ratio * 0x46746729c3220a3d27d6e1f7d8b7d3c) >> 128;
        if (absTick & 0x2000000000000 != 0) ratio = (ratio * 0x23a949a2d3d7c7d4b5e5a4a5d6c7d9e) >> 128;
        if (absTick & 0x4000000000000 != 0) ratio = (ratio * 0x11d5089e7f2d4a3f4b5e5a5d6c7d9e) >> 128;
        if (absTick & 0x8000000000000 != 0) ratio = (ratio * 0x8e8c0d4f6d5e4f3e2d1c0b9a8765432) >> 128;

        if (tick > 0) ratio = type(uint256).max / ratio;

        sqrtPriceX96 = uint160(
            (ratio >> 32) +
            (ratio % (1 << 32) == 0 ? 0 : 1)
        );

        require(
            sqrtPriceX96 >= MIN_SQRT_RATIO &&
            sqrtPriceX96 < MAX_SQRT_RATIO,
            'R'
        );
    }

    /**
     * @dev 从 sqrt(P * Q) 获取 tick
     * @param sqrtPriceX96 sqrt(P * Q) * 2^96
     * @return tick Tick 值
     */
    function getTickAtSqrtRatio(
        uint160 sqrtPriceX96
    ) internal pure returns (int24 tick) {
        require(
            sqrtPriceX96 >= MIN_SQRT_RATIO &&
            sqrtPriceX96 < MAX_SQRT_RATIO,
            'R'
        );

        uint256 ratio = uint256(sqrtPriceX96) << 32;

        uint256 r = ratio;
        uint256 msb = 0;

        assembly {
            let f := shl(7, gt(r, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF))
            msb := or(msb, f)
            r := shr(f, r)
        }

        assembly {
            let f := shl(6, gt(r, 0xFFFFFFFFFFFFFFFF))
            msb := or(msb, f)
            r := shr(f, r)
        }

        assembly {
            let f := shl(5, gt(r, 0xFFFFFFFF))
            msb := or(msb, f)
            r := shr(f, r)
        }

        assembly {
            let f := shl(4, gt(r, 0xFFFF))
            msb := or(msb, f)
            r := shr(f, r)
        }

        assembly {
            let f := shl(3, gt(r, 0xFF))
            msb := or(msb, f)
            r := shr(f, r)
        }

        assembly {
            let f := shl(2, gt(r, 0xF))
            msb := or(msb, f)
            r := shr(f, r)
        }

        assembly {
            let f := shl(1, gt(r, 0x3))
            msb := or(msb, f)
            r := shr(f, r)
        }

        assembly {
            let f := gt(r, 0x1)
            msb := or(msb, f)
        }

        if (msb >= 128) r = ratio >> (msb - 127);
        else r = ratio << (127 - msb);

        int256 log_2 = (int256(msb) - 128) << 64;

        assembly {
            r := shr(127, r)
            let f := shr(128, mul(r, r))
            log_2 := or(log_2, shl(63, f))
            r := shr(f, r)
        }

        assembly {
            let f := shr(127, mul(r, 0x2aaaaaaaaa))
            log_2 := or(log_2, shl(62, f))
            r := shr(f, r)
        }

        assembly {
            let f := shr(127, mul(r, 0x3513229e9a))
            log_2 := or(log_2, shl(61, f))
            r := shr(f, r)
        }

        assembly {
            let f := shr(127, mul(r, 0x49e5f415c9))
            log_2 := or(log_2, shl(60, f))
            r := shr(f, r)
        }

        assembly {
            let f := shr(127, mul(r, 0x5c7d4d7858))
            log_2 := or(log_2, shl(59, f))
            r := shr(f, r)
        }

        assembly {
            let f := shr(127, mul(r, 0x6c847d233f))
            log_2 := or(log_2, shl(58, f))
            r := shr(f, r)
        }

        assembly {
            let f := shr(127, mul(r, 0x7b6a6a6d3f))
            log_2 := or(log_2, shl(57, f))
            r := shr(f, r)
        }

        assembly {
            let f := shr(127, mul(r, 0x886c0c6c7c))
            log_2 := or(log_2, shl(56, f))
            r := shr(f, r)
        }

        assembly {
            let f := shr(127, mul(r, 0x9403a2610b))
            log_2 := or(log_2, shl(55, f))
            r := shr(f, r)
        }

        assembly {
            let f := shr(127, mul(r, 0x9e36f9480f))
            log_2 := or(log_2, shl(54, f))
            r := shr(f, r)
        }

        assembly {
            let f := shr(127, mul(r, 0xa706c89526))
            log_2 := or(log_2, shl(53, f))
            r := shr(f, r)
        }

        assembly {
            let f := shr(127, mul(r, 0xadc407c874))
            log_2 := or(log_2, shl(52, f))
            r := shr(f, r)
        }

        assembly {
            let f := shr(127, mul(r, 0xb413c4cd3e))
            log_2 := or(log_2, shl(51, f))
            r := shr(f, r)
        }

        assembly {
            let f := shr(127, mul(r, 0xbab87634b7))
            log_2 := or(log_2, shl(50, f))
            r := shr(f, r)
        }

        assembly {
            let f := shr(127, mul(r, 0xc06c3f0252))
            log_2 := or(log_2, shl(49, f))
            r := shr(f, r)
        }

        assembly {
            let f := shr(127, mul(r, 0xc5b6a5c698))
            log_2 := or(log_2, shl(48, f))
            r := shr(f, r)
        }

        assembly {
            let f := shr(127, mul(r, 0xcfd004742a))
            log_2 := or(log_2, shl(47, f))
            r := shr(f, r)
        }

        assembly {
            let f := shr(127, mul(r, 0xd9dd3c3a0d))
            log_2 := or(log_2, shl(46, f))
            r := shr(f, r)
        }

        assembly {
            let f := shr(127, mul(r, 0xe33c45966a))
            log_2 := or(log_2, shl(45, f))
            r := shr(f, r)
        }

        assembly {
            let f := shr(127, mul(r, 0xec42479b9a))
            log_2 := or(log_2, shl(44, f))
            r := shr(f, r)
        }

        assembly {
            let f := shr(127, mul(r, 0xf4674f0c0c))
            log_2 := or(log_2, shl(43, f))
            r := shr(f, r)
        }

        assembly {
            let f := shr(127, mul(r, 0xfd9d032b27))
            log_2 := or(log_2, shl(42, f))
            r := shr(f, r)
        }

        log_2shr128 := int128(log_2);

        int24 log_sqrt10001 = log_2shr128 * 255738958999603826347141;

        tick = int24((log_sqrt10001 - 3402992956809132418596140100660247210) >> 128);
    }
}
```

### 24.3 Uniswap V3 集成合约

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

/**
 * @title Uniswap V3 集成合约
 * @author 上等兵•甘
 */
contract UniswapV3Integration {
    using SafeERC20 for IERC20;

    // ========== 接口 ==========
    interface ISwapRouter {
        struct ExactInputSingleParams {
            address tokenIn;
            address tokenOut;
            uint24 fee;
            address recipient;
            uint256 amountIn;
            uint256 amountOutMinimum;
            uint160 sqrtPriceLimitX96;
        }

        function exactInputSingle(
            ExactInputSingleParams calldata params
        ) external payable returns (uint256 amountOut);

        struct ExactInputParams {
            bytes path;
            address recipient;
            uint256 amountIn;
            uint256 amountOutMinimum;
        }

        function exactInput(
            ExactInputParams calldata params
        ) external payable returns (uint256 amountOut);
    }

    interface INonfungiblePositionManager {
        struct MintParams {
            address token0;
            address token1;
            uint24 fee;
            int24 tickLower;
            int24 tickUpper;
            uint256 amount0Desired;
            uint256 amount1Desired;
            uint256 amount0Min;
            uint256 amount1Min;
            address recipient;
            uint256 deadline;
        }

        function mint(
            MintParams calldata params
        ) external payable returns (
            uint256 tokenId,
            uint128 liquidity,
            uint256 amount0,
            uint256 amount1
        );

        struct IncreaseLiquidityParams {
            uint256 tokenId;
            uint128 amount0Desired;
            uint128 amount1Desired;
            uint256 amount0Min;
            uint256 amount1Min;
            uint256 deadline;
        }

        function increaseLiquidity(
            IncreaseLiquidityParams calldata params
        ) external payable returns (
            uint128 liquidity,
            uint256 amount0,
            uint256 amount1
        );

        struct DecreaseLiquidityParams {
            uint256 tokenId;
            uint128 liquidity;
            uint256 amount0Min;
            uint256 amount1Min;
            uint256 deadline;
        }

        function decreaseLiquidity(
            DecreaseLiquidityParams calldata params
        ) external returns (
            uint256 amount0,
            uint256 amount1
        );

        struct CollectParams {
            uint256 tokenId;
            address recipient;
            uint128 amount0Max;
            uint128 amount1Max;
        }

        function collect(
            CollectParams calldata params
        ) external returns (
            uint256 amount0,
            uint256 amount1
        );

        function positions(
            uint256 tokenId
        ) external view returns (
            uint96 nonce,
            address operator,
            address token0,
            address token1,
            uint24 fee,
            int24 tickLower,
            int24 tickUpper,
            int128 liquidity,
            uint256 feeGrowthInside0LastX128,
            uint256 feeGrowthInside1LastX128,
            uint128 tokensOwed0,
            uint128 tokensOwed1
        );
    }

    // ========== 常量 ==========
    address public constant SWAP_ROUTER =
        0xE592427A0AEce92De3Edee1F18E0157C05861564;
    address public constant POSITION_MANAGER =
        0xC36442b4a4522E871399CD717aBDD847Ab11FE88;

    // ========== 状态变量 ==========
    address public owner;

    // ========== 事件 ==========
    event SwapExecuted(
        address indexed tokenIn,
        address indexed tokenOut,
        uint256 amountIn,
        uint256 amountOut
    );

    event PositionCreated(
        uint256 indexed tokenId,
        address token0,
        address token1,
        uint24 fee,
        int24 tickLower,
        int24 tickUpper
    );

    event FeesCollected(
        uint256 indexed tokenId,
        uint256 amount0,
        uint256 amount1
    );

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
     * @dev 单次交换
     */
    function swapExactInputSingle(
        address tokenIn,
        address tokenOut,
        uint24 fee,
        uint256 amountIn,
        uint256 amountOutMinimum
    ) external returns (uint256 amountOut) {
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

        IERC20(tokenIn).safeTransferFrom(
            msg.sender,
            address(this),
            amountIn
        );
        IERC20(tokenIn).safeApprove(SWAP_ROUTER, amountIn);

        amountOut = ISwapRouter(SWAP_ROUTER).exactInputSingle(params);

        emit SwapExecuted(tokenIn, tokenOut, amountIn, amountOut);
    }

    /**
     * @dev 创建流动性位置
     */
    function createPosition(
        address token0,
        address token1,
        uint24 fee,
        int24 tickLower,
        int24 tickUpper,
        uint256 amount0,
        uint256 amount1
    ) external returns (
        uint256 tokenId,
        uint128 liquidity,
        uint256 deposited0,
        uint256 deposited1
    ) {
        INonfungiblePositionManager.MintParams memory params = INonfungiblePositionManager
            .MintParams({
                token0: token0,
                token1: token1,
                fee: fee,
                tickLower: tickLower,
                tickUpper: tickUpper,
                amount0Desired: amount0,
                amount1Desired: amount1,
                amount0Min: 0,
                amount1Min: 0,
                recipient: msg.sender,
                deadline: block.timestamp
            });

        IERC20(token0).safeTransferFrom(msg.sender, address(this), amount0);
        IERC20(token1).safeTransferFrom(msg.sender, address(this), amount1);
        IERC20(token0).safeApprove(POSITION_MANAGER, amount0);
        IERC20(token1).safeApprove(POSITION_MANAGER, amount1);

        (tokenId, liquidity, deposited0, deposited1) = INonfungiblePositionManager(
            POSITION_MANAGER
        ).mint(params);

        emit PositionCreated(
            tokenId,
            token0,
            token1,
            fee,
            tickLower,
            tickUpper
        );
    }

    /**
     * @dev 收集手续费
     */
    function collectFees(
        uint256 tokenId
    ) external returns (
        uint256 amount0,
        uint256 amount1
    ) {
        INonfungiblePositionManager.CollectParams memory params = INonfungiblePositionManager
            .CollectParams({
                tokenId: tokenId,
                recipient: msg.sender,
                amount0Max: type(uint128).max,
                amount1Max: type(uint128).max
            });

        (amount0, amount1) = INonfungiblePositionManager(POSITION_MANAGER)
            .collect(params);

        emit FeesCollected(tokenId, amount0, amount1);
    }

    /**
     * @dev 获取位置信息
     */
    function getPositionInfo(
        uint256 tokenId
    ) external view returns (
        address token0,
        address token1,
        uint24 fee,
        int24 tickLower,
        int24 tickUpper,
        uint128 liquidity,
        uint128 tokensOwed0,
        uint128 tokensOwed1
    ) {
        (
            , // nonce
            , // operator
            token0,
            token1,
            fee,
            tickLower,
            tickUpper,
            liquidity,
            , // feeGrowthInside0LastX128
            , // feeGrowthInside1LastX128
            tokensOwed0,
            tokensOwed1
        ) = INonfungiblePositionManager(POSITION_MANAGER).positions(tokenId);
    }

    // ========== 管理函数 ==========

    function withdraw(address token, uint256 amount) external onlyOwner {
        IERC20(token).safeTransfer(owner, amount);
    }
}
```

---

## 二十五、Curve StableSwap 算法

### 25.1 StableSwap 核心原理

**为什么需要 StableSwap？**

```
Uniswap V2 恒定乘积 (x × y = k):

场景：USDT-USDC 稳定币交易对

初始状态：
  USDT: 1,000,000
  USDC: 1,000,000
  总计: 2,000,000

用户用 10,000 USDT 买入 USDC：

  USDT: 1,010,000
  USDC: 999,900

计算：
  USDC 输出 = 1,000,000 - (1,000,000 × 1,000,000) / 1,010,000
            = 9,900.99

问题：
  USDT 和 USDC 都是 1:1 锚定
  但用户只得到 9,900.99 USDC（损失 99 USDC！）
  滑点约 1%，对于稳定币来说太大了！
```

**StableSwap 解决方案：**

```
使用混合公式，在小额交易时接近常数和公式（无滑点），在大额交易时逐渐过渡到恒定乘积公式。

公式：
  D^n = Σ xi^n + k × D^n / Σ xi

其中：
- D = 总供应量（常数）
- xi = 代币 i 的余额
- n = 放大因子（通常为 2 或 3）
- k = 惩罚系数（防止不平衡）
```

### 25.2 Curve 池类型

#### 2pool（两个资产）

```
支持的资产对：
- USDT/USDC
- USDC/DAI
- USDT/DAI

特点：
- 最简单，滑点最小
- 适合 1:1 锚定的稳定币
```

#### 3pool（三个资产）

```
支持的资产：
- DAI/USDC/USDT

特点：
- 资产更多，流动性更好
- 但滑点略高于 2pool
```

#### Metapool（Meta 池）

```
结构：
  2pool（USDT/USDC）←─→ Meta 池（2pool + 新稳定币）

支持的资产：
  - sUSD/3pool
  - USDD/3pool
  - FRAX/3pool

特点：
- 支持更多稳定币
- 通过 meta 池连接
```

### 25.3 Curve 集成合约

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

/**
 * @title Curve 集成合约
 * @author 上等兵•甘
 */
contract CurveIntegration {
    using SafeERC20 for IERC20;

    // ========== 接口 ==========
    interface ICurvePool {
        function exchange(
            int128 i,
            int128 j,
            uint256 dx,
            uint256 min_dy
        ) external returns (uint256);

        function exchange_underlying(
            int128 i,
            int128 j,
            uint256 dx,
            uint256 min_dy
        ) external returns (uint256);

        function get_dy(
            int128 i,
            int128 j,
            uint256 dx
        ) external view returns (uint256);

        function balances(uint256 i) external view returns (uint256);

        function coins(uint256 i) external view returns (address);
    }

    interface ICurveRegistry {
        function get_pool_from_lp_token(
            address lp_token
        ) external view returns (address);

        function get_n_coins(
            address pool
        ) external view returns (uint256);

        function get_coin_indices(
            address pool,
            address from_coin,
            address to_coin
        ) external view returns (int128, int128);
    }

    // ========== 常量 ==========
    // 3pool 池地址
    address public constant CURVE_3POOL =
        0xbEbc44782C7dB0a1A60Cb6fe97d0bB3A840dAbE;

    // 2pool 池地址
    address public constant CURVE_2POOL =
        0x4DEcE878EA96D5D56cF8Cfe5eAc1AcCf76D7aB3;

    // Registry
    address public constant CURVE_REGISTRY =
        0x90E00ACe148ca3B23d1f083eC736Da8Bb8c4758;

    // ========== 状态变量 ==========
    address public owner;

    // ========== 事件 ==========
    event CurveSwap(
        address indexed pool,
        address indexed tokenIn,
        address indexed tokenOut,
        uint256 amountIn,
        uint256 amountOut
    );

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
     * @dev Curve 交换
     * @param pool Curve 池地址
     * @param tokenIn 输入代币
     * @param tokenOut 输出代币
     * @param amountIn 输入金额
     * @param minAmountOut 最小输出金额
     */
    function curveSwap(
        address pool,
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 minAmountOut
    ) external returns (uint256 amountOut) {
        // 获取代币索引
        (int128 i, int128 j) = _getCoinIndices(
            pool,
            tokenIn,
            tokenOut
        );

        // 转入代币
        IERC20(tokenIn).safeTransferFrom(
            msg.sender,
            address(this),
            amountIn
        );

        // 批准池
        IERC20(tokenIn).safeApprove(pool, amountIn);

        // 执行交换
        amountOut = ICurvePool(pool).exchange(
            i,
            j,
            amountIn,
            minAmountOut
        );

        // 转出代币
        IERC20(tokenOut).safeTransfer(msg.sender, amountOut);

        emit CurveSwap(pool, tokenIn, tokenOut, amountIn, amountOut);
    }

    /**
     * @dev 获取交换价格
     */
    function getExchangeAmount(
        address pool,
        address tokenIn,
        address tokenOut,
        uint256 amountIn
    ) external view returns (uint256 amountOut) {
        (int128 i, int128 j) = _getCoinIndices(
            pool,
            tokenIn,
            tokenOut
        );

        return ICurvePool(pool).get_dy(i, j, amountIn);
    }

    /**
     * @dev 获取代币索引
     */
    function _getCoinIndices(
        address pool,
        address tokenIn,
        address tokenOut
    ) internal view returns (int128 i, int128 j) {
        uint256 nCoins = ICurveRegistry(CURVE_REGISTRY).get_n_coins(pool);

        for (uint256 k = 0; k < nCoins; ) {
            if (ICurvePool(pool).coins(k) == tokenIn) {
                i = int128(int256(k));
            }
            if (ICurvePool(pool).coins(k) == tokenOut) {
                j = int128(int256(k));
            }
            unchecked { ++k; }
        }

        require(i != -1 && j != -1, "Coins not found in pool");
    }

    // ========== 批量操作 ==========

    /**
     * @dev 批量交换（Multi-hop）
     */
    function multiHopSwap(
        address[] calldata pools,
        address[] calldata tokens,
        uint256 amountIn,
        uint256 minAmountOut
    ) external returns (uint256 amountOut) {
        require(pools.length == tokens.length - 1, "Invalid params");

        amountOut = amountIn;

        for (uint256 i = 0; i < pools.length; ) {
            amountOut = this.curveSwap(
                pools[i],
                tokens[i],
                tokens[i + 1],
                amountOut,
                0 // 中间步骤不设最小值
            );

            unchecked { ++i; }
        }

        require(amountOut >= minAmountOut, "Slippage too high");
    }

    // ========== 管理函数 ==========

    function withdraw(address token, uint256 amount) external onlyOwner {
        IERC20(token).safeTransfer(owner, amount);
    }
}
```

---

## 二十六、Balancer Weighted Pools

### 26.1 核心原理

**Balancer 公式：**

```
价值恒定公式：
  Σ (wi × bi) = C

其中：
- wi = 代币 i 的权重
- bi = 代币 i 的余额
- C = 常数

例如：50% ETH, 30% USDC, 20% WBTC

初始状态：
  ETH: 10 ETH
  USDC: 18,500 USDC
  WBTC: 0.57 WBTC

总价值 = 0.5 × 10 + 0.3 × 18,500 + 0.2 × 0.57
         = 5 + 5,550 + 1,150
         = $6,705
```

### 26.2 Balancer 池类型

#### Weighted Pool（加权池）

```
自定义权重：
  - 可以设置任意权重（如 50/30/20）
  - 适用于不平衡的交易对

费率：
  - 根据池子的权重分布计算
  - 通常在 0.01% - 1%
```

#### Stable Pool（稳定池）

```
专为稳定币设计：
  - 类似 Curve StableSwap
  - 低滑点
  - 支持 2-5 个稳定币
```

#### MetaStable Pool（Meta 稳定池）

```
连接其他池：
  - 如：wstETH (stETH 池）↔️ ETH
  - 通过包装代币连接
```

### 26.3 Balancer 集成合约

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

/**
 * @title Balancer 集成合约
 * @author 上等兵•甘
 */
contract BalancerIntegration {
    using SafeERC20 for IERC20;

    // ========== 接口 ==========
    interface IVault {
        enum SwapKind {
            GIVEN_IN,
            GIVEN_OUT
        }

        struct SingleSwap {
            bytes32 poolId;
            SwapKind kind;
            address assetIn;
            address assetOut;
            uint256 amount;
            bytes userData;
        }

        struct FundManagement {
            address sender;
            bool fromInternalBalance;
            address payable recipient;
            bool toInternalBalance;
        }

        function swap(
            SingleSwap memory singleSwap,
            FundManagement memory funds,
            uint256 limit,
            uint256 deadline
        ) external payable returns (uint256 amountOut);

        function queryBatchSwap(
            SwapKind kind,
            bytes32[] memory assets,
            FundManagement memory funds,
            int256[] memory limits,
            uint256 deadline
        ) external returns (int256[] memory deltas);
    }

    interface IWeightedPool {
        function getPoolId() external view returns (bytes32);

        function swap(
            address tokenIn,
            address tokenOut,
            uint256 amount
        ) external returns (uint256);
    }

    // ========== 常量 ==========
    address public constant BALANCER_VAULT =
        0xBA12222222228d8Ba445958a75a0704d566BF2C8;

    // ETH/USDC 池 ID
    bytes32 public constant ETH_USDC_POOL_ID =
        0x0b09dea1b0a0d9f7e07c6d6e95e2ecfc3d2e0298d0ab0ae3201db5e62a4e909;

    // ========== 状态变量 ==========
    address public owner;

    // ========== 事件 ==========
    event BalancerSwap(
        bytes32 indexed poolId,
        address indexed tokenIn,
        address indexed tokenOut,
        uint256 amountIn,
        uint256 amountOut
    );

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
     * @dev Balancer 交换
     * @param poolId 池 ID
     * @param tokenIn 输入代币
     * @param tokenOut 输出代币
     * @param amountIn 输入金额
     * @param minAmountOut 最小输出金额
     */
    function balancerSwap(
        bytes32 poolId,
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 minAmountOut
    ) external payable returns (uint256 amountOut) {
        IVault.SingleSwap memory singleSwap = IVault.SingleSwap({
            poolId: poolId,
            kind: IVault.SwapKind.GIVEN_IN,
            assetIn: tokenIn,
            assetOut: tokenOut,
            amount: amountIn,
            userData: bytes("")
        });

        IVault.FundManagement memory funds = IVault.FundManagement({
            sender: msg.sender,
            fromInternalBalance: false,
            recipient: payable(msg.sender),
            toInternalBalance: false
        });

        // 如果是 ETH，直接发送
        if (tokenIn == address(0)) {
            require(msg.value == amountIn, "ETH amount mismatch");
        } else {
            IERC20(tokenIn).safeTransferFrom(
                msg.sender,
                address(this),
                amountIn
            );
            IERC20(tokenIn).safeApprove(BALANCER_VAULT, amountIn);
        }

        amountOut = IVault(BALANCER_VAULT).swap(
            singleSwap,
            funds,
            minAmountOut,
            block.timestamp
        );

        emit BalancerSwap(poolId, tokenIn, tokenOut, amountIn, amountOut);
    }

    /**
     * @dev 查询交换金额
     */
    function querySwap(
        bytes32 poolId,
        address tokenIn,
        address tokenOut,
        uint256 amountIn
    ) external view returns (uint256 amountOut) {
        IVault.SingleSwap memory singleSwap = IVault.SingleSwap({
            poolId: poolId,
            kind: IVault.SwapKind.GIVEN_IN,
            assetIn: tokenIn,
            assetOut: tokenOut,
            amount: amountIn,
            userData: bytes("")
        });

        IVault.FundManagement memory funds = IVault.FundManagement({
            sender: address(this),
            fromInternalBalance: false,
            recipient: payable(address(this)),
            toInternalBalance: false
        });

        int256[] memory limits = new int256[](2);
        limits[0] = type(int256).max;
        limits[1] = 0;

        bytes32[] memory assets = new bytes32[](2);
        assets[0] = bytes32(uint256(uint160(tokenIn)));
        assets[1] = bytes32(uint256(uint160(tokenOut)));

        int256[] memory deltas = IVault(BALANCER_VAULT).queryBatchSwap(
            IVault.SwapKind.GIVEN_IN,
            assets,
            funds,
            limits,
            block.timestamp
        );

        amountOut = uint256(-deltas[1]);
    }

    // ========== 管理函数 ==========

    function withdraw(address token, uint256 amount) external onlyOwner {
        IERC20(token).safeTransfer(owner, amount);
    }

    receive() external payable {}
}
```

---

## 二十七、DEX 对比总结

| 特性 | Uniswap V3 | Curve | Balancer |
|------|------------|-------|----------|
| **算法** | 集中流动性 | StableSwap | Weighted |
| **费率层级** | 4 个（0.01-1%） | 1-3 个（0.02-0.04%） | 动态（0.01-1%） |
| **资产类型** | 所有 | 稳定币 | 所有 |
| **流动性代币** | ERC-721 NFT | ERC-20 LP Token | ERC-20 BPT |
| **适用场景** | 高频交易、套利 | 稳定币交换 | 多资产、定制化 |
| **Gas 成本** | 较高 | 中等 | 较高 |
| **资金效率** | x4000 | x20-50 | 可定制 |

---

## 第八小时学到的技能总结

### 27.1 核心技能

1. **Uniswap V3 深度**
   - 集中流动性原理
   - Tick 和区间机制
   - 价格转换公式
   - NFT 位置管理

2. **Curve StableSwap**
   - StableSwap 混合公式
   - 池类型（2pool, 3pool, metapool）
   - 稳定币优化

3. **Balancer Weighted Pools**
   - 加权池原理
   - 池类型（weighted, stable, metastable）
   - 自定义权重

4. **实战集成**
   - Uniswap V3 Router 集成
   - Curve Pool 集成
   - Balancer Vault 集成

5. **Solidity 技巧**
   - 内联汇编（TickMath）
   - ERC-721 位置管理
   - 批量操作

### 27.2 代码产出

- ✅ TickMath 价格计算库
- ✅ UniswapV3Integration 完整集成合约
- ✅ CurveIntegration Curve 集成
- ✅ BalancerIntegration Balancer 集成

---

**【第8小时汇报完毕】**
