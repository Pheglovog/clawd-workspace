"""
配置管理模块
管理 API 密钥、LLM 模型选择等配置
"""

import os
from dotenv import load_dotenv
from typing import Optional

# 加载环境变量
load_dotenv()

# API 配置
OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
DEFAULT_LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")

# 模型选择映射
MODEL_MAPPING = {
    "gpt-4o-mini": {"name": "GPT-4o-Mini", "cost": "low"},
    "gpt-4o": {"name": "GPT-4o", "cost": "medium"},
    "gpt-4-turbo": {"name": "GPT-4-Turbo", "cost": "medium"},
    "claude-opus-4": {"name": "Claude Opus 4", "cost": "high"},
    "claude-sonnet-4": {"name": "Claude Sonnet 4", "cost": "medium"},
    "gpt-4o-mini": {"name": "GPT-4o-Mini", "cost": "low"}  # 备用
}

# 旅游特定配置
DEFAULT_DAYS: int = 7  # 默认旅行天数
DEFAULT_BUDGET: int = 200000  # 默认预算（人民币）
DEFAULT_PREFERENCE: str = "3"  # 默认偏好（综合体验）


def get_api_key() -> str:
    """获取 OpenAI API 密钥"""
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY 未配置！请在 config/api_keys.json 中设置或使用环境变量。")
    return OPENAI_API_KEY


def get_llm_model(model_name: Optional[str] = None) -> str:
    """获取 LLM 模型配置"""
    if model_name:
        return model_name
    return DEFAULT_LLM_MODEL


def get_llm_cost(model_name: str) -> dict:
    """获取模型成本信息"""
    return MODEL_MAPPING.get(model_name, {"name": "Unknown", "cost": "medium"})


def get_default_destination() -> str:
    """获取默认目的地"""
    return "东京"


def get_default_days() -> int:
    """获取默认天数"""
    return DEFAULT_DAYS


def get_default_budget() -> int:
    """获取默认预算"""
    return DEFAULT_BUDGET


def get_default_preference() -> str:
    """获取默认偏好"""
    return DEFAULT_PREFERENCE


def validate_budget(budget: int, days: int) -> bool:
    """验证预算是否合理"""
    minimum_daily = 10000  # 每天 1 万人民币
    if budget < minimum_daily * days:
        print(f"⚠️ 预算过低！{days} 天最少需要 {minimum_daily * days:,} 元")
        return False
    return True


def calculate_total_budget(budget: int, days: int) -> dict:
    """计算总预算分配"""
    # 简单分配（实际应该根据汇率和物价动态调整）
    breakdown = {
        "total": budget,
        "transportation": int(budget * 0.3),  # 30%
        "accommodation": int(budget * 0.25),  # 25%
        "food": int(budget * 0.20),  # 20%
        "tickets_entertainment": int(budget * 0.10),  # 10%
        "shopping": int(budget * 0.10),  # 5%
        "others": int(budget * 0.05)  # 10%
    }
    
    return breakdown


def print_config():
    """打印当前配置"""
    print("\n" + "="*60)
    print("📋 当前配置")
    print("="*60)
    print()
    
    print(f"LLM 模型: {get_llm_model()}")
    print(f"API 密钥: {'已配置' if get_api_key() else '未配置'}")
    print(f"默认天数: {DEFAULT_DAYS} 天")
    print(f"默认预算: {DEFAULT_BUDGET:,} 元")
    print(f"默认偏好: {get_default_preference()}")
    print()
    print("="*60)
