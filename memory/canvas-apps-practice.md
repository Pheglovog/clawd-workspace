# Canvas 应用开发实践 - 2026-02-10

## 概述

基于之前对 Canvas Skill 的学习，实际创建了两个可视化应用：
1. AlphaGPT Dashboard - 量化系统仪表板
2. CarLife Demo - 区块链汽车平台展示

## 创建的应用

### 1. AlphaGPT Dashboard

**文件**: `/root/clawd/canvas/apps/alphagpt-dashboard.html`

**功能模块**:
- 统计卡片：因子维度（24）、夏普比率（2.35）、年化收益率（45.8%）、最大回撤（-8.2%）
- 权益曲线：对比 AlphaGPT 和沪深300 的收益走势
- 因子重要性：展示 RSI、MACD、布林带、ATR、KDJ、北向资金、融资融券、动量等因子的权重
- 月度收益：柱状图展示每月收益率，正收益绿色、负收益红色
- 行业配置：甜甜圈图展示科技、消费、医药、金融、制造、能源、其他行业的占比
- 交易统计：总交易次数、胜率（58.3%）、平均盈利（+2.45%）、平均亏损（-1.82%）、盈亏比（1.35）
- 风险指标：波动率（18.5%）、Beta（0.87）、Alpha（12.3%）、信息比率（1.45）、VaR（-3.2%）
- 模型状态：模型版本、最后训练时间、训练数据量、当前信号、信号强度

**技术特点**:
- Chart.js 数据可视化
- 渐变色和玻璃态设计
- 响应式布局（适配移动端）
- 实时时间更新

### 2. CarLife Demo

**文件**: `/root/clawd/canvas/apps/carlife-demo.html`

**功能模块**:
- 核心功能展示：6大特性（车辆 NFT、服务注册、数据 Token 化、隐私保护、Gas 优化、安全审计）
- 统计数据：31 测试用例、6 智能合约、0 Solhint 警告、100% 测试通过率
- 车辆 NFT 示例：Tesla Model S、BMW X5、Mazda CX-5（包含 VIN、年份、里程、状况）
- 技术栈展示：Solidity、Hardhat、OpenZeppelin、Ethers.js、ERC721 等
- 交互式动效：卡片悬停、渐变动画、鼠标跟随背景
- CTA 区域：引导用户了解更多

**技术特点**:
- 动态渐变标题
- 卡片悬停效果
- 滚动入场动画
- 鼠标移动背景变化
- Live Reload 支持

### 3. Canvas Apps README

**文件**: `/root/clawd/canvas/apps/README.md`

**内容**:
- 应用列表和功能说明
- 详细的使用指南
- 命令示例
- 开发最佳实践
- 故障排除
- 学习资源链接

## 技术实现

### HTML 结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>App Title</title>
    <!-- 外部资源 -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        /* 内联 CSS */
    </style>
</head>
<body>
    <!-- 页面内容 -->
    <script>
        // 内联 JavaScript
    </script>
</body>
</html>
```

### CSS 设计模式

#### 1. 渐变背景
```css
background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
```

#### 2. 玻璃态效果
```css
background: rgba(255, 255, 255, 0.05);
backdrop-filter: blur(10px);
border: 1px solid rgba(255, 255, 255, 0.1);
```

#### 3. 渐变文字
```css
background: linear-gradient(90deg, #00d4ff, #7b2cbf);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
background-clip: text;
```

#### 4. 悬停动画
```css
transition: all 0.3s ease;
transform: translateY(-5px);
box-shadow: 0 10px 30px rgba(0, 212, 255, 0.2);
```

### JavaScript 交互

#### 1. Chart.js 图表
```javascript
const ctx = document.getElementById('chart').getContext('2d');
new Chart(ctx, {
    type: 'line',
    data: { ... },
    options: { ... }
});
```

#### 2. 实时更新
```javascript
setInterval(() => {
    document.getElementById('updateTime').textContent = new Date().toLocaleString('zh-CN');
}, 1000);
```

#### 3. 滚动动画
```javascript
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, { threshold: 0.1 });
```

## 开发经验总结

### 1. 设计原则

- **简洁明了**: 避免过度设计，聚焦核心功能
- **响应式布局**: 确保在不同设备上都能正常显示
- **性能优化**: 减少外部资源，内联 CSS/JS
- **视觉一致性**: 统一的颜色、字体、间距

### 2. Chart.js 最佳实践

- 使用 CDN 加载最新版本
- 配置全局颜色和样式
- 使用合适的图表类型
- 添加图例和标签
- 响应式配置（maintainAspectRatio: false）

### 3. 动画效果

- 使用 CSS transition 实现平滑过渡
- 使用 CSS animation 实现持续动画
- 使用 JavaScript 实现复杂交互
- 避免过多动画影响性能

### 4. Live Reload 开发流程

1. 创建/修改 HTML 文件
2. 保存文件
3. Canvas 自动重新加载
4. 查看效果
5. 重复步骤 2-4

## 使用指南

### 展示 Canvas 应用

```bash
# 1. 查找节点
openclaw nodes list

# 2. 展示应用
canvas action:present node:<node-id> target:http://<hostname>:18793/__moltbot__/canvas/apps/alphagpt-dashboard.html

# 3. 隐藏应用
canvas action:hide node:<node-id>

# 4. 截图
canvas action:snapshot node:<node-id>
```

### 查找 Canvas Host URL

```bash
# 检查绑定模式
cat ~/.openclaw/openclaw.json | jq '.gateway.bind'

# 查找 Tailscale 主机名
tailscale status --json | jq -r '.Self.DNSName' | sed 's/\.$//'

# 组合 URL
# loopback: http://127.0.0.1:18793
# lan: http://<LAN IP>:18793
# tailnet: http://<hostname>.ts.net:18793
```

## 未来改进方向

### 1. AlphaGPT Dashboard
- 连接真实数据 API
- 添加实时数据更新
- 增加更多技术指标
- 添加策略回测功能

### 2. CarLife Demo
- 添加 3D 车辆模型（Three.js）
- 实现交互式 NFT 浏览
- 添加服务预约功能
- 集成钱包连接

### 3. 新应用创意
- 项目进度追踪器
- 任务管理看板
- 代码质量监控
- Git 提交可视化

## 学习资源

- [Chart.js 文档](https://www.chartjs.org/docs/)
- [CSS Gradient Generator](https://cssgradient.io/)
- [Glassmorphism Generator](https://glassmorphism.com/)
- [OpenClaw Canvas Docs](https://docs.openclaw.ai)

---

*创建时间: 2026-02-10 07:00*
*用途: Canvas 应用开发实践记录*
