"""
真实 API 集成配置
包含天气、地图、货币等 API 的配置管理
"""

import os
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from pathlib import Path


class APIConfig(BaseModel):
    """API 配置基类"""

    api_key: str = Field(..., description="API 密钥")
    base_url: str = Field(..., description="API 基础 URL")
    timeout: int = Field(default=30, description="请求超时时间（秒）")
    rate_limit: int = Field(default=100, description="每分钟请求限制")
    enabled: bool = Field(default=True, description="是否启用")


class WeatherAPIConfig(APIConfig):
    """天气 API 配置"""

    base_url: str = "https://api.openweathermap.org/data/2.5"
    provider: str = Field(default="openweathermap", description="天气数据提供商")

    # 支持的提供商
    SUPPORTED_PROVIDERS = {
        "openweathermap": {
            "base_url": "https://api.openweathermap.org/data/2.5",
            "units": "metric",
            "lang": "zh_cn"
        },
        "weatherapi": {
            "base_url": "https://api.weatherapi.com/v1",
            "lang": "zh"
        }
    }


class CurrencyAPIConfig(APIConfig):
    """汇率 API 配置"""

    base_url: str = "https://api.exchangerate-api.com/v4"
    provider: str = Field(default="exchangerate", description="汇率数据提供商")
    base_currency: str = Field(default="CNY", description="基础货币")

    # 支持的提供商
    SUPPORTED_PROVIDERS = {
        "exchangerate": {
            "base_url": "https://api.exchangerate-api.com/v4",
            "free_tier": True
        },
        "fixer": {
            "base_url": "https://data.fixer.io/api",
            "free_tier": False
        },
        "currencyapi": {
            "base_url": "https://api.currencyapi.com/v3",
            "free_tier": True
        }
    }


class MapsAPIConfig(APIConfig):
    """地图 API 配置"""

    base_url: str = "https://maps.googleapis.com/maps/api"
    provider: str = Field(default="googlemaps", description="地图数据提供商")
    api_key_type: str = Field(default="browser", description="API 密钥类型（browser/server）")

    # 支持的提供商
    SUPPORTED_PROVIDERS = {
        "googlemaps": {
            "base_url": "https://maps.googleapis.com/maps/api",
            "features": ["directions", "geocoding", "places", "static_maps"]
        },
        "mapbox": {
            "base_url": "https://api.mapbox.com",
            "features": ["directions", "geocoding", "static_images"]
        },
        "openrouteservice": {
            "base_url": "https://api.openrouteservice.org",
            "features": ["directions", "geocoding"],
            "free_tier": True
        }
    }


class OpenAIConfig(APIConfig):
    """OpenAI API 配置"""

    base_url: str = "https://api.openai.com/v1"
    model: str = Field(default="gpt-4", description="模型名称")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="温度参数")
    max_tokens: int = Field(default=2000, ge=1, description="最大 token 数")


class FlightAPIConfig(APIConfig):
    """航班 API 配置"""

    base_url: str = "https://test.api.amadeus.com/v1"
    provider: str = Field(default="amadeus", description="航班数据提供商")

    # 支持的提供商
    SUPPORTED_PROVIDERS = {
        "amadeus": {
            "base_url": "https://test.api.amadeus.com/v1",
            "features": ["flights", "hotels", "activities"]
        },
        "skyscanner": {
            "base_url": "https://partners.api.skyscanner.net/apiservices",
            "features": ["flights"]
        }
    }


class HotelAPIConfig(APIConfig):
    """酒店 API 配置"""

    base_url: str = "https://test.api.amadeus.com/v1"
    provider: str = Field(default="amadeus", description="酒店数据提供商")


class TravelAPIManager:
    """旅行 API 管理器

    统一管理所有 API 的配置和状态
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化 API 管理器

        Args:
            config_path: 配置文件路径（可选）
        """
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__),
            "../../config/apis.json"
        )

        self.weather: Optional[WeatherAPIConfig] = None
        self.currency: Optional[CurrencyAPIConfig] = None
        self.maps: Optional[MapsAPIConfig] = None
        self.openai: Optional[OpenAIConfig] = None
        self.flight: Optional[FlightAPIConfig] = None
        self.hotel: Optional[HotelAPIConfig] = None

        self._load_config()

    def _load_config(self):
        """加载配置文件"""
        if Path(self.config_path).exists():
            with open(self.config_path, 'r') as f:
                import json
                config_data = json.load(f)

            # 加载各个 API 的配置
            if "weather" in config_data:
                self.weather = WeatherAPIConfig(**config_data["weather"])
            if "currency" in config_data:
                self.currency = CurrencyAPIConfig(**config_data["currency"])
            if "maps" in config_data:
                self.maps = MapsAPIConfig(**config_data["maps"])
            if "openai" in config_data:
                self.openai = OpenAIConfig(**config_data["openai"])
            if "flight" in config_data:
                self.flight = FlightAPIConfig(**config_data["flight"])
            if "hotel" in config_data:
                self.hotel = HotelAPIConfig(**config_data["hotel"])
        else:
            # 使用环境变量初始化
            self._init_from_env()

    def _init_from_env(self):
        """从环境变量初始化配置"""
        # 天气 API
        if os.getenv("WEATHER_API_KEY"):
            self.weather = WeatherAPIConfig(
                api_key=os.getenv("WEATHER_API_KEY"),
                enabled=True
            )

        # 汇率 API
        if os.getenv("CURRENCY_API_KEY"):
            self.currency = CurrencyAPIConfig(
                api_key=os.getenv("CURRENCY_API_KEY"),
                enabled=True
            )

        # 地图 API
        if os.getenv("MAPS_API_KEY"):
            self.maps = MapsAPIConfig(
                api_key=os.getenv("MAPS_API_KEY"),
                enabled=True
            )

        # OpenAI API
        if os.getenv("OPENAI_API_KEY"):
            self.openai = OpenAIConfig(
                api_key=os.getenv("OPENAI_API_KEY"),
                model=os.getenv("OPENAI_MODEL", "gpt-4"),
                temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
                enabled=True
            )

        # 航班 API
        if os.getenv("FLIGHT_API_KEY"):
            self.flight = FlightAPIConfig(
                api_key=os.getenv("FLIGHT_API_KEY"),
                enabled=True
            )

        # 酒店 API
        if os.getenv("HOTEL_API_KEY"):
            self.hotel = HotelAPIConfig(
                api_key=os.getenv("HOTEL_API_KEY"),
                enabled=True
            )

    def is_api_enabled(self, api_name: str) -> bool:
        """
        检查 API 是否启用

        Args:
            api_name: API 名称（weather, currency, maps, openai, flight, hotel）

        Returns:
            bool 是否启用
        """
        api_config = getattr(self, api_name, None)
        return api_config is not None and api_config.enabled

    def get_api_config(self, api_name: str) -> Optional[APIConfig]:
        """
        获取 API 配置

        Args:
            api_name: API 名称

        Returns:
            Optional[APIConfig] API 配置
        """
        return getattr(self, api_name, None)

    def save_config(self, path: Optional[str] = None):
        """
        保存配置到文件

        Args:
            path: 配置文件路径（可选）
        """
        config_path = path or self.config_path

        config_data = {}

        if self.weather:
            config_data["weather"] = self.weather.model_dump()
        if self.currency:
            config_data["currency"] = self.currency.model_dump()
        if self.maps:
            config_data["maps"] = self.maps.model_dump()
        if self.openai:
            config_data["openai"] = self.openai.model_dump()
        if self.flight:
            config_data["flight"] = self.flight.model_dump()
        if self.hotel:
            config_data["hotel"] = self.hotel.model_dump()

        # 确保目录存在
        Path(config_path).parent.mkdir(parents=True, exist_ok=True)

        # 保存配置
        with open(config_path, 'w') as f:
            import json
            json.dump(config_data, f, indent=2)

        print(f"✅ 配置已保存到: {config_path}")

    def get_status(self) -> Dict[str, Any]:
        """
        获取所有 API 的状态

        Returns:
            Dict[str, Any] API 状态
        """
        status = {
            "weather": {
                "enabled": self.is_api_enabled("weather"),
                "provider": self.weather.provider if self.weather else None
            },
            "currency": {
                "enabled": self.is_api_enabled("currency"),
                "provider": self.currency.provider if self.currency else None
            },
            "maps": {
                "enabled": self.is_api_enabled("maps"),
                "provider": self.maps.provider if self.maps else None
            },
            "openai": {
                "enabled": self.is_api_enabled("openai"),
                "model": self.openai.model if self.openai else None
            },
            "flight": {
                "enabled": self.is_api_enabled("flight"),
                "provider": self.flight.provider if self.flight else None
            },
            "hotel": {
                "enabled": self.is_api_enabled("hotel"),
                "provider": self.hotel.provider if self.hotel else None
            }
        }

        return status


# 使用示例
if __name__ == "__main__":
    # 创建 API 管理器
    manager = TravelAPIManager()

    # 获取状态
    status = manager.get_status()
    print("📊 API 状态:")
    print(f"  天气 API: {'✅' if status['weather']['enabled'] else '❌'} ({status['weather']['provider']})")
    print(f"  汇率 API: {'✅' if status['currency']['enabled'] else '❌'} ({status['currency']['provider']})")
    print(f"  地图 API: {'✅' if status['maps']['enabled'] else '❌'} ({status['maps']['provider']})")
    print(f"  OpenAI API: {'✅' if status['openai']['enabled'] else '❌'} ({status['openai']['model']})")
    print(f"  航班 API: {'✅' if status['flight']['enabled'] else '❌'} ({status['flight']['provider']})")
    print(f"  酒店 API: {'✅' if status['hotel']['enabled'] else '❌'} ({status['hotel']['provider']})")
