"""
地图路线规划工具
提供主要城市间的交通路线和交通方式推荐
"""

import os
from typing import Dict, List, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def get_route_recommendation(origin: str, destination: str) -> Dict[str, Any]:
    """获取交通路线推荐"""
    
    routes = {
        ("东京", "京都"): {
            "type": "新干线",
            "description": "最快最便利的选择",
            "duration": "约2.5 小时",
            "cost": "约 13,000 日元",
            "tips": ["可以在东京站购买西瓜卡", "推荐使用 Nozomi 指定席", "下车后步行即可"]
        },
        ("东京", "大阪"): {
            "type": "新干线 + 地铁",
            "description": "灵活选择，经济实惠",
            "duration": "约2 小时",
            "cost": "约 14,500 日元",
            "tips": ["推荐使用大阪周游卡", "可以在新大阪站购买 JR Pass", "性价比高"]
        },
        ("东京", "奈良"): {
            "type": "JR 特急列车",
            "description": "快速直达，适合一日游",
            "duration": "约1 小时",
            "cost": "约 6,000 日元",
            "tips": ["需要额外支付特急券费用", "到站后可以乘坐公交或打车"]
        },
        ("京都", "大阪"): {
            "type": "JR + 地铁",
            "description": "经典路线，兼顾效率和经济",
            "duration": "约1.5 小时",
            "cost": "约 12,000 日元",
            "tips": ["推荐购买京阪电车往返票", "可以在京都站乘坐 Haruka 到大阪"]
        },
        ("大阪", "奈良"): {
            "type": "JR + 电铁",
            "description": "便捷的选择，适合自由行",
            "duration": "约1 小时",
            "cost": "约 10,000 日元",
            "tips": ["推荐购买近铁电车票", "道顿堀到奈良可以乘坐近铁电车"]
        }
    }
    
    if (origin, destination) in routes:
        return {
            "origin": origin,
            "destination": destination,
            "route": routes[(origin, destination)],
            "total_routes": len(routes)
        }
    else:
        return {
            "origin": origin,
            "destination": destination,
            "route": [],
            "total_routes": 0
        }


def calculate_route_cost(origin: str, destination: str, days: int, daily_cost: float = 5000.0) -> Dict[str, Any]:
    """计算交通费用"""
    
    if (origin, destination) in get_route_recommendation(origin, destination)["route"]:
        route_info = get_route_recommendation(origin, destination)["route"][0]
        return {
            "origin": origin,
            "destination": destination,
            "type": route_info["type"],
            "daily_cost": route_info["cost"],
            "total_cost": route_info["cost"] * days,
            "tips": route_info["tips"]
        }
    else:
        return {
            "origin": origin,
            "destination": destination,
            "type": "unknown",
            "daily_cost": daily_cost,
            "total_cost": daily_cost * days,
            "tips": ["建议购买 JR Pass 周游券"]
        }


def print_route_recommendation(origin: str, destination: str):
    """打印路线推荐"""
    result = get_route_recommendation(origin, destination)
    
    print("\n" + "="*50)
    print(f"🚉 路线推荐：{result['origin']} → {result['destination']}")
    print("="*50)
    print()
    
    if result["total_routes"] > 0:
        print(f"推荐方式：{result['route'][0]['type']}")
        print(f"⏱️ 时间：约 {result['route'][0]['duration']}")
        print(f"💰 费用：约 {result['route'][0]['cost']:,} 日元/次")
        print(f"📝 总费用：{result['total_cost']:,} 日元")
        
        for i, tip in enumerate(result["route"][0]["tips"], 1):
            print(f"  {i}. {tip}")
    else:
        print("❌ 无可用路线")
        print("="*50)
        print()


def create_route_map(destination: str, routes: List[str]) -> Dict[str, Any]:
    """创建路线图"""
    route_map = {}
    
    if "东京" in routes:
        route_map["东京"] = ["京都", "大阪", "奈良"]
    elif "京都" in routes:
        route_map["京都"] = ["东京", "大阪", "奈良"]
    elif "大阪" in routes:
        route_map["大阪"] = ["东京", "京都", "奈良"]
    elif "奈良" in routes:
        route_map["奈良"] = ["京都", "大阪"]
    
    return route_map.get(destination, [])
