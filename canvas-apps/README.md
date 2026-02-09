# Canvas Skill 应用开发示例

**项目**: OpenClaw Canvas 应用演示
**创建时间**: 2026-02-09

---

## 目录

1. [项目结构](#项目结构)
2. [应用列表](#应用列表)
3. [部署指南](#部署指南)
4. [使用说明](#使用说明)
5. [开发指南](#开发指南)

---

## 项目结构

```
canvas-apps/
├── alphagpt-dashboard/    # AlphaGPT 量化交易仪表板
│   └── index.html
├── games/                # 游戏集合
│   ├── snake.html        # 贪吃蛇游戏
│   └── ...
└── README.md             # 本文档
```

---

## 应用列表

### 1. AlphaGPT 量化交易仪表板

**文件**: `alphagpt-dashboard/index.html`

**功能**:
- 📊 实时资产监控
- 📈 收益曲线可视化
- 📋 持仓详情展示
- 🎯 关键指标卡片
- 💹 资产配置饼图
- ⚡ 交易频率分析

**特色**:
- 响应式设计
- 自动刷新（30 秒）
- 渐变色彩主题
- Chart.js 数据可视化

**预览**:
```
总收益率: +24.5%
总资产: ¥1,245,678
活跃仓位: 8
夏普比率: 2.34
最大回撤: -5.2%
胜率: 68.5%
```

### 2. 贪吃蛇游戏

**文件**: `games/snake.html`

**功能**:
- 🐍 经典贪吃蛇玩法
- 🎮 键盘 + 触摸控制
- 💾 高分记录（本地存储）
- 🚀 渐进式难度
- 📊 实时分数显示

**控制方式**:
- 键盘: 方向键或 WASD
- 触摸: 屏幕控制按钮

**特色**:
- 响应式设计（适配移动端）
- 渐进加速机制
- 视觉特效（蛇身、眼睛、食物光泽）
- 网格背景装饰

---

## 部署指南

### 方法 1: 使用 OpenClaw Canvas Host

#### 步骤 1: 配置 Canvas Host

编辑 `~/.openclaw/openclaw.json`:

```json
{
  "canvasHost": {
    "enabled": true,
    "port": 18793,
    "root": "/root/clawd/canvas-apps",
    "liveReload": true
  },
  "gateway": {
    "bind": "auto"
  }
}
```

#### 步骤 2: 重启 OpenClaw Gateway

```bash
openclaw gateway restart
```

#### 步骤 3: 获取 Canvas URL

检查网关绑定模式：

```bash
cat ~/.openclaw/openclaw.json | jq '.gateway.bind'
```

根据绑定模式构建 URL：

| 绑定模式 | URL 格式 |
|---------|---------|
| `loopback` | `http://127.0.0.1:18793/__moltbot__/canvas/alphagpt-dashboard/index.html` |
| `lan` | `http://<LAN IP>:18793/__moltbot__/canvas/alphagpt-dashboard/index.html` |
| `tailscale`/`auto` | `http://<hostname>:18793/__moltbot__/canvas/alphagpt-dashboard/index.html` |

获取 Tailscale 主机名：

```bash
tailscale status --json | jq -r '.Self.DNSName' | sed 's/\.$//'
```

#### 步骤 4: 查找连接的节点

```bash
openclaw nodes list
```

查找具有 `canvas` 能力的节点（通常是 Mac 或 Android）。

#### 步骤 5: 展示 Canvas

```bash
# 节点 ID
NODE_ID="your-node-id"

# Canvas URL
CANVAS_URL="http://your-hostname:18793/__moltbot__/canvas/alphagpt-dashboard/index.html"

# 展示
openclaw canvas action:present node:$NODE_ID target:$CANVAS_URL
```

### 方法 2: 直接访问（本地测试）

```bash
# 启动简单的 HTTP 服务器
cd /root/clawd/canvas-apps
python3 -m http.server 8000

# 访问
open http://localhost:8000/alphagpt-dashboard/index.html
open http://localhost:8000/games/snake.html
```

---

## 使用说明

### AlphaGPT 仪表板

#### 功能说明

**1. 关键指标卡片**
- 总收益率: 显示策略整体表现
- 总资产: 当前持仓总价值
- 活跃仓位: 当前持有的股票数量
- 夏普比率: 风险调整后收益指标
- 最大回撤: 最大亏损百分比
- 胜率: 盈利交易占比

**2. 图表说明**
- 资产曲线: 展示资产增长趋势
- 收益分布: 各只股票盈亏情况
- 资产配置: 持仓占比分析
- 交易频率: 每日交易次数

**3. 持仓表格**
- 显示当前所有持仓
- 实时计算盈亏和盈亏率
- 状态指示（盈利/亏损）

#### 交互方式

- **自动刷新**: 每 30 秒自动更新数据
- **手动刷新**: 点击刷新按钮立即更新
- **悬停查看**: 鼠标悬停查看详细数据

### 贪吃蛇游戏

#### 游戏规则

1. 使用方向键或 WASD 控制蛇的移动
2. 吃到红色食物得分（+10 分）
3. 每 50 分加速一次
4. 撞墙或撞到自己游戏结束
5. 按空格键重新开始

#### 技巧

- **预判路径**: 不要盲目追食物
- **控制节奏**: 不要频繁转向
- **利用空间**: 充分利用角落区域
- **渐进加速**: 适应节奏后再追求高分

---

## 开发指南

### 创建新的 Canvas 应用

#### 步骤 1: 创建 HTML 文件

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>My Canvas App</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #1a1a2e;
            color: #e0e0e0;
            padding: 20px;
        }
    </style>
</head>
<body>
    <h1>Hello Canvas!</h1>
    <p>This is my first canvas app.</p>
</body>
</html>
```

#### 步骤 2: 保存到 canvas-apps 目录

```bash
mkdir /root/clawd/canvas-apps/my-app
vim /root/clawd/canvas-apps/my-app/index.html
```

#### 步骤 3: 测试应用

```bash
# 本地测试
python3 -m http.server 8000
open http://localhost:8000/my-app/index.html

# 使用 Canvas Host 展示
openclaw canvas action:present node:$NODE_ID target:$CANVAS_URL
```

### 使用 JavaScript 库

#### Chart.js (数据可视化)

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<canvas id="myChart"></canvas>
<script>
    const ctx = document.getElementById('myChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar'],
            datasets: [{
                label: 'Sales',
                data: [10, 20, 30],
                borderColor: '#4facfe'
            }]
        }
    });
</script>
```

#### D3.js (复杂可视化)

```html
<script src="https://d3js.org/d3.v7.min.js"></script>
<div id="chart"></div>
<script>
    const svg = d3.select("#chart")
        .append("svg")
        .attr("width", 400)
        .attr("height", 400);

    svg.append("circle")
        .attr("cx", 200)
        .attr("cy", 200)
        .attr("r", 50)
        .style("fill", "#4facfe");
</script>
```

### 实现实时更新

#### 方法 1: 轮询更新

```javascript
setInterval(() => {
    fetch('/api/data')
        .then(response => response.json())
        .then(data => updateDashboard(data));
}, 30000);
```

#### 方法 2: WebSocket 实时推送

```javascript
const ws = new WebSocket('ws://your-server:port/ws');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    updateDashboard(data);
};

function updateDashboard(data) {
    // 更新图表和表格
}
```

### Live Reload 功能

当 `liveReload: true` 时：

1. Canvas Host 监控文件变化
2. 自动向 HTML 注入 WebSocket 客户端
3. 文件更改时自动刷新
4. 极大提升开发效率

**注意**: 确保 HTML 文件在 `canvas root` 目录中。

---

## Canvas Actions

### 展示 Canvas

```bash
openclaw canvas action:present node:<node-id> target:<url>
```

### 隐藏 Canvas

```bash
openclaw canvas action:hide node:<node-id>
```

### 导航到新 URL

```bash
openclaw canvas action:navigate node:<node-id> url:<new-url>
```

### 执行 JavaScript

```bash
openclaw canvas action:eval node:<node-id> javascript:<code>
```

### 捕获截图

```bash
openclaw canvas action:snapshot node:<node-id>
```

---

## 常见问题

### Q1: Canvas 显示白屏

**A**: 检查以下几点：

1. 检查服务器绑定模式
   ```bash
   cat ~/.openclaw/openclaw.json | jq '.gateway.bind'
   ```

2. 使用正确的 URL 格式
   - 不要使用 `localhost`
   - 使用完整的主机名（Tailscale 主机名）

3. 直接测试 URL
   ```bash
   curl http://your-hostname:18793/__moltbot__/canvas/index.html
   ```

### Q2: 文件更新后 Canvas 没有刷新

**A**:

1. 检查 `liveReload` 是否启用
   ```bash
   cat ~/.openclaw/openclaw.json | jq '.canvasHost.liveReload'
   ```

2. 确保文件在 `canvas root` 目录中

3. 查看 Canvas Host 日志

### Q3: 如何获取 Tailscale 主机名？

**A**:

```bash
tailscale status --json | jq -r '.Self.DNSName' | sed 's/\.$//'
```

### Q4: 如何调试 Canvas 应用？

**A**:

1. 使用浏览器开发者工具
2. 查看 Console 日志
3. 检查 Network 请求
4. 使用 `alert()` 或 `console.log()` 调试

---

## 参考资源

### OpenClaw 文档

- [Canvas 文档](https://docs.openclaw.ai/platforms/mac/canvas)
- [OpenClaw 总文档](https://docs.openclaw.ai)
- [GitHub 仓库](https://github.com/openclaw/openclaw)

### Web 开发资源

- [Chart.js](https://www.chartjs.org/)
- [D3.js](https://d3js.org/)
- [MDN Web Docs](https://developer.mozilla.org/)

### Canvas 技能

- [Canvas SKILL.md](/root/clawd/openclaw/skills/canvas/SKILL.md)
- [Canvas 学习笔记](/root/clawd/memory/canvas-skill-learning.md)

---

## 总结

本仓库提供了两个完整的 Canvas Skill 应用示例：

1. **AlphaGPT 仪表板**: 数据可视化仪表板
2. **贪吃蛇游戏**: 交互式游戏应用

通过这些示例，你可以学习：
- Canvas 基础配置和部署
- HTML/CSS/JavaScript 开发
- 数据可视化技术
- 游戏开发基础
- 实时数据更新

继续探索 Canvas Skill 的更多可能性！

---

**项目版本**: 1.0.0
**创建时间**: 2026-02-09
**最后更新**: 2026-02-09
