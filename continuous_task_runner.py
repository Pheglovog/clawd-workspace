#!/usr/bin/env python3
"""
持续任务执行器 - 自动循环执行任务直到完成
"""

import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

TASKS_FILE = Path("/root/clawd/daily-tasks.json")
PROGRESS_FILE = Path("/root/clawd/task-progress.json")

# 任务列表
TASKS = [
    {
        "id": "1",
        "name": "CarLife 部署到测试网络",
        "description": "部署智能合约到 Sepolia 测试网",
        "steps": [
            "检查余额并获取测试币",
            "部署合约",
            "验证合约功能"
        ],
        "command": "cd /root/clawd/CarLife && npx hardhat run scripts/deploy.js --network sepolia",
        "status": "pending",
        "requires_user_input": True,
        "notes": "需要用户配置私钥和获取测试币"
    },
    {
        "id": "2",
        "name": "AlphaGPT 真实数据训练",
        "description": "运行真实数据训练脚本",
        "steps": [
            "修复代码问题",
            "运行训练",
            "分析结果"
        ],
        "command": "cd /root/clawd/AlphaGPT && python train_simple.py",
        "status": "in_progress",
        "requires_user_input": False,
        "notes": "正在修复数据加载和因子计算问题"
    },
    {
        "id": "3",
        "name": "Travel Planner Agent 功能完善",
        "description": "完善 Agent 协作功能",
        "steps": [
            "检查 API 配置",
            "测试 Agent 协作",
            "编写测试文档"
        ],
        "command": "cd /root/clawd/travel-planner-agent && python src/main.py",
        "status": "pending",
        "requires_user_input": False,
        "notes": "待完成"
    },
    {
        "id": "4",
        "name": "添加更多项目内容",
        "description": "为网站添加更多项目详情",
        "steps": [
            "添加项目详情",
            "添加项目截图",
            "更新统计数据"
        ],
        "command": "echo '添加项目内容'",
        "status": "pending",
        "requires_user_input": False,
        "notes": "待完成"
    }
]


def load_progress() -> Dict[str, Any]:
    """加载任务进度"""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {
        "current_task": "1",
        "completed_tasks": [],
        "last_run": None,
        "attempts": {}
    }


def save_progress(progress: Dict[str, Any]):
    """保存任务进度"""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)


def get_next_task() -> Dict[str, Any]:
    """获取下一个待执行任务"""
    progress = load_progress()
    current_id = progress.get("current_task", "1")

    for task in TASKS:
        if task["id"] == current_id and task["status"] != "completed":
            return task

    # 如果当前任务已完成，找下一个
    for task in TASKS:
        if task["status"] not in ["completed", "in_progress"]:
            return task

    # 所有任务都完成了
    return None


def execute_task(task: Dict[str, Any]) -> bool:
    """执行任务"""
    print(f"\n{'='*60}")
    print(f"🎯 执行任务: {task['name']}")
    print(f"📝 描述: {task['description']}")
    print(f"🔧 状态: {task['status']}")
    print(f"{'='*60}\n")

    # 检查是否需要用户输入
    if task["requires_user_input"]:
        print(f"⚠️  此任务需要用户输入:")
        print(f"   {task['notes']}")
        print("\n请提供所需输入后重试，或手动执行:")
        print(f"   {task['command']}\n")
        return False

    # 执行命令
    try:
        result = subprocess.run(
            task["command"],
            shell=True,
            capture_output=True,
            text=True,
            timeout=600  # 10 分钟超时
        )

        print(result.stdout)
        if result.stderr:
            print("❌ 错误输出:")
            print(result.stderr)

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print("⏰ 任务超时（10分钟）")
        return False
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        return False


def update_task_status(task_id: str, status: str, notes: str = ""):
    """更新任务状态"""
    for task in TASKS:
        if task["id"] == task_id:
            task["status"] = status
            if notes:
                task["notes"] = notes
            break

    # 更新进度
    progress = load_progress()

    if status == "completed":
        if task_id not in progress["completed_tasks"]:
            progress["completed_tasks"].append(task_id)
        # 移动到下一个任务
        next_id = str(int(task_id) + 1)
        if any(t["id"] == next_id for t in TASKS):
            progress["current_task"] = next_id

    progress["last_run"] = datetime.now().isoformat()

    # 记录尝试次数
    if task_id not in progress["attempts"]:
        progress["attempts"][task_id] = 0
    progress["attempts"][task_id] += 1

    save_progress(progress)


def print_status():
    """打印当前状态"""
    print(f"\n{'='*60}")
    print("📊 当前任务状态")
    print(f"{'='*60}\n")

    for task in TASKS:
        status_icon = {
            "pending": "⏳",
            "in_progress": "🔄",
            "completed": "✅",
            "failed": "❌",
            "blocked": "🚫"
        }.get(task["status"], "❓")

        print(f"{status_icon} 任务 {task['id']}: {task['name']}")
        print(f"   状态: {task['status']}")
        print(f"   备注: {task['notes']}")
        print()


def main():
    """主循环"""
    print("\n" + "="*60)
    print("🔄 持续任务执行器")
    print("自动循环执行任务直到完成")
    print("="*60 + "\n")

    max_cycles = 100  # 最多循环 100 次
    cycle = 0

    while cycle < max_cycles:
        cycle += 1
        print(f"\n📌 循环 {cycle}/{max_cycles}")

        # 打印状态
        print_status()

        # 获取下一个任务
        task = get_next_task()

        if task is None:
            print("\n" + "="*60)
            print("🎉 所有任务已完成！")
            print("="*60 + "\n")
            break

        # 执行任务
        task["status"] = "in_progress"
        update_task_status(task["id"], "in_progress")

        success = execute_task(task)

        if success:
            task["status"] = "completed"
            task["notes"] = f"于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 完成"
            update_task_status(task["id"], "completed")
            print(f"\n✅ 任务 {task['id']} 完成！\n")
        else:
            task["status"] = "blocked"
            task["notes"] = f"执行失败，需要检查"
            update_task_status(task["id"], "blocked")
            print(f"\n⚠️  任务 {task['id']} 被阻塞，将在下次循环重试\n")

            # 如果是阻塞状态，等待一段时间后重试
            time.sleep(30)  # 等待 30 秒

    if cycle >= max_cycles:
        print(f"\n⚠️  达到最大循环次数 ({max_cycles})")
        print("任务可能需要人工干预\n")


if __name__ == "__main__":
    main()
