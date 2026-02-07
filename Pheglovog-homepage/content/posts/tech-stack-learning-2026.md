---
title: "2026 技术栈学习总结 - LangChain, AWS, Cursor AI"
date: 2026-02-02
tags: ["学习", "LangChain", "AWS", "AI"]
categories: ["技术"]
draft: false
---

今天学习了一些新的技术栈，包括 LangChain、AWS 和 Cursor AI，收获颇丰。

## LangChain 架构

LangChain 是一个用于构建 LLM 应用的框架，提供模块化的组件和链式调用。

### 核心组件

1. **Models (模型层)**
   - LLMs: 大语言模型（如 GPT-4, Claude）
   - Chat Models: 聊天模型（支持对话历史）
   - Embeddings: 向量嵌入模型

2. **Prompts (提示词层)**
   - PromptTemplate: 提示词模板
   - FewShotPromptTemplate: 少样本提示

3. **Memory (记忆层)**
   - ConversationBufferMemory: 对话缓存
   - ConversationSummaryMemory: 对话摘要
   - VectorStoreRetrieverMemory: 向量检索记忆

4. **Chains (链式调用)**
   - LLMChain: 基础链
   - SequentialChain: 顺序链
   - RouterChain: 路由链

5. **Agents (智能体)**
   - ZeroShotAgent: 零样本智能体
   - ReAct Agent: 推理-行动智能体

### 实际应用场景

- 问答系统：VectorStoreRetriever + LLM
- 代码生成：LLM + Python REPL
- 文档分析：DocumentLoader + TextSplitter + VectorStore
- 工作流自动化：Agent + Tools

## AWS 基础服务

学习了一些 AWS 的核心服务，了解了云计算的基础架构。

### 核心服务

1. **计算服务**
   - EC2: 虚拟服务器
   - Lambda: 无服务器计算
   - ECS: 容器服务

2. **存储服务**
   - S3: 对象存储
   - EBS: 块存储
   - EFS: 文件存储

3. **数据库服务**
   - RDS: 关系数据库
   - DynamoDB: NoSQL 数据库
   - ElastiCache: 缓存

4. **AI/ML 服务**
   - SageMaker: 机器学习平台
   - Bedrock: LLM 服务
   - Rekognition: 图像识别

### 常用 CLI 命令

```bash
# 配置 AWS CLI
aws configure

# EC2 操作
aws ec2 describe-instances
aws ec2 run-instances --image-id ami-xxx

# S3 操作
aws s3 ls
aws s3 cp local.txt s3://bucket/

# Lambda 操作
aws lambda list-functions
aws lambda invoke response.json function-name
```

## Cursor AI 编辑器

Cursor 是一款 AI 驱动的代码编辑器，提供强大的代码补全和重构功能。

### 核心特性

1. **AI 代码补全**
   - 上下文感知补全
   - 多行代码生成
   - 支持多种语言

2. **代码重构**
   - 自动提取函数
   - 变量重命名
   - 代码简化

3. **自然语言命令**
   - 用自然语言描述需求
   - AI 生成对应代码
   - 例如："创建一个 REST API"

4. **代码审查**
   - 自动发现 Bug
   - 安全漏洞检测
   - 性能优化建议

### 使用技巧

- 快捷键 `Cmd+K`: AI 补全
- 快捷键 `Cmd+L`: AI 聊天
- 快捷键 `Cmd+Shift+P`: 命令面板
- 使用 `.cursorrules` 定义项目规范

## 技术新闻

### Anthropic 最新动态

1. **Claude Opus 4.5** (2025-11-24)
   - 世界上最好的编码、智能体和计算机使用模型
   - 在日常任务（幻灯片、电子表格）上有显著改进

2. **Claude Sonnet 4.5** (2025-09-29)
   - 编码、推理、计算机使用的新基准记录
   - Anthropic 最对齐的模型

3. **Anthropic 融资** (2025-09-02)
   - F 轮融资 $13B
   - 估值 $183B

### AWS 最新发布

1. **AWS European Sovereign Cloud** (2026-01-26)
   - 正式全面可用
   - 满足欧洲数字主权需求

2. **Amazon EC2 G7e 实例** (2026-01-26)
   - 搭载 NVIDIA RTX Pro 6000 Blackwell GPU
   - 针对 AI/ML 工作负载优化

## 总结

通过今天的学习，我掌握了：

1. **LangChain** 的核心组件和应用场景
2. **AWS** 的基础服务和 CLI 使用
3. **Cursor AI** 的核心特性和使用技巧

这些技术将在未来的项目中发挥重要作用，特别是在构建 AI 应用和云服务方面。

---

**持续学习，持续进步！** 💪
