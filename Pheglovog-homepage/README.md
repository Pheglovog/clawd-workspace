# Pheglovog Home - 个人主页

基于 [Hugo](https://gohugo.io/) 构建的现代化个人主页，展示项目、博客和个人信息。

## 🌟 特性

- 🎨 简洁美观的界面设计
- 📱 响应式布局，支持移动端
- ⚡ 快速加载，SEO 友好
- 📝 支持博客文章和分类
- 🏷️ 标签系统
- 🔍 内置搜索功能（可选）
- 🌙 深色模式支持（可选）

## 🚀 快速开始

### 环境要求

- Hugo 0.100.0+
- Git

### 安装 Hugo

#### Linux/Mac

```bash
# 使用 Homebrew (Mac)
brew install hugo

# 使用 snap (Linux)
snap install hugo

# 或下载二进制文件
wget https://github.com/gohugoio/hugo/releases/download/v0.134.0/hugo_extended_0.134.0_linux-amd64.tar.gz
tar -xvf hugo_extended_0.134.0_linux-amd64.tar.gz
sudo mv hugo /usr/local/bin/
```

#### Windows

下载 [Hugo Releases](https://github.com/gohugoio/hugo/releases) 中的 Windows 二进制文件。

### 本地运行

```bash
# 克隆仓库（如果还没克隆）
git clone https://github.com/Pheglovog/Pheglovog-homepage.git
cd Pheglovog-homepage

# 启动开发服务器
hugo server -D

# 访问 http://localhost:1313
```

### 构建

```bash
# 生产构建
hugo

# 输出到 public/ 目录
```

## 📂 项目结构

```
Pheglovog-homepage/
├── content/               # 内容目录
│   ├── posts/           # 博客文章
│   ├── projects/        # 项目展示
│   └── about/           # 关于页面
├── themes/              # 主题目录
│   └── [theme-name]/   # 使用的主题
├── static/              # 静态资源
│   ├── css/            # 自定义 CSS
│   ├── js/             # 自定义 JS
│   └── images/         # 图片
├── layouts/             # 自定义布局
├── config.toml          # 配置文件
└── hugo.toml           # 主配置文件
```

## 📝 添加内容

### 新建文章

```bash
# 创建新文章
hugo new posts/my-first-post.md

# 文章文件：content/posts/my-first-post.md
```

文章模板：
```markdown
---
title: "文章标题"
date: 2026-02-07T11:00:00+08:00
draft: false
tags: ["标签1", "标签2"]
categories: ["分类"]
---

文章内容...
```

### 新建项目

```bash
# 创建项目页面
hugo new projects/my-project.md
```

## ⚙️ 配置

编辑 `hugo.toml` 修改站点配置：

```toml
baseURL = "https://pheglovog.github.io/"
languageCode = "zh-CN"
title = "Pheglovog"
theme = "your-theme-name"

[params]
  # 站点描述
  description = "Pheglovog 的个人主页"
  # 作者
  author = "Pheglovog"
  # 社交链接
  social = [
    { name = "GitHub", url = "https://github.com/Pheglovog" },
    { name = "Email", url = "mailto:3042569263@qq.com" }
  ]
```

## 🚢 部署

### GitHub Pages

1. 仓库名设为 `username.github.io`
2. 推送到 GitHub

```bash
git add .
git commit -m "Update site"
git push origin main
```

### 自定义域名

1. 在 `static/` 目录创建 `CNAME` 文件
2. 添加域名内容（如：`www.yourdomain.com`）

```bash
echo "www.yourdomain.com" > static/CNAME
```

3. 在域名服务商配置 DNS 解析

## 📚 自定义

### 自定义 CSS

在 `static/css/` 目录添加 `custom.css`，然后在 `layouts/partials/head.html` 中引入：

```html
<link rel="stylesheet" href="{{ "css/custom.css" | relURL }}">
```

### 自定义布局

在 `layouts/` 目录创建自定义模板：

```
layouts/
├── _default/          # 默认模板
│   ├── baseof.html   # 基础模板
│   ├── single.html   # 单页模板
│   └── list.html     # 列表页模板
└── index.html        # 首页模板
```

## 🎨 主题推荐

- [PaperMod](https://github.com/adityatelange/hugo-PaperMod) - 简洁现代
- [LoveIt](https://github.com/dillonzq/LoveIt) - 功能丰富
- [Even](https://github.com/olOwOlo/hugo-theme-even) - 优雅设计
- [NexT](https://github.com/hugo-next/hugo-theme-next) - 多样化

## 📖 学习资源

- [Hugo 官方文档](https://gohugo.io/documentation/)
- [Hugo 主题库](https://themes.gohugo.io/)
- [Hugo 示例站](https://gohugo.io/showcase/)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 License

MIT

---

**开发者**: Pheglovog
**最后更新**: 2026-02-07
