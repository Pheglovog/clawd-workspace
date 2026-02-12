# Canvas Apps - OpenClaw 可视化应用

本目录包含 OpenClaw Canvas 的可视化应用示例。

## 应用列表

### 1. AlphaGPT Dashboard
- 文件: `alphagpt-dashboard.html`
- 用途: AlphaGPT 量化系统的可视化仪表板
- 功能: 权益曲线、因子分析、月度收益、交易统计等

### 2. CarLife Demo
- 文件: `carlife-demo.html`
- 用途: CarLife 区块链汽车生活平台的展示页面
- 功能: 核心功能展示、统计数据、车辆 NFT 示例

### 3. DeFi 收益计算器
- 文件: `defi-yield-calculator.html`
- 用途: DeFi 协议收益计算和预测
- 功能:
  - 支持多种 DeFi 协议（Curve、Aave、Uniswap、Compound）
  - 实时计算收益、手续费、净收益
  - 收益增长趋势图表
  - 收益构成分析
  - 热门收益池展示

### 4. 学习进度追踪器
- 文件: `learning-tracker.html`
- 用途: DeFi 区块链学习成果可视化
- 功能:
  - 学习统计概览（小时、字数、协议数、合约数）
  - 学习时长趋势
  - 字数增长趋势
  - 研究方向雷达图
  - 各主题进度追踪

## 如何使用

### 1. 查找节点
```bash
openclaw nodes list
```

### 2. 展示应用
```bash
# AlphaGPT Dashboard
canvas action:present node:<node-id> target:http://<hostname>:18793/__moltbot__/canvas/apps/alphagpt-dashboard.html

# CarLife Demo
canvas action:present node:<node-id> target:http://<hostname>:18793/__moltbot__/canvas/apps/carlife-demo.html

# DeFi 收益计算器
canvas action:present node:<node-id> target:http://<hostname>:18793/__moltbot__/canvas/apps/defi-yield-calculator.html

# 学习进度追踪器
canvas action:present node:<node-id> target:http://<hostname>:18793/__moltbot__/canvas/apps/learning-tracker.html
```

### 3. 其他操作
```bash
canvas action:hide node:<node-id>
canvas action:snapshot node:<node-id>
```

## Live Reload

Canvas Host 默认启用 Live Reload，修改 HTML 文件后自动重新加载。

## 开发新应用

在本目录创建新的 HTML 文件即可，支持实时预览。

---

*最后更新: 2026-02-10*
