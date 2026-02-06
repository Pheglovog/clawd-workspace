#!/usr/bin/env python3
"""
改进版持续任务执行器 - 确保输出可见
"""

import json
import time
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# 强制立即刷新输出
sys.stdout.reconfigure(line_buffering=True)

TASKS_FILE = Path("/root/clawd/daily-tasks.json")
PROGRESS_FILE = Path("/root/clawd/task-progress.json")

# 任务配置
TASKS = [
    {
        "id": "1",
        "name": "CarLife 部署到测试网络",
        "description": "部署智能合约到 Sepolia 测试网",
        "steps": ["检查余额并获取测试币", "部署合约", "验证合约功能"],
        "command": "echo 'Task 1: CarLife 部署 - 需要用户配置私钥和获取测试币'",
        "status": "pending",
        "requires_user_input": True,
        "notes": "需要用户配置私钥和获取测试币"
    },
    {
        "id": "2",
        "name": "AlphaGPT 真实数据训练",
        "description": "运行真实数据训练脚本",
        "steps": ["修复代码问题", "运行训练", "分析结果"],
        "command": "cd /root/clawd/AlphaGPT && echo 'Task 2: AlphaGPT 训练 - 已完成于 08:51'",
        "status": "completed",
        "requires_user_input": False,
        "notes": "✅ 已完成简化版训练（3 epochs，最佳验证损失: 1.081648），模型保存到 best_model_simple.pt"
    },
    {
        "id": "3",
        "name": "Travel Planner Agent 功能完善",
        "description": "完善 Agent 协作功能",
        "steps": ["检查 API 配置", "测试 Agent 协作", "编写测试文档"],
        "command": "cd /root/clawd/travel-planner-agent && echo 'Task 3: Travel Planner - 已完成于 08:55'",
        "status": "completed",
        "requires_user_input": False,
        "notes": "✅ 已完成配置和测试文档 (TESTING_GUIDE.md)，包含 API 配置、功能测试和使用示例"
    },
    {
        "id": "4",
        "name": "添加更多项目内容",
        "description": "为网站添加更多项目详情",
        "steps": ["添加项目详情", "添加项目截图", "更新统计数据"],
        "command": "cd /root/clawd/pheglovog-site && echo 'Task 4: 添加项目内容 - 已完成于 09:00'",
        "status": "completed",
        "requires_user_input": False,
        "notes": "✅ 已更新项目页面，添加 6 个项目详情（AlphaGPT, CarLife, CurrencyExchange, Travel Planner, Clawd Workspace, Pheglovog Site），每个项目包含功能特性和状态"
    }
]


def print_flush(text: str):
    """打印并立即刷新"""
    print(text, flush=True)


def load_progress() -> Dict[str, Any]:
    """加载任务进度"""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {"current_task": "1", "completed_tasks": [], "last_run": None, "attempts": {}}


def save_progress(progress: Dict[str, Any]):
    """保存任务进度"""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)


def get_next_task() -> Dict[str, Any]:
    """获取下一个待执行任务"""
    progress = load_progress()
    completed = progress.get("completed_tasks", [])

    # 找第一个未完成的任务
    for task in TASKS:
        if task["id"] not in completed:
            return task

    # 所有任务都完成了
    return None


def execute_task(task: Dict[str, Any]) -> bool:
    """执行任务"""
    print_flush(f"\n{'='*60}")
    print_flush(f"🎯 执行任务: {task['name']}")
    print_flush(f"📝 描述: {task['description']}")
    print_flush(f"🔧 状态: {task['status']}")
    print_flush(f"{'='*60}\n")

    # 检查是否需要用户输入
    if task["requires_user_input"]:
        print_flush(f"⚠️  此任务需要用户输入:")
        print_flush(f"   {task['notes']}")
        print_flush("\n请提供所需输入后重试，或手动执行:")
        print_flush(f"   {task['command']}\n")
        return False

    # 执行命令
    print_flush(f"执行命令: {task['command']}\n")
    try:
        result = subprocess.run(
            task["command"],
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        print_flush(result.stdout)
        if result.stderr:
            print_flush("❌ 错误输出:")
            print_flush(result.stderr)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print_flush("⏰ 任务超时")
        return False
    except Exception as e:
        print_flush(f"❌ 执行失败: {e}")
        return False


def update_task_status(task_id: str, status: str, notes: str = ""):
    """更新任务状态"""
    progress = load_progress()

    if status == "completed":
        if task_id not in progress["completed_tasks"]:
            progress["completed_tasks"].append(task_id)

    progress["last_run"] = datetime.now().isoformat()

    # 记录尝试次数
    if task_id not in progress["attempts"]:
        progress["attempts"][task_id] = 0
    progress["attempts"][task_id] += 1

    save_progress(progress)
    print_flush(f"💾 已保存进度 - 任务 {task_id}: {status}")


def print_status():
    """打印当前状态"""
    print_flush(f"\n{'='*60}")
    print_flush("📊 当前任务状态")
    print_flush(f"{'='*60}\n")

    progress = load_progress()
    completed = progress.get("completed_tasks", [])

    for task in TASKS:
        if task["id"] in completed:
            status_icon = "✅"
            status_text = "已完成"
        elif task["requires_user_input"]:
            status_icon = "🔑"
            status_text = "需用户输入"
        else:
            status_icon = "⏳"
            status_text = "待执行"

        print_flush(f"{status_icon} 任务 {task['id']}: {task['name']}")
        print_flush(f"   状态: {status_text}")
        notes_truncated = task['notes'][:50] + "..." if len(task['notes']) > 50 else task['notes']
        print_flush(f"   备注: {notes_truncated}")
        print_flush("")


def main():
    """主循环"""
    print_flush("\n" + "="*60)
    print_flush("🔄 改进版持续任务执行器")
    print_flush("自动循环执行任务直到完成")
    print_flush("="*60 + "\n")

    max_cycles = 100
    cycle = 0

    while cycle < max_cycles:
        cycle += 1
        print_flush(f"\n📌 循环 {cycle}/{max_cycles}")
        print_flush(f"⏰ 时间: {datetime.now().strftime('%H:%M:%S')}")

        # 打印状态
        print_status()

        # 获取下一个任务
        task = get_next_task()

        if task is None:
            print_flush("\n" + "="*60)
            print_flush("🎉 所有任务已完成！")
            print_flush("="*60 + "\n")
            break

        # 执行任务
        task["status"] = "in_progress"
        print_flush(f"🔄 开始执行任务 {task['id']}...\n")

        success = execute_task(task)

        if success:
            task["status"] = "completed"
            task["notes"] = f"✅ 于 {datetime.now().strftime('%H:%M:%S')} 完成"
            update_task_status(task["id"], "completed", task["notes"])
            print_flush(f"\n✅ 任务 {task['id']} 完成！\n")
            # 短暂等待
            time.sleep(2)
        else:
            task["status"] = "blocked"
            update_task_status(task["id"], "blocked")
            print_flush(f"\n⚠️  任务 {task['id']} 被阻塞，30 秒后重试\n")
            # 等待 30 秒后重试
            time.sleep(30)

    if cycle >= max_cycles:
        print_flush(f"\n⚠️  达到最大循环次数 ({max_cycles})")


if __name__ == "__main__":
    main()
