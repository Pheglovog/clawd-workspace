# CarLife - 区块链汽车生活平台

一个基于区块链的汽车生活服务平台，连接车主、服务商和区块链生态。

## ✨ 核心特性

- 🚗 **车辆 NFT** - 车辆信息上链，不可篡改的所有权证明
- 📋 **服务注册** - 去中心化的服务商注册和评价系统
- 💬 **评价上链** - 用户评价存储在区块链，不可删除
- 💰 **数据 Token 化** - 车主拥有数据，可以安全交易

## 🛠️ 技术栈

### 区块链
- **Solidity ^0.8.19** - 智能合约
- **OpenZeppelin** - ERC721, Ownable, Counters
- **Hardhat** - 开发框架

### 后端（开发中）
- **Go 1.21+** - 高性能
- **Gin** - Web 框架
- **GORM** - ORM
- **PostgreSQL** - 数据库

### 前端（开发中）
- **Vue 3** - 渐进式框架
- **TypeScript** - 类型安全
- **Element Plus** - UI 组件库

## 🚀 快速开始

### 前置要求
- Node.js 18+
- Go 1.21+
- MetaMask（浏览器扩展）

### 1. 查看智能合约

```
contracts/
├── CarNFT.sol          # 车辆 NFT 合约
└── ServiceRegistry.sol # 服务注册合约
```

### 2. 部署到测试网络
```bash
npx hardhat compile
npx hardhat run scripts/deploy.js --network localhost
```

### 3. 前端连接
```bash
cd frontend
npm install
npm run dev
```

## 📋 项目结构

```
CarLife/
├── contracts/          # 智能合约
│   ├── CarNFT.sol
│   └── ServiceRegistry.sol
├── backend/           # 后端（开发中）
│   ├── api/
│   ├── models/
│   ├── services/
│   └── main.go
├── frontend/          # 前端（开发中）
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   └── router/
│   └── package.json
└── docs/             # 文档
```

## 🔑 智能合约功能

### CarNFT
- ✅ 车辆 NFT 铸造
- ✅ 车辆信息上链
- ✅ 里程更新
- ✅ 维修记录
- ✅ NFT 转移
- ✅ VIN 验证

### ServiceRegistry
- ✅ 服务商注册
- ✅ 服务发布
- ✅ 用户评价
- ✅ 评分自动更新
- ✅ 服务商停用

## 🎯 开发计划

### Phase 1: MVP (进行中）
- [x] 项目结构
- [x] 智能合约开发
- [ ] 后端 API 开发
- [ ] 前端基础页面

### Phase 2: 核心功能
- [ ] 车辆 NFT 系统
- [ ] 服务注册系统
- [ ] 评价系统
- [ ] 用户认证

### Phase 3: 高级功能
- [ ] 数据 Token 化
- [ ] 数据交易市场
- [ ] 移动端适配
- [ ] 多语言支持

## 📄 License

MIT

---

**开发者**: 上等兵•甘
**最后更新**: 2026-02-01
