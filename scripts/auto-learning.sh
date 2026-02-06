#!/bin/bash
# 自动化学习启动脚本
# 每30分钟自动执行一个区块链学习任务

echo "=== 自动化学习系统 ==="
echo "每30分钟自动执行一个区块链学习任务"
echo "按 Ctrl+C 停止"
echo ""

# 确保脚本有执行权限
chmod +x /root/clawd/scripts/task_scheduler.py

# 循环执行任务调度器
while true; do
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 启动任务调度器..."
    
    # 执行任务调度器（内部每30分钟执行一个任务）
    python3 /root/clawd/scripts/task_scheduler.py
    
    # 检查执行结果
    if [ $? -eq 0 ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 任务执行成功"
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 任务执行失败，将重试..."
    fi
    
    # 等待30分钟
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 等待下一个任务（30分钟）..."
    echo "=================================================="
    sleep 1800
done
