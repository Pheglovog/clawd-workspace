"""
汇率查询工具
支持多货币汇率转换，帮助用户估算旅行预算
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# API 配置
EXCHANGE_API_KEY: str = os.getenv("EXCHANGE_API_KEY", "")
DEFAULT_EXCHANGE_RATE: float = 0.21  # 1 人民币 = 0.21 日元（参考）


def get_exchange_rate() -> float:
    """获取汇率"""
    return DEFAULT_EXCHANGE_RATE


def calculate_exchange(amount_cny: float, target_currency: str = "JPY") -> Dict[str, Any]:
    """计算汇率转换"""
    
    rates = {
        "CNY": 1.0,
        "JPY": DEFAULT_EXCHANGE_RATE,  # 人民币换日元
        "USD": 0.14,  # 人民币换美元（参考）
        "EUR": 0.11
        "KRW": 0.0007  # 人民币换韩元
    }
    
    if target_currency not in rates:
        return {
            "amount": amount_cny,
            "from_currency": "CNY",
            "to_currency": target_currency,
            "converted_amount": amount_cny * rates["CNY"],  # 默认转成 CNY
            "rate": 1.0,
            "note": f"不支持的货币：{target_currency}"
        }
    
    converted_amount = amount_cny * rates[target_currency]
    
    return {
        "amount": amount_cny,
        "from_currency": "CNY",
        "to_currency": target_currency,
        "converted_amount": round(converted_amount, 2),
        "rate": rates[target_currency],
        "note": f"汇率仅供参考，实际以银行兑换汇率为准"
    }


def create_currency_suggestion(destination: str, days: int, budget: int) -> Dict[str, Any]:
    """根据目的地提供货币建议"""
    
    suggestions = []
    
    if destination in ["东京", "京都", "大阪"]:
        suggestions = [
            "✅ 日本使用日元（JPY），建议在中国银行兑换部分现金",
            "✅ 日本信用卡支持银联和 JCB",
            "✅ 7-11 有大量支持银联的 ATM",
            "✅ 便利店和大部分商店都支持现金",
            "⚠️ 需要准备一些 1000 日元零钱（硬币和纸币）"
        ]
    else:
        suggestions = [
            "✅ 建议提前兑换当地货币",
            "✅ 告知当地信用卡和现金使用情况",
            "⚠️ 准备国际信用卡和美元现金"
        ]
    
    return {
        "destination": destination,
        "days": days,
        "budget": budget,
        "budget_jpy": round(budget * DEFAULT_EXCHANGE_RATE, 2),  # 人民币转日元
        "budget_jpy_per_day": round(budget * DEFAULT_EXCHANGE_RATE / days, 2),
        "suggestions": suggestions
    }


def format_currency(amount: float, currency: str) -> str:
    """格式化货币显示"""
    return f"{amount:,.0f} {currency}"


def print_exchange_result(result: Dict[str, Any]):
    """打印汇率转换结果"""
    print("\n" + "="*50)
    print(f"💱 汇率转换")
    print("="*50)
    print()
    
    print(f"原金额：{format_currency(result['amount'], 'CNY')}")
    print(f"转换金额：{format_currency(result['converted_amount'], result['to_currency'])}")
    print(f"汇率：{result['rate']}")
    
    if "note" in result:
        print(f"📌 注意：{result['note']}")
    
    print()
    print("="*50)
