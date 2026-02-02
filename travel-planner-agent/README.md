# Travel Planner Agent

一个基于 LangChain 的智能旅游规划助手，帮助用户规划行程、计算预算和生成打包清单。

## 🎯 核心功能

1. **智能行程规划**
   - 根据目的地、天数、预算和偏好规划详细行程
   - 考虑用户偏好（喜欢自然景观、历史古迹、购物等）
   - 推荐交通方式、住宿选择
   - 优化行程路线，避免走回头路

2. **智能物品清单生成**
   - 根据旅行天数、活动类型和天气生成 packing list
   - 分类整理（衣物、电子设备、洗护用品、文件）
   - 提醒重要物品（充电器、相机、药品）

3. **智能预算计算**
   - 计算总旅行费用
   - 分类统计（交通、住宿、餐饮、景点门票、购物）
   - 提供汇率转换（支持多货币）
   - 生成费用分析报告
   - 提供节约建议

4. **实用工具集成**
   - 天气查询（获取目的地天气）
   - 汇率查询（实时汇率转换）
   - 地图路线规划（交通方式推荐）

## 🛠 技术栈

- **LangChain**: 框架核心（Chains, Agents, Tools, Memory, Prompts）
- **Python**: 主要编程语言
- **OpenAI API**: 可选的 LLM 提供商
- **Pydantic**: 数据验证和输出模型
- **LangChain Output Parser**: 结构化输出解析

### 核心组件

1. **Models (模型层)**
   - LLMs: 大语言模型（GPT-4, Claude）
   - Chat Models: 支持对话历史

2. **Prompts (提示词层)**
   - PromptTemplate: 提示词模板
   - FewShotPromptTemplate: 少样本提示
   - SystemMessage: 系统消息

3. **Memory (记忆层)**
   - ConversationBufferMemory: 对话缓存
   - ConversationSummaryMemory: 对话摘要

4. **Chains (链式调用)**
   - LLMChain: 基础链
   - AgentExecutor: 多 Agent 执行器（新）
   - SequentialChain: 顺序链

5. **Agents (智能体)**
   - Planner Agent: 行程规划专家
   - Checklist Agent: 打包清单专家
   - Budget Agent: 预算计算专家

6. **Tools (工具集)**
   - Weather Tool: 天气查询
   - Currency Tool: 汇率转换
   - Route Tool: 地图路线规划
   - StructuredTool: 结构化工具接口

7. **Output Parsers (输出解析器)**
   - StrOutputParser: 字符串解析
   - OutputFixingParser: 输出修复
   - Pydantic Output Parser: 模型输出解析

## 📁 项目结构

```
travel-planner-agent/
├── README.md              # 项目说明
├── src/                   # 源代码
│   ├── main.py           # 主程序入口
│   ├── agents/           # Agent 定义和执行器
│   │   ├── planner.py       # 行程规划 Agent
│   │   ├── checklist.py     # 物品清单 Agent
│   │   ├── budget.py        # 预算计算 Agent
│   │   └── agent_executor.py  # 多 Agent 执行器（新）
│   ├── tools/             # LangChain 工具定义
│   │   ├── weather.py       # 天气查询工具
│   │   ├── currency.py      # 汇率查询工具
│   │   └── maps.py          # 路线规划工具
│   ├── utils/             # 工具函数
│   │   ├── config.py        # 配置管理
│   │   ├── prompts.py       # 提示词模板（新）
│   │   └── models.py       # Pydantic 数据模型（新）
└── config/              # 配置文件
    ├── api_keys.json       # API 密钥（不提交到 Git）
    ├── .env.example        # 环境变量示例
    └── requirements.txt     # Python 依赖
```

## 🚀 核心改进

### 1. 真正的 Multi-Agent 架构 ⭐
**新功能**: 使用 `AgentExecutor` 创建多个专业 Agent
- **Planner Agent**: 专门负责行程规划
- **Checklist Agent**: 专门负责生成打包清单
- **Budget Agent**: 专门负责预算计算
- **智能工具调用**: Agent 自动调用天气、汇率、路线工具
- **共享记忆**: 所有 Agent 共享同一个 `ConversationBufferMemory`

**优势**:
- ✅ 更好的任务分配
- ✅ 专业化分工
- ✅ 并行处理能力
- ✅ 更清晰的职责划分

### 2. 结构化输出 📊
**新功能**: 使用 Pydantic 和 Output Parser
- **Pydantic Models**: 定义所有输入输出模型
- **OutputFixingParser**: 自动修复 LLM 输出格式
- **JSON 解析**: 自动解析 Agent 返回的 JSON

**优势**:
- ✅ 类型安全
- ✅ 自动验证
- ✅ 清晰的数据结构
- ✅ 更好的错误处理

### 3. 模块化提示词系统 💬
**新功能**: 集中的提示词模板
- **专业提示词**: 为每个 Agent 创建专门的提示词
- **Few-Shot**: 提供示例提升输出质量
- **系统提示**: 清晰的角色定义

**提示词模板**:
```python
# 行程规划提示词
planning_prompt = PromptTemplate.from_template(
    "你是一位专业的日本旅行规划师..."
)

# 打包清单提示词
checklist_prompt = PromptTemplate.from_template(
    "你是一位专业的旅行顾问..."
)

# 预算计算提示词
budget_prompt = PromptTemplate.from_template(
    "你是一位专业的旅行财务顾问..."
)
```

### 4. 增强的工具集成 🛠
**新功能**: 使用 `StructuredTool` 包装自定义函数
- **天气工具**: 异步天气查询
- **汇率工具**: 实时汇率转换
- **路线工具**: 智能路线推荐

**工具特性**:
- ✅ 类型注解（Pydantic）
- ✅ 异步支持
- ✅ 错误处理
- ✅ 描述性名称

### 5. 改进的主程序 🎯
**新功能**: 统一的用户界面
- **交互式菜单**: 清晰的选项选择
- **彩欢迎界面**: 更好的用户体验
- **智能输入**: 自动填充和验证
- **格式化输出**: 美观的 JSON 展示

## 🚀 快速开始

### 安装依赖
```bash
cd travel-planner-agent
pip install -r requirements.txt
```

### 配置 API 密钥
```bash
cp config/api_keys.json.example config/api_keys.json
# 编辑 config/api_keys.json 添加你的 API 密钥
```

### 设置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件添加你的 API 密钥
```

### 运行程序
```bash
cd travel-planner-agent
python src/main.py
```

## 🎨 使用示例

### 示例 1: 完整的旅行规划
```
请帮我规划一个 5 天的日本旅行行程，喜欢历史古迹和自然景观，预算约 200,000 人民币。
```

**输出**:
- 详细的 JSON 格式行程规划
- 打包清单（分类整理）
- 预算分析报告（每日费用明细）
- 货币转换建议
- 天气查询结果
- 路线推荐

---

### 示例 2: 仅生成打包清单
```
我计划去日本旅行 7 天，请生成一份完整的打包清单。
```

**输出**:
- 7 天的衣物（14 套内衣 + 7 套外衣）
- 7 天的洗护用品（3 套牙具）
- 电子产品清单
- 医疗用品包
- 重要文件提醒

---

### 示例 3: 预算计算
```
目的地：东京、京都、大阪，旅行 5 天，预算 150,000 人民币。
```

**输出**:
- 交通费用明细（机票 + JR Pass）
- 住宿费用明细（酒店预订）
- 餐饮费用计算（每日餐费）
- 门票和娱乐费用估算
- 总预算对比和节约建议
- 汇率转换（人民币 → 日元）

---

## 🚀 核心优势

### 1. Multi-Agent 架构 🤖
- ✅ **专业分工**: 每个 Agent 专注于特定任务
- ✅ **并行执行**: 多个 Agent 可以同时工作
- ✅ **智能工具选择**: 根据任务自动选择合适的工具
- ✅ **共享记忆**: 对话上下文在所有 Agent 间共享
- ✅ **可扩展性**: 轻松添加新的 Agent 和工具

### 2. 结构化输出 📊
- ✅ **类型安全**: Pydantic 模型确保数据完整性
- ✅ **自动验证**: 输入输出自动验证
- ✅ **格式统一**: 所有输出都是标准化的 JSON
- ✅ **易于集成**: 结构化数据便于后续处理

### 3. 模块化设计 🧩
- ✅ **清晰分离**: 工具、Agents、提示词独立管理
- ✅ **可重用性**: 提示词和工具可以跨项目使用
- ✅ **易维护性**: 修改一个 Agent 不影响其他

### 4. 智能工具集成 🛠
- ✅ **实时数据**: 天气、汇率、路线信息
- ✅ **上下文感知**: 根据旅行地点提供本地化建议
- ✅ **专业建议**: 基于目的地和行程的实用贴士

## 🎯 架构亮点

```
┌─────────────────────────────────────────────────────────┐
│                    User Input                      │
│                      (用户输入)                     │
│                         ↓                                 │
│         ┌─────────────────────────┐                    │
│         │  Agent Executor      │                    │
│         │ (Multi-Agent Manager) │                    │
│         └─────────┬─────────────┘                    │
│                   ↓                                   │
│    ┌──────┬──────────┬──────────┬───────────┐      │
│    │      │        │       │       │      │     │
│    │ Planner│Checklist│ Budget │Weather│Currency│Route│     │
│    │ Agent │ Agent  │  Agent │ Agent │ Agent │ Agent │     │
│    └──────┴─────────┴───────┴───────┴───────┘      │
│                   ↓                                   │
│              Shared Memory                           │
│         (ConversationBufferMemory)                  │
│                   ↓                                   │
│               LLM Response                            │
│         (Structured Output)                         │
└─────────────────────────────────────────────────────────┘
```

## 🚀 贡献指南

欢迎贡献代码、建议新功能或报告 Bug！

### 如何贡献
1. Fork 本仓库
2. 创建新分支 (`git checkout -b feature/xxx`)
3. 提交代码更改 (`git commit -m "Add feature"`)
4. 推送到你的分支并创建 Pull Request

### 新功能建议
- ✅ 添加新的 Agent 类型（如天气 Agent、美食推荐 Agent）
- ✅ 支持更多目的地（韩国、泰国、欧洲等）
- ✅ 集成更多实用工具（地图 API、旅游指南 API）
- ✅ 添加语音输入支持
- ✅ 实现 PDF 行程单导出功能
- ✅ 添加费用追踪和预算提醒
- ✅ 集成社交媒体分享功能

### Bug 报告
- 🐛 发现 Bug 请在 Issues 中报告
- 📝 请提供详细的复现步骤
- 📸 请说明你的环境配置（Python 版本、依赖版本）

### 代码规范
- ✅ 遵循 PEP 8 编码规范
- ✅ 添加类型注解（Type Hints）
- ✅ 编写文档字符串（docstrings）
- ✅ 编写单元测试
- ✅ 使用有意义的变量名和函数名

## 📄 许可证

MIT License

---

**开始使用 Travel Planner Agent，让你的旅行规划更加智能和便捷！** ✈️

**项目特点**:
- 🤖 Multi-Agent 架构
- 📊 结构化输出（Pydantic）
- 🧩 模块化设计
- 🛠 智能工具集成
- 🧠 模块化提示词系统
- 🎯 专业化的提示词工程
- 💾 共享记忆管理
- 🔒 可扩展的架构

---

**版本**: 2.0.0 (LangChain 重构版)
**更新时间**: 2026-02-02 10:25
