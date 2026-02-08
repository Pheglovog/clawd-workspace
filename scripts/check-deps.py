#!/usr/bin/env python3
"""
依赖检查脚本
检查项目依赖是否需要更新，并生成报告
"""

import subprocess
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# ANSI 颜色代码
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"


def run_command(cmd: List[str], cwd: Path) -> Tuple[bool, str]:
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)


def check_python_deps(project_path: Path) -> Dict:
    """检查 Python 项目依赖"""
    requirements_file = project_path / "requirements.txt"
    if not requirements_file.exists():
        return {"status": "no_requirements", "updates": []}

    print(f"\n{BLUE}检查 Python 依赖: {project_path.name}{RESET}")

    # 获取已安装包信息（使用简单格式）
    success, output = run_command(["pip", "list"], project_path)
    total = 0
    if success:
        # 解析 pip list 输出（跳过头部空行和标题）
        lines = output.strip().split('\n')
        total = len([line for line in lines if line and not line.startswith('Package')])

    # 获取过期的包
    success, output = run_command(["pip", "list", "--outdated", "--format=json"], project_path)
    updates = []

    if success:
        try:
            outdated = json.loads(output)
            for pkg in outdated:
                updates.append({
                    "package": pkg["name"],
                    "current": pkg["version"],
                    "latest": pkg["latest_version"],
                    "type": pkg["latest_filetype"]
                })
        except json.JSONDecodeError:
            pass  # 没有过时的包

    return {
        "status": "checked",
        "total": total,
        "outdated": len(updates),
        "updates": updates
    }


def check_node_deps(project_path: Path) -> Dict:
    """检查 Node.js 项目依赖"""
    package_json = project_path / "package.json"
    if not package_json.exists():
        return {"status": "no_package", "updates": []}

    print(f"\n{BLUE}检查 Node.js 依赖: {project_path.name}{RESET}")

    # 获取过时的包
    success, output = run_command(["npm", "outdated", "--json"], project_path)
    updates = []

    if success:
        try:
            outdated = json.loads(output)
            for name, info in outdated.items():
                updates.append({
                    "package": name,
                    "current": info.get("current", "unknown"),
                    "wanted": info.get("wanted", "unknown"),
                    "latest": info.get("latest", "unknown")
                })
        except json.JSONDecodeError:
            pass  # 没有过时的包时输出不是有效的 JSON

    # 获取总包数
    success, output = run_command(["npm", "list", "--json", "--depth=0"], project_path)
    total = 0
    if success:
        try:
            data = json.loads(output)
            total = len(data.get("dependencies", {}))
        except json.JSONDecodeError:
            pass

    return {
        "status": "checked",
        "total": total,
        "outdated": len(updates),
        "updates": updates
    }


def format_report(results: Dict) -> str:
    """格式化报告"""
    report = []
    report.append("=" * 80)
    report.append(f"依赖检查报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 80)

    total_updates = 0

    for project, data in results.items():
        report.append(f"\n{BLUE}项目: {project}{RESET}")
        report.append(f"  状态: {data['status']}")

        if data['status'] == 'checked':
            report.append(f"  总包数: {data['total']}")
            report.append(f"  需要更新: {data['outdated']}")

            if data['updates']:
                report.append(f"\n  {YELLOW}可用的更新:{RESET}")
                for update in data['updates']:
                    pkg = update['package']
                    current = update['current']
                    latest = update.get('latest', update.get('wanted', 'unknown'))

                    # 安全关键包标记
                    security_mark = ""
                    critical_packages = ['cryptography', 'httplib2', 'requests', 'urllib3', 'pyopenssl']
                    if pkg.lower() in critical_packages:
                        security_mark = f" {RED}[安全关键]{RESET}"

                    report.append(f"    {YELLOW}•{RESET} {pkg}: {current} → {latest}{security_mark}")
                    total_updates += 1
            else:
                report.append(f"  {GREEN}✓ 所有包都是最新版本{RESET}")

    report.append("\n" + "=" * 80)
    if total_updates > 0:
        report.append(f"{YELLOW}总计需要更新: {total_updates} 个包{RESET}")
    else:
        report.append(f"{GREEN}所有依赖都是最新版本！{RESET}")
    report.append("=" * 80)

    return "\n".join(report)


def save_report(report: str, output_path: Path):
    """保存报告到文件"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n{GREEN}报告已保存到: {output_path}{RESET}")


def main():
    """主函数"""
    clawd_path = Path("/root/clawd")

    # 定义要检查的项目
    projects = {
        "AlphaGPT": clawd_path / "AlphaGPT",
        "CarLife": clawd_path / "CarLife",
    }

    results = {}

    # 检查每个项目
    for project_name, project_path in projects.items():
        if not project_path.exists():
            print(f"{YELLOW}⚠ 项目不存在: {project_name}{RESET}")
            results[project_name] = {"status": "not_found", "updates": []}
            continue

        # 检查 Python 依赖
        py_result = check_python_deps(project_path)
        if py_result['status'] == 'checked':
            results[project_name] = py_result
            continue

        # 检查 Node.js 依赖
        node_result = check_node_deps(project_path)
        if node_result['status'] == 'checked':
            results[project_name] = node_result
            continue

        results[project_name] = {"status": "no_deps", "updates": []}

    # 生成报告
    report = format_report(results)
    print("\n" + report)

    # 保存报告
    report_dir = clawd_path / "reports" / "deps"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = report_dir / f"deps-check-{timestamp}.txt"
    save_report(report, report_path)

    # 保存最新报告
    latest_path = report_dir / "deps-check-latest.txt"
    save_report(report, latest_path)


if __name__ == "__main__":
    main()
