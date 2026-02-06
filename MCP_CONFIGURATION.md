# MCP 配置完成文档

## ✅ 已配置的 MCP 服务器

我已经成功配置了以下 MCP (Model Context Protocol) 服务器，用于增强 AI 能力：

### 1. 网页读取 MCP (web-reader)
- **功能**: 抓取网页内容，转换为 markdown 或文本
- **服务器**: https://open.bigmodel.cn/api/mcp/web_reader/mcp
- **工具**: `webReader`

### 2. 网络搜索 MCP (web-search)
- **功能**: 搜索网络信息，返回网页标题、URL、摘要等
- **服务器**: https://open.bigmodel.cn/api/mcp/web_search_prime/mcp
- **工具**: `webSearchPrime`

### 3. GitHub 仓库 MCP (zread)
- **功能**: 搜索 GitHub 仓库文档、读取文件、获取目录结构
- **服务器**: https://open.bigmodel.cn/api/mcp/zread/mcp
- **工具**:
  - `search_doc` - 搜索仓库文档
  - `read_file` - 读取文件内容
  - `get_repo_structure` - 获取仓库结构

---

## 🚀 使用示例

### 网页读取 (web-reader)

**场景**: 读取一个技术文章的完整内容

```
请帮我读取这篇文章：https://docs.python.org/3/tutorial/index.html
```

**参数选项**:
- `return_format`: markdown (默认) 或 text
- `timeout`: 请求超时时间（默认 20 秒）
- `no_cache`: 禁用缓存（默认 false）
- `retain_images`: 保留图片（默认 true）

---

### 网络搜索 (web-search)

**场景**: 搜索最新的技术信息

```
请搜索 Python 3.12 的新特性
```

**参数选项**:
- `search_query`: 搜索内容（建议不超过 70 字符）
- `search_domain_filter`: 域名过滤（白名单）
- `search_recency_filter`: 时间范围过滤
  - `oneDay` - 一天内
  - `oneWeek` - 一周内
  - `oneMonth` - 一个月内
  - `oneYear` - 一年内
  - `noLimit` - 无限制
- `content_size`: 内容大小控制
  - `medium` - 平衡模式，400-600 字（默认）
  - `high` - 高质量模式，2500 字
- `location`: 区域设置
  - `cn` - 中国区域
  - `us` - 非中国区域

---

### GitHub 仓库读取 (zread)

#### 搜索文档 (search_doc)

**场景**: 搜索 GitHub 仓库的文档

```
请搜索 vuejs/core 仓库中关于响应式系统的文档
```

**参数**:
- `repo_name`: GitHub 仓库（如 "vuejs/core"）
- `query`: 搜索关键词或问题
- `language`: 语言选择（'zh' 或 'en'）

#### 读取文件 (read_file)

**场景**: 读取仓库中的特定文件

```
请读取 vitejs/vite 仓库的 package.json 文件
```

**参数**:
- `repo_name`: GitHub 仓库（如 "vitejs/vite"）
- `file_path`: 文件相对路径（如 "package.json"）

#### 获取仓库结构 (get_repo_structure)

**场景**: 查看仓库的目录结构

```
请获取 openclaw/openclaw 仓库的目录结构
```

**参数**:
- `repo_name`: GitHub 仓库（如 "openclaw/openclaw"）

---

## 🔧 配置文件位置

- **项目配置**: `/root/clawd/config/mcporter.json`
- **系统配置**: `/root/.mcporter/mcporter.json` (未使用)

---

## 📋 MCP 管理命令

### 列出所有服务器
```bash
mcporter config list
```

### 列出服务器的工具（带 schema）
```bash
mcporter list <server-name> --schema
```

### 调用工具
```bash
mcporter call <server-name>.<tool-name> [key=value ...]
```

### 移除服务器
```bash
mcporter config remove <server-name>
```

---

## 💡 使用技巧

### 1. 组合使用多个 MCP
```
请帮我搜索最新的 AI 技术发展，然后读取这篇技术文章的详细内容：https://example.com/article
```

### 2. 使用时间过滤
```
请搜索最近一周关于 Python 异步编程的文章
```

### 3. 限定搜索范围
```
请搜索 Vue.js 官方文档中关于 Composition API 的内容
```

### 4. 深度阅读 GitHub 项目
```
请读取 openclaw/openclaw 仓库的 README.md，然后获取主要目录结构
```

---

## ⚠️ 注意事项

1. **API Key**: 使用的是 bigmodel API key，已配置在 headers 中
2. **速率限制**: 请注意 API 调用频率，避免超限
3. **搜索优化**: 搜索查询建议简洁明确，不超过 70 字符
4. **缓存**: web-reader 默认启用缓存，可使用 `no_cache` 禁用

---

## 🔜 待添加的 MCP

### 视觉理解 MCP (vision-mcp-server)
需要安装 npm 包，配置方式略有不同：
- **类型**: stdio
- **命令**: `npx -y @z_ai/mcp-server`
- **工具**:
  - ui_to_artifact - UI 截图转代码
  - extract_text_from_screenshot - OCR 文字提取
  - diagnose_error_screenshot - 错误分析
  - understand_technical_diagram - 图表理解
  - analyze_data_visualization - 数据可视化分析
  - ui_diff_check - UI 对比
  - image_analysis - 图像理解
  - video_analysis - 视频分析

---

**配置完成时间**: 2026-02-04
**配置状态**: ✅ 已完成 (3/4 MCP 服务器)
