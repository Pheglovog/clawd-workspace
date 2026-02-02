"""
Travel Planner Agent - 命令行工具
快速测试和体验核心功能
"""

import asyncio
import sys
from typing import Optional
from datetime import datetime

# 添加项目路径
sys.path.insert(0, "/root/clawd/travel-planner-agent/src")

from tools.weather_api import WeatherAPI
from tools.currency_api import CurrencyAPI


class TravelPlannerCLI:
    """旅行规划助手命令行工具"""

    def __init__(self):
        self.weather_api = WeatherAPI()
        self.currency_api = CurrencyAPI()

    def print_banner(self):
        """打印横幅"""
        banner = r"""
    ╔═══════════════════════════════════════════════╗
    ║                                                      ║
    ║     🌸  Travel Planner Agent 🌸                 ║
    ║                                                      ║
    ║     智能旅行规划助手（CLI 版本）           ║
    ║                                                      ║
    ║     功能：天气查询 · 汇率转换 · 旅行建议       ║
    ║                                                      ║
    ╚═══════════════════════════════════════════════╝
    """
        print(banner)

    def print_menu(self):
        """打印菜单"""
        print("\n" + "="*50)
        print("🌸 Travel Planner Agent 命令行工具")
        print("="*50)
        print()
        print("请选择功能：\n")
        print("  1. 🌤️  查询天气")
        print("  2. 💱 汇率转换")
        print("  3. 🌸  获取旅行建议")
        print("  4. 📊  批量查询（多个城市）")
        print("  5. ❌  退出")
        print()

    async def query_weather(self):
        """查询天气"""
        print("\n" + "-"*50)
        print("🌤️ 查询天气")
        print("-"*50)
        print()

        city = input("请输入城市名称（默认：东京）：").strip() or "东京"

        try:
            weather = await self.weather_api.get_weather(city)

            print(f"\n📍 {weather.city} 天气信息")
            print(f"   天气：{weather.condition}")
            print(f"   温度：{weather.temperature}°C (最高 {weather.temp_high}°C, 最低 {weather.temp_low}°C)")
            print(f"   湿度：{weather.humidity}%")
            print(f"   风速：{weather.wind_speed} m/s")
            print(f"   气压：{weather.pressure} hPa")
            print(f"   描述：{weather.description}")
            print(f"   更新时间：{weather.date.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   数据来源：{weather.source}")

        except Exception as e:
            print(f"\n❌ 查询失败: {e}")

        print()

    async def convert_currency(self):
        """汇率转换"""
        print("\n" + "-"*50)
        print("💱 汇率转换")
        print("-"*50)
        print()

        amount = input("请输入金额（默认：10000）：").strip() or "10000"
        from_currency = input("请输入基础货币（默认：CNY）：").strip() or "CNY"
        to_currency = input("请输入目标货币（默认：JPY）：").strip() or "JPY"

        try:
            conversion = await self.currency_api.convert_currency(
                float(amount),
                from_currency,
                to_currency
            )

            print(f"\n💱 货币转换结果")
            print(f"   {conversion.amount} {conversion.from_currency} =")
            print(f"   {conversion.converted_amount:.2f} {conversion.to_currency}")
            print(f"   汇率：1 {conversion.from_currency} = {conversion.rate:.4f} {conversion.to_currency}")
            print(f"   更新时间：{conversion.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   数据来源：{conversion.source}")

        except Exception as e:
            print(f"\n❌ 转换失败: {e}")

        print()

    async def get_travel_advice(self):
        """获取旅行建议"""
        print("\n" + "-"*50)
        print("🌸 获取旅行建议")
        print("-"*50)
        print()

        city = input("请输入目的地城市（默认：东京）：").strip() or "东京"
        days = input("请输入旅行天数（默认：7）：").strip() or "7"

        try:
            advice = await self.weather_api.get_travel_advice(city, int(days))

            print(f"\n🌸 {city} {days} 天旅行建议")
            print("="*50)
            print()

            # 天气信息
            weather = advice["weather"]
            print(f"🌤️ 当前天气")
            print(f"   天气：{weather.condition}，温度：{weather.temperature}°C")
            print(f"   最高：{weather.temp_high}°C，最低：{weather.temp_low}°C")
            print(f"   描述：{weather.description}")
            print()

            # 旅行贴士
            print(f"💡 旅行贴士")
            for i, tip in enumerate(advice["tips"], 1):
                print(f"   {i}. {tip}")
            print()

            # 衣物建议
            print(f"👕 建议穿着")
            for i, clothing in enumerate(advice["clothing"], 1):
                print(f"   {i}. {clothing}")
            print()

            # 最适合的几天
            print(f"📅 最适合旅游的几天")
            for i, day in enumerate(advice["best_days"], 1):
                date = day["date"].strftime("%m-%d")
                weather = day["weather"]
                print(f"   {i}. {date} - {weather['condition']} {weather['temperature']}°C (评分：{day['score']})")
            print()

        except Exception as e:
            print(f"\n❌ 获取建议失败: {e}")

        print()

    async def batch_query(self):
        """批量查询"""
        print("\n" + "-"*50)
        print("📊 批量查询（多个城市）")
        print("-"*50)
        print()

        cities_str = input("请输入城市列表，用逗号分隔（默认：东京,京都,大阪）：").strip()
        cities_str = cities_str or "东京,京都,大阪"
        cities = [city.strip() for city in cities_str.split(",") if city.strip()]

        if not cities:
            print("\n❌ 请输入至少一个城市")
            return

        print(f"\n📊 批量查询 {len(cities)} 个城市")
        print("="*50)
        print()

        try:
            # 并发查询所有城市的天气
            weather_tasks = [self.weather_api.get_weather(city) for city in cities]
            weather_results = await asyncio.gather(*weather_tasks)

            for weather in weather_results:
                print(f"📍 {weather.city}")
                print(f"   天气：{weather.condition}，温度：{weather.temperature}°C")
                print()

            # 汇率转换
            from_currency = input("请输入基础货币（默认：CNY）：").strip() or "CNY"
            amount = input("请输入金额（默认：10000）：").strip() or "10000"

            currency_tasks = [
                self.currency_api.convert_currency(float(amount), from_currency, city)
                for city in cities
            ]
            currency_results = await asyncio.gather(*currency_tasks)

            print("💱 批量汇率转换")
            print("="*50)
            print()

            for conversion in currency_results:
                print(f"   {conversion.amount} {conversion.from_currency} =")
                print(f"   {conversion.converted_amount:.2f} {conversion.to_currency} (汇率：{conversion.rate:.4f})")
                print()

        except Exception as e:
            print(f"\n❌ 批量查询失败: {e}")

        print()

    async def run(self):
        """运行主循环"""
        self.print_banner()

        while True:
            self.print_menu()

            choice = input("请输入选项（1-5）：").strip()

            if choice == "1":
                await self.query_weather()

            elif choice == "2":
                await self.convert_currency()

            elif choice == "3":
                await self.get_travel_advice()

            elif choice == "4":
                await self.batch_query()

            elif choice == "5":
                print("\n👋 感谢使用 Travel Planner Agent CLI！")
                print("祝您旅途愉快！✈️")
                print()

                # 关闭 API 连接
                await self.weather_api.close()
                await self.currency_api.close()

                break

            else:
                print("\n❌ 无效选项，请重新选择")
                print()


async def main():
    """主函数"""
    cli = TravelPlannerCLI()
    await cli.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 感谢使用 Travel Planner Agent CLI！")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        sys.exit(1)
