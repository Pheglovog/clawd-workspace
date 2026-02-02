---
title: "Tushare Pro 2000 积分配置指南"
date: 2026-01-31
tags: ["Python", "Tushare", "API"]
categories: ["量化交易"]
draft: false
---

## Tushare Pro 简介

Tushare Pro 是中国股市最全面的数据接口平台，提供股票行情、财务数据、宏观经济等数据。

## 积分说明

- **2000 积分**: 每日可调用 3000 次，并发限制 5
- **5000 积分**: 每日可调用 10000 次，并发限制 10
- **更高积分**: 更多调用次数和并发数

## 配置步骤

### 1. 注册账号

访问 https://tushare.pro 注册账号并登录

### 2. 获取 Token

1. 进入「用户中心」→「接口TOKEN」
2. 复制 Token

### 3. 配置环境变量

创建 `.env` 文件：

```env
TUSHARE_TOKEN=your_token_here
```

### 4. Python 代码示例

```python
import tushare as ts
import os
from dotenv import load_dotenv

load_dotenv()

# 初始化 API
ts.set_token(os.getenv('TUSHARE_TOKEN'))
pro = ts.pro_api()

# 获取股票列表
stock_list = pro.stock_basic(exchange='', list_status='L')
print(stock_list.head())
```

## 429 错误处理

### 问题
当请求频率超过限制时，会收到 429 错误。

### 解决方案：指数退避重试

```python
import asyncio
import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=60)
)
async def fetch_tushare_data(url, params):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 429:
                raise Exception("Rate limited")
            return await response.json()
```

### 并发控制

```python
import asyncio
from asyncio import Semaphore

# 限制并发数为 5
semaphore = Semaphore(5)

async def fetch_with_semaphore(url, params):
    async with semaphore:
        return await fetch_tushare_data(url, params)

# 批量获取数据
tasks = [fetch_with_semaphore(url, params) for _ in range(100)]
results = await asyncio.gather(*tasks)
```

## 常用 API

### 获取日线行情
```python
df = pro.daily(ts_code='000001.SZ', start_date='20240101', end_date='20240201')
```

### 获取财务指标
```python
df = pro.fina_indicator(ts_code='000001.SZ', start_date='20240101')
```

### 获取北向资金
```python
df = pro.moneyflow_hsgt(start_date='20240101', end_date='20240201')
```

## 总结

Tushare Pro 是量化交易的重要工具，合理配置并发控制和错误处理可以提高数据获取效率。

---

**祝你的量化交易之路顺利！** 📈
