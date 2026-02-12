"""
缓存预热器 - AlphaGPT
启动时加载热门股票数据到缓存
"""

import time
from datetime import datetime, timedelta
from typing import List, Optional
from loguru import logger
import pandas as pd
import numpy as np


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
    "600570.SH",  # 海能证券
    "000651.SZ",  # 格力电器
    "000725.SZ",  # 京东方A
    "601888.SH",  # 中国中车
    "600585.SH",  # 海螺水泥
]

# 美股热门股票
HOT_US_STOCKS = [
    "AAPL",  # Apple
    "MSFT",  # Microsoft
    "GOOGL",  # Google
    "AMZN",  # Amazon
    "TSLA",  # Tesla
    "META",  # Meta
    "NVDA",  # NVIDIA
    "JPM",   # JPMorgan
    "BAC",   # Bank of America
    "DIS",   # Disney
    "NFLX",  # Netflix
    "INTC",  # Intel
    "AMD",   # AMD
    "ORCL",  # Oracle
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
# 缓存预热器
# ============================================================

class CacheWarmer:
    """
    缓存预热器
    启动时加载热门股票数据到缓存
    """

    def __init__(
        self,
        cache: 'DataCache',
        pro_api_token: Optional[str] = None
    ):
        """
        初始化缓存预热器

        Args:
            cache: 数据缓存实例
            pro_api_token: Tushare Pro API Token
        """
        self.cache = cache
        self.pro_api_token = pro_api_token

        # 设置历史日期范围
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')

        self.start_date = start_date
        self.end_date = end_date

        logger.info(f"Cache warmer initialized: {start_date} - {end_date}")

    def warmup_cn_stocks(
        self,
        stocks: Optional[List[str]] = None
    ) -> int:
        """
        预热 A 股数据

        Args:
            stocks: 股票代码列表（可选）

        Returns:
            int: 预热的股票数量
        """
        if self.pro_api_token is None:
            logger.warning("Tushare Pro token not provided, skipping CN stocks warmup")
            return 0

        if stocks is None:
            stocks = get_hot_stocks("CN")

        import tushare as ts
        pro = ts.pro_api(self.pro_api_token)

        warmed_count = 0
        start_time = time.time()

        for symbol in stocks:
            try:
                params = {
                    'symbol': symbol,
                    'start_date': self.start_date,
                    'end_date': self.end_date
                }

                # 检查是否已缓存
                if self.cache.is_cached(params):
                    logger.debug(f"{symbol} already cached, skipping")
                    continue

                # 从 Tushare Pro 加载数据
                logger.info(f"Loading {symbol} from Tushare Pro...")
                df_daily = pro.daily(
                    ts_code=symbol,
                    start_date=self.start_date,
                    end_date=self.end_date
                )

                df_basic = pro.daily_basic(
                    ts_code=symbol,
                    start_date=self.start_date,
                    end_date=self.end_date
                )

                # 合并数据
                df = pd.merge(df_daily, df_basic, on=['ts_code', 'trade_date'])

                # 缓存数据
                self.cache.set_data(params, df, ttl=86400)  # 24 小时过期
                warmed_count += 1

                logger.success(f"Warmed up {symbol} ({len(df)} rows)")

            except Exception as e:
                logger.error(f"Failed to warm up {symbol}: {e}")

        elapsed = time.time() - start_time
        logger.info(f"CN stocks warmup completed: {warmed_count}/{len(stocks)} in {elapsed:.2f}s")

        return warmed_count

    def warmup_us_stocks(
        self,
        stocks: Optional[List[str]] = None
    ) -> int:
        """
        预热美股数据

        Args:
            stocks: 股票代码列表（可选）

        Returns:
            int: 预热的股票数量
        """
        try:
            import yfinance as yf
        except ImportError:
            logger.warning("yfinance not installed, skipping US stocks warmup")
            return 0

        if stocks is None:
            stocks = get_hot_stocks("US")

        warmed_count = 0
        start_time = time.time()

        for symbol in stocks:
            try:
                params = {
                    'symbol': symbol,
                    'start_date': self.start_date,
                    'end_date': self.end_date
                }

                # 检查是否已缓存
                if self.cache.is_cached(params):
                    logger.debug(f"{symbol} already cached, skipping")
                    continue

                # 从 yfinance 加载数据
                logger.info(f"Loading {symbol} from yfinance...")
                df = yf.download(
                    symbol,
                    start=self.start_date,
                    end=self.end_date,
                    progress=False
                )

                # 重置索引并添加 ts_code
                df.reset_index(inplace=True)
                df['ts_code'] = symbol
                df.rename(columns={'Date': 'trade_date'}, inplace=True)

                # 缓存数据
                self.cache.set_data(params, df, ttl=86400)  # 24 小时过期
                warmed_count += 1

                logger.success(f"Warmed up {symbol} ({len(df)} rows)")

            except Exception as e:
                logger.error(f"Failed to warm up {symbol}: {e}")

        elapsed = time.time() - start_time
        logger.info(f"US stocks warmup completed: {warmed_count}/{len(stocks)} in {elapsed:.2f}s")

        return warmed_count

    def warmup_all(self) -> int:
        """
        预热所有热门股票数据

        Returns:
            int: 预热的股票总数
        """
        logger.info("Starting cache warmup...")
        start_time = time.time()

        total_warmed = 0

        # 预热 A 股
        cn_stocks = get_hot_stocks("CN")
        total_warmed += self.warmup_cn_stocks(cn_stocks)

        # 预热美股
        us_stocks = get_hot_stocks("US")
        total_warmed += self.warmup_us_stocks(us_stocks)

        # 获取缓存统计
        stats = self.cache.get_stats()
        logger.info(f"Cache warmup completed: {total_warmed} stocks warmed")
        logger.info(f"Cache stats: {stats}")

        elapsed = time.time() - start_time
        logger.info(f"Total warmup time: {elapsed:.2f}s")

        return total_warmed


# ============================================================
# 模拟缓存（用于测试）
# ============================================================

class MockDataCache:
    """模拟缓存（用于测试）"""

    def __init__(self):
        """初始化模拟缓存"""
        self.cache: dict = {}

    def is_cached(self, params: dict, version: str = "v1") -> bool:
        """检查是否已缓存"""
        key = str(params)
        return key in self.cache

    def set_data(self, params: dict, data: Any, version: str = "v1", ttl: int = 3600):
        """设置缓存数据"""
        key = str(params)
        self.cache[key] = data

    def get_data(self, params: dict, version: str = "v1"):
        """获取缓存数据"""
        key = str(params)
        return self.cache.get(key)

    def get_stats(self) -> dict:
        """获取缓存统计"""
        return {
            'used_memory': "0.0B",
            'connected_clients': "0",
            'total_keys': len(self.cache)
        }


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    # 测试缓存预热
    print("Testing cache warmer...")

    # 创建模拟缓存
    mock_cache = MockDataCache()

    # 创建缓存预热器
    warmer = CacheWarmer(
        cache=mock_cache,
        pro_api_token=None  # 不使用真实 Tushare API
    )

    # 预热 A 股（模拟）
    print("\n1. Warming up CN stocks (mock)...")
    cn_stocks = get_hot_stocks("CN")[:3]  # 只预热前 3 个
    print(f"CN stocks: {cn_stocks}")

    # 模拟数据
    import pandas as pd
    import numpy as np

    for symbol in cn_stocks:
        params = {
            'symbol': symbol,
            'start_date': warmer.start_date,
            'end_date': warmer.end_date
        }

        # 检查是否已缓存
        if mock_cache.is_cached(params):
            print(f"  {symbol} already cached, skipping")
            continue

        # 创建模拟数据
        n = 250  # 250 个交易日
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', periods=n, freq='D')
        prices = np.cumprod(1 + np.random.randn(n) * 0.01)

        df = pd.DataFrame({
            'ts_code': symbol,
            'trade_date': dates.strftime('%Y%m%d').values,
            'close': prices,
            'vol': np.random.randint(100000, 1000000, n),
            'amount': np.random.randint(1000000000, 10000000000, n)
        })

        # 缓存数据
        mock_cache.set_data(params, df)
        print(f"  Warmed up {symbol} ({len(df)} rows)")

    # 获取缓存统计
    stats = mock_cache.get_stats()
    print(f"\nCache stats: {stats}")
    print(f"Total keys: {stats['total_keys']}")

    print("\nCache warmer test completed!")
