# Curve Finance 研究

**作者**: 上等兵•甘
**日期**: 2026-02-11
**版本**: 1.0.0

---

## 目录

1. [概述](#概述)
2. [核心原理](#核心原理)
3. [数学模型](#数学模型)
4. [池类型](#池类型)
5. [智能合约架构](#智能合约架构)
6. [开发实战](#开发实战)
7. [高级功能](#高级功能)
8. [安全考虑](#安全考虑)

---

## 概述

### 什么是 Curve Finance？

Curve Finance 是一个专门针对稳定币交易优化的去中心化交易协议（DEX）。与其他 AMM（如 Uniswap）不同，Curve 使用专门针对相似资产（如稳定币）优化的算法，实现极低滑点和高效交易。

### 核心特点

1. **低滑点**：稳定币之间交易滑点极低（通常 < 0.1%）
2. **高资本效率**：专为相似资产设计，流动性利用率高
3. **低费用**：交易费用通常为 0.04%
4. **稳定的汇率**：针对锚定资产优化
5. **流动性挖矿**：提供 CRV 治理代币奖励
6. **多种池类型**：支持不同类型的资产组合

### 适用场景

- 稳定币交易（USDT、USDC、DAI 等）
- 包装代币交易（如 WBTC、renBTC）
- 权益资产交易（如 stETH、rETH）
- 高频稳定币套利
- 流动性挖矿收益

### 重要指标

| 指标 | 说明 |
|------|------|
| TVL（总锁仓量） | 流动性池中的总资金 |
| APY（年化收益率） | 流动性提供者的年化收益 |
| 交易量 | 日均交易量 |
| 池费用 | 每笔交易的手续费 |
| 滑点 | 大额交易的价格影响 |

---

## 核心原理

### StableSwap 算法

Curve 使用 StableSwap 算法，结合了恒定乘积（x*y=k）和恒定和（x+y=k）的优点：

```
StableSwap 方程：
A * (x + y)^2 * z + x * y * z = k

其中：
- A = 增强系数（决定池的"平坦度"）
- x, y = 两种代币的数量
- z = 池的总代币数量
- k = 常数（代表流动性）
```

### 工作原理

#### 1. 恒定和部分（x + y ≈ constant）

当 A 值很大时，曲线变得平坦：
- 稳定币之间交易几乎 1:1
- 适合锚定资产
- 极低滑点

#### 2. 恒定乘积部分（x * y = constant）

当 A 值较小时，曲线接近 Uniswap：
- 提供流动性保护
- 防止流动性枯竭
- 作为安全网

#### 3. 平衡机制

A 值动态调整：
- A 越大：曲线越平坦，滑点越低
- A 越小：曲线越陡峭，流动性越好

---

## 数学模型

### StableSwap 公式

```python
def stable_swap(x_i, x_j, A, D):
    """
    StableSwap 核心算法

    参数:
        x_i: 输入代币数量
        x_j: 输出代币数量
        A: 增强系数（通常 10-100）
        D: 总虚拟余额

    返回:
        交易后的输出数量
    """
    # 计算池的总虚拟余额
    # D = Σ x_i * n^2 / A * (1 + ...)

    # 迭代求解交易
    y = x_j
    for _ in range(255):  # 最多 255 次迭代
        # 计算新的 y 值
        y_new = compute_y(x_i + x_i_in, y - y_out, D, A, n)

        # 检查收敛
        if abs(y_new - y) < 1:
            break

        y = y_new

    return y_out
```

### 池余额计算

```python
def get_y(x, D, A, n):
    """
    计算 StableSwap 曲线上的 y 值

    参数:
        x: 已知代币数量
        D: 总虚拟余额
        A: 增强系数
        n: 代币种类数

    返回:
        对应的 y 值
    """
    # 二分查找求解
    y = D / n

    for _ in range(255):
        # 计算曲线值
        c = D
        S = 0
        for i in range(n):
            if i != j:
                S += x_i

        Ann = A * n
        c = c * D / (Ann * S + D)

        # 更新 y
        y = (D ** 2 + S * y) / (D + (n + 1) * y)

    return y
```

### 费用计算

```python
def calculate_fees(amount, fee=0.0004):
    """
    计算交易费用

    参数:
        amount: 交易金额
        fee: 费率（默认 0.04%）

    返回:
        (输出金额, 费用)
    """
    fee_amount = amount * fee
    output_amount = amount - fee_amount
    return output_amount, fee_amount
```

---

## 池类型

### 1. 基础稳定币池

**代币类型**：相同类型的稳定币
**示例**：3pool（USDT、USDC、DAI）
**特点**：
- 最低滑点
- 最高流动性
- 适合稳定币套利

```solidity
// 3pool 池配置
address[3] public tokens = [
    0xdAC17F958D2ee523a2206206994597C13D831ec7,  // USDT
    0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48,  // USDC
    0x6B175474E89094C44Da98b954EedeAC495271d0F   // DAI
];

uint256[3] public decimals = [6, 6, 18];
```

### 2. 元池（Meta Pool）

**代币类型**：包含另一个池的 LP 代币
**示例**：UST 2pool（UST、3pool LP）
**特点**：
- 复合流动性
- 可以访问多个池
- 更复杂的路由

```solidity
// Meta Pool 示例
address public basePool;  // 3pool 地址
address public metaToken; // UST

function exchange(
    uint256 i,
    uint256 j,
    uint256 dx,
    uint256 min_dy
) external {
    if (j == 1) {  // 交换到 3pool
        // 1. 将 UST 换成 3pool LP
        // 2. 在 3pool 中进一步交换
    } else {  // 从 3pool 交换
        // 1. 从 3pool 获取代币
        // 2. 换成 UST
    }
}
```

### 3. 加密货币池

**代币类型**：不同类型的加密货币
**示例**：sBTC（WBTC、renBTC、sBTC）
**特点**：
- 较高滑点
- 更高的流动性深度
- 适合 BTC 类资产

```solidity
// 加密货币池配置
address[3] public tokens = [
    0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599,  // WBTC
    0xEB4C2781e4ebA804CE9a9803C67d0893436bB27D,  // renBTC
    0xfE4eE6aDdE9d1360C69A0922f9bF4fAaFf4A2Dd9   // sBTC
];

uint256 A = 2000;  // 较低的 A 值
```

### 4. 权益资产池

**代币类型**：质押代币
**示例**：stETH（stETH、ETH）
**特点**：
- 价格略有波动
- 需要更高的 A 值
- 杠杆交易友好

### 5. 贷款池（Lending Pool）

**代币类型**：流动性提供代币（如 aUSDC、cUSDC）
**示例**：Aave Pool
**特点**：
- 整合借贷协议
- 获取双重收益
- 更高的风险

---

## 智能合约架构

### 核心合约

#### 1. Curve Pool（池合约）

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract CurvePool is ERC20 {
    address[2] public tokens;
    uint256[2] public balances;
    uint256 public A;  // 增强系数
    uint256 public fee;  // 交易费用

    event Exchange(
        address indexed buyer,
        address indexed tokenSold,
        address indexed tokenBought,
        uint256 amountSold,
        uint256 amountBought
    );

    event AddLiquidity(
        address indexed provider,
        uint256[2] tokenAmounts,
        uint256 liquidity
    );

    constructor(
        string memory _name,
        string memory _symbol,
        address[2] memory _tokens,
        uint256 _A,
        uint256 _fee
    ) ERC20(_name, _symbol) {
        tokens = _tokens;
        A = _A;
        fee = _fee;
    }

    // 交换代币
    function exchange(
        int128 i,
        int128 j,
        uint256 dx,
        uint256 min_dy
    ) external returns (uint256) {
        // 1. 转移代币到合约
        IERC20(tokens[uint128(i)]).transferFrom(
            msg.sender,
            address(this),
            dx
        );

        // 2. 计算 StableSwap 交换
        uint256 dy = get_dy(i, j, dx);

        // 3. 扣除费用
        uint256 fee_amount = dy * fee / 10**18;
        dy -= fee_amount;

        // 4. 转移代币给用户
        IERC20(tokens[uint128(j)]).transfer(msg.sender, dy);

        // 5. 更新余额
        balances[uint128(i)] += dx;
        balances[uint128(j)] -= dy + fee_amount;

        emit Exchange(
            msg.sender,
            tokens[uint128(i)],
            tokens[uint128(j)],
            dx,
            dy
        );

        return dy;
    }

    // 计算交换输出
    function get_dy(
        int128 i,
        int128 j,
        uint256 dx
    ) public view returns (uint256) {
        // StableSwap 算法
        uint256 x = balances[uint128(i)] + dx;
        uint256 y = calculate_y(x, balances[uint128(j)], A);

        uint256 dy = balances[uint128(j)] - y - 1;

        return dy;
    }

    // StableSwap y 计算
    function calculate_y(
        uint256 x,
        uint256 y,
        uint256 _A
    ) internal pure returns (uint256) {
        // 简化版 StableSwap 计算
        uint256 D = x + y;
        uint256 Ann = _A * 2;

        uint256 y_prev = y;
        for (uint256 i = 0; i < 255; i++) {
            uint256 y_new = (
                D ** 2 + x * y_prev
            ) / (
                D + Ann * y_prev
            );

            if (y_new == y_prev) {
                return y_new;
            }

            y_prev = y_new;
        }

        return y_prev;
    }

    // 添加流动性
    function add_liquidity(
        uint256[2] calldata amounts,
        uint256 min_mint_amount
    ) external returns (uint256) {
        // 1. 转移代币到合约
        for (uint256 i = 0; i < 2; i++) {
            if (amounts[i] > 0) {
                IERC20(tokens[i]).transferFrom(
                    msg.sender,
                    address(this),
                    amounts[i]
                );
                balances[i] += amounts[i];
            }
        }

        // 2. 计算流动性代币
        uint256 totalSupply = totalSupply();
        uint256 mintAmount;

        if (totalSupply == 0) {
            // 首次添加
            mintAmount = amounts[0] + amounts[1];
        } else {
            // 比例添加
            uint256[2] memory ratios;
            for (uint256 i = 0; i < 2; i++) {
                ratios[i] = amounts[i] * totalSupply / balances[i];
            }

            mintAmount = ratios[0] < ratios[1] ? ratios[0] : ratios[1];
        }

        require(mintAmount >= min_mint_amount, "Slippage");

        // 3. 铸造 LP 代币
        _mint(msg.sender, mintAmount);

        emit AddLiquidity(msg.sender, amounts, mintAmount);

        return mintAmount;
    }

    // 移除流动性
    function remove_liquidity(
        uint256 amount,
        uint256[2] calldata min_amounts
    ) external {
        uint256 totalSupply = totalSupply();
        require(amount <= balanceOf(msg.sender), "Insufficient balance");

        // 1. 销毁 LP 代币
        _burn(msg.sender, amount);

        // 2. 计算代币数量
        uint256[2] memory amounts;
        for (uint256 i = 0; i < 2; i++) {
            amounts[i] = balances[i] * amount / totalSupply;
            require(amounts[i] >= min_amounts[i], "Slippage");

            // 3. 转移代币
            IERC20(tokens[i]).transfer(msg.sender, amounts[i]);
            balances[i] -= amounts[i];
        }
    }
}
```

#### 2. Curve Registry（注册表合约）

```solidity
contract CurveRegistry {
    struct PoolInfo {
        address pool;
        address[8] tokens;
        uint256[8] decimals;
        address lp_token;
        bool is_meta;
    }

    mapping(address => PoolInfo) public pools;
    address[] public poolList;

    event PoolAdded(address indexed pool, address[8] tokens);

    function addPool(
        address _pool,
        address[8] memory _tokens,
        address _lp_token,
        bool _is_meta
    ) external {
        require(_pool != address(0), "Invalid pool");

        pools[_pool] = PoolInfo({
            pool: _pool,
            tokens: _tokens,
            decimals: [uint256(0), 0, 0, 0, 0, 0, 0, 0],
            lp_token: _lp_token,
            is_meta: _is_meta
        });

        poolList.push(_pool);

        emit PoolAdded(_pool, _tokens);
    }

    function getPool(address _pool)
        external
        view
        returns (PoolInfo memory)
    {
        return pools[_pool];
    }

    function getPoolCount() external view returns (uint256) {
        return poolList.length;
    }
}
```

#### 3. CRV 代币（治理代币）

```solidity
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Votes.sol";

contract CRVToken is ERC20, ERC20Votes {
    constructor() ERC20("Curve DAO Token", "CRV") ERC20Permit("Curve DAO Token") {
        _mint(msg.sender, 1_303_030_303 * 10**18);
    }

    function _update(address from, address to, uint256 value)
        internal
        override(ERC20, ERC20Votes)
    {
        super._update(from, to, value);
    }

    function nonces(address owner)
        public
        view
        override(ERC20, ERC20Votes)
        returns (uint256)
    {
        return super.nonces(owner);
    }
}
```

---

## 开发实战

### 1. 创建简单的 StableSwap 池

#### 合约代码

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract SimpleCurvePool is ERC20 {
    using SafeERC20 for IERC20;

    // 池配置
    address[2] public tokens;
    uint256[2] public balances;

    // 参数
    uint256 public A;  // 增强系数
    uint256 public fee;  // 费率（1e18 = 100%）
    uint256 public admin_fee;  // 管理费

    // 权限
    address public admin;
    address public feeRecipient;

    // 事件
    event Exchange(
        address indexed buyer,
        address indexed sold,
        address indexed bought,
        uint256 amountIn,
        uint256 amountOut
    );

    event AddLiquidity(
        address indexed provider,
        uint256[2] amounts,
        uint256 liquidity
    );

    event RemoveLiquidity(
        address indexed provider,
        uint256[2] amounts,
        uint256 liquidity
    );

    event NewFee(uint256 fee);
    event NewA(uint256 A);
    event RampA(uint256 oldA, uint256 newA, uint256 initialTime, uint256 futureTime);

    // 参数
    uint256 constant FEE_DENOMINATOR = 10**18;
    uint256 constant A_PRECISION = 100;
    uint256 constant MAX_A = 10**6;
    uint256 constant MAX_A_CHANGE = 10;
    uint256 constant MIN_RAMP_TIME = 86400;  // 1 天

    // A 值调整
    uint256 public initial_A;
    uint256 public future_A;
    uint256 public initial_A_time;
    uint256 public future_A_time;

    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin");
        _;
    }

    constructor(
        string memory _name,
        string memory _symbol,
        address[2] memory _tokens,
        uint256 _A,
        uint256 _fee,
        address _admin,
        address _feeRecipient
    ) ERC20(_name, _symbol) {
        require(_tokens[0] != _tokens[1], "Same tokens");
        require(_fee <= FEE_DENOMINATOR / 100, "Fee too high");
        require(_A > 0, "A must be > 0");
        require(_A <= MAX_A, "A too high");

        tokens = _tokens;
        A = _A;
        initial_A = _A;
        future_A = _A;
        initial_A_time = block.timestamp;
        future_A_time = block.timestamp;
        fee = _fee;
        admin = _admin;
        feeRecipient = _feeRecipient;
    }

    // 获取当前 A 值（考虑 ramp）
    function get_A() public view returns (uint256) {
        if (block.timestamp >= future_A_time) {
            return future_A;
        }

        uint256 A1 = initial_A;
        uint256 A2 = future_A;
        uint256 t1 = initial_A_time;
        uint256 t2 = future_A_time;

        if (A2 > A1) {
            return A1 + (A2 - A1) * (block.timestamp - t1) / (t2 - t1);
        } else {
            return A1 - (A1 - A2) * (block.timestamp - t1) / (t2 - t1);
        }
    }

    // 交换代币
    function exchange(
        uint256 i,
        uint256 j,
        uint256 dx,
        uint256 min_dy
    ) external returns (uint256) {
        require(i != j, "Same index");
        require(i < 2 && j < 2, "Invalid index");
        require(dx > 0, "Amount must be > 0");

        // 转入代币
        IERC20(tokens[i]).safeTransferFrom(msg.sender, address(this), dx);

        // 计算 A
        uint256 _A = get_A();

        // 计算交换
        uint256 dy = get_dy(i, j, dx, _A);

        require(dy >= min_dy, "Slippage");

        // 扣除费用
        uint256 fee_amount = dy * fee / FEE_DENOMINATOR;
        uint256 admin_fee_amount = fee_amount * admin_fee / FEE_DENOMINATOR;
        uint256 output_amount = dy - fee_amount;

        // 更新余额
        balances[i] += dx;
        balances[j] -= dy;

        // 转出代币
        IERC20(tokens[j]).safeTransfer(msg.sender, output_amount);
        IERC20(tokens[j]).safeTransfer(feeRecipient, admin_fee_amount);

        emit Exchange(
            msg.sender,
            tokens[i],
            tokens[j],
            dx,
            output_amount
        );

        return output_amount;
    }

    // 计算交换输出（简化版）
    function get_dy(
        uint256 i,
        uint256 j,
        uint256 dx,
        uint256 _A
    ) public view returns (uint256) {
        uint256 x = balances[i] + dx;
        uint256 y = balances[j];

        // StableSwap 计算（简化版）
        uint256 D = x + y;
        uint256 Ann = _A * 2;

        // 迭代求解 y
        uint256 y_prev = y;
        for (uint256 n = 0; n < 255; n++) {
            uint256 y_new = (D * D + x * y_prev) / (D + Ann * y_prev);

            if (y_new >= y_prev) {
                return y - y_prev;
            }

            y_prev = y_new;
        }

        return y - y_prev;
    }

    // 添加流动性
    function add_liquidity(
        uint256[2] calldata amounts,
        uint256 min_mint_amount
    ) external returns (uint256) {
        uint256 totalSupply = totalSupply();

        // 转入代币
        for (uint256 i = 0; i < 2; i++) {
            if (amounts[i] > 0) {
                IERC20(tokens[i]).safeTransferFrom(
                    msg.sender,
                    address(this),
                    amounts[i]
                );
                balances[i] += amounts[i];
            }
        }

        // 计算流动性
        uint256 mint_amount;
        if (totalSupply == 0) {
            mint_amount = amounts[0] + amounts[1];
        } else {
            // 按比例计算
            uint256 d0 = get_D();
            uint256 d1 = get_D();

            mint_amount = totalSupply * (d1 - d0) / d0;
        }

        require(mint_amount >= min_mint_amount, "Slippage");

        _mint(msg.sender, mint_amount);

        emit AddLiquidity(msg.sender, amounts, mint_amount);

        return mint_amount;
    }

    // 计算虚拟余额 D
    function get_D() public view returns (uint256) {
        uint256 Ann = get_A() * 2;
        uint256 sum = balances[0] + balances[1];

        // 简化版 D 计算
        return sum;
    }

    // 移除流动性
    function remove_liquidity(
        uint256 amount,
        uint256[2] calldata min_amounts
    ) external {
        uint256 totalSupply = totalSupply();
        require(amount <= balanceOf(msg.sender), "Insufficient balance");
        require(amount > 0, "Amount must be > 0");

        // 销毁 LP 代币
        _burn(msg.sender, amount);

        // 计算代币数量
        uint256[2] memory amounts;
        for (uint256 i = 0; i < 2; i++) {
            amounts[i] = balances[i] * amount / totalSupply;
            require(amounts[i] >= min_amounts[i], "Slippage");

            // 转出代币
            IERC20(tokens[i]).safeTransfer(msg.sender, amounts[i]);
            balances[i] -= amounts[i];
        }

        emit RemoveLiquidity(msg.sender, amounts, amount);
    }

    // 设置费率
    function set_fee(uint256 _fee) external onlyAdmin {
        require(_fee <= FEE_DENOMINATOR / 100, "Fee too high");
        fee = _fee;
        emit NewFee(_fee);
    }

    // 调整 A 值
    function ramp_A(uint256 _future_A, uint256 _future_time) external onlyAdmin {
        require(
            block.timestamp + MIN_RAMP_TIME >= _future_time,
            "Insufficient time"
        );
        require(
            _future_time >= block.timestamp + MIN_RAMP_TIME,
            "Insufficient time"
        );

        uint256 _initial_A = get_A();
        require(_future_A < MAX_A * A_PRECISION / MAX_A_CHANGE, "A too high");
        require(_future_A * MAX_A_CHANGE > _initial_A, "A too low");
        require(_future_A * MAX_A_CHANGE > _initial_A, "A too low");

        initial_A = _initial_A;
        future_A = _future_A;
        initial_A_time = block.timestamp;
        future_A_time = _future_time;

        emit RampA(_initial_A, _future_A, block.timestamp, _future_time);
    }

    // 停止 A 值调整
    function stop_ramp_A() external onlyAdmin {
        future_A = get_A();
        future_A_time = block.timestamp;
    }

    // 更新管理员
    function set_admin(address _admin) external onlyAdmin {
        admin = _admin;
    }

    // 更新费用接收者
    function set_fee_recipient(address _feeRecipient) external onlyAdmin {
        feeRecipient = _feeRecipient;
    }
}
```

#### 部署脚本

```javascript
// scripts/deployCurvePool.js
const hre = require("hardhat");

async function main() {
  console.log("Deploying SimpleCurvePool...");

  // 代币地址（测试网示例）
  const tokens = [
    "0x94a9D9AC8a22534E3FaCa9F4e7F2E2cf85d5E4C8",  // USDC
    "0xff795577d9ac8bd7d90ee22b6c1703490b6512fd",  // DAI
  ];

  const A = 100;  // 增强系数
  const fee = 40000000000000000;  // 0.04% (4e16 / 1e18)
  const admin = (await hre.ethers.getSigners())[0].address;
  const feeRecipient = admin;

  const SimpleCurvePool = await hre.ethers.getContractFactory(
    "SimpleCurvePool"
  );
  const pool = await SimpleCurvePool.deploy(
    "Curve USDC-DAI",
    "crvUSDCDAI",
    tokens,
    A,
    fee,
    admin,
    feeRecipient
  );

  await pool.waitForDeployment();
  const address = await pool.getAddress();

  console.log("SimpleCurvePool deployed to:", address);

  // 验证合约
  if (hre.network.name !== "hardhat" && hre.network.name !== "localhost") {
    console.log("Waiting for block confirmations...");
    await pool.deploymentTransaction().wait(6);

    console.log("Verifying contract...");
    await hre.run("verify:verify", {
      address: address,
      constructorArguments: [
        "Curve USDC-DAI",
        "crvUSDCDAI",
        tokens,
        A,
        fee,
        admin,
        feeRecipient,
      ],
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

#### 测试用例

```javascript
// test/CurvePool.test.js
const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("SimpleCurvePool", function () {
  let pool;
  let tokenA, tokenB;
  let owner, user1, user2;

  beforeEach(async function () {
    [owner, user1, user2] = await ethers.getSigners();

    // 部署测试代币
    const MockERC20 = await ethers.getContractFactory("MockERC20");
    tokenA = await MockERC20.deploy("Token A", "TKA", 18);
    tokenB = await MockERC20.deploy("Token B", "TKB", 18);

    // 铸造代币
    await tokenA.mint(user1.address, ethers.parseEther("10000"));
    await tokenB.mint(user1.address, ethers.parseEther("10000"));
    await tokenA.mint(user2.address, ethers.parseEther("10000"));
    await tokenB.mint(user2.address, ethers.parseEther("10000"));

    // 部署池
    const SimpleCurvePool = await ethers.getContractFactory("SimpleCurvePool");
    pool = await SimpleCurvePool.deploy(
      "Curve A-B",
      "crvAB",
      [await tokenA.getAddress(), await tokenB.getAddress()],
      100,
      40000000000000000,
      owner.address,
      owner.address
    );
    await pool.waitForDeployment();
  });

  describe("Deployment", function () {
    it("Should set the correct tokens", async function () {
      const tokens = await pool.tokens();
      expect(tokens[0]).to.equal(await tokenA.getAddress());
      expect(tokens[1]).to.equal(await tokenB.getAddress());
    });

    it("Should set the correct A value", async function () {
      const A = await pool.get_A();
      expect(A).to.equal(100);
    });

    it("Should set the correct fee", async function () {
      const fee = await pool.fee();
      expect(fee).to.equal(40000000000000000);
    });
  });

  describe("Add Liquidity", function () {
    it("Should add liquidity successfully", async function () {
      const amountA = ethers.parseEther("1000");
      const amountB = ethers.parseEther("1000");

      await tokenA.connect(user1).approve(await pool.getAddress(), amountA);
      await tokenB.connect(user1).approve(await pool.getAddress(), amountB);

      const liquidity = await pool.add_liquidity(
        [amountA, amountB],
        0
      );

      expect(liquidity).to.be.gt(0);
    });

    it("Should mint LP tokens proportional to deposits", async function () {
      const amount1 = ethers.parseEther("1000");
      const amount2 = ethers.parseEther("2000");

      await tokenA.connect(user1).approve(await pool.getAddress(), amount1);
      await tokenB.connect(user1).approve(await pool.getAddress(), amount1);
      await pool.add_liquidity([amount1, amount1], 0);

      const liquidity1 = await pool.balanceOf(user1.address);

      await tokenA.connect(user2).approve(await pool.getAddress(), amount2);
      await tokenB.connect(user2).approve(await pool.getAddress(), amount2);
      await pool.add_liquidity([amount2, amount2], 0);

      const liquidity2 = await pool.balanceOf(user2.address);

      // user2 存入 2 倍，应该获得约 2 倍 LP
      expect(liquidity2).to.be.gt(liquidity1.mul(1).div(1));
      expect(liquidity2).to.be.lt(liquidity1.mul(3).div(1));
    });
  });

  describe("Exchange", function () {
    beforeEach(async function () {
      // 添加流动性
      const amount = ethers.parseEther("10000");

      await tokenA.mint(owner.address, amount.mul(2));
      await tokenB.mint(owner.address, amount.mul(2));

      await tokenA.approve(await pool.getAddress(), amount);
      await tokenB.approve(await pool.getAddress(), amount);

      await pool.add_liquidity([amount, amount], 0);
    });

    it("Should exchange tokens successfully", async function () {
      const amountIn = ethers.parseEther("100");

      await tokenA.connect(user1).approve(await pool.getAddress(), amountIn);

      const amountOut = await pool.connect(user1).exchange(
        0,  // i
        1,  // j
        amountIn,
        0
      );

      expect(amountOut).to.be.gt(0);
    });

    it("Should have low slippage", async function () {
      const amountIn = ethers.parseEther("100");

      const expectedOut = ethers.parseEther("99");  // 1% slippage
      await tokenA.connect(user1).approve(await pool.getAddress(), amountIn);

      const amountOut = await pool.connect(user1).exchange(
        0,
        1,
        amountIn,
        expectedOut
      );

      expect(amountOut).to.be.gte(expectedOut);
    });

    it("Should revert with insufficient slippage", async function () {
      const amountIn = ethers.parseEther("100");
      const minOut = ethers.parseEther("110");  // 不可能达到

      await tokenA.connect(user1).approve(await pool.getAddress(), amountIn);

      await expect(
        pool.connect(user1).exchange(
          0,
          1,
          amountIn,
          minOut
        )
      ).to.be.revertedWith("Slippage");
    });
  });

  describe("Remove Liquidity", function () {
    it("Should remove liquidity successfully", async function () {
      const amount = ethers.parseEther("1000");

      await tokenA.connect(user1).approve(await pool.getAddress(), amount);
      await tokenB.connect(user1).approve(await pool.getAddress(), amount);

      const liquidity = await pool.connect(user1).add_liquidity(
        [amount, amount],
        0
      );

      await pool.connect(user1).remove_liquidity(
        liquidity,
        [0, 0]
      );

      expect(await pool.balanceOf(user1.address)).to.equal(0);
    });
  });
});
```

---

## 高级功能

### 1. 偏离参数（D 参数）

Curve 使用偏离参数 D 来表示池的状态：

```solidity
uint256 public D;

function _D() internal view returns (uint256) {
    uint256 D = 0;
    for (uint256 i = 0; i < N; i++) {
        D += balances[i];
    }
    return D;
}
```

### 2. 动态费用

根据池状态动态调整费用：

```solidity
function dynamic_fee(
    uint256 i,
    uint256 j,
    uint256 dx
) public view returns (uint256) {
    uint256 fee = base_fee;

    // 根据交易量调整
    uint256 volume = get_volume(i, j);
    if (volume > high_volume_threshold) {
        fee = fee * 95 / 100;  // 高交易量时降低费用
    }

    // 根据不平衡度调整
    uint256 imbalance = get_imbalance();
    if (imbalance > high_imbalance_threshold) {
        fee = fee * 110 / 100;  // 不平衡时增加费用
    }

    return fee;
}
```

### 3. 流动性挖矿

奖励流动性提供者 CRV 代币：

```solidity
contract GaugeV5 {
    mapping(address => uint256) public balanceOf;
    uint256 public totalSupply;

    IERC20 public crv_token;
    address public pool;

    uint256 public inflation_rate;
    uint256 public last_update_time;

    function deposit(uint256 _value) external {
        // 1. 计算待领取奖励
        uint256 reward = _claimable_reward(msg.sender);

        // 2. 更新余额
        balanceOf[msg.sender] += _value;
        totalSupply += _value;

        // 3. 转移 CRV 代币
        if (reward > 0) {
            crv_token.transfer(msg.sender, reward);
        }
    }

    function _claimable_reward(address _user) internal returns (uint256) {
        uint256 time_elapsed = block.timestamp - last_update_time;
        uint256 new_crv = inflation_rate * time_elapsed / 1 days;
        uint256 user_share = balanceOf[_user] * new_crv / totalSupply;
        return user_share;
    }
}
```

### 4. 跨池路由

支持跨多个池的交易路由：

```solidity
contract CurveRouter {
    address[] public pools;

    function exchange_best(
        address[8] memory _route,
        uint256[3] memory _swap_params,
        uint256 _amount,
        uint256 _expected
    ) external returns (uint256) {
        address[8] memory route = _route;

        for (uint256 i = 0; i < route.length; i++) {
            if (route[i] == address(0)) {
                break;
            }

            // 在每个池中交换
            _amount = ICurvePool(route[i]).exchange(
                _swap_params[0],
                _swap_params[1],
                _amount,
                _expected
            );
        }

        return _amount;
    }
}
```

---

## 安全考虑

### 常见漏洞

#### 1. A 值操纵

**问题**：A 值操纵可能导致价格操纵

**防御**：
- 限制 A 值变化范围（MAX_A_CHANGE）
- 设置最小调整时间（MIN_RAMP_TIME）
- 实现时间锁

```solidity
modifier onlyAfter(uint256 _time) {
    require(block.timestamp >= _time, "Too early");
    _;
}

function set_A(uint256 _A) external onlyAdmin onlyAfter(ramp_end_time) {
    A = _A;
}
```

#### 2. 重入攻击

**问题**：重入可能导致余额不一致

**防御**：
```solidity
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract CurvePool is ReentrancyGuard {
    function exchange(...) external nonReentrant {
        // ...
    }
}
```

#### 3. 滑点攻击

**问题**：大额交易可能被操纵

**防御**：
```solidity
function exchange(
    uint256 i,
    uint256 j,
    uint256 dx,
    uint256 min_dy,
    uint256 deadline
) external {
    require(block.timestamp <= deadline, "Deadline");
    require(dy >= min_dy, "Slippage");
}
```

#### 4. 精度损失

**问题**：数学计算精度问题

**防御**：
```solidity
// 使用高精度计算
uint256 constant PRECISION = 10**18;

function calculate(uint256 x, uint256 y) internal pure returns (uint256) {
    return x * PRECISION / y;
}
```

---

## 资源链接

- [Curve Finance 官网](https://curve.fi)
- [Curve GitHub](https://github.com/curvefi)
- [Curve 文档](https://docs.curve.fi)
- [StableSwap 白皮书](https://www.curve.fi/stableswap-paper.pdf)
- [Curve SDK](https://github.com/curvefi/curve-contract)
- [Yearn Finance（使用 Curve 池）](https://yearn.finance)

---

## 总结

### 关键要点

1. **专精稳定币**：Curve 专为相似资产设计，稳定币交易优势明显
2. **低滑点**：StableSwap 算法实现极低滑点
3. **高流动性**：集中稳定币流动性，效率更高
4. **治理代币**：CRV 代币提供流动性挖矿激励
5. **安全优先**：经过严格审计，多次更新改进

### 与其他 DEX 比较

| 特性 | Curve | Uniswap V2 | Uniswap V3 | Balancer |
|------|--------|-------------|-------------|----------|
| 滑点 | 最低 | 中 | 可变 | 可变 |
| 费用 | 0.04% | 0.3% | 可变 | 可变 |
| 适用场景 | 稳定币 | 通用 | 通用 | 通用 |
| 资本效率 | 高 | 中 | 极高 | 高 |
| 复杂度 | 中 | 低 | 高 | 中 |

---

**文档版本**: 1.0.0
**最后更新**: 2026-02-11
**作者**: 上等兵•甘
