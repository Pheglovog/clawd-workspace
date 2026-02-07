# TOOLS.md - Local Notes

Skills define *how* tools work. This file is for *your* specifics — the stuff that's unique to your setup.

## Proxy Configuration

### 代理服务器
- **地址**: http://127.0.0.1:7890
- **类型**: HTTP/HTTPS 代理
- **进程**: mihomo (PID: 88611)

### 启动/关闭代理
```bash
# 启动代理
source ~/proxy_on.sh

# 关闭代理
source ~/proxy_off.sh
```

### 在命令中使用代理
```bash
bash -c 'source ~/proxy_on.sh && <command>'
```

### Git 使用代理
```bash
bash -c 'source ~/proxy_on.sh && git clone <repo>'
bash -c 'source ~/proxy_on.sh && git push'
```

### curl 使用代理
```bash
bash -c 'source ~/proxy_on.sh && curl <url>'
```

---

## What Else Goes Here

Things like:
- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

---

## OpenClaw Skills 查找网站

- **URL**: https://github.com/VoltAgent/awesome-openclaw-skills
- **用途**: 查找和获取 OpenClaw 技能（Skills）
- **本地技能位置**: /root/clawd/openclaw/skills/
- **主要技能**:
  - coding-agent: 编程助手（Codex, Claude Code, OpenCode, Pi）
  - skill-creator: 创建和管理技能
  - github: GitHub 交互
  - mcporter: MCP 服务器管理
  - weather: 天气查询
  - 等等...

**注意**: 查找技能时优先去这个网站，然后可以参考本地 `/root/clawd/openclaw/skills/` 目录下的实现。

---

## Git 全局配置

```bash
user.name: 上等兵•甘
user.email: 3042569263@qq.com
```

## Tushare Pro 2000 积分

```
Token: cc9f4227a4be5c67699791c24526d2ec3947877f1cec3619866078f4
积分: 2000
并发限制: 5
测试: ✅ 全部通过
```

---

*Updated: 2026-02-01*
