# AI 热门项目每日推送

## 功能说明

每天早上 10 点自动获取 GitHub 上 AI 领域的热门项目，并发送到飞书。

## 文件位置

- **脚本**: `/root/clawd/scripts/ai-trending-cron.sh`
- **日志**: `/root/clawd/logs/ai-trending-cron.log`
- **结果**: `/root/clawd/memory/ai-trending-YYYY-MM-DD.md`

## 查看当前定时任务

```bash
crontab -l
```

## 手动运行测试

```bash
/root/clawd/scripts/ai-trending-cron.sh
```

## 删除定时任务

```bash
crontab -e
# 删除对应的行，保存退出
```

## 输出格式示例

```
🔥 今日 AI 热门项目 (2026-01-30)

## AUTOGPT
📝 AutoGPT is the vision of accessible AI for everyone...
⭐ 181559 stars | 🍴 46283 forks
🔗 https://github.com/Significant-Gravitas/AutoGPT
🏷️ 语言: Python
📅 更新: 2026-01-30

---
## DEEP-LIVE-CAM
📝 real time face swap and one-click video deepfake...
⭐ 79139 stars | 🍴 11541 forks
🔗 https://github.com/hacksider/Deep-Live-Cam
🏷️ 语言: Python
📅 更新: 2026-01-30
```
