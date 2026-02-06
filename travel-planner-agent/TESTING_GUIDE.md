# Travel Planner Agent - 配置和测试文档

## 📋 概述

Travel Planner Agent 是一个基于 LangChain 的智能旅游规划助手，支持多 Agent 协作和多种 API 集成。

## 🔧 配置步骤

### 1. 创建环境变量文件

```bash
cd /root/clawd/travel-planner-agent
cp .env.example .env
```

### 2. 编辑 .env 文件

填入你的 API 密钥：

```bash
# OpenAI API (必需)
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7

# 天气 API (可选)
WEATHER_API_KEY=your-openweathermap-api-key-here

# 汇率 API (可选)
CURRENCY_API_KEY=your-exchangerate-api-key-here

# 地图 API (可选)
MAPS_API_KEY=your-google-maps-api-key-here
```

### 3. 安装依赖

```bash
cd /root/clawd/travel-planner-agent
pip install -r requirements.txt
```

### 4. 运行测试

```bash
cd /root/clawd/travel-planner-agent
python src/main.py
```

## 🧪 测试功能

### 测试 1: 天气查询

```python
from src.tools.weather_api import WeatherAPI
import asyncio

async def test_weather():
    api = WeatherAPI(api_key="your-api-key")
    weather = await api.get_weather("Tokyo")
    print(f"东京天气: {weather.condition}, {weather.temperature}°C")

asyncio.run(test_weather())
```

### 测试 2: 汇率转换

```python
from src.tools.currency_api import CurrencyAPI
import asyncio

async def test_currency():
    api = CurrencyAPI(api_key="your-api-key")
    rate = await api.get_exchange_rate("USD", "CNY")
    print(f"USD -> CNY: {rate}")

asyncio.run(test_currency())
```

### 测试 3: Agent 协作

```python
from src.agents.agent_executor import AgentExecutor
from langchain_openai import ChatOpenAI

# 创建 LLM
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.7,
    api_key="your-openai-api-key"
)

# 创建执行器
executor = AgentExecutor(llm=llm)

# 运行任务
result = executor.run(
    task="规划一个5天的日本旅行",
    destination="日本",
    days=5,
    budget=20000
)

print(result)
```

## 📊 API 状态检查

运行配置检查：

```bash
cd /root/clawd/travel-planner-agent
python -c "
from src.utils.api_config import TravelAPIManager

manager = TravelAPIManager()
status = manager.get_status()

print('📊 API 状态:')
for api, info in status.items():
    enabled = '✅' if info['enabled'] else '❌'
    print(f'  {api}: {enabled} ({info.get(\"provider\", \"N/A\")})')
"
```

## 🔑 获取 API 密钥

### OpenAI API
- 地址: https://platform.openai.com/api-keys
- 费用: 按使用量计费
- 免费额度: 新用户有 $5 免费额度

### OpenWeatherMap API
- 地址: https://openweathermap.org/api
- 费用: 免费版限制为 1000 次/天
- 推荐: 免费版足够测试使用

### ExchangeRate-API
- 地址: https://www.exchangerate-api.com
- 费用: 免费版 1500 次/月
- 推荐: 免费版足够测试使用

### Google Maps API
- 地址: https://console.cloud.google.com/apis/credentials
- 费用: $200 免费额度/月
- 推荐: 测试时可以使用免费额度

## ⚠️ 常见问题

### 问题 1: API 密钥无效
**错误**: `401 Unauthorized`

**解决**: 检查 API 密钥是否正确，是否过期

### 问题 2: OpenAI API 超限
**错误**: `Rate limit exceeded`

**解决**: 检查账户余额，或使用更便宜的模型

### 问题 3: 模块导入失败
**错误**: `ModuleNotFoundError`

**解决**: 运行 `pip install -r requirements.txt`

### 问题 4: 异步执行错误
**错误**: `RuntimeError: This event loop is already running`

**解决**: 使用 `asyncio.run()` 或创建新的事件循环

## 📝 使用示例

### 示例 1: 简单的旅行规划

```
输入: 请帮我规划一个 3 天的京都旅行，预算 5000 元

输出:
{
  "itinerary": [
    {"day": 1, "activities": ["清水寺", "祇园", "伏见稻荷"]},
    {"day": 2, "activities": ["金阁寺", "岚山", "渡月桥"]},
    {"day": 3, "activities": ["二条城", "锦市场", "鸭川"]}
  ],
  "budget": {
    "total": 5000,
    "breakdown": {
      "accommodation": 2000,
      "food": 1500,
      "transport": 800,
      "tickets": 700
    }
  },
  "checklist": [
    "护照", "日元", "充电器", "相机", "药品"
  ]
}
```

### 示例 2: 多 Agent 协作

```
输入: 规划一个7天的泰国旅行，预算 15000 元

输出:
- Planner Agent: 生成详细行程
- Checklist Agent: 生成打包清单
- Budget Agent: 计算费用预算
- Weather Tool: 查询天气
- Currency Tool: 转换汇率 (THB)
- Maps Tool: 推荐路线
```

## 🚀 下一步

1. ✅ 配置 API 密钥
2. ✅ 安装依赖
3. ⏳ 运行测试
4. ⏳ 评估功能
5. ⏳ 优化提示词
6. ⏳ 添加更多工具

---

**更新时间**: 2026-02-04
**作者**: 上等兵•甘
**状态**: ✅ 配置文档已完成
