"""
用户偏好管理器
持久化用户偏好（目的地、预算、日期等）
"""

import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, validator
from loguru import logger
from pathlib import Path


class TravelPreferences(BaseModel):
    """旅行偏好模型"""
    
    # 基本信息
    user_name: str = Field(default="Traveler", description="用户名称")
    user_email: str = Field(default="", description="用户邮箱")
    
    # 目的地信息
    preferred_destinations: List[str] = Field(default_factory=list, description="偏好的目的地")
    primary_destination: Optional[str] = Field(default=None, description="主要目的地")
    
    # 旅行日期
    travel_date_start: Optional[datetime] = Field(default=None, description="旅行开始日期")
    travel_date_end: Optional[datetime] = Field(default=None, description="旅行结束日期")
    travel_days: int = Field(default=7, description="旅行天数", ge=1, le=30)
    
    # 预算
    budget: float = Field(default=100000.0, description="总预算（人民币）", ge=0)
    currency: str = Field(default="CNY", description="货币类型")
    
    # 人员信息
    num_travelers: int = Field(default=1, description="旅行人数", ge=1, le=10)
    travelers_info: List[Dict[str, str]] = Field(default_factory=list, description="旅行者信息")
    
    # 交通偏好
    transportation: str = Field(default="economy", description="交通等级（economy/business/first）")
    transportation_mode: str = Field(default="flight", description="交通方式（flight/train/bus/car）")
    
    # 住宿偏好
    accommodation_type: str = Field(default="hotel", description="住宿类型（hotel/hostel/apartment）")
    accommodation_rating: str = Field(default="4", description="住宿星级（3/4/5）")
    
    # 活动偏好
    activities: List[str] = Field(default_factory=list, description="偏好的活动")
    interests: List[str] = Field(default_factory=list, description="兴趣标签")
    
    # 饮食偏好
    dietary_restrictions: List[str] = Field(default_factory=list, description="饮食限制")
    preferred_cuisine: List[str] = Field(default_factory=list, description="偏好的菜系")
    
    # 其他偏好
    special_requests: str = Field(default="", description="特殊要求")
    is_business_trip: bool = Field(default=False, description="是否商务旅行")
    
    # 创建时间
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserPreferenceManager:
    """用户偏好管理器"""

    def __init__(self, storage_dir: str = "./preferences"):
        """
        初始化用户偏好管理器

        Args:
            storage_dir: 存储目录
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # 偏好文件
        self.preferences_file = self.storage_dir / "preferences.json"
        self.preferences_history_file = self.storage_dir / "preferences_history.json"

        # 加载偏好
        self.preferences: Dict[str, TravelPreferences] = {}
        self.preferences_history: List[Dict[str, Any]] = []

        self._load_preferences()
        self._load_preferences_history()

    def _load_preferences(self):
        """加载用户偏好"""
        if self.preferences_file.exists():
            try:
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 转换 datetime 字符串为 datetime 对象
                    for key, pref_data in data.items():
                        pref_data['travel_date_start'] = datetime.fromisoformat(pref_data['travel_date_start']) if pref_data['travel_date_start'] else None
                        pref_data['travel_date_end'] = datetime.fromisoformat(pref_data['travel_date_end']) if pref_data['travel_date_end'] else None
                        pref_data['created_at'] = datetime.fromisoformat(pref_data['created_at'])
                        pref_data['updated_at'] = datetime.fromisoformat(pref_data['updated_at'])
                        
                        self.preferences[key] = TravelPreferences(**pref_data)

                    logger.info(f"已加载 {len(self.preferences)} 个用户偏好")
            except Exception as e:
                logger.warning(f"加载偏好失败: {e}")
                self.preferences = {}

    def _load_preferences_history(self):
        """加载偏好历史"""
        if self.preferences_history_file.exists():
            try:
                with open(self.preferences_history_file, 'r', encoding='utf-8') as f:
                    self.preferences_history = json.load(f)
                    
                # 转换 datetime 字符串为 datetime 对象
                    for hist in self.preferences_history:
                        if 'created_at' in hist:
                            hist['created_at'] = datetime.fromisoformat(hist['created_at'])
                        if 'updated_at' in hist:
                            hist['updated_at'] = datetime.fromisoformat(hist['updated_at'])

                    logger.info(f"已加载 {len(self.preferences_history)} 条偏好历史记录")
            except Exception as e:
                logger.warning(f"加载偏好历史失败: {e}")
                self.preferences_history = []

    def _save_preferences(self):
        """保存用户偏好"""
        try:
            # 转换为 JSON 可序列化的格式
            data = {}
            for key, pref in self.preferences.items():
                pref_dict = pref.dict()
                
                # 转换 datetime 为字符串
                pref_dict['travel_date_start'] = pref_dict['travel_date_start'].isoformat() if pref_dict['travel_date_start'] else None
                pref_dict['travel_date_end'] = pref_dict['travel_date_end'].isoformat() if pref_dict['travel_date_end'] else None
                pref_dict['created_at'] = pref_dict['created_at'].isoformat()
                pref_dict['updated_at'] = pref_dict['updated_at'].isoformat()
                
                data[key] = pref_dict

            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)

            logger.debug(f"偏好已保存到 {self.preferences_file}")
            return True

        except Exception as e:
            logger.error(f"保存偏好失败: {e}")
            return False

    def _save_preferences_history(self):
        """保存偏好历史"""
        try:
            # 转换为 JSON 可序列化的格式
            history_data = []
            for hist in self.preferences_history:
                hist_copy = hist.copy()
                
                # 转换 datetime 为字符串
                if 'created_at' in hist_copy:
                    hist_copy['created_at'] = hist_copy['created_at'].isoformat()
                if 'updated_at' in hist_copy:
                    hist_copy['updated_at'] = hist_copy['updated_at'].isoformat()
                
                history_data.append(hist_copy)

            with open(self.preferences_history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2, ensure_ascii=False, default=str)

            logger.debug(f"偏好历史已保存到 {self.preferences_history_file}")
            return True

        except Exception as e:
            logger.error(f"保存偏好历史失败: {e}")
            return False

    def save_preference(
        self,
        key: str,
        preferences: TravelPreferences
    ) -> bool:
        """
        保存用户偏好

        Args:
            key: 用户唯一标识
            preferences: 偏好对象

        Returns:
            是否成功
        """
        try:
            # 添加到历史记录
            history_entry = {
                'key': key,
                'preferences': preferences.dict(),
                'action': 'save',
                'timestamp': datetime.now().isoformat()
            }
            self.preferences_history.append(history_entry)
            self._save_preferences_history()

            # 保存当前偏好
            self.preferences[key] = preferences
            self._save_preferences()

            logger.info(f"已保存偏好：{key}")
            return True

        except Exception as e:
            logger.error(f"保存偏好失败: {e}")
            return False

    def get_preference(self, key: str) -> Optional[TravelPreferences]:
        """
        获取用户偏好

        Args:
            key: 用户唯一标识

        Returns:
            偏好对象（如果存在），否则返回 None
        """
        return self.preferences.get(key)

    def get_all_preferences(self) -> Dict[str, TravelPreferences]:
        """
        获取所有用户偏好

        Returns:
            所有用户偏好字典
        """
        return self.preferences

    def update_preference(
        self,
        key: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        更新用户偏好

        Args:
            key: 用户唯一标识
            updates: 要更新的字段字典

        Returns:
            是否成功
        """
        if key not in self.preferences:
            logger.warning(f"偏好不存在：{key}")
            return False

        try:
            # 更新偏好的更新时间
            updates['updated_at'] = datetime.now()

            # 更新偏好
            old_pref = self.preferences[key].dict()
            old_pref.update(updates)

            new_pref = TravelPreferences(**old_pref)
            
            # 添加到历史记录
            history_entry = {
                'key': key,
                'preferences': old_pref,
                'action': 'update',
                'updates': updates,
                'timestamp': datetime.now().isoformat()
            }
            self.preferences_history.append(history_entry)
            self._save_preferences_history()

            # 保存更新后的偏好
            self.preferences[key] = new_pref
            self._save_preferences()

            logger.info(f"已更新偏好：{key}")
            return True

        except Exception as e:
            logger.error(f"更新偏好失败: {e}")
            return False

    def delete_preference(self, key: str) -> bool:
        """
        删除用户偏好

        Args:
            key: 用户唯一标识

        Returns:
            是否成功
        """
        if key not in self.preferences:
            logger.warning(f"偏好不存在：{key}")
            return False

        try:
            # 添加到历史记录
            history_entry = {
                'key': key,
                'preferences': self.preferences[key].dict(),
                'action': 'delete',
                'timestamp': datetime.now().isoformat()
            }
            self.preferences_history.append(history_entry)
            self._save_preferences_history()

            # 删除偏好
            del self.preferences[key]
            self._save_preferences()

            logger.info(f"已删除偏好：{key}")
            return True

        except Exception as e:
            logger.error(f"删除偏好失败: {e}")
            return False

    def get_preferences_history(self, key: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取偏好历史

        Args:
            key: 用户唯一标识（可选，如果不提供，返回所有历史）

        Returns:
            偏好历史记录
        """
        if key is None:
            return self.preferences_history
        else:
            return [hist for hist in self.preferences_history if hist['key'] == key]

    def clear_all_preferences(self) -> bool:
        """
        清空所有偏好

        Returns:
            是否成功
        """
        try:
            # 备份到历史记录
            backup_entry = {
                'key': 'ALL',
                'action': 'clear_all',
                'timestamp': datetime.now().isoformat(),
                'count': len(self.preferences)
            }
            self.preferences_history.append(backup_entry)
            self._save_preferences_history()

            # 清空偏好
            self.preferences = {}
            self._save_preferences()

            logger.info(f"已清空所有偏好（共 {backup_entry['count']} 个）")
            return True

        except Exception as e:
            logger.error(f"清空偏好失败: {e}")
            return False

    def export_preferences(self, file_path: str = "preferences_export.json"):
        """导出所有偏好到 JSON 文件"""
        export_path = Path(file_path)
        export_path = self.storage_dir / export_path if not export_path.is_absolute() else export_path

        try:
            # 导出偏好
            export_data = {
                'export_time': datetime.now().isoformat(),
                'total_users': len(self.preferences),
                'total_history_records': len(self.preferences_history),
                'preferences': {key: pref.dict() for key, pref in self.preferences.items()},
                'history': self.preferences_history
            }

            # 转换 datetime 为字符串
            def convert_datetime(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                elif isinstance(obj, dict):
                    return {k: convert_datetime(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_datetime(item) for item in obj]
                return obj

            export_data_converted = convert_datetime(export_data)

            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data_converted, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"已导出偏好到：{export_path}")
            return True

        except Exception as e:
            logger.error(f"导出偏好失败: {e}")
            return False

    def import_preferences(self, file_path: str):
        """从 JSON 文件导入偏好"""
        import_path = Path(file_path)
        import_path = self.storage_dir / import_path if not import_path.is_absolute() else import_path

        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 导入偏好
            imported_count = 0
            for key, pref_data in data.get('preferences', {}).items():
                pref_data['travel_date_start'] = datetime.fromisoformat(pref_data['travel_date_start']) if pref_data['travel_date_start'] else None
                pref_data['travel_date_end'] = datetime.fromisoformat(pref_data['travel_date_end']) if pref_data['travel_date_end'] else None
                pref_data['created_at'] = datetime.fromisoformat(pref_data['created_at'])
                pref_data['updated_at'] = datetime.fromisoformat(pref_data['updated_at'])
                
                self.preferences[key] = TravelPreferences(**pref_data)
                imported_count += 1

            # 导入历史
            for hist in data.get('history', []):
                if 'created_at' in hist['preferences']:
                    hist['preferences']['created_at'] = datetime.fromisoformat(hist['preferences']['created_at'])
                if 'updated_at' in hist['preferences']:
                    hist['preferences']['updated_at'] = datetime.fromisoformat(hist['preferences']['updated_at'])
                    
                self.preferences_history.append(hist)

            self._save_preferences()
            self._save_preferences_history()

            logger.info(f"已导入 {imported_count} 个偏好和 {len(data.get('history', []))} 条历史记录")
            return True

        except Exception as e:
            logger.error(f"导入偏好失败: {e}")
            return False

    def get_preferences_summary(self) -> Dict[str, Any]:
        """
        获取偏好统计摘要

        Returns:
            偏好统计摘要
        """
        total_users = len(self.preferences)
        total_history = len(self.preferences_history)

        if total_users == 0:
            return {
                'total_users': 0,
                'total_history': 0,
                'avg_budget': 0,
                'most_popular_destination': None,
                'most_popular_transportation': None
            }

        # 统计信息
        destinations = []
        budgets = []
        transportation_modes = []

        for pref in self.preferences.values():
            destinations.extend(pref.preferred_destinations)
            if pref.primary_destination:
                destinations.append(pref.primary_destination)
            budgets.append(pref.budget)
            transportation_modes.append(pref.transportation_mode)

        # 最受欢迎的目的地
        from collections import Counter
        dest_counter = Counter(destinations)

        # 平均预算
        avg_budget = sum(budgets) / len(budgets) if budgets else 0

        # 最受欢迎的交通方式
        transport_counter = Counter(transportation_modes)

        summary = {
            'total_users': total_users,
            'total_history': total_history,
            'avg_budget': avg_budget,
            'most_popular_destination': dest_counter.most_common(1)[0][0] if dest_counter else None,
            'most_popular_transportation': transport_counter.most_common(1)[0][0] if transport_counter else None,
            'transportation_distribution': {k: v for k, v in transport_counter.items()}
        }

        return summary

    def generate_preferences_report(self) -> str:
        """
        生成偏好报告

        Returns:
            偏好报告字符串
        """
        summary = self.get_preferences_summary()

        report = f"""
        === 用户偏好报告 ===

        基本信息：
        - 总用户数：{summary['total_users']}
        - 总历史记录数：{summary['total_history']}

        预算统计：
        - 平均预算：{summary['avg_budget']:,.2f} 元

        目的地偏好：
        - 最受欢迎的目的地：{summary.get('most_popular_destination', 'N/A')}

        交通偏好：
        - 最受欢迎的交通方式：{summary.get('most_popular_transportation', 'N/A')}
        - 交通方式分布：
        """

        # 添加交通方式分布
        for mode, count in summary.get('transportation_distribution', {}).items():
            report += f"  - {mode}: {count} 次\n"

        return report


# 使用示例
def example_usage():
    """使用示例"""
    # 创建偏好管理器
    manager = UserPreferenceManager()

    # 1. 创建示例偏好
    print("=== 创建示例偏好 ===")
    pref1 = TravelPreferences(
        user_name="张三",
        user_email="zhangsan@example.com",
        primary_destination="东京",
        travel_days=7,
        budget=20000.0,
        currency="CNY",
        num_travelers=2,
        travelers_info=[
            {"name": "张三", "age": "30", "gender": "男"},
            {"name": "李四", "age": "28", "gender": "女"}
        ],
        transportation_mode="flight",
        transportation="economy",
        accommodation_type="hotel",
        activities=["观光", "购物", "美食"],
        interests=["历史", "文化", "美食"],
        preferred_cuisine=["日本料理", "中华料理"],
        is_business_trip=False
    )

    # 2. 保存偏好
    print("\n=== 保存偏好 ===")
    manager.save_preference("user1", pref1)
    print(manager.get_preference("user1"))

    # 3. 更新偏好
    print("\n=== 更新偏好 ===")
    manager.update_preference("user1", {"budget": 25000.0, "updated_at": datetime.now()})
    print(manager.get_preference("user1"))

    # 4. 创建另一个用户的偏好
    print("\n=== 创建另一个用户的偏好 ===")
    pref2 = TravelPreferences(
        user_name="王五",
        user_email="wangwu@example.com",
        primary_destination="京都",
        travel_days=5,
        budget=15000.0,
        currency="CNY",
        num_travelers=1,
        travelers_info=[
            {"name": "王五", "age": "25", "gender": "男"}
        ],
        transportation_mode="train",
        transportation="business",
        accommodation_type="hostel",
        activities=["观光", "摄影"],
        interests=["历史", "摄影"],
        preferred_cuisine=["中华料理"],
        is_business_trip=False
    )

    manager.save_preference("user2", pref2)

    # 5. 获取所有偏好
    print("\n=== 获取所有偏好 ===")
    all_prefs = manager.get_all_preferences()
    print(f"总用户数：{len(all_prefs)}")
    for key, pref in all_prefs.items():
        print(f"  {key}: {pref.user_name} - {pref.primary_destination} ({pref.budget} 元)")

    # 6. 获取偏好统计
    print("\n=== 获取偏好统计 ===")
    summary = manager.get_preferences_summary()
    print(f"平均预算：{summary['avg_budget']:,.2f} 元")
    print(f"最受欢迎的目的地：{summary.get('most_popular_destination', 'N/A')}")
    print(f"最受欢迎的交通方式：{summary.get('most_popular_transportation', 'N/A')}")

    # 7. 生成偏好报告
    print("\n=== 生成偏好报告 ===")
    report = manager.generate_preferences_report()
    print(report)

    # 8. 导出偏好
    print("\n=== 导出偏好 ===")
    manager.export_preferences("preferences_export.json")

    # 9. 删除偏好
    print("\n=== 删除偏好 ===")
    manager.delete_preference("user1")
    print(manager.get_preference("user1"))

    # 10. 导入偏好
    print("\n=== 导入偏好 ===")
    manager.import_preferences("preferences_export.json")
    print(manager.get_preferences_summary())


if __name__ == "__main__":
    example_usage()
