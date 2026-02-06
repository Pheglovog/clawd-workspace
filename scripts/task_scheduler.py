#!/usr/bin/env python3
"""
自动化任务调度器
将区块链学习计划分成可执行的小任务
每30分钟自动发送一个子任务到系统
"""

import os
import json
import time
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any

# 任务存储文件
TASKS_FILE = "/root/clawd/docs/task_scheduler.json"
LOG_FILE = "/root/clawd/docs/task_scheduler.log"

class TaskScheduler:
    def __init__(self):
        self.tasks = self.load_tasks()
        self.current_task_index = 0
        self.running = True

    def load_tasks(self) -> Dict[str, Any]:
        """加载任务配置"""
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self.get_default_tasks()

    def save_tasks(self):
        """保存任务配置"""
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, indent=2, ensure_ascii=False)

    def get_default_tasks(self) -> Dict[str, Any]:
        """获取默认任务配置"""
        return {
            "tasks": self.get_blockchain_tasks(),
            "current_task_index": 0,
            "last_update": datetime.now().isoformat(),
            "completed_tasks": []
        }

    def get_blockchain_tasks(self) -> List[Dict[str, Any]]:
        """获取区块链学习任务"""
        return [
            {
                "id": 1,
                "title": "Solidity 基础 - 安装和配置",
                "category": "基础",
                "estimated_time": "30分钟",
                "difficulty": "初级",
                "description": "安装 Solidity 编译器、配置开发环境、编写第一个 Solidity 合约",
                "files": ["solidity/hello-world.sol"],
                "commands": [
                    "solc --version",
                    "mkdir -p solidity",
                    "echo 'pragma solidity ^0.8.20;' > solidity/hello-world.sol"
                ],
                "output": ["solidity/hello-world.sol"],
                "prerequisites": ["Node.js", "npm"],
                "verification": "文件 solidity/hello-world.sol 存在并包含合约代码",
                "success_criteria": [
                    "合约编译无错误",
                    "理解 pragma 声明",
                    "能够编写简单的合约"
                ]
            },
            {
                "id": 2,
                "title": "Solidity 基础 - 数据类型和变量",
                "category": "基础",
                "estimated_time": "30分钟",
                "difficulty": "初级",
                "description": "学习 Solidity 的数据类型（uint, int, bool, address, string）、变量声明、常量和不可变变量",
                "files": ["solidity/types.sol"],
                "commands": [],
                "prerequisites": ["任务1"],
                "verification": "理解所有数据类型的特性和用途",
                "success_criteria": [
                    "能够正确选择数据类型",
                    "理解变量和常量的区别"
                ]
            },
            {
                "id": 3,
                "title": "Solidity 基础 - 函数和修饰符",
                "category": "基础",
                "estimated_time": "30分钟",
                "difficulty": "初级",
                "description": "学习 Solidity 的函数定义、参数、返回值、修饰符（public, private, internal, external）",
                "files": ["solidity/functions.sol"],
                "prerequisites": ["任务2"],
                "verification": "能够定义和调用函数，理解不同可见性修饰符",
                "success_criteria": [
                    "能够编写带参数的函数",
                    "理解 public 和 private 的区别"
                ]
            },
            {
                "id": 4,
                "title": "Solidity 基础 - 映射和数组",
                "category": "基础",
                "estimated_time": "30分钟",
                "difficulty": "初级",
                "description": "学习 Solidity 的映射（Mapping）和数组（Array）数据结构，动态数组和固定大小数组",
                "files": ["solidity/mappings.sol"],
                "prerequisites": ["任务3"],
                "verification": "能够使用映射和数组存储和检索数据",
                "success_criteria": [
                    "能够使用 mapping(key => value) 语法",
                    "理解 push、pop 和 length 方法"
                ]
            },
            {
                "id": 5,
                "title": "Solidity 基础 - 结构体和枚举",
                "category": "基础",
                "estimated_time": "30分钟",
                "difficulty": "初级",
                "description": "学习 Solidity 的结构体（Struct）和枚举类型，自定义数据类型的定义和使用",
                "files": ["solidity/structs.sol"],
                "prerequisites": ["任务4"],
                "verification": "能够定义和使用自定义数据类型",
                "success_criteria": [
                    "能够定义 struct 类型",
                    "能够使用 enum 定义选项"
                ]
            },
            {
                "id": 6,
                "title": "Solidity 基础 - 继承和接口",
                "category": "基础",
                "estimated_time": "30分钟",
                "difficulty": "中级",
                "description": "学习 Solidity 的继承机制、接口（Interface）定义和实现、抽象合约",
                "files": ["solidity/inheritance.sol", "solidity/interfaces.sol"],
                "prerequisites": ["任务5"],
                "verification": "能够使用继承扩展合约功能，能够定义和实现接口",
                "success_criteria": [
                    "能够使用 is 关字继承",
                    "能够定义 interface"
                ]
            },
            {
                "id": 7,
                "title": "Solidity 基础 - 错误处理和事件",
                "category": "基础",
                "estimated_time": "30分钟",
                "difficulty": "中级",
                "description": "学习 Solidity 的错误处理（require, revert, assert, custom errors）、事件（Event）的定义和触发",
                "files": ["solidity/errors-events.sol"],
                "prerequisites": ["任务6"],
                "verification": "能够正确使用 require 和 revert，能够定义和触发事件",
                "success_criteria": [
                    "能够使用 require 检查条件",
                    "能够定义 event 并触发它"
                ]
            },
            {
                "id": 8,
                "title": "Solidity 基础 - 修饰符详解",
                "category": "基础",
                "estimated_time": "30分钟",
                "difficulty": "中级",
                "description": "深入学习 Solidity 的修饰符：view, pure, payable, constant, immutable, virtual, override",
                "files": ["solidity/modifiers.sol"],
                "prerequisites": ["任务7"],
                "verification": "理解所有修饰符的特性和用途",
                "success_criteria": [
                    "理解 view 和 pure 的区别",
                    "理解 payable 的作用"
                ]
            },
            {
                "id": 9,
                "title": "Solidity 基础 - 全局变量和环境",
                "category": "基础",
                "estimated_time": "30分钟",
                "difficulty": "中级",
                "description": "学习 Solidity 的全局变量、环境变量、区块和交易信息、msg.sender 和 msg.value",
                "files": ["solidity/globals.sol"],
                "prerequisites": ["任务8"],
                "verification": "能够访问全局变量和交易信息",
                "success_criteria": [
                    "能够使用 msg.sender 和 msg.value",
                    "理解 block 和 tx 对象"
                ]
            },
            {
                "id": 10,
                "title": "ERC20 标准 - 基础实现",
                "category": "智能合约",
                "estimated_time": "30分钟",
                "difficulty": "中级",
                "description": "使用 OpenZeppelin 实现 ERC20 代币合约，理解 totalSupply、balanceOf、transfer、approve",
                "files": ["contracts/erc20/MyToken.sol"],
                "prerequisites": ["任务9"],
                "verification": "实现完整的 ERC20 代币合约",
                "success_criteria": [
                    "继承自 IERC20",
                    "实现所有必需的函数"
                ]
            },
            {
                "id": 11,
                "title": "ERC20 标准 - 铸币和铸造",
                "category": "智能合约",
                "estimated_time": "30分钟",
                "difficulty": "中级",
                "description": "在 ERC20 代币中实现铸币（mint）和销币（burn）功能，理解增发机制",
                "files": ["contracts/erc20/MyToken.sol"],
                "prerequisites": ["任务10"],
                "verification": "能够安全地实现铸造和销币功能",
                "success_criteria": [
                    "添加 mint 和 burn 函数",
                    "添加适当的访问控制"
                ]
            },
            {
                "id": 12,
                "title": "ERC20 标准 - 授权和余额",
                "category": "智能合约",
                "estimated_time": "30分钟",
                "difficulty": "中级",
                "description": "实现 allowance（授权）和 transferFrom（授权转账）功能，理解批准机制",
                "files": ["contracts/erc20/MyToken.sol"],
                "prerequisites": ["任务11"],
                "verification": "能够实现完整的授权和授权转账功能",
                "success_criteria": [
                    "实现 approve 函数",
                    "实现 transferFrom 函数"
                ]
            },
            {
                "id": 13,
                "title": "ERC721 标准 - 基础实现",
                "category": "智能合约",
                "estimated_time": "30分钟",
                "difficulty": "中级",
                "description": "使用 OpenZeppelin 实现 ERC721 NFT 合约，理解 tokenURI、transferFrom、safeTransferFrom",
                "files": ["contracts/erc721/MyNFT.sol"],
                "prerequisites": ["任务12"],
                "verification": "实现完整的 ERC721 NFT 合约",
                "success_criteria": [
                    "继承自 ERC721",
                    "实现 NFT 基本功能"
                ]
            },
            {
                "id": 14,
                "title": "ERC721 标准 - 铸造和批量操作",
                "category": "智能合约",
                "estimated_time": "30分钟",
                "difficulty": "中级",
                "description": "在 ERC721 NFT 中实现批量铸造（mintBatch）和安全传输功能",
                "files": ["contracts/erc721/MyNFT.sol"],
                "prerequisites": ["任务13"],
                "verification": "能够安全地实现批量铸造功能",
                "success_criteria": [
                    "实现 mintBatch 函数",
                    "实现安全传输检查"
                ]
            },
            {
                "id": 15,
                "title": "Gas 优化 - 存储优化",
                "category": "优化",
                "estimated_time": "30分钟",
                "difficulty": "高级",
                "description": "学习存储优化技巧：使用 uint256 代替 uint8（存储打包）、减少存储读写、使用 calldata",
                "files": ["contracts/gas-optimization/StorageOptimization.sol"],
                "prerequisites": ["任务14"],
                "verification": "能够优化合约的 Gas 使用",
                "success_criteria": [
                    "理解存储打包原理",
                    "能够使用 uint256 优化"
                ]
            },
            {
                "id": 16,
                "title": "Gas 优化 - 循环优化",
                "category": "优化",
                "estimated_time": "30分钟",
                "difficulty": "高级",
                "description": "学习循环优化技巧：使用短路求值、减少循环迭代、使用 unchecked 数学运算",
                "files": ["contracts/gas-optimization/LoopOptimization.sol"],
                "prerequisites": ["任务15"],
                "verification": "能够优化循环和条件判断的 Gas 使用",
                "success_criteria": [
                    "理解短路求值原理",
                    "能够使用 unchecked"
                ]
            },
            {
                "id": 17,
                "title": "Gas 优化 - 事件优化",
                "category": "优化",
                "estimated_time": "30分钟",
                "difficulty": "高级",
                "description": "学习事件优化技巧：使用 indexed 参数、减少事件数据、合理使用事件记录",
                "files": ["contracts/gas-optimization/EventOptimization.sol"],
                "prerequisites": ["任务16"],
                "verification": "能够优化事件的 Gas 使用",
                "success_criteria": [
                    "理解 indexed 的作用",
                    "合理设计事件参数"
                ]
            },
            {
                "id": 18,
                "title": "OpenZeppelin AccessControl - Role-based",
                "category": "安全",
                "estimated_time": "30分钟",
                "difficulty": "中级",
                "description": "学习 OpenZeppelin 的 AccessControl 权限管理系统，理解角色（Role）和默认管理员角色",
                "files": ["contracts/access-control/RoleBased.sol"],
                "prerequisites": ["任务17"],
                "verification": "能够实现基于角色的访问控制",
                "success_criteria": [
                    "定义多个角色",
                    "实现角色检查修饰符"
                ]
            },
            {
                "id": 19,
                "title": "OpenZeppelin Pausable - 紧急暂停",
                "category": "安全",
                "estimated_time": "30分钟",
                "difficulty": "中级",
                "description": "学习 OpenZeppelin 的 Pausable 紧急暂停功能，理解 whenNotPaused 修饰符",
                "files": ["contracts/security/Pausable.sol"],
                "prerequisites": ["任务18"],
                "verification": "能够实现紧急暂停功能",
                "success_criteria": [
                    "继承自 Pausable",
                    "使用 whenNotPaused 修饰符"
                ]
            },
            {
                "id": 20,
                "title": "智能合约安全 - 重入攻击防护",
                "category": "安全",
                "estimated_time": "30分钟",
                "difficulty": "高级",
                "description": "学习重入攻击原理，使用 OpenZeppelin 的 ReentrancyGuard 保护合约",
                "files": ["contracts/security/ReentrancyGuard.sol"],
                "prerequisites": ["任务19"],
                "verification": "能够理解和防止重入攻击",
                "success_criteria": [
                    "理解重入攻击原理",
                    "使用 nonReentrant 修饰符"
                ]
            },
            {
                "id": 21,
                "title": "智能合约安全 - 整数溢出防护",
                "category": "安全",
                "estimated_time": "30分钟",
                "difficulty": "高级",
                "description": "学习整数溢出攻击原理，使用 SafeMath 库或 Solidity 0.8+ 的内置检查",
                "files": ["contracts/security/IntegerOverflow.sol"],
                "prerequisites": ["任务20"],
                "verification": "能够理解和防止整数溢出攻击",
                "success_criteria": [
                    "理解溢出/下溢出原理",
                    "使用 SafeMath 或 Solidity 0.8+ 检查"
                ]
            },
            {
                "id": 22,
                "title": "Layer2 - Optimism 基础",
                "category": "Layer2",
                "estimated_time": "30分钟",
                "difficulty": "中级",
                "description": "学习 Optimism Layer2 的基础：Optimism Portal、跨链桥接、Gas 优势",
                "files": ["docs/layer2/optimism-basics.md"],
                "prerequisites": ["任务21"],
                "verification": "理解 Optimism 的基本概念和优势",
                "success_criteria": [
                    "理解 Layer2 的优势",
                    "了解 Optimism 的架构"
                ]
            },
            {
                "id": 23,
                "title": "Layer2 - Optimism 部署",
                "category": "Layer2",
                "estimated_time": "30分钟",
                "difficulty": "高级",
                "description": "在 Optimism 测试网上部署智能合约，理解跨链部署流程",
                "files": ["contracts/optimism-deployment/DeployOptimism.sol"],
                "prerequisites": ["任务22"],
                "verification": "能够在 Optimism 测试网上部署合约",
                "success_criteria": [
                    "获得 Optimism 测试网 ETH",
                    "成功部署合约到 Optimism"
                ]
            },
            {
                "id": 24,
                "title": "Layer2 - Arbitrum 基础",
                "category": "Layer2",
                "estimated_time": "30分钟",
                "difficulty": "中级",
                "description": "学习 Arbitrum Layer2 的基础：Nitro 技术栈、跨链桥接、Gas 优势",
                "files": ["docs/layer2/arbitrum-basics.md"],
                "prerequisites": ["任务23"],
                "verification": "理解 Arbitrum 的基本概念和优势",
                "success_criteria": [
                    "理解 Layer2 的优势",
                    "了解 Arbitrum 的架构"
                ]
            },
            {
                "id": 25,
                "title": "DeFi - AMM 原理",
                "category": "DeFi",
                "estimated_time": "30分钟",
                "difficulty": "中级",
                "description": "深入理解 AMM（自动做市商）的数学模型：x * y = k、流动性的添加和移除",
                "files": ["docs/defi/amm-principles.md", "contracts/amm/SimpleAMM.sol"],
                "prerequisites": ["任务24"],
                "verification": "理解 AMM 的数学原理和实现",
                "success_criteria": [
                    "理解 x * y = k 公式",
                    "能够实现简单的 AMM"
                ]
            },
            {
                "id": 26,
                "title": "DeFi - Uniswap V2 实现",
                "category": "DeFi",
                "estimated_time": "30分钟",
                "difficulty": "高级",
                "description": "使用 OpenZeppelin 的 Uniswap V2 库实现一个简单的 AMM 合约",
                "files": ["contracts/defi/uniswap-v2/MyUniswap.sol"],
                "prerequisites": ["任务25"],
                "verification": "能够使用 OpenZeppelin 实现 AMM",
                "success_criteria": [
                    "继承自 UniswapV2Factory 或类似接口",
                    "实现基本的 AMM 功能"
                ]
            },
            {
                "id": 27,
                "title": "DeFi - 借贷协议原理",
                "category": "DeFi",
                "estimated_time": "30分钟",
                "difficulty": "中级",
                "description": "深入理解借贷协议的原理：抵押品、借贷利率、清算机制、利率模型",
                "files": ["docs/defi/lending-principles.md"],
                "prerequisites": ["任务26"],
                "verification": "理解借贷协议的核心机制",
                "success_criteria": [
                    "理解抵押品的计算",
                    "理解清算触发条件"
                ]
            },
            {
                "id": 28,
                "title": "DeFi - Compound 集成",
                "category": "DeFi",
                "estimated_time": "30分钟",
                "difficulty": "高级",
                "description": "学习如何与 Compound 协议集成：使用 cToken、提供流动性、借贷",
                "files": ["contracts/defi/compound-integration/CompoundIntegration.sol"],
                "prerequisites": ["任务27"],
                "verification": "能够与 Compound 协议集成",
                "success_criteria": [
                    "理解 cToken 机制",
                    "能够提供流动性和借贷"
                ]
            },
            {
                "id": 29,
                "title": "ZK-Rollup - 基础概念",
                "category": "Layer2",
                "estimated_time": "30分钟",
                "difficulty": "高级",
                "description": "学习 ZK-Rollup 的基础原理：零知识证明、Rollup、有效性证明（Validity Proofs）",
                "files": ["docs/layer2/zk-rollup-basics.md"],
                "prerequisites": ["任务28"],
                "verification": "理解 ZK-Rollup 的基本概念和优势",
                "success_criteria": [
                    "理解零知识证明",
                    "理解 Rollup 架构"
                ]
            },
            {
                "id": 30,
                "title": "ZK-Rollup - 实现原理",
                "category": "Layer2",
                "estimated_time": "30分钟",
                "difficulty": "高级",
                "description": "学习 ZK-Rollup 的实现原理：证明生成、验证、Rollup 合约",
                "files": ["docs/layer2/zk-rollup-implementation.md"],
                "prerequisites": ["任务29"],
                "verification": "理解 ZK-Rollup 的实现流程",
                "success_criteria": [
                    "理解证明生成流程",
                    "理解 Rollup 合约的工作原理"
                ]
            }
        ]

    def log(self, message: str, level: str = "INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"

        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_entry)

        print(log_entry.strip())

    def get_next_task(self) -> Dict[str, Any]:
        """获取下一个任务"""
        if self.current_task_index < len(self.tasks["tasks"]):
            task = self.tasks["tasks"][self.current_task_index]
            self.log(f"Task {task['id']}: {task['title']}", "INFO")
            self.log(f"  Category: {task['category']}", "INFO")
            self.log(f"  Estimated Time: {task['estimated_time']}", "INFO")
            self.log(f"  Difficulty: {task['difficulty']}", "INFO")
            self.log(f"  Description: {task['description']}", "INFO")
            return task
        else:
            self.log("所有任务已完成！", "INFO")
            return None

    def execute_task(self, task: Dict[str, Any]) -> bool:
        """执行任务"""
        try:
            self.log(f"开始执行任务 {task['id']}: {task['title']}", "INFO")

            # 创建必要的目录
            for file_path in task.get("files", []):
                dir_path = os.path.dirname(f"/root/clawd/{file_path}")
                if dir_path:
                    os.makedirs(dir_path, exist_ok=True)

            # 执行命令
            if task.get("commands"):
                for command in task["commands"]:
                    self.log(f"  执行命令: {command}", "INFO")
                    try:
                        subprocess.run(command, shell=True, check=True, cwd="/root/clawd")
                    except subprocess.CalledProcessError as e:
                        self.log(f"  命令执行失败: {e}", "ERROR")
                        return False

            # 验证结果
            if task.get("verification"):
                self.log(f"  验证: {task['verification']}", "INFO")

            # 标记任务为完成
            if task["id"] not in self.tasks["completed_tasks"]:
                self.tasks["completed_tasks"].append(task["id"])
                self.tasks["last_update"] = datetime.now().isoformat()
                self.save_tasks()

            self.log(f"任务 {task['id']} 执行完成！", "INFO")
            return True

        except Exception as e:
            self.log(f"任务执行错误: {str(e)}", "ERROR")
            return False

    def update_task_index(self):
        """更新任务索引"""
        self.current_task_index += 1
        self.log(f"更新任务索引到: {self.current_task_index}", "INFO")

    def get_progress(self) -> Dict[str, Any]:
        """获取进度"""
        total = len(self.tasks["tasks"])
        completed = len(self.tasks["completed_tasks"])
        progress = (completed / total) * 100 if total > 0 else 100

        return {
            "total": total,
            "completed": completed,
            "progress": progress,
            "current_task_index": self.current_task_index
        }

    def print_progress(self):
        """打印进度"""
        progress = self.get_progress()
        self.log(f"=== 进度概览 ===", "INFO")
        self.log(f"总任务: {progress['total']}", "INFO")
        self.log(f"已完成: {progress['completed']}", "INFO")
        self.log(f"进度: {progress['progress']:.1f}%", "INFO")
        self.log(f"当前任务索引: {progress['current_task_index']}", "INFO")

        # 分类统计
        categories = {}
        for task in self.tasks["tasks"]:
            category = task["category"]
            if category not in categories:
                categories[category] = {"total": 0, "completed": 0}
            categories[category]["total"] += 1
            if task["id"] in self.tasks["completed_tasks"]:
                categories[category]["completed"] += 1

        self.log(f"=== 分类进度 ===", "INFO")
        for category, stats in categories.items():
            category_progress = (stats["completed"] / stats["total"]) * 100 if stats["total"] > 0 else 100
            self.log(f"{category}: {stats['completed']}/{stats['total']} ({category_progress:.1f}%)", "INFO")

    def run_scheduler(self, interval_minutes: int = 30):
        """运行调度器"""
        self.log("=== 任务调度器启动 ===", "INFO")
        self.log(f"任务间隔: {interval_minutes} 分钟", "INFO")
        self.log(f"总任务数: {len(self.tasks['tasks'])}", "INFO")

        # 打印初始进度
        self.print_progress()

        # 定期执行任务
        while self.running:
            # 获取下一个任务
            task = self.get_next_task()

            if task is None:
                self.log("所有任务已完成！调度器将停止。", "INFO")
                break

            # 执行任务
            success = self.execute_task(task)

            if success:
                self.update_task_index()
                self.print_progress()
            else:
                self.log(f"任务 {task['id']} 执行失败，将重试...", "ERROR")

            # 等待下一个任务
            self.log(f"等待 {interval_minutes} 分钟...", "INFO")
            time.sleep(interval_minutes * 60)


def main():
    """主函数"""
    print("=== 自动化任务调度器 ===")
    print("每30分钟自动执行一个区块链学习任务")
    print("按 Ctrl+C 停止")
    print("")

    # 创建调度器
    scheduler = TaskScheduler()

    # 运行调度器
    try:
        scheduler.run_scheduler(interval_minutes=30)
    except KeyboardInterrupt:
        print("\n\n调度器已停止")
        scheduler.running = False
        scheduler.log("调度器手动停止", "INFO")
        scheduler.print_progress()


if __name__ == "__main__":
    main()
