"""
AlphaGPT 因子计算性能基准测试（不使用 Numba）
对比 Pandas 向量化 vs NumPy 优化的性能
"""

import time
import numpy as np
import pandas as pd
from typing import Dict, Tuple


# ============================================================
# Pandas 向量化版本
# ============================================================

def calculate_momentum_pandas(prices: pd.Series, period: int = 20) -> pd.Series:
    """
    计算动量因子（Pandas 向量化）

    Args:
        prices: 价格 Series
        period: 计算周期

    Returns:
        pd.Series: 动量因子
    """
    # 使用 pct_change 直接计算收益率
    return prices.pct_change(period)


def calculate_volatility_pandas(prices: pd.Series, period: int = 20) -> pd.Series:
    """
    计算波动率因子（Pandas 向量化）

    Args:
        prices: 价格 Series
        period: 计算周期

    Returns:
        pd.Series: 波动率因子
    """
    # 计算收益率
    returns = prices.pct_change()

    # 计算滚动标准差
    return returns.rolling(period).std()


def calculate_skew_pandas(prices: pd.Series, period: int = 20) -> pd.Series:
    """
    计算偏度因子（Pandas 向量化）

    Args:
        prices: 价格 Series
        period: 计算周期

    Returns:
        pd.Series: 偏度因子
    """
    # 计算收益率
    returns = prices.pct_change()

    # 计算滚动偏度
    return returns.rolling(period).skew()


# ============================================================
# NumPy 优化版本
# ============================================================

def calculate_momentum_numpy(prices: np.ndarray, period: int = 20) -> np.ndarray:
    """
    计算动量因子（NumPy 向量化）

    Args:
        prices: 价格数组
        period: 计算周期

    Returns:
        np.ndarray: 动量因子
    """
    # 使用广播计算收益率
    returns = prices[1:] / prices[:-1] - 1

    # 计算动量
    momentum = np.zeros_like(prices)
    momentum[period:] = prices[period:] / prices[:-period] - 1

    return momentum


def calculate_volatility_numpy(prices: np.ndarray, period: int = 20) -> np.ndarray:
    """
    计算波动率因子（NumPy 向量化）

    Args:
        prices: 价格数组
        period: 计算周期

    Returns:
        np.ndarray: 波动率因子
    """
    # 计算收益率
    returns = prices[1:] / prices[:-1] - 1
    returns_padded = np.concatenate([[0], returns])

    # 计算滚动标准差
    volatility = np.zeros_like(prices)
    for i in range(period, len(prices)):
        window_returns = returns_padded[i-period:i]
        volatility[i] = np.std(window_returns)

    return volatility


def calculate_skew_numpy(prices: np.ndarray, period: int = 20) -> np.ndarray:
    """
    计算偏度因子（NumPy 向量化）

    Args:
        prices: 价格数组
        period: 计算周期

    Returns:
        np.ndarray: 偏度因子
    """
    # 计算收益率
    returns = prices[1:] / prices[:-1] - 1
    returns_padded = np.concatenate([[0], returns])

    # 计算滚动偏度
    skew = np.zeros_like(prices)
    for i in range(period, len(prices)):
        window_returns = returns_padded[i-period:i]
        skew[i] = pd.Series(window_returns).skew()

    return skew


# ============================================================
# 性能基准测试
# ============================================================

def benchmark_all_methods(
    prices_series: pd.Series,
    prices_array: np.ndarray,
    period: int = 20
) -> Dict:
    """
    基准测试所有方法

    Args:
        prices_series: Pandas Series
        prices_array: NumPy array
        period: 计算周期

    Returns:
        Dict: 性能基准测试结果
    """
    results = {}

    # 测试 1: Pandas 动量
    start = time.time()
    momentum_pd = calculate_momentum_pandas(prices_series, period)
    end = time.time()
    pandas_momentum_time = end - start
    results['pandas_momentum'] = pandas_momentum_time

    # 测试 2: NumPy 动量
    start = time.time()
    momentum_np = calculate_momentum_numpy(prices_array, period)
    end = time.time()
    numpy_momentum_time = end - start
    results['numpy_momentum'] = numpy_momentum_time

    # 测试 3: Pandas 波动率
    start = time.time()
    vol_pd = calculate_volatility_pandas(prices_series, period)
    end = time.time()
    pandas_volatility_time = end - start
    results['pandas_volatility'] = pandas_volatility_time

    # 测试 4: NumPy 波动率
    start = time.time()
    vol_np = calculate_volatility_numpy(prices_array, period)
    end = time.time()
    numpy_volatility_time = end - start
    results['numpy_volatility'] = numpy_volatility_time

    # 测试 5: Pandas 偏度
    start = time.time()
    skew_pd = calculate_skew_pandas(prices_series, period)
    end = time.time()
    pandas_skew_time = end - start
    results['pandas_skew'] = pandas_skew_time

    # 测试 6: NumPy 偏度
    start = time.time()
    skew_np = calculate_skew_numpy(prices_array, period)
    end = time.time()
    numpy_skew_time = end - start
    results['numpy_skew'] = numpy_skew_time

    # 计算提升倍数
    speedup_momentum = pandas_momentum_time / numpy_momentum_time
    speedup_volatility = pandas_volatility_time / numpy_volatility_time
    speedup_skew = pandas_skew_time / numpy_skew_time

    print(f"\n性能基准测试结果（{len(prices_array):,} 个数据点）：")
    print(f"  Pandas -> NumPy (动量）: {speedup_momentum:.2f}x 提升")
    print(f"  Pandas -> NumPy (波动率）: {speedup_volatility:.2f}x 提升")
    print(f"  Pandas -> NumPy (偏度）: {speedup_skew:.2f}x 提升")

    return results


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    # 创建测试数据（1000 个数据点）
    n = 1_000
    np.random.seed(42)
    prices = np.cumprod(1 + np.random.randn(n) * 0.01)
    prices_series = pd.Series(prices)
    prices_array = prices

    print(f"测试数据: {n:,} 个数据点")
    print(f"价格范围: {prices.min():.2f} - {prices.max():.2f}")

    # 性能基准测试
    results = benchmark_all_methods(prices_series, prices_array, period=20)

    # 计算总时间
    pandas_total = (results['pandas_momentum'] +
                    results['pandas_volatility'] +
                    results['pandas_skew'])
    numpy_total = (results['numpy_momentum'] +
                   results['numpy_volatility'] +
                   results['numpy_skew'])

    print(f"\n总时间：")
    print(f"  Pandas: {pandas_total:.4f}s")
    print(f"  NumPy: {numpy_total:.4f}s")
    print(f"  总提升: {pandas_total / numpy_total:.2f}x")
