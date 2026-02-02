---
title: "AlphaQuant 中国股市量化系统开发总结"
date: 2026-02-01
tags: ["量化", "Python", "PyTorch"]
categories: ["量化交易"]
draft: false
---

## 项目概述

AlphaQuant 是一个基于符号回归的中国股市量化交易系统，专注于因子挖掘和策略回测。

## 核心模块

### 1. 数据管道 (Data Pipeline)
- Tushare Pro 异步接口
- 并发控制（支持 2000 积分 = 5 并发）
- 429 错误重试（指数退避）
- API 数据解析

### 2. 因子引擎 (Factor Engine)
- 6 维基础因子（RET, PRESSURE, FOMO, DEV, VOL, AMP）
- 18 维高级因子（RSI, MACD, 布林带, ATR, 北向资金等）
- 24 维总因子空间

### 3. 回测引擎 (Backtest Engine)
- T+1 交易规则
- 涨跌停限制（主板10%、创业板20%、科创板20%、北交所30%）
- 交易成本（佣金、印花税、过户费）
- 滑点模型

### 4. AlphaQuant 模型
- QK-Norm 注意力
- SwiGLU 前馈网络
- RMSNorm 归一化
- 市场情绪编码
- 多任务学习（收益、夏普、回撤）

### 5. 策略管理器
- 信号生成
- 持仓管理
- 风险控制（止损止盈、移动止损）
- 仓位计算

### 6. 可视化面板
- Streamlit 可视化
- 权益曲线
- 回撤曲线
- 收益分布
- 交易记录

## 技术栈

- **语言**: Python
- **深度学习**: PyTorch
- **数据处理**: Pandas, NumPy
- **数据源**: Tushare Pro (2000 积分)
- **可视化**: Streamlit, Matplotlib
- **规范**: OpenSpec

## 项目地址

[GitHub](https://github.com/Pheglovog/AlphaGPT)

## 收获与总结

通过这个项目，我深入学习了：

1. Tushare Pro API 集成和并发控制
2. OpenSpec 开发规范
3. 中国股市交易规则（T+1、涨跌停、交易成本）
4. 量化系统架构设计
5. 模型训练和回测框架

---

**持续学习中，欢迎交流！** 💪
