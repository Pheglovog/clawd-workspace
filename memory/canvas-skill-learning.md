# Canvas Skill 学习笔记 - 2026-02-08

## 概述

Canvas 是 OpenClaw 的一个可视化工具，允许在连接的节点上展示 HTML 内容。非常适合：

- 显示仪表板
- 展示游戏
- 交互式演示
- 实时数据可视化

## 架构

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Canvas Host   │────▶│   Node Bridge    │────▶│   Node App       │
│  (HTTP Server) │     │   (TCP Server)    │     │   (Mac/iOS/      │
│  Port 18793     │     │   Port 18790      │     │   Android)        │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### 组件

1. **Canvas Host Server**: 从 `canvasHost.root` 目录提供静态 HTML/CSS/JS 文件
2. **Node Bridge**: 将 canvas URL 传递给连接的节点
3. **Node Apps**: 在 WebView 中渲染内容

### 绑定模式

`gateway.bind` 设置决定了服务器如何绑定：

| 绑定模式 | 服务器绑定到 | Canvas URL 使用 |
|---------|------------|----------------|
| `loopback` | 127.0.0.1 | localhost (仅本地） |
| `lan` | LAN 接口 | LAN IP 地址 |
| `tailnet` | Tailscale 接口 | Tailscale 主机名 |
| `auto` | 最佳可用 | Tailscale > LAN > loopback |

**关键点**: 当绑定到 Tailscale 时，节点会收到类似这样的 URL：
```
http://<tailscale-hostname>:18793/__moltbot__/canvas/<file>.html
```

这就是为什么 localhost URL 不起作用——节点接收的是 Tailscale 主机名！

## Actions

| Action | 描述 |
|--------|--------|
| `present` | 显示 canvas（可选目标 URL） |
| `hide` | 隐藏 canvas |
| `navigate` | 导航到新的 URL |
| `eval` | 在 canvas 中执行 JavaScript |
| `snapshot` | 捕获 canvas 截图 |

## 配置

### 配置文件

`~/.openclaw/openclaw.json`:

```json
{
  "canvasHost": {
    "enabled": true,
    "port": 18793,
    "root": "/Users/you/clawd/canvas",
    "liveReload": true
  },
  "gateway": {
    "bind": "auto"
  }
}
```

### Live Reload

当 `liveReload: true` 时（默认）：

- Canvas host 监控根目录的变化（通过 chokidar）
- 向 HTML 文件中注入 WebSocket 客户端
- 当文件更改时，自动重新加载连接的 canvas
- 非常适合开发！

## 工作流程

### 1. 创建 HTML 内容

将文件放在 canvas root 目录中（默认 `~/clawd/canvas/`）：

```bash
cat > ~/clawd/canvas/my-game.html << 'HTML'
<!DOCTYPE html>
<html>
<head><title>My Game</title></head>
<body>
  <h1>Hello Canvas!</h1>
</body>
</html>
HTML
```

### 2. 查找你的 canvas host URL

检查你的网关是如何绑定的：

```bash
cat ~/.openclaw/openclaw.json | jq '.gateway.bind'
```

然后构建 URL：

- **loopback**: `http://127.0.0.1:18793/__moltbot__/canvas/<file>.html`
- **lan**: `http://<LAN IP>:18793/__moltbot__/canvas/<file>.html`
- **lan/tailnet/auto**: `http://<hostname>:18793/__moltbot__/canvas/<file>.html`

查找你的 Tailscale 主机名：

```bash
tailscale status --json | jq -r '.Self.DNSName' | sed 's/\.$//'
```

### 3. 查找连接的节点

```bash
openclaw nodes list
```

查找具有 canvas 能力的 Mac/iOS/Android 节点。

### 4. 展示内容

```bash
canvas action:present node:<node-id> target:<full-url>
```

**示例**:

```bash
canvas action:present node:mac-63599bc4-b54d-4392-9048-b97abd58343a target:http://peters-mac-studio-1.sheep-coho.ts.net:18793/__moltbot__/canvas/snake.html
```

### 5. 导航、截图或隐藏

```bash
canvas action:navigate node:<node-id> url:<new-url>
canvas action:snapshot node:<node-id>
canvas action:hide node:<node-id>
```

## 调试

### 白屏 / 内容未加载

**原因**: 服务器绑定与节点预期之间的 URL 不匹配。

**调试步骤**:

1. 检查服务器绑定：`cat ~/.openclaw/openclaw.json | jq '.gateway.bind'`
2. 检查 canvas 端口：`lsof -i :18793`
3. 直接测试 URL：`curl http://<hostname>:18793/__moltbot__/canvas/<file>.html`

**解决方案**: 使用与你的绑定模式匹配的完整主机名，而非 localhost。

### "node required" 错误

始终指定 `node:<node-id>` 参数。

### "node not connected" 错误

节点离线。使用 `openclaw nodes list` 查找在线节点。

### 内容未更新

如果 live reload 没有工作：

1. 检查配置中 `liveReload: true`
2. 确保文件在 canvas root 目录中
3. 查看日志中的 watcher 错误

## URL 路径结构

Canvas host 服务从 `/__moltbot__/canvas/` 前缀提供服务：

```
http://<host>:18793/__moltbot__/canvas/index.html  → ~/clawd/canvas/index.html
http://<host>:18793/__moltbot__/canvas/games/snake.html  → ~/clawd/canvas/games/snake.html
```

`/__moltbot__/canvas/` 前缀由 `CANVAS_HOST_PATH` 常量定义。

## 提示

- 保持 HTML 自包含（内联 CSS/JS）以获得最佳结果
- 使用默认 index.html 作为测试页（具有桥接诊断）
- Live reload 使开发变得快速——只需保存，它就会更新！
- Canvas 会保持显示，直到你 `hide` 它或导航离开
- A2UI JSON 推送已被弃用——现在使用 HTML 文件

## 应用场景

### 1. 数据可视化仪表板

为 AlphaGPT 创建可视化仪表板：

```html
<!DOCTYPE html>
<html>
<head>
  <title>AlphaGPT Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
  <h1>AlphaGPT Dashboard</h1>
  <canvas id="myChart"></canvas>
  <script>
    const ctx = document.getElementById('myChart').getContext('2d');
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
        datasets: [{
          label: '收益',
          data: [12, 19, 3, 5, 2],
          borderColor: 'rgb(75, 192, 192)',
          tension: 0.1
        }]
      }
    });
  </script>
</body>
</html>
```

### 2. 交互式游戏

使用 Canvas 展示游戏：

```html
<!DOCTYPE html>
<html>
<head>
  <title>Snake Game</title>
  <style>
    body { margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; background: #1a1a1a; }
    canvas { background: #000; border: 2px solid #333; }
  </style>
</head>
<body>
  <canvas id="gameCanvas" width="400" height="400"></canvas>
  <script>
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');

    // Snake game logic
    let snake = [{x: 200, y: 200}];
    let dx = 10, dy = 0;
    let food = {x: 100, y: 100};

    function draw() {
      ctx.fillStyle = '#000';
      ctx.fillRect(0, 0, 400, 400);

      ctx.fillStyle = '#0f0';
      snake.forEach(segment => ctx.fillRect(segment.x, segment.y, 10, 10));

      ctx.fillStyle = '#f00';
      ctx.fillRect(food.x, food.y, 10, 10);
    }

    function update() {
      const head = {x: snake[0].x + dx, y: snake[0].y + dy};
      snake.unshift(head);

      if (head.x === food.x && head.y === food.y) {
        food = {x: Math.floor(Math.random() * 40) * 10, y: Math.floor(Math.random() * 40) * 10};
      } else {
        snake.pop();
      }

      if (head.x < 0 || head.x >= 400 || head.y < 0 || head.y >= 400) {
        snake = [{x: 200, y: 200}];
        dx = 10; dy = 0;
      }
    }

    setInterval(() => { update(); draw(); }, 100);

    document.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowUp') { dx = 0; dy = -10; }
      if (e.key === 'ArrowDown') { dx = 0; dy = 10; }
      if (e.key === 'ArrowLeft') { dx = -10; dy = 0; }
      if (e.key === 'ArrowRight') { dx = 10; dy = 0; }
    });
  </script>
</body>
</html>
```

### 3. 实时数据监控

使用 Live Reload 实现实时更新：

```javascript
// Injected by canvas host
const ws = new WebSocket('ws://canvas-host:18793/__moltbot__/ws');

ws.onmessage = (event) => {
  if (event.type === 'reload') {
    location.reload();
  }
};

// Custom data update
ws.send(JSON.stringify({ type: 'get_data' }));

ws.onmessage = (event) => {
  if (event.type === 'data') {
    updateDashboard(event.data);
  }
};
```

## 学习资源

- [Canvas SKILL.md](/root/clawd/openclaw/skills/canvas/SKILL.md)
- [OpenClaw Docs](https://docs.openclaw.ai)
- [OpenClaw Skills](https://github.com/VoltAgent/awesome-openclaw-skills)

## 总结

Canvas 是一个功能强大的可视化工具，特别适合：
- 开发交互式仪表板
- 展示游戏和演示
- 实时数据可视化
- 快速原型设计

Live Reload 功能使开发变得极其高效——只需保存，它就会更新！

---

*研究时间: 2026-02-08*
*用途: Canvas Skill 学习笔记*
