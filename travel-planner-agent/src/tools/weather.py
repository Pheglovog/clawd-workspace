"""
天气查询工具
获取目的地的天气预报信息
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# API 配置
WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")


def get_weather(destination: str) -> Dict[str, Any]:
    """获取天气信息"""
    
    # 模拟数据（实际应该从天气 API 获取）
    weather_data = {
        "东京": {"condition": "晴", "temp": "15°C", "temp_high": "20°C", "temp_low": "10°C", "humidity": "60%"},
        "京都": {"condition": "多云", "temp": "12°C", "temp_high": "18°C", "temp_low": "8°C", "humidity": "70%"},
        "大阪": {"condition": "阴", "temp": "18°C", "temp_high": "22°C", "temp_low": "14°C", "humidity": "75%"},
        "奈良": {"condition": "晴", "temp": "20°C", "temp_high": "25°C", "temp_low": "15°C", "humidity": "55%"},
        "奈良": {"condition": "多云", "temp": "19°C", "temp_high": "23°C", "temp_low": "15°C", "humidity": "60%"},
    }
    
    if destination in weather_data:
        return {
            "destination": destination,
            "weather": weather_data[destination],
            "condition": weather_data[destination]["condition"],
            "temperature": weather_data[destination]["temp"],
            "tips": [
                f"建议：天气{weather_data[destination]['condition']}，适合户外活动",
                f"温差较大（{weather_data[destination]['temp_high'] - weather_data[destination]['temp_low']}°C）"
            ]
        }
    else:
        return {
            "destination": destination,
            "weather": {"condition": "未知", "temp": "--", "humidity": "--"},
            "tips": ["暂无天气数据"]
        }


def get_travel_advice(destination: str, days: int) -> Dict[str, Any]:
    """获取旅行建议"""
    advice = {
        "东京": [
            "建议购买地铁一日券（Tokyo Metro 24h券）",
            "浅草寺门票可以提前购买",
            "银座、新宿等繁华区步行即可",
            "便利店早餐（7-11）很方便且经济",
            "推荐使用 JR Pass 连接箱根-京都-大阪-奈良"
        ],
        "京都": [
            "建议使用巴士或出租车",
            "很多寺庙需要脱鞋",
            "推荐购买京都市巴士通票",
            "岚山景区建议一日游"
        ],
        "大阪": [
            "建议购买大阪周游卡（Osaka Metro Pass）",
            "道顿掘、大阪城可以乘坐出租车",
            "环球影城需要全天游览",
            "梅田寺、住吉大社在一条线上",
            "推荐使用一日券"
        ],
        "奈良": [
            "建议租借自行车或徒步",
            "主要景点可以步行到达",
            "住宿建议住奈良町，交通便利"
        ],
        "通用": [
            "提前预订热门景点门票",
            "购买旅游保险",
            "准备移动电源和充电宝",
            "学习几句日语问候语",
            "准备零钱现金"
        ]
    }
    
    if destination in advice:
        return {
            "destination": destination,
            "advice": advice[destination] + advice.get("通用", []),
            "total_days": len(advice[destination]) + len(advice["通用"])
        }
    else:
        return {
            "destination": destination,
            "advice": advice["通用"],
            "total_days": len(advice["通用"])
        }
