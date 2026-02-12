"""
优化的因子计算模块 - AlphaGPT
使用 NumPy 和 Numba 实现高性能因子计算
"""

import numpy as np
import pandas as pd
from numba import jit, prange, float64, int32
from typing import Tuple, Dict, Optional
import time


# ============================================================
# Numba JIT 编译的函数（机器码级别执行）
# ============================================================

@jit(nopython=True, cache=True)
def calculate_returns_numba(prices: float64[:]) -> float64[:]:
    """
    使用 Numba JIT 编译计算收益率

    Args:
        prices: 价格数组

    Returns:
        float64[:]: 收益率数组
    """
    n = len(prices)
    returns = np.zeros(n - 1, dtype=np.float64)

    for i in prange(n - 1):
        returns[i] = (prices[i + 1] / prices[i]) - 1

    return returns


@jit(nopython=True, cache=True)
def calculate_momentum_numba(prices: float64[:], period: int32) -> float64[:]:
    """
    使用 Numba JIT 编译计算动量因子

    Args:
        prices: 价格数组
        period: 计算周期

    Returns:
        float64[:]: 动量因子数组
    """
    n = len(prices)
    momentum = np.zeros(n, dtype=np.float64)

    for i in prange(period, n):
        momentum[i] = (prices[i] / prices[i - period]) - 1

    return momentum


@jit(nopython=True, cache=True)
def calculate_volatility_numba(prices: float64[:], period: int32) -> float64[:]:
    """
    使用 Numba JIT 编译计算波动率因子

    Args:
        prices: 价格数组
        period: 计算周期

    Returns:
        float64[:]: 波动率数组
    """
    n = len(prices)
    volatility = np.zeros(n, dtype=np.float64)

    for i in prange(period, n):
        # 计算滚动均值
        mean = 0.0
        for j in range(i - period, i):
            mean += prices[j]
        mean /= period

        # 计算滚动标准差
        sum_sq = 0.0
        for j in range(i - period, i):
            diff = prices[j] - mean
            sum_sq += diff * diff

        variance = sum_sq / period
        volatility[i] = np.sqrt(variance)

    return volatility


@jit(nopython=True, cache=True)
def calculate_skew_numba(prices: float64[:], period: int32) -> float64[:]:
    """
    使用 Numba JIT 编译计算偏度因子

    Args:
        prices: 价格数组
        period: 计算周期

    Returns:
        float64[:]: 偏度因子数组
    """
    n = len(prices)
    skew = np.zeros(n, dtype=np.float64)

    for i in prange(period, n):
        # 计算滚动均值
        mean = 0.0
        for j in range(i - period, i):
            mean += prices[j]
        mean /= period

        # 计算滚动标准差
        sum_sq = 0.0
        for j in range(i - period, i):
            diff = prices[j] - mean
            sum_sq += diff * diff

        std = np.sqrt(sum_sq / period)

        if std > 0:
            skew[i] = (prices[i] - mean) / std
        else:
            skew[i] = 0.0

    return skew


@jit(nopython=True, parallel=True, cache=True)
def calculate_all_factors_parallel(
    prices: float64[:],
    period: int32
) -> Tuple[float64[:], float64[:], float64[:]]:
    """
    使用 Numba JIT 并行计算所有因子

    Args:
        prices: 价格数组
        period: 计算周期

    Returns:
        Tuple[float64[:], float64[:], float64[:]]: (动量, 波动率, 偏度)
    """
    n = len(prices)
    momentum = np.zeros(n, dtype=np.float64)
    volatility = np.zeros(n, dtype=np.float64)
    skew = np.zeros(n, dtype=np.float64)

    # 并行计算
    for i in prange(period, n):
        # 计算动量
        momentum[i] = (prices[i] / prices[i - period]) - 1

        # 计算波动率
        mean = 0.0
        for j in range(i - period, i):
            mean += prices[j]
        mean /= period

        sum_sq = 0.0
        for j in range(i - period, i):
            diff = prices[j] - mean
            sum_sq += diff * diff

        volatility[i] = np.sqrt(sum_sq / period)

        # 计算偏度
        if volatility[i] > 0:
            skew[i] = (prices[i] - mean) / volatility[i]
        else:
            skew[i] = 0.0

    return momentum, volatility, skew


# ============================================================
# NumPy 向量化函数（中等性能）
# ============================================================

def calculate_momentum_numpy(prices: np.ndarray, period: int = 20) -> np.ndarray:
    """
    使用 NumPy 向量化计算动量因子

    Args:
        prices: 价格数组
        period: 计算周期

    Returns:
        np.ndarray: 动量因子数组
    """
    # 使用广播计算收益率
    returns = prices[1:] / prices[:-1] - 1

    # 计算动量：当前价格 / N 期前价格 - 1
    momentum = np.zeros_like(prices)
    momentum[period:] = prices[period:] / prices[:-period] - 1

    return momentum


def calculate_volatility_numpy(prices: np.ndarray, period: int = 20) -> np.ndarray:
    """
    使用 NumPy 向量化计算波动率因子

    Args:
        prices: 价格数组
        period: 计算周期

    Returns:
        np.ndarray: 波动率因子数组
    """
    # 计算收益率
    returns = prices[1:] / prices[:-1] - 1

    # 计算滚动标准差
    volatility = np.zeros_like(prices)
    for i in range(period, len(prices)):
        window_returns = returns[i-period:i]
        volatility[i] = np.std(window_returns)

    return volatility


def calculate_skew_numpy(prices: np.ndarray, period: int = 20) -> np.ndarray:
    """
    使用 NumPy 向量化计算偏度因子

    Args:
        prices: 价格数组
        period: 计算周期

    Returns:
        np.ndarray: 偏度因子数组
    """
    # 计算收益率
    returns = prices[1:] / prices[:-1] - 1

    # 计算滚动偏度
    skew = np.zeros_like(prices)
    for i in range(period, len(prices)):
        window_returns = returns[i-period:i]
        skew[i] = pd.Series(window_returns).skew()

    return skew


# ============================================================
# 高级优化类
# ============================================================

class OptimizedFactorCalculator:
    """
    优化的因子计算器
    使用 Numba JIT 和 NumPy 实现高性能因子计算
    """

    def __init__(self, warmup: bool = True):
        """
        初始化因子计算器

        Args:
            warmup: 是否预热 Numba JIT 编译器
        """
        if warmup:
            self._warmup_jit()

    def _warmup_jit(self) -> None:
        """
        预热 Numba JIT 编译器

        第一次调用会较慢，之后会非常快
        """
        prices = np.random.randn(100).astype(np.float64)
        calculate_momentum_numba(prices, 20)
        calculate_volatility_numba(prices, 20)
        calculate_skew_numba(prices, 20)

    def calculate_momentum(
        self,
        prices: np.ndarray,
        period: int = 20,
        method: str = 'numba'
    ) -> np.ndarray:
        """
        计算动量因子

        Args:
            prices: 价格数组
            period: 计算周期
            method: 计算方法 ('pandas', 'numpy', 'numba', 'numba_parallel')

        Returns:
            np.ndarray: 动量因子数组
        """
        if method == 'pandas':
            # 使用 Pandas（最慢）
            df = pd.DataFrame({'close': prices})
            return df['close'].pct_change(period).values

        elif method == 'numpy':
            # 使用 NumPy 向量化（中等）
            return calculate_momentum_numpy(prices, period)

        elif method == 'numba':
            # 使用 Numba JIT（快）
            return calculate_momentum_numba(prices.astype(np.float64), period)

        elif method == 'numba_parallel':
            # 使用 Numba 并行（最快）
            prices_arr = prices.astype(np.float64)
            result, _, _ = calculate_all_factors_parallel(prices_arr, period)
            return result

        else:
            raise ValueError(f"Unknown method: {method}")

    def calculate_volatility(
        self,
        prices: np.ndarray,
        period: int = 20,
        method: str = 'numba'
    ) -> np.ndarray:
        """
        计算波动率因子

        Args:
            prices: 价格数组
            period: 计算周期
            method: 计算方法 ('pandas', 'numpy', 'numba')

        Returns:
            np.ndarray: 波动率因子数组
        """
        if method == 'pandas':
            df = pd.DataFrame({'close': prices})
            returns = df['close'].pct_change()
            return returns.rolling(period).std().values

        elif method == 'numpy':
            return calculate_volatility_numpy(prices, period)

        elif method == 'numba':
            return calculate_volatility_numba(prices.astype(np.float64), period)

        else:
            raise ValueError(f"Unknown method: {method}")

    def calculate_skew(
        self,
        prices: np.ndarray,
        period: int = 20,
        method: str = 'numpy'
    ) -> np.ndarray:
        """
        计算偏度因子

        Args:
            prices: 价格数组
            period: 计算周期
            method: 计算方法 ('pandas', 'numpy', 'numba')

        Returns:
            np.ndarray: 偏度因子数组
        """
        if method == 'pandas':
            df = pd.DataFrame({'close': prices})
            returns = df['close'].pct_change()
            return returns.rolling(period).skew().values

        elif method == 'numpy':
            return calculate_skew_numpy(prices, period)

        elif method == 'numba':
            return calculate_skew_numba(prices.astype(np.float64), period)

        else:
            raise ValueError(f"Unknown method: {method}")

    def calculate_all_factors(
        self,
        df: pd.DataFrame,
        period: int = 20
    ) -> pd.DataFrame:
        """
        计算所有因子

        Args:
            df: 包含收盘价的 DataFrame
            period: 计算周期

        Returns:
            pd.DataFrame: 包含所有因子的 DataFrame
        """
        prices = df['close'].values

        # 使用最快的 Numba 并行方法
        momentum, volatility, skew = calculate_all_factors_parallel(
            prices.astype(np.float64),
            period
        )

        # 添加因子到 DataFrame
        df['momentum_20'] = momentum
        df['volatility_20'] = volatility
        df['skew_20'] = skew

        return df

    def benchmark(self, df: pd.DataFrame, period: int = 20) -> Dict:
        """
        性能基准测试

        Args:
            df: 包含收盘价的 DataFrame
            period: 计算周期

        Returns:
            Dict: 性能基准测试结果
        """
        prices = df['close'].values

        results = {}

        # 测试 1: Pandas 向量化
        start = time.time()
        momentum_pd = self.calculate_momentum(prices, period, 'pandas')
        end = time.time()
        results['pandas'] = end - start

        # 测试 2: NumPy 向量化
        start = time.time()
        momentum_np = self.calculate_momentum(prices, period, 'numpy')
        end = time.time()
        results['numpy'] = end - start

        # 测试 3: Numba JIT
        start = time.time()
        momentum_nb = self.calculate_momentum(prices, period, 'numba')
        end = time.time()
        results['numba'] = end - start

        # 测试 4: Numba 并行
        start = time.time()
        momentum_nbp = self.calculate_momentum(prices, period, 'numba_parallel')
        end = time.time()
        results['numba_parallel'] = end - start

        # 计算提升倍数
        speedup_numpy = results['pandas'] / results['numpy']
        speedup_numba = results['pandas'] / results['numba']
        speedup_parallel = results['pandas'] / results['numba_parallel']

        print(f"\n性能基准测试结果（{len(prices)} 个数据点）：")
        print(f"  Pandas 向量化:   {results['pandas']:.4f}s")
        print(f"  NumPy 向量化:    {results['numpy']:.4f}s ({speedup_numpy:.1f}x 提升)")
        print(f"  Numba JIT:        {results['numba']:.4f}s ({speedup_numba:.1f}x 提升)")
        print(f"  Numba 并行:       {results['numba_parallel']:.4f}s ({speedup_parallel:.1f}x 提升)")

        return results


# ============================================================
# 便捷函数
# ============================================================

def calculate_all_factors_fast(
    df: pd.DataFrame,
    period: int = 20
) -> pd.DataFrame:
    """
    快速计算所有因子（使用 Numba 并行）

    Args:
        df: 包含收盘价的 DataFrame
        period: 计算周期

    Returns:
        pd.DataFrame: 包含所有因子的 DataFrame
    """
    calculator = OptimizedFactorCalculator(warmup=True)
    return calculator.calculate_all_factors(df, period)


def benchmark_factor_calculation(
    df: pd.DataFrame,
    period: int = 20
) -> Dict:
    """
    因子计算基准测试

    Args:
        df: 包含收盘价的 DataFrame
        period: 计算周期

    Returns:
        Dict: 性能基准测试结果
    """
    calculator = OptimizedFactorCalculator(warmup=True)
    return calculator.benchmark(df, period)


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    # 创建测试数据
    n = 1_000_000  # 100 万个数据点
    np.random.seed(42)
    prices = np.cumprod(1 + np.random.randn(n) * 0.01)
    df = pd.DataFrame({'close': prices})

    print(f"测试数据: {n:,} 个数据点")
    print(f"价格范围: {prices.min():.2f} - {prices.max():.2f}")

    # 计算所有因子（最快版本）
    start = time.time()
    df_with_factors = calculate_all_factors_fast(df, period=20)
    end = time.time()

    print(f"\n因子计算耗时: {end - start:.4f}s")
    print(f"计算因子数: 3")
    print(f"数据行数: {len(df_with_factors)}")

    # 显示因子统计
    print("\n因子统计:")
    for col in ['momentum_20', 'volatility_20', 'skew_20']:
        if col in df_with_factors.columns:
            stats = df_with_factors[col].describe()
            print(f"  {col}:")
            print(f"    均值: {stats['mean']:.6f}")
            print(f"    标准差: {stats['std']:.6f}")
            print(f"    最小值: {stats['min']:.6f}")
            print(f"    最大值: {stats['max']:.6f}")

    # 性能基准测试
    print("\n性能基准测试:")
    benchmark_results = benchmark_factor_calculation(df.head(100000))  # 使用 10 万点进行基准测试
