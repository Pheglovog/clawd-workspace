# Canvas Apps - OpenClaw Canvas 应用集合

> 创建时间：2026-02-12
> 位置：/root/clawd/canvas/

---

## 目录

1. [关于 Canvas Apps](#关于-canvas-apps)
2. [应用列表](#应用列表)
3. [如何使用](#如何使用)
4. [开发指南](#开发指南)
5. [Live Reload](#live-reload)

---

## 关于 Canvas Apps

Canvas Apps 是运行在 OpenClaw Canvas 上的交互式 Web 应用。Canvas 是 OpenClaw 的 UI 呈现层，允许你在浏览器中展示数据可视化、仪表板、Demo 等。

### 特性

- ✨ **Live Reload**：代码修改后自动刷新
- 🎨 **现代 UI**：使用最新的 CSS 和 JavaScript
- 📊 **数据可视化**：支持 Chart.js、Three.js 等库
- 🚀 **快速开发**：无需构建步骤，直接运行 HTML/CSS/JS
- 📱 **响应式设计**：支持桌面和移动设备

---

## 应用列表

### 1. AlphaGPT Dashboard

**文件：** `apps/alphagpt-dashboard.html`

**描述：** AlphaGPT 中国股市量化系统的实时监控仪表板

**功能：**
- 📈 权益曲线对比（AlphaGPT vs 沪深300）
- 📊 因子重要性分析
- 📅 月度收益分布
- 🎯 行业配置饼图
- 📊 交易统计（胜率、盈亏比）
- ⚡ 风险指标（波动率、Beta、Alpha）
- 🔮 模型状态和当前信号

**技术栈：**
- HTML5 + CSS3
- Chart.js 4.4.0
- 响应式设计

**访问方式：**
```bash
# 在 Canvas 中展示
canvas present --file canvas/apps/alphagpt-dashboard.html
```

---

### 2. CarLife Demo

**文件：** `apps/carlife-demo.html`

**描述：** CarLife 区块链汽车生活平台的交互式 Demo

**功能：**
- 🔗 车辆 NFT 系统展示
- 📋 服务注册系统
- 💰 数据 Token 化
- 🛡️ 隐私保护机制
- ⚡ Gas 优化展示
- 🐛 安全审计状态
- 🎫 NFT 车辆卡片展示
- ⚙️ 技术栈展示

**技术栈：**
- HTML5 + CSS3
- Three.js 0.160.0（3D 效果）
- 渐变动画
- 鼠标交互效果

**访问方式：**
```bash
# 在 Canvas 中展示
canvas present --file canvas/apps/carlife-demo.html
```

---

### 3. DeFi Yield Calculator

**文件：** `apps/defi-yield-calculator.html`

**描述：** DeFi 收益率计算器

**功能：**
- 📊 APY/APR 计算
- 💰 复利计算
- ⏰ 时间周期选择
- 📈 收益曲线展示

**技术栈：**
- HTML5 + CSS3
- JavaScript

**访问方式：**
```bash
# 在 Canvas 中展示
canvas present --file canvas/apps/defi-yield-calculator.html
```

---

### 4. Learning Tracker

**文件：** `apps/learning-tracker.html`

**描述：** 学习进度追踪器

**功能：**
- 📊 学习时间统计
- 🎯 目标进度
- 📅 每日学习记录
- 🏆 成就系统

**技术栈：**
- HTML5 + CSS3
- Chart.js
- LocalStorage

**访问方式：**
```bash
# 在 Canvas 中展示
canvas present --file canvas/apps/learning-tracker.html
```

### 5. CarLife Dashboard (2026-02-20)

**文件：** `carlife-dashboard.html`

**描述：** CarLife 项目实时监控仪表板

**功能：**
- 📊 项目统计卡片（测试覆盖率、AA 测试、Gas 优化、安全扫描）
- 📈 项目进度（85% 完成进度条）
- ✅ 测试结果展示（7 个测试套件）
- 🎨 NFT 预览（4 个模拟 Car NFT）
- 🔜 即将推出功能（跨链、Gasless、会话密钥、社交恢复、动态 NFT）

**技术栈：**
- HTML5 + CSS3
- 渐变背景（蓝紫色）
- 卡片悬停动画
- 进度条动画
- 状态指示器脉冲动画

**访问方式：**
```bash
# 在 Canvas 中展示
canvas present --file canvas/carlife-dashboard.html
```

### 6. AlphaGPT Dashboard (2026-02-20)

**文件：** `alphagpt-dashboard.html`

**描述：** AlphaGPT 量化交易系统可视化界面

**功能：**
- 📦 数据覆盖（5000+ 股票，Tushare Pro 2000 积分）
- ⚡ 性能基准（数据加载 10x、因子计算 100x、内存 -50%）
- 🧮 技术因子（SMA、RSI、MACD、BOLL、KDJ、ATR）
- 🔗 系统模块（6 个核心模块）
- 📊 数据可视化（股价图表、因子信号、回测收益）
- 🔗 API 状态（Tushare Pro API 在线）

**技术栈：**
- HTML5 + CSS3
- 渐变背景（粉橙色）
- 响应式布局
- 实时时间更新

**访问方式：**
```bash
# 在 Canvas 中展示
canvas present --file canvas/alphagpt-dashboard.html
```

---

## 如何使用

### 方法 1：使用 OpenClaw Canvas CLI

```bash
# 显示应用
canvas present --file canvas/apps/alphagpt-dashboard.html

# 指定 Canvas 尺寸
canvas present --file canvas/apps/carlife-demo.html --width 1280 --height 720

# 生成截图
canvas snapshot --output snapshot.png
```

### 方法 2：通过 OpenClaw Skills

```bash
# 使用 canvas skill
canvas present --target <node-id> --file canvas/apps/alphagpt-dashboard.html
```

### 方法 3：直接在浏览器中打开

所有 Canvas Apps 都是纯 HTML/CSS/JS，可以直接在浏览器中打开：

```bash
# 使用 Python HTTP 服务器
python -m http.server 8000

# 或使用 Node.js
npx serve canvas

# 然后在浏览器中打开
# http://localhost:8000/apps/alphagpt-dashboard.html
```

---

## 开发指南

### 创建新的 Canvas App

#### 1. 创建 HTML 文件

```bash
# 创建新应用
touch canvas/apps/my-app.html
```

#### 2. 基础模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My App</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #ffffff;
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>My Canvas App</h1>
        <!-- 你的内容 -->
    </div>

    <script>
        // 你的 JavaScript 代码
        console.log('Canvas App loaded!');
    </script>
</body>
</html>
```

#### 3. 添加样式

推荐使用现代 CSS 特性：

```css
/* 渐变背景 */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* 卡片效果 */
.card {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 20px;
    backdrop-filter: blur(10px);
}

/* 动画 */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.fade-in {
    animation: fadeIn 0.5s ease;
}
```

#### 4. 添加交互

```javascript
// DOM 操作
const button = document.querySelector('button');
button.addEventListener('click', () => {
    console.log('Button clicked!');
});

// 获取 API 数据
async function fetchData() {
    const response = await fetch('https://api.example.com/data');
    const data = await response.json();
    console.log(data);
}

// 更新 UI
function updateUI(data) {
    document.querySelector('.value').textContent = data.value;
}

// 定时更新
setInterval(() => {
    fetchData().then(updateUI);
}, 5000); // 每 5 秒更新
```

---

## Live Reload

### 什么是 Live Reload？

Live Reload 是一个功能，当 Canvas App 的代码修改后，自动刷新页面。

### 如何启用

#### 方法 1：使用 Canvas CLI

```bash
# 启动带 Live Reload 的服务器
canvas serve --file canvas/apps/alphagpt-dashboard.html --reload

# 修改文件后，页面会自动刷新
```

#### 方法 2：使用浏览器扩展

1. 安装 LiveReload 扩展：
   - Chrome: https://chrome.google.com/webstore/detail/livereload/jnihajbhpnppcggbcgagniiblbdjg
   - Firefox: https://addons.mozilla.org/en-US/firefox/addon/livereload/

2. 在 HTML 中添加 LiveReload 脚本：

```html
<script src="http://localhost:35729/livereload.js?snipver=1"></script>
```

3. 修改文件后，浏览器会自动刷新

#### 方法 3：手动刷新

最简单的方式是保存文件后手动刷新浏览器（F5 或 Cmd+R）。

### Live Reload 指示器

在所有 Canvas Apps 中，你可以看到 Live Reload 状态指示器：

```html
<div class="live-indicator">
    <div class="live-dot"></div>
    <span>Live Reload Enabled</span>
</div>
```

样式：

```css
.live-indicator {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: rgba(0, 255, 136, 0.9);
    color: #0a0a0a;
    padding: 10px 20px;
    border-radius: 25px;
    font-size: 14px;
    font-weight: bold;
    display: flex;
    align-items: center;
    gap: 8px;
    box-shadow: 0 5px 20px rgba(0, 255, 136, 0.3);
}

.live-dot {
    width: 10px;
    height: 10px;
    background: #ff0000;
    border-radius: 50%;
    animation: pulse 1s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(1.2); }
}
```

---

## 最佳实践

### 1. 响应式设计

```css
/* 使用 CSS Grid 和 Flexbox */
.container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
}

/* 移动设备适配 */
@media (max-width: 768px) {
    .container {
        grid-template-columns: 1fr;
    }
}
```

### 2. 性能优化

```javascript
// 使用 requestAnimationFrame
function animate() {
    requestAnimationFrame(animate);
}

// 防抖和节流
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

// 懒加载图片
const lazyImages = document.querySelectorAll('img.lazy');
lazyImages.forEach(img => {
    img.addEventListener('load', () => {
        img.classList.remove('lazy');
    });
});
```

### 3. 错误处理

```javascript
// try-catch
try {
    const data = JSON.parse(response);
} catch (error) {
    console.error('JSON parse error:', error);
}

// 错误边界
window.onerror = function(message, source, lineno, colno, error) {
    console.error('Error:', message);
};

// Promise 错误处理
fetch(url)
    .then(response => response.json())
    .catch(error => console.error('Fetch error:', error));
```

### 4. 可访问性

```html
<!-- 语义化 HTML -->
<header>
    <nav>
        <ul>
            <li><a href="#section1">Section 1</a></li>
        </ul>
    </nav>
</header>

<main>
    <section id="section1">
        <h1>Section 1</h1>
        <p>Content</p>
    </section>
</main>

<footer>
    <p>&copy; 2026 Pheglovog</p>
</footer>

<!-- ARIA 标签 -->
<button aria-label="Close" onclick="closeModal()">
    <span aria-hidden="true">&times;</span>
</button>
```

---

## 资源链接

### 学习资源
- [MDN Web Docs](https://developer.mozilla.org/)
- [Chart.js Documentation](https://www.chartjs.org/docs/latest/)
- [Three.js Documentation](https://threejs.org/docs/)

### 工具
- [OpenClaw Canvas](https://docs.openclaw.ai/tools/canvas)
- [CodePen](https://codepen.io/)
- [JSFiddle](https://jsfiddle.net/)

### 设计灵感
- [Dribbble](https://dribbble.com/)
- [Behance](https://www.behance.net/)
- [Awwwards](https://www.awwwards.com/)

---

## 常见问题

### Q: 如何调试 Canvas App？

A: 使用浏览器的开发者工具（F12）：
- Elements：检查 HTML/CSS
- Console：查看日志和错误
- Network：检查网络请求
- Sources：断点调试 JavaScript

### Q: 如何添加外部库？

A: 使用 CDN：

```html
<!-- Chart.js -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>

<!-- Three.js -->
<script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>

<!-- Ethers.js -->
<script src="https://cdn.jsdelivr.net/npm/ethers@6.9.0/dist/ethers.umd.min.js"></script>
```

### Q: 如何与 OpenClaw 集成？

A: 使用 OpenClaw API：

```javascript
// 获取 Canvas 状态
fetch('/api/canvas/status')
    .then(res => res.json())
    .then(data => console.log(data));

// 发送事件到 OpenClaw
fetch('/api/canvas/event', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ type: 'click', data: { button: 'submit' } })
});
```

---

## 贡献指南

### 添加新应用

1. 在 `canvas/apps/` 目录下创建新的 HTML 文件
2. 更新本 README，添加应用说明
3. 确保应用在不同浏览器中正常运行
4. 提交 Pull Request

### 代码规范

- 使用 4 空格缩进
- CSS 使用 BEM 命名规范
- JavaScript 使用 ES6+ 语法
- 添加注释说明复杂逻辑

---

## 更新日志

### 2026-02-12
- ✅ 添加 AlphaGPT Dashboard
- ✅ 添加 CarLife Demo
- ✅ 添加 DeFi Yield Calculator
- ✅ 添加 Learning Tracker
- ✅ 创建 Canvas Apps README

---

**文档维护者：吕布（上等兵•甘的AI助手）**
**最后更新：2026-02-12**
