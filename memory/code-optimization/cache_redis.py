"""
Redis 缓存模块 - AlphaGPT
高性能内存缓存，支持序列化、TTL、版本控制、LRU 淘汰
"""

import redis
import pickle
import json
import time
import hashlib
from typing import Optional, Dict, Any, List
from loguru import logger
from abc import ABC, abstractmethod


# ============================================================
# 基础 Redis 缓存
# ============================================================

class RedisCache:
    """
    Redis 缓存包装器
    支持序列化、TTL、版本控制
    """

    def __init__(
        self,
        host: str = 'localhost',
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        default_ttl: int = 3600,  # 默认 1 小时过期
        decode_responses: bool = False
    ):
        """
        初始化 Redis 缓存

        Args:
            host: Redis 服务器地址
            port: Redis 服务器端口
            db: 数据库编号
            password: Redis 密码
            default_ttl: 默认 TTL（秒）
            decode_responses: 是否解码响应
        """
        self.host = host
        self.port = port
        self.db = db
        self.default_ttl = default_ttl
        self.decode_responses = decode_responses

        # 创建 Redis 连接
        self.redis = redis.StrictRedis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=decode_responses
        )

        # 测试连接
        try:
            self.redis.ping()
            logger.info(f"Redis cache connected: {host}:{port}, db={db}")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    def _generate_key(self, prefix: str, params: Dict[str, Any]) -> str:
        """
        生成缓存键

        Args:
            prefix: 键前缀
            params: 参数字典

        Returns:
            str: 缓存键
        """
        # 将参数转换为字符串并哈希
        params_str = json.dumps(params, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]

        return f"{prefix}:{params_hash}"

    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存数据

        Args:
            key: 缓存键

        Returns:
            Any: 缓存的数据，如果不存在返回 None
        """
        try:
            data = self.redis.get(key)
            if data is None:
                return None
            return pickle.loads(data)
        except (pickle.PickleError, redis.RedisError) as e:
            logger.error(f"Failed to get cache key {key}: {e}")
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        设置缓存数据

        Args:
            key: 缓存键
            value: 要缓存的数据
            ttl: 过期时间（秒）

        Returns:
            bool: 是否成功
        """
        try:
            data = pickle.dumps(value)
            if ttl is None:
                ttl = self.default_ttl
            self.redis.setex(key, ttl, data)
            return True
        except (pickle.PickleError, redis.RedisError) as e:
            logger.error(f"Failed to set cache key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        删除缓存数据

        Args:
            key: 缓存键

        Returns:
            bool: 是否成功
        """
        try:
            self.redis.delete(key)
            return True
        except redis.RedisError as e:
            logger.error(f"Failed to delete cache key {key}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """
        检查缓存是否存在

        Args:
            key: 缓存键

        Returns:
            bool: 缓存是否存在
        """
        try:
            return self.redis.exists(key) > 0
        except redis.RedisError as e:
            logger.error(f"Failed to check cache key {key}: {e}")
            return False

    def clear(self) -> bool:
        """
        清空当前数据库的所有缓存

        Returns:
            bool: 是否成功
        """
        try:
            self.redis.flushdb()
            logger.info(f"Cleared cache for db={self.db}")
            return True
        except redis.RedisError as e:
            logger.error(f"Failed to clear cache: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息

        Returns:
            Dict[str, Any]: 缓存统计
        """
        try:
            info = self.redis.info()
            return {
                'used_memory': info.get('used_memory_human', 'unknown'),
                'used_memory_bytes': info.get('used_memory', 0),
                'connected_clients': info.get('connected_clients', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'total_keys': self.redis.dbsize(),
                'db_size': self.redis.dbsize()
            }
        except redis.RedisError as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {}


# ============================================================
# 智能数据缓存（支持版本控制）
# ============================================================

class DataCache(RedisCache):
    """
    智能数据缓存
    支持版本控制、自动更新、LRU 淘汰
    """

    def __init__(
        self,
        host: str = 'localhost',
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        default_ttl: int = 3600,
        prefix: str = 'alphaquant:data'
    ):
        """
        初始化数据缓存

        Args:
            host: Redis 服务器地址
            port: Redis 服务器端口
            db: 数据库编号
            password: Redis 密码
            default_ttl: 默认 TTL（秒）
            prefix: 键前缀
        """
        super().__init__(
            host=host,
            port=port,
            db=db,
            password=password,
            default_ttl=default_ttl
        )
        self.prefix = prefix

    def get_data(
        self,
        params: Dict[str, Any],
        version: str = "v1"
    ) -> Optional[Any]:
        """
        获取缓存数据（支持版本控制）

        Args:
            params: 参数字典
            version: 版本号

        Returns:
            Any: 缓存的数据，如果不存在返回 None
        """
        key = self._generate_key(self.prefix, {'params': params, 'version': version})
        cached = self.get(key)

        if cached is not None:
            # 验证版本
            if cached.get('version') == version:
                return cached.get('data')
            else:
                # 版本不匹配，删除旧缓存
                self.delete(key)
                return None

        return None

    def set_data(
        self,
        params: Dict[str, Any],
        data: Any,
        version: str = "v1",
        ttl: Optional[int] = None
    ) -> bool:
        """
        设置缓存数据（支持版本控制）

        Args:
            params: 参数字典
            data: 要缓存的数据
            version: 版本号
            ttl: 过期时间（秒）

        Returns:
            bool: 是否成功
        """
        key = self._generate_key(self.prefix, {'params': params, 'version': version})
        cached_data = {'version': version, 'data': data, 'timestamp': time.time()}
        return self.set(key, cached_data, ttl)

    def is_cached(
        self,
        params: Dict[str, Any],
        version: str = "v1"
    ) -> bool:
        """
        检查数据是否已缓存

        Args:
            params: 参数字典
            version: 版本号

        Returns:
            bool: 是否已缓存
        """
        key = self._generate_key(self.prefix, {'params': params, 'version': version})
        return self.exists(key)


# ============================================================
# 自动更新缓存
# ============================================================

class AutoUpdateCache(DataCache):
    """
    自动更新缓存
    支持后台更新、版本控制
    """

    def __init__(self, *args, **kwargs):
        """
        初始化自动更新缓存
        """
        super().__init__(*args, **kwargs)

    def get_or_load(
        self,
        params: Dict[str, Any],
        loader_func,
        force_refresh: bool = False,
        version: str = "v1",
        ttl: Optional[int] = None
    ) -> Any:
        """
        获取缓存数据，如果不存在则加载

        Args:
            params: 参数字典
            loader_func: 数据加载函数
            force_refresh: 是否强制刷新
            version: 版本号
            ttl: 过期时间（秒）

        Returns:
            Any: 缓存或加载的数据
        """
        # 检查缓存是否存在
        if not force_refresh and self.is_cached(params, version):
            logger.debug(f"Cache hit for {params}")
            cached_data = self.get_data(params, version)
            if cached_data is not None:
                return cached_data.get('data')

        # 缓存不存在或强制刷新
        logger.info(f"Cache miss for {params}, loading from source")
        data = loader_func(params)

        # 更新缓存
        self.set_data(params, data, version, ttl)

        return data

    def get_or_load_multiple(
        self,
        params_list: List[Dict[str, Any]],
        loader_func,
        force_refresh: bool = False,
        version: str = "v1"
    ) -> Dict[str, Any]:
        """
        批量获取缓存数据

        Args:
            params_list: 参数字典列表
            loader_func: 数据加载函数
            force_refresh: 是否强制刷新
            version: 版本号

        Returns:
            Dict[str, Any]: 股票代码到数据的映射
        """
        results = {}

        for params in params_list:
            symbol = params.get('symbol', 'unknown')
            results[symbol] = self.get_or_load(
                params,
                loader_func,
                force_refresh,
                version
            )

        return results


# ============================================================
# LRU 淘汰缓存
# ============================================================

class LRUCache(DataCache):
    """
    LRU 淘汰策略缓存
    基于访问时间和命中率自动淘汰
    """

    def __init__(
        self,
        *args,
        max_keys: int = 1000,
        **kwargs
    ):
        """
        初始化 LRU 缓存

        Args:
            max_keys: 最大缓存键数
        """
        super().__init__(*args, **kwargs)
        self.max_keys = max_keys
        self.access_time: Dict[str, float] = {}

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        设置缓存数据（带 LRU 淘汰）

        Args:
            key: 缓存键
            value: 要缓存的数据
            ttl: 过期时间（秒）

        Returns:
            bool: 是否成功
        """
        # 检查是否需要淘汰
        if len(self.access_time) >= self.max_keys:
            self._evict_lru()

        # 设置缓存
        result = super().set(key, value, ttl)

        # 更新访问时间
        if result:
            self.access_time[key] = time.time()

        return result

    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存数据（更新访问时间）

        Args:
            key: 缓存键

        Returns:
            Any: 缓存的数据，如果不存在返回 None
        """
        # 更新访问时间
        if self.exists(key):
            self.access_time[key] = time.time()

        return super().get(key)

    def _evict_lru(self) -> int:
        """
        淘汰最少使用的缓存

        Returns:
            int: 淘汰的键数量
        """
        # 找到最少访问的键
        if not self.access_time:
            return 0

        # 排序访问时间
        sorted_keys = sorted(self.access_time.items(), key=lambda x: x[1])

        # 淘汰最老的 10% 的键
        evict_count = max(1, len(sorted_keys) // 10)
        for key, _ in sorted_keys[:evict_count]:
            self.delete(key)
            del self.access_time[key]

        logger.info(f"Evicted {evict_count} keys from cache (LRU)")

        return evict_count


# ============================================================
# 热门股票列表
# ============================================================

# A 股热门股票
HOT_CN_STOCKS = [
    "600519.SH",  # 贵州茅台
    "000001.SZ",  # 平安银行
    "600000.SH",  # 浦发银行
    "600036.SH",  # 招商银行
    "601318.SH",  # 中国平安
    "000002.SZ",  # 万科A
    "000858.SZ",  # 五粮液
    "600887.SH",  # 伊利股份
    "000333.SZ",  # 美的集团
    "600276.SH",  # 恒瑞医药
    "600570.SH",  # 恒生电子
    "000651.SZ",  # 格力电器
    "000725.SZ",  # 京东方A
    "601888.SH",  # 中国中车
    "600585.SH",  # 海螺水泥
]

# 美股热门股票
HOT_US_STOCKS = [
    "AAPL",   # Apple
    "MSFT",   # Microsoft
    "GOOGL",  # Google
    "AMZN",   # Amazon
    "TSLA",   # Tesla
    "META",   # Meta
    "NVDA",   # NVIDIA
    "JPM",    # JPMorgan
    "BAC",    # Bank of America
    "DIS",    # Disney
    "NFLX",   # Netflix
    "INTC",   # Intel
    "AMD",    # AMD
    "ORCL",   # Oracle
]


def get_hot_stocks(market: str = "CN") -> List[str]:
    """
    获取热门股票列表

    Args:
        market: 市场（CN: A股，US: 美股）

    Returns:
        List[str]: 股票代码列表
    """
    if market == "CN":
        return HOT_CN_STOCKS
    elif market == "US":
        return HOT_US_STOCKS
    else:
        return []


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    import pandas as pd

    # 测试 Redis 缓存
    print("Testing Redis cache...")

    # 初始化缓存
    cache = DataCache(host='localhost', port=6379, default_ttl=3600)

    # 测试 1: 基本缓存操作
    print("\n1. Basic cache operations:")
    test_data = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})

    # 设置缓存
    cache.set("test_key", test_data, ttl=3600)
    print(f"   Set cache: test_key")

    # 获取缓存
    cached = cache.get("test_key")
    print(f"   Get cache: {cached is not None}")
    print(f"   Data shape: {cached.shape}")

    # 检查缓存是否存在
    exists = cache.exists("test_key")
    print(f"   Cache exists: {exists}")

    # 测试 2: 版本控制
    print("\n2. Version control:")
    params = {'symbol': '600519.SH', 'start_date': '20230101'}
    cache.set_data(params, "data_v1", version="v1")
    print(f"   Set cache v1: {cache.is_cached(params, 'v1')}")

    # 获取 v1
    data_v1 = cache.get_data(params, "v1")
    print(f"   Get cache v1: {data_v1 is not None}")

    # 设置 v2
    cache.set_data(params, "data_v2", version="v2")
    print(f"   Set cache v2: {cache.is_cached(params, 'v1')}")

    # 测试 3: LRU 缓存
    print("\n3. LRU cache:")
    lru_cache = LRUCache(max_keys=5, host='localhost', port=6379)

    # 添加 5 个数据
    for i in range(5):
        lru_cache.set(f"key_{i}", f"value_{i}")
    print(f"   Added key_{i} to cache")

    # 添加第 6 个数据（应该淘汰 1 个）
    lru_cache.set("key_5", "value_5")
    print(f"   Added key_5 to cache (should evict key_0)")

    # 测试 4: 获取缓存统计
    print("\n4. Cache statistics:")
    stats = cache.get_stats()
    print(f"   Used memory: {stats.get('used_memory', 'unknown')}")
    print(f"   Total keys: {stats.get('total_keys', 0)}")
    print(f"   Keyspace hits: {stats.get('keyspace_hits', 0)}")
    print(f"   Keyspace misses: {stats.get('keyspace_misses', 0)}")

    print("\nRedis cache test completed!")
