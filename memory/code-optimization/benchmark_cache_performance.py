"""
Redis 缓存性能基准测试
对比 Redis 缓存 vs 文件 I/O 的性能
"""

import time
import pandas as pd
import numpy as np
from typing import Dict, Optional


# ============================================================
# 模拟 Redis 缓存（用于测试）
# ============================================================

class MockRedisCache:
    """
    模拟 Redis 缓存
    使用 Python 字典模拟内存缓存
    """

    def __init__(self, default_ttl: int = 3600):
        """
        初始化模拟 Redis 缓存

        Args:
            default_ttl: 默认 TTL（秒）
        """
        self.cache: Dict[str, bytes] = {}
        self.default_ttl = default_ttl
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0
        }

    def get(self, key: str) -> Optional[pd.DataFrame]:
        """
        获取缓存数据

        Args:
            key: 缓存键

        Returns:
            pd.DataFrame: 缓存的数据，如果不存在返回 None
        """
        if key in self.cache:
            self.stats['hits'] += 1
            # 模拟 pickle 反序列化开销
            import pickle
            try:
                return pickle.loads(self.cache[key])
            except:
                return None
        else:
            self.stats['misses'] += 1
            return None

    def set(self, key: str, value: pd.DataFrame, ttl: Optional[int] = None) -> None:
        """
        设置缓存数据

        Args:
            key: 缓存键
            value: 要缓存的数据
            ttl: 过期时间（秒）
        """
        import pickle
        self.cache[key] = pickle.dumps(value)
        self.stats['sets'] += 1

    def exists(self, key: str) -> bool:
        """
        检查缓存是否存在

        Args:
            key: 缓存键

        Returns:
            bool: 缓存是否存在
        """
        return key in self.cache

    def get_stats(self) -> Dict[str, any]:
        """
        获取缓存统计信息

        Returns:
            Dict: 缓存统计
        """
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = self.stats['hits'] / total_requests if total_requests > 0 else 0

        return {
            'total_keys': len(self.cache),
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'sets': self.stats['sets'],
            'hit_rate': hit_rate,
            'used_memory': '0.0B'  # 模拟
        }


# ============================================================
# 模拟文件 I/O
# ============================================================

class MockFileIO:
    """
    模拟文件 I/O
    使用 CSV 文件模拟磁盘读取
    """

    def __init__(self, temp_dir: str = "/tmp"):
        """
        初始化模拟文件 I/O

        Args:
            temp_dir: 临时目录
        """
        import tempfile
        import os

        self.temp_dir = temp_dir
        os.makedirs(temp_dir, exist_ok=True)

    def save(self, path: str, df: pd.DataFrame) -> None:
        """
        保存 DataFrame 到 CSV 文件

        Args:
            path: 文件路径
            df: 要保存的 DataFrame
        """
        full_path = f"{self.temp_dir}/{path}"
        df.to_csv(full_path, index=False)

    def load(self, path: str) -> pd.DataFrame:
        """
        从 CSV 文件加载 DataFrame

        Args:
            path: 文件路径

        Returns:
            pd.DataFrame: 加载的 DataFrame
        """
        full_path = f"{self.temp_dir}/{path}"
        return pd.read_csv(full_path)


# ============================================================
# 性能基准测试
# ============================================================

def benchmark_cache_vs_file(
    df: pd.DataFrame,
    n_reads: int = 100
    cache_ttl: int = 3600
) -> Dict:
    """
    基准测试：Redis 缓存 vs 文件 I/O

    Args:
        df: 测试数据
        n_reads: 读取次数
        cache_ttl: 缓存 TTL（秒）

    Returns:
        Dict: 性能基准测试结果
    """
    print(f"\n性能基准测试（{len(df):,} 行数据, {n_reads} 次读取）：")

    # 初始化模拟组件
    cache = MockRedisCache(default_ttl=cache_ttl)
    file_io = MockFileIO()

    # 缓存键
    cache_key = "test_data"

    # 保存数据到文件（模拟文件 I/O）
    print(f"  保存数据到文件...")
    file_io.save("test_data.csv", df)
    print(f"  完成！")

    # 测试 1: 文件 I/O（慢）
    print(f"\n测试 1: 文件 I/O（模拟磁盘读取）")
    start = time.time()
    for i in range(n_reads):
        df_copy = file_io.load("test_data.csv")
        # 模拟处理（深拷贝）
        processed = df_copy.copy()
    file_io_time = time.time() - start
    print(f"  文件 I/O: {file_io_time:.4f}s")

    # 测试 2: Redis 缓存（快）
    print(f"\n测试 2: Redis 缓存（模拟内存读取）")
    cache.set(cache_key, df, ttl=cache_ttl)

    start = time.time()
    for i in range(n_reads):
        cached_df = cache.get(cache_key)
        if cached_df is not None:
            # 模拟处理（浅拷贝）
            processed = cached_df.copy()
    cache_time = time.time() - start
    print(f"  Redis 缓存: {cache_time:.4f}s")

    # 计算提升倍数
    speedup = file_io_time / cache_time

    print(f"\n性能提升：")
    print(f"  Redis 缓存 vs 文件 I/O: {speedup:.1f}x")

    # 获取缓存统计
    stats = cache.get_stats()
    print(f"\n缓存统计：")
    print(f"  总缓存键数: {stats['total_keys']}")
    print(f"  缓存命中: {stats['hits']}")
    print(f"  缓存未命中: {stats['misses']}")
    print(f"  命中率: {stats['hit_rate']*100:.2f}%")

    return {
        'file_io_time': file_io_time,
        'cache_time': cache_time,
        'speedup': speedup,
        'cache_stats': stats
    }


def benchmark_cache_sizes(
    df: pd.DataFrame,
    sizes: list = [100, 1000, 10000, 100000]
) -> Dict:
    """
    基准测试：不同数据规模的性能

    Args:
        df: 测试数据
        sizes: 数据规模列表

    Returns:
        Dict: 性能基准测试结果
    """
    print(f"\n性能基准测试（不同数据规模）：")
    print(f"  原始数据: {len(df):,} 行")

    results = {}

    for size in sizes:
        # 截取数据
        df_test = df.head(size).copy()

        # 运行基准测试
        print(f"\n数据规模: {size:,} 行")
        benchmark_result = benchmark_cache_vs_file(df_test, n_reads=100)

        # 记录结果
        results[size] = benchmark_result

        # 打印结果
        print(f"  文件 I/O: {benchmark_result['file_io_time']:.4f}s")
        print(f"  Redis 缓存: {benchmark_result['cache_time']:.4f}s")
        print(f"  性能提升: {benchmark_result['speedup']:.1f}x")

    # 汇总结果
    print(f"\n性能基准测试结果汇总：")
    print(f"  {'数据规模':<12} {'文件 I/O':<12} {'Redis 缓存':<12} {'性能提升':<12}")
    print(f"  {'='*12:<12} {'='*12:<12} {'='*12:<12} {'='*12:<12}")

    for size, result in results.items():
        file_io_time = result['file_io_time']
        cache_time = result['cache_time']
        speedup = result['speedup']

        print(f"  {size:<12,} {file_io_time:>12.4f}s {cache_time:>12.4f}s {speedup:>11.1f}x")

    return results


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    # 创建测试数据（10 万个数据点）
    n = 100000
    np.random.seed(42)
    prices = np.cumprod(1 + np.random.randn(n) * 0.01)
    dates = pd.date_range('2023-01-01', periods=n, freq='D')

    df = pd.DataFrame({
        'ts_code': '600519.SH',
        'trade_date': dates,
        'close': prices,
        'open': prices * (1 + np.random.randn(n) * 0.01),
        'high': prices * (1 + np.abs(np.random.randn(n)) * 0.01),
        'low': prices * (1 - np.abs(np.random.randn(n)) * 0.01),
        'vol': np.random.randint(100000, 1000000, n)
    })

    print(f"测试数据: {n:,} 个数据点")
    print(f"数据列: {', '.join(df.columns)}")
    print(f"内存占用: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")

    # 基准测试：不同数据规模
    results = benchmark_cache_sizes(df, sizes=[100, 1000, 10000, 100000])

    # 详细的基准测试（100K 数据）
    print(f"\n详细性能基准测试（{n:,} 行数据）：")
    print(f"  读取次数: 100")
    detailed_result = benchmark_cache_vs_file(df, n_reads=100)

    # 输出结果
    print(f"\n详细性能基准测试结果：")
    print(f"  文件 I/O: {detailed_result['file_io_time']:.4f}s")
    print(f"  Redis 缓存: {detailed_result['cache_time']:.4f}s")
    print(f"  性能提升: {detailed_result['speedup']:.1f}x")
    print(f"\n缓存统计：")
    for key, value in detailed_result['cache_stats'].items():
        print(f"  {key}: {value}")
