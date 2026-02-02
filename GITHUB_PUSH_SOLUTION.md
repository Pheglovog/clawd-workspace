# GitHub 推送问题解决方案

## 问题描述

```
error: src refspec main does not match any
fatal: unable to access 'https://github.com/Pheglovog/CarLife.git/': gnutls_handshake() failed
```

## 原因分析

### 1. TLS 连接失败
- 可能原因：代理配置问题
- 影响：无法连接到 GitHub

### 2. 分支名称不匹配
- 可能原因：本地是 `main`，远程是 `master`（或反之）
- 影响：无法推送

### 3. 远程仓库不存在
- 可能原因：尚未在 GitHub 上创建仓库

---

## 解决方案

### 方案 1: 手动在浏览器创建仓库

**步骤：**

1. 访问 https://github.com/new
2. 仓库名称：`CarLife`
3. 选择私有或公开
4. 不初始化 README（已有代码）
5. 点击"Create repository"

**推送代码：**

```bash
# 1. 进入项目目录
cd /root/clawd/CarLife

# 2. 移除旧的远程配置
git remote remove origin

# 3. 添加新的远程
git remote add origin https://github.com/Pheglovog/CarLife.git

# 4. 推送代码
git branch -M main  # 确保是 main 分支
git push -u origin main
```

### 方案 2: 配置 SSH 密钥

**步骤：**

1. 生成 SSH 密钥
```bash
ssh-keygen -t ed25519 -C "clawdbot" -f ~/.ssh/clawdbot_ed25519
```

2. 添加到 GitHub
- 复制 `~/.ssh/clawdbot_ed25519.pub` 的内容
- 访问 https://github.com/settings/keys
- 点击"New SSH key"
- 粘贴并保存

3. 测试连接
```bash
ssh -T git@github.com
```

4. 更改远程地址为 SSH
```bash
cd /root/clawd/CarLife
git remote set-url origin git@github.com:Pheglovog/CarLife.git
git push origin main
```

### 方案 3: 修复代理配置

如果使用代理，确保 Git 正确配置：

```bash
# 设置代理
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890

# 测试连接
curl -v https://api.github.com
```

---

## 检查仓库状态

### 查看所有本地提交
```bash
cd /root/clawd/CarLife
git log --oneline
```

### 查看远程仓库状态
```bash
git remote -v
git branch -a
```

---

## 推送所有项目

### AlphaGPT
```bash
cd /root/clawd/AlphaGPT
git push origin main
```

### CurrencyExchange
```bash
cd /root/clawd/CurrencyExchange
git push origin master
```

### CarLife
```bash
cd /root/clawd/CarLife
# 先手动创建仓库，然后：
git branch -M main
git remote add origin https://github.com/Pheglovog/CarLife.git
git push -u origin main
```

### Pheglovog.github.io
```bash
cd /root/clawd/Pheglovog-homepage
# 先手动创建仓库，然后：
git remote add origin https://github.com/Pheglovog/Pheglovog.github.io.git
git push -u origin main
```

---

## 验证推送

访问以下链接检查推送是否成功：

- https://github.com/Pheglovog/AlphaGPT
- https://github.com/Pheglovog/CurrencyExchange
- https://github.com/Pheglovog/CarLife
- https://github.com/Pheglovog/Pheglovog.github.io

---

## 备注

如果所有推送都失败，可以：

1. **使用 GitHub Desktop** - 图形界面，支持代理
2. **使用 GitHub CLI** - `gh repo create`
3. **手动上传代码** - 压缩项目后在浏览器上传

---

**创建者**: 上等兵•甘 💪
**更新时间**: 2026-02-01 03:30
