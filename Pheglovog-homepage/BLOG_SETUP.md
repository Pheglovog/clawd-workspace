# 博客系统设置指南

本项目已集成 **Decap CMS** + **Pagefind 搜索**，以下是完成设置的步骤。

## 🚀 快速开始

### 1. 启用 GitHub Pages

1. 进入仓库 **Settings → Pages**
2. Source 选择 **GitHub Actions**
3. 保存设置

### 2. 推送代码触发部署

```bash
git add .
git commit -m "feat: 添加 Decap CMS 和 Pagefind 搜索"
git push origin main
```

GitHub Actions 会自动构建并部署网站。

### 3. 访问 CMS 后台

部署完成后，访问：
```
https://pheglovog.github.io/pheglovog-site/admin/
```

首次访问会跳转到 GitHub 授权页面，授权后即可使用 CMS。

### 4. 本地开发

```bash
# 安装 Hugo（如果没有）
# macOS
brew install hugo

# Linux
snap install hugo

# 启动本地服务器
hugo server -D

# 启动 Decap CMS 本地后端（可选）
npx decap-server
```

本地访问：
- 博客: http://localhost:1313/
- CMS 后台: http://localhost:1313/admin/

## 📝 使用 CMS

访问 `https://pheglovog.github.io/pheglovog-site/admin/` 进入管理后台。

### 功能
- ✅ 创建/编辑/删除博客文章
- ✅ 管理分类和标签
- ✅ 图片上传
- ✅ Markdown 编辑器
- ✅ 实时预览

### 工作流程
1. 访问 `/admin/` 登录 GitHub
2. 创建或编辑文章
3. 点击发布
4. GitHub Actions 自动构建部署
5. 几分钟后文章上线

## 🔍 搜索功能

Pagefind 会在构建时自动索引所有文章内容。

- 搜索页面: `/search/`
- 支持中文搜索
- 实时结果高亮

## 📁 项目结构

```
content/
├── posts/          # 博客文章
├── categories/     # 分类定义
├── tags/           # 标签定义
├── projects/       # 项目展示
└── search/         # 搜索页面

static/
└── admin/
    ├── index.html  # CMS 入口
    └── config.yml  # CMS 配置

.github/
└── workflows/
    └── deploy.yml  # 自动部署配置
```

## ❓ 常见问题

### Q: CMS 登录失败？
A: 检查 OAuth 代理配置是否正确，确保 GitHub OAuth App 的 callback URL 匹配。

### Q: 搜索不工作？
A: Pagefind 索引在构建时生成，本地开发需要先运行 `hugo && npx pagefind --site public`。

### Q: 如何添加新分类？
A: 在 CMS 后台点击"分类" → "新建分类"，或直接在 `content/categories/` 下创建 `.md` 文件。

## 🔗 相关链接

- [Decap CMS 文档](https://decapcms.org/docs/)
- [Pagefind 文档](https://pagefind.app/)
- [Hugo 文档](https://gohugo.io/documentation/)
