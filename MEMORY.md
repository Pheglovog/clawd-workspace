# MEMORY.md - 长期记忆

## 项目概览

### AlphaGPT - 中国股市量化系统
- **位置**: /root/clawd/AlphaGPT
- **状态**: 活跃开发中
- **核心模块**:
  - data_providers: 数据获取（Tushare Pro 2000 积分）
  - data_cache: 数据缓存
  - data_validation: 数据验证
  - execution: Solana 交易执行
  - 策略引擎（待完善）
- **技术栈**: Python, Tushare API, Solana SDK
- **重要**: 已有完整的数据模块和 API 文档（API.md），错误处理和日志完善（loguru + 重试机制），需要继续完善策略部分

### CarLife - 汽车生活平台
- **位置**: /root/clawd/CarLife
- **状态**: 活跃开发中
- **核心合约**: 6 个智能合约（1 个主合约 + 5 个 backup 版本）
- **链下工具**: Hardhat 部署脚本
- **研究方向**: NFT 汽车 DApp
- **技术栈**: Solidity, Hardhat, OpenZeppelin
- **重要**: CarNFT_Fixed.sol 为主合约，已创建完整测试用例（31 个测试全部通过）

### Pheglovog-homepage - 个人主页
- **位置**: /root/clawd/Pheglovog-homepage
- **状态**: 活跃维护中
- **技术栈**: HTML, CSS, JavaScript
- **子模块**: /root/clawd/clawd-workspace/Pheglovog-homepage
- **已添加**: 量化交易入门、CarLife 介绍、AlphaGPT 架构等文章

---

## 环境配置

### 代理服务器
- **地址**: http://127.0.0.1:7890
- **类型**: HTTP/HTTPS 代理
- **进程**: mihomo (PID: 88611)

### 启动/关闭代理
```bash
source ~/proxy_on.sh  # 启动
source ~/proxy_off.sh # 关闭
```

### Git 全局配置
```
user.name: 上等兵•甘
user.email: 3042569263@qq.com
```

### Tushare Pro 配置
```
Token: cc9f4227a4be5c67699791c24526d2ec3947877f1cec3619866078f4
积分: 2000
并发限制: 5
测试: ✅ 全部通过
```

---

## 重要事件和决策

### 2026-02-01
- 🎯 确立主动性原则：从被动等待到主动进取
- 📝 创建 IDENTITY.md、TOOLS.md、HEARTBEAT.md
- ⏰ 设置 cron 定时任务：每小时汇报进度

### 2026-02-05
- 🌐 创建个人主页文章（量化交易、CarLife、AlphaGPT）
- 📦 更新 projects.html 添加 3 个新项目
- 🚀 推送更新到 GitHub

### 2026-02-08 凌晨-早上
- ✅ 完成所有主动任务
- 🔧 磁盘清理（释放 7G 空间）
- 📊 项目健康检查（所有项目干净）
- 🧠 OpenClaw Skills 生态研究（1700+ 技能）
- 📝 加密货币学习资料整理（4 个文档）
- ✅ CarLife 测试套件创建和运行（31 个测试全部通过）
- ✅ AlphaGPT API 文档创建（API.md，806 行）

---

## 学习进展

### 加密货币和区块链
- ✅ 智能合约基础（CarNFT 多个版本优化）
- ✅ Solidity + Hardhat 开发
- 📚 DeFi 生态系统研究
- 🎯 深度学习：10 小时，208K+ 字

### 待深入研究
- [ ] DeFi 协议原理（深入）
- [ ] Layer2 扩容方案（ZK Rollup, Optimistic Rollup）
- [ ] 零知识证明（zk-SNARKs）
- [ ] 跨链技术（原子交换、消息传递）

---

## 工作原则

### 🎯 主动性
- 每天早上 8:00 列出 10 个今日任务
- 优先执行用户任务
- 空隙时间主动工作
- 每日总结汇报

### 🔐 安全
- ⚠️ 永远不要提交 .env 文件
- ⚠️ 推送前先检查敏感信息
- ⚠️ 大改动前先询问用户
- ✅ 小改动可以自主完成（文档、注释、测试等）

### 🧠 记忆管理
- 每日笔记：memory/YYYY-MM-DD.md
- 长期记忆：MEMORY.md
- 重要事件记录于此文件

---

## 工具和资源

### OpenClaw Skills
- **查找网站**: https://github.com/VoltAgent/awesome-openclaw-skills
- **本地位置**: /root/clawd/openclaw/skills/
- **已研究**: 1700+ 技能分析

### 主要技能
- coding-agent: 编程助手
- skill-creator: 创建和管理技能
- github: GitHub 交互
- mcporter: MCP 服务器管理
- weather: 天气查询
- feishu-doc: 飞书文档操作
- image-generate: 图片生成
- video-generate: 视频生成

---

## 待办事项优先级

### 高优先级
- [ ] 等待义父的新任务指令
- [x] AlphaGPT - 添加错误处理和日志（已完成，使用 loguru + 重试机制）
- [x] CarLife - 创建 CarNFT_Fixed.sol 测试用例（31 个测试全部通过）

### 中优先级
- [ ] 记录加密货币学习笔记
- [x] 完善 AlphaGPT API 文档（已创建 API.md）
- [ ] 研究 DeFi 协议原理

### 低优先级
- [ ] 研究 Layer2 扩容方案
- [ ] 研究零知识证明

---

*最后更新: 2026-02-08 04:00*
