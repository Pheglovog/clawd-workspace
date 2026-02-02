"""
天气查询 API 集成
支持多个天气数据源
"""

import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import httpx
from pydantic import BaseModel

# 基础配置
BASE_URL = "https://api.openweathermap.org/data/2.5"
API_KEY = os.getenv("WEATHER_API_KEY", "demo_key")


class WeatherData(BaseModel):
    """天气数据模型"""
    city: str
    condition: str
    temperature: float
    temp_high: float
    temp_low: float
    humidity: int
    wind_speed: float
    pressure: float
    description: str
    date: datetime
    source: str = "OpenWeatherMap"


class WeatherAPI:
    """天气查询 API"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or API_KEY
        self.client = httpx.AsyncClient(timeout=10.0)

    async def get_weather(self, city: str) -> WeatherData:
        """
        获取当前天气

        Args:
            city: 城市名称

        Returns:
            WeatherData 天气数据
        """
        try:
            # 调用 OpenWeatherMap API
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric",
                "lang": "zh_cn"
            }

            response = await self.client.get(f"{BASE_URL}/weather", params=params)
            response.raise_for_status()

            data = response.json()

            # 解析响应
            weather = WeatherData(
                city=data.get("name", city),
                condition=data.get("weather", [{}])[0].get("main", "未知"),
                temperature=data.get("main", {}).get("temp", 0),
                temp_high=data.get("main", {}).get("temp_max", 0),
                temp_low=data.get("main", {}).get("temp_min", 0),
                humidity=data.get("main", {}).get("humidity", 0),
                wind_speed=data.get("wind", {}).get("speed", 0),
                pressure=data.get("main", {}).get("pressure", 0),
                description=data.get("weather", [{}])[0].get("description", ""),
                date=datetime.now(),
                source="OpenWeatherMap"
            )

            return weather

        except httpx.HTTPError as e:
            # 如果 API 调用失败，返回模拟数据
            return self._get_mock_weather(city)
        except Exception as e:
            # 其他错误也返回模拟数据
            return self._get_mock_weather(city)

    async def get_forecast(self, city: str, days: int = 5) -> Dict[str, Any]:
        """
        获取天气预报

        Args:
            city: 城市名称
            days: 预报天数

        Returns:
            Dict[str, Any] 天气预报数据
        """
        try:
            # 调用 OpenWeatherMap Forecast API
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric",
                "cnt": days * 8,  # 每 3 小时一次，8 个数据点/天
                "lang": "zh_cn"
            }

            response = await self.client.get(f"{BASE_URL}/forecast", params=params)
            response.raise_for_status()

            data = response.json()

            # 解析响应
            forecast_list = []
            for item in data.get("list", []):
                forecast = {
                    "date": datetime.fromtimestamp(item["dt"]),
                    "temperature": item["main"]["temp"],
                    "temp_high": item["main"]["temp_max"],
                    "temp_low": item["main"]["temp_min"],
                    "humidity": item["main"]["humidity"],
                    "condition": item["weather"][0]["main"],
                    "description": item["weather"][0]["description"]
                }
                forecast_list.append(forecast)

            return {
                "city": data.get("city", {}).get("name", city),
                "forecast": forecast_list
            }

        except httpx.HTTPError as e:
            # 如果 API 调用失败，返回模拟数据
            return self._get_mock_forecast(city, days)
        except Exception as e:
            # 其他错误也返回模拟数据
            return self._get_mock_forecast(city, days)

    def _get_mock_weather(self, city: str) -> WeatherData:
        """获取模拟天气数据"""
        # 根据城市生成不同的模拟数据
        city_weather = {
            "东京": {"condition": "晴", "temp": 15, "high": 20, "low": 10},
            "京都": {"condition": "多云", "temp": 12, "high": 18, "low": 8},
            "大阪": {"condition": "阴", "temp": 18, "high": 22, "low": 14},
            "奈良": {"condition": "晴", "temp": 20, "high": 25, "low": 15},
            "上海": {"condition": "多云", "temp": 18, "high": 22, "low": 14},
            "北京": {"condition": "晴", "temp": 16, "high": 20, "low": 12}
        }

        # 默认天气
        default_weather = {
            "condition": "晴",
            "temp": 20,
            "high": 25,
            "low": 15
        }

        # 获取城市天气或默认天气
        weather = city_weather.get(city, default_weather)

        return WeatherData(
            city=city,
            condition=weather["condition"],
            temperature=weather["temp"],
            temp_high=weather["high"],
            temp_low=weather["low"],
            humidity=65,
            wind_speed=5.5,
            pressure=1013.25,
            description=self._get_weather_description(weather["condition"]),
            date=datetime.now(),
            source="Mock"
        )

    def _get_mock_forecast(self, city: str, days: int) -> Dict[str, Any]:
        """获取模拟天气预报"""
        base_weather = self._get_mock_weather(city)

        forecast_list = []
        for day in range(days):
            date = datetime.now() + timedelta(days=day)

            # 每天的天气略有不同
            temp_variation = (day - days // 2) * 2

            forecast = {
                "date": date,
                "temperature": base_weather.temperature + temp_variation,
                "temp_high": base_weather.temp_high + temp_variation,
                "temp_low": base_weather.temp_low + temp_variation,
                "humidity": base_weather.humidity + (day % 5) * 2,
                "condition": base_weather.condition,
                "description": base_weather.description
            }
            forecast_list.append(forecast)

        return {
            "city": city,
            "forecast": forecast_list
        }

    def _get_weather_description(self, condition: str) -> str:
        """获取天气描述"""
        descriptions = {
            "晴": "天气晴朗，适合户外活动",
            "多云": "天气多云，建议携带雨伞",
            "阴": "天气阴天，注意保暖",
            "雨": "下雨天气，建议携带雨具",
            "雪": "下雪天气，注意保暖和防滑"
        }
        return descriptions.get(condition, "天气晴朗，适合户外活动")

    async def get_travel_advice(self, city: str, days: int) -> Dict[str, Any]:
        """
        获取旅行建议

        Args:
            city: 目的地城市
            days: 旅行天数

        Returns:
            Dict[str, Any] 旅行建议
        """
        weather = await self.get_weather(city)
        forecast = await self.get_forecast(city, days)

        # 生成建议
        advice = {
            "weather": weather,
            "forecast": forecast,
            "tips": self._generate_tips(weather, forecast),
            "clothing": self._generate_clothing_advice(weather, forecast),
            "best_days": self._find_best_days(forecast)
        }

        return advice

    def _generate_tips(self, weather: WeatherData, forecast: Dict) -> List[str]:
        """生成旅行贴士"""
        tips = []

        # 根据天气条件生成建议
        if weather.temperature < 10:
            tips.append("建议：天气较冷，请携带保暖衣物")
        elif weather.temperature > 25:
            tips.append("建议：天气较热，请注意防暑和防晒")
        else:
            tips.append("建议：天气宜人，适合户外活动")

        # 根据湿度生成建议
        if weather.humidity > 80:
            tips.append("建议：湿度较高，请注意防潮")

        # 根据天气状况生成建议
        if "雨" in weather.condition.lower():
            tips.append("建议：下雨天气，请携带雨具并注意路面湿滑")
        elif "雪" in weather.condition.lower():
            tips.append("建议：下雪天气，请注意保暖和防滑")
        else:
            tips.append("建议：天气晴朗，适合拍照和户外活动")

        return tips

    def _generate_clothing_advice(self, weather: WeatherData, forecast: Dict) -> List[str]:
        """生成衣物建议"""
        clothing = []

        # 根据温度生成建议
        if weather.temperature < 5:
            clothing.append("建议穿着：厚外套 + 毛衣 + 保暖内衣")
        elif weather.temperature < 15:
            clothing.append("建议穿着：外套 + 薄毛衣 + 薄内衣")
        elif weather.temperature < 25:
            clothing.append("建议穿着：长袖衬衫 + 薄外套（可选）")
        else:
            clothing.append("建议穿着：短袖衬衫 + 薄外套（空调房间）")

        # 根据天气状况生成建议
        if "雨" in weather.condition.lower():
            clothing.append("携带物品：雨伞或雨衣 + 防水鞋")
        elif "雪" in weather.condition.lower():
            clothing.append("携带物品：防寒衣物 + 防滑鞋 + 防滑垫")

        return clothing

    def _find_best_days(self, forecast: Dict) -> List[Dict[str, Any]]:
        """找出最适合旅游的几天"""
        forecast_list = forecast.get("forecast", [])

        # 按照温度和天气条件评分
        scored_days = []
        for day_data in forecast_list:
            score = 0

            # 温度评分（15-25°C 最好）
            temp = day_data["temperature"]
            if 15 <= temp <= 25:
                score += 10
            elif 10 <= temp < 15 or 25 < temp <= 30:
                score += 5
            else:
                score += 0

            # 天气状况评分（晴 > 多云 > 阴 > 雨 > 雪）
            condition = day_data["condition"]
            if condition == "晴":
                score += 10
            elif condition == "多云":
                score += 7
            elif condition == "阴":
                score += 5
            elif condition == "雨":
                score += 2
            elif condition == "雪":
                score += 1

            # 湿度评分（40-70% 最好）
            humidity = day_data["humidity"]
            if 40 <= humidity <= 70:
                score += 5
            else:
                score += 2

            scored_days.append({
                "date": day_data["date"],
                "score": score,
                "weather": day_data
            })

        # 排序并返回前 3 天
        sorted_days = sorted(scored_days, key=lambda x: x["score"], reverse=True)
        return sorted_days[:3]

    async def close(self):
        """关闭 HTTP 客户端"""
        await self.client.aclose()


# 使用示例
async def example_usage():
    """使用示例"""
    api = WeatherAPI()

    # 获取当前天气
    weather = await api.get_weather("东京")
    print(f"当前天气：{weather.condition}, 温度：{weather.temperature}°C")

    # 获取天气预报
    forecast = await api.get_forecast("东京", days=5)
    print(f"天气预报：{len(forecast['forecast'])} 天")

    # 获取旅行建议
    advice = await api.get_travel_advice("东京", days=5)
    print(f"旅行建议：{advice}")

    # 关闭连接
    await api.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
