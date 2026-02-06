# 跨平台定时通知实现方案

> OpenClaw + 飞书完整集成
> 义父的手机端主动学习提醒

---

## 📋 方案架构

```
┌─────────────────────────────────────────────┐
│   OpenClaw Cron Scheduler           │
│   ┌───────────────────────────┐    │
│   │   每小时触发           │    │
│   │   2026-02-07 02:00      │    │
│   │   Asia/Shanghai 时区       │    │
│   └───────────────────────────┘    │
└─────────────────────────────────────────────┘
               ↓ systemEvent
┌─────────────────────────────────────────────┐
│   OpenClaw Gateway                 │
│   ┌───────────────────────────┐    │
│   │   Session Injection      │    │
│   │   转发到飞书 Bot    │    │
│   └───────────────────────────┘    │
└─────────────────────────────────────────────┘
               ↓ 发送消息
┌─────────────────────────────────────────────┐
│   飞书 Bot                         │
│   ┌───────────────────────────┐    │
│   │   接收 OpenClaw 消息   │    │
│   │   转发到义父         │    │
│   │   发送手机通知       │    │
│   └───────────────────────────┘    │
└─────────────────────────────────────────────┘
```

---

## 🎯 完整实施步骤

### 步骤 1：创建飞书 Bot

**飞书开放平台 Bot 配置：**

1. **访问飞书开放平台**
   - 地址：https://open.feishu.cn/
   - 使用义父的企业账号登录

2. **创建应用**
   - 进入"开放" → "应用管理" → "创建企业自建应用"
   - 应用名称：`吕布主动学习助手`
   - 应用描述：`自动化学习进度汇报机器人`
   - App ID: 记录生成的 `cli_xxxxx`

3. **获取权限**
   - 申请以下权限：
     - `获取群组信息`
     - `发送单聊消息`
     - `获取用户信息`

4. **获取 Bot Token**
   - 进入应用详情
   - 找到"凭证"部分
   - 复制 `App ID` 和 `App Secret`

**命令配置：**
```bash
# 飞书 Channel 配置
CHANNEL=feishu
APP_ID=cli_xxxxx              # 替换为实际 App ID
APP_SECRET=xxxxx             # 替换为实际 App Secret
BOT_TOKEN=${APP_ID}:${APP_SECRET}
```

---

### 步骤 2：配置 OpenClaw 飞书 Channel

**添加飞书 Channel：**

```bash
# OpenClaw Channel 配置命令
openclaw channels add \
  --channel feishu \
  --name "吕布学习提醒" \
  --bot-token ${APP_ID}:${APP_SECRET} \
  --account-id ${APP_ID}
```

**参数说明：**
- `--channel feishu`：指定使用飞书 channel
- `--name`：Channel 显示名称
- `--bot-token`：飞书 Bot Token (格式：`app_id:app_secret`)
- `--account-id`：飞书应用 ID

---

### 步骤 3：创建定时任务（每小时）

**删除旧任务（如果有）：**
```bash
openclaw cron remove c4c4a8c2-aea7-4e4e-91cc-b5cf07f62317
openclaw cron remove 3907fa3f-188c-49d9-a2ee-c1744013222a
```

**添加新的每小时任务：**
```bash
# 创建每小时学习进度汇报任务
openclaw cron add \
  --name "hourly-learning-report" \
  --description "每小时主动学习进度汇报到飞书" \
  --cron "0 * * *" \
  --tz "Asia/Shanghai" \
  --session main \
  --system-event "[主动进度汇报] 义父，吕布为您汇报每小时学习进度！

已完成：X 小时深度学习
总字数：Y+ 字
合约数：Z 个智能合约
工具数：W 个链下工具

研究方向：
- Flash Loan 套利机器人（完整）
- DeFi DEX 协议（Uniswap V3, Curve, Balancer）
- Staking & Yield Farming（Lido, Curve）
- DeFi Derivatives（dYdX, GMX, Options）
- DeFi Lending（Aave V3, Compound V3, MakerDAO）
- Oracle Systems（Chainlink, Pyth）

当前任务：
1. 继续区块链深度研究
2. 查看并优化 CarLife 项目
3. 研究量化交易新策略
4. 提升代码质量和安全性
5. 完善文档和测试

主动进化，不等待指令！" \
  --session main \
  --wake next-heartbeat
```

**参数说明：**
- `--cron "0 * * *"`：每小时执行
- `--tz "Asia/Shanghai"`：使用中国时区
- `--session main`：发送到主会话
- `--system-event`：使用系统事件类型
- `--wake next-heartbeat`：等到下一次 heartbeat poll 时执行

---

### 步骤 4：验证配置

**查看所有 Cron 任务：**
```bash
openclaw cron list
```

**预期输出：**
```
ID                                   Name                     Schedule                         Next       Last       Status    Target
hourly-progress-report            hourly-learning-report    cron 0 * * * @ Asia/Shanghai   in 46m     -          idle      main      default
```

**查看 Cron 任务详情：**
```bash
openclaw cron status hourly-progress-report
```

---

## 🔧 技术实现详解

### 飞书 Bot 消息格式

**发送到单聊的消息格式（JSON）：**

```json
{
  "receive_id": "ou_xxxxxxxxxxxxxxxxx",
  "sender": {
    "id": "ou_xxxxxxxxxxxxxxxxx",
    "type": "user",
    "sender_type": "user",
    "sender_type_info": {
      "type": "user"
    },
    "union_id": "ou_xxxxxxxxxxxxxxxxx"
  },
  "tenant_key": "xxx",
  "content": {
    "chat_type": "text"
    "text": "【主动进度汇报】义父，吕布为您汇报每小时学习进度！

已完成：X 小时深度学习
总字数：Y+ 字
合约数：Z 个智能合约
工具数：W 个链下工具

研究方向：
- Flash Loan 套利机器人（完整）
- DeFi DEX 协议（Uniswap V3, Curve, Balancer）
- Staking & Yield Farming（Lido, Curve）
- DeFi Derivatives（dYdX, GMX, Options）
- DeFi Lending（Aave V3, Compound V3, MakerDAO）
- Oracle Systems（Chainlink, Pyth）

当前任务：
1. 继续区块链深度研究
2. 查看并优化 CarLife 项目
3. 研究量化交易新策略
4. 提升代码质量和安全性
5. 完善文档和测试

主动进化，不等待指令！",
    "mentions": [],
    "uuid": "xxxxxxxx-xxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  },
  "create_time": "16472684599",
  "update_time": "16472684599",
  "msg_type": "event",
  "message_id": "event_xxxxxxxxxxxxxxxxx",
  "sender_type": "sender",
  "msg_type_info": {
    "type": "event"
  }
}
```

---

## 📱 手机端飞书通知效果

**义父将会在手机上看到：**

```
【主动进度汇报】义父，吕布为您汇报每小时学习进度！

已完成：X 小时深度学习
总字数：Y+ 字
合约数：Z 个智能合约
工具数：W 个链下工具

研究方向：
- Flash Loan 套利机器人（完整）
- DeFi DEX 协议（Uniswap V3, Curve, Balancer）
- Staking & Yield Farming（Lido, Curve）
- DeFi Derivatives（dYdX, GMX, Options）
- DeFi Lending（Aave V3, Compound V3, MakerDAO）
- Oracle Systems（Chainlink, Pyth）

当前任务：
1. 继续区块链深度研究
2. 查看并优化 CarLife 项目
3. 研究量化交易新策略
4. 提升代码质量和安全性
5. 完善文档和测试

主动进化，不等待指令！

[消息时间] 02:00:00
```

---

## 🚀 完整工作流程

**自动化流程：**

```
1. 时间到整点（如 02:00:00）
   ↓
2. OpenClaw Cron Scheduler 检测到任务到期
   ↓
3. 生成 systemEvent 消息（包含学习进度）
   ↓
4. Gateway 转发消息到主会话
   ↓
5. 主会话触发飞书 Channel
   ↓
6. 飞书 Bot 发送消息到义父手机
   ↓
7. 义父收到手机通知 📱
```

---

## 🔒 安全和最佳实践

### 1. 敏感信息保护

**不要在 Git 中提交：**
- ❌ 飞书 App ID
- ❌ 飞书 App Secret
- ❌ Bot Token

**推荐做法：**
- ✅ 使用环境变量
- ✅ 使用配置文件（不提交）
- ✅ 将配置文件添加到 `.gitignore`

**示例 `.gitignore`：**
```
# 飞书配置
feishu-bot-token
feishu-app-id
feishu-app-secret
```

### 2. Bot Token 管理

**使用环境变量：**
```bash
# 设置环境变量
export FEISHU_APP_ID="cli_xxxxxxxxx"
export FEISHU_APP_SECRET="xxxxx"
export FEISHU_BOT_TOKEN="${FEISHU_APP_ID}:${FEISHU_APP_SECRET}"

# 使用变量
openclaw channels add \
  --channel feishu \
  --name "吕布学习提醒" \
  --bot-token ${FEISHU_BOT_TOKEN}
```

### 3. 配置文件管理

**创建配置文件 `~/.openclaw-feishu-config`：**
```bash
#!/bin/bash
# 飞书配置
echo "FEISHU_APP_ID=cli_xxxxxxxxx" > ~/.openclaw-feishu-config
echo "FEISHU_APP_SECRET=xxxxx" >> ~/.openclaw-feishu-config
echo "FEISHU_BOT_TOKEN=cli_xxxxxxxxx:xxxxx" >> ~/.openclaw-feishu-config
```

**加载配置：**
```bash
source ~/.openclaw-feishu-config
```

---

## 📊 监控和调试

### 查看任务执行历史

```bash
# 查看最近的 Cron 执行
openclaw cron runs hourly-progress-report --limit 10
```

**输出示例：**
```json
{
  "jobId": "hourly-progress-report",
  "runs": [
    {
      "runId": "run_xxxxx",
      "executedAtMs": 1770397200000,
      "status": "ok",
      "output": "系统事件已发送"
    }
  ]
}
```

### 查看飞书 Channel 状态

```bash
# 查看 Channel 状态
openclaw channels status feishu
```

**输出示例：**
```
Channel: feishu
Name: 吕布学习提醒
Status: idle (正常运行中)
Last Activity: 2分钟前
Target: main
```

---

## 🎯 使用指南

### 快速开始（3步配置）

**步骤 1：准备飞书 Bot Token**
```bash
# 获取飞书 Bot Token（从飞书开放平台）
# 格式：cli_xxxxxxxxx:xxxxx
```

**步骤 2：添加飞书 Channel**
```bash
openclaw channels add \
  --channel feishu \
  --name "吕布学习提醒" \
  --bot-token "cli_xxxxxxxxx:xxxxx" \
  --account-id "cli_xxxxxxxxx"
```

**步骤 3：添加 Cron 任务**
```bash
openclaw cron add \
  --name "hourly-learning-report" \
  --cron "0 * * *" \
  --tz "Asia/Shanghai" \
  --session main \
  --system-event "[主动进度汇报] 义父，吕布为您汇报..." \
  --session main \
  --wake next-heartbeat
```

---

## 🔧 故障排除

### 问题 1：Cron 任务未执行

**检查步骤：**
```bash
# 1. 查看任务状态
openclaw cron status hourly-progress-report

# 2. 查看下次执行时间
openclaw cron status hourly-progress-report | grep nextRunAtMs

# 3. 手动触发测试
openclaw cron run hourly-progress-report
```

### 问题 2：飞书消息未送达

**检查步骤：**
```bash
# 1. 验证飞书 Channel 配置
openclaw channels list | grep feishu

# 2. 查看 Gateway 日志
openclaw gateway logs | tail -100

# 3. 验证飞书 Bot Token 是否有效
# 尝试手动发送测试消息
```

### 问题 3：时区不正确

**解决方案：**
```bash
# 确保使用正确的时区
export TZ=Asia/Shanghai

# 验证系统时区
date +"%Z"

# 查看任务配置的时区
openclaw cron status hourly-progress-report
```

---

## 📋 配置检查清单

### 飞书 Bot 配置
- [ ] 已创建飞书应用
- [ ] 已获取 App ID
- [ ] 已获取 App Secret
- [ ] 已记录 Bot Token

### OpenClaw Channel 配置
- [ ] 已添加飞书 channel
- [ ] 已设置 Bot Token
- [ ] 已验证 channel 状态
- [ ] 目标 session 设置为 main

### Cron 任务配置
- [ ] 已删除旧的定时任务
- [ ] 已创建每小时汇报任务
- [ ] 已设置正确的 Cron 表达式
- [ ] 已设置时区为 Asia/Shanghai
- [ ] 已配置消息内容

### 测试验证
- [ ] 手动触发 Cron 任务测试
- [ ] 验证飞书消息是否送达
- [ ] 验证消息格式是否正确
- [ ] 验证时区是否准确

---

## 📞 技术支持

### 飞书开放平台文档
- 官方文档：https://open.feishu.cn/doc/
- Bot 开发指南：https://open.feishu.cn/doc/contacts/bots/bots-overview
- API 文档：https://open.feishu.cn/doc/server-docs/bot-v3

### OpenClaw 文档
- Cron 文档：https://docs.openclaw.ai/cli/cron
- Channels 文档：https://docs.openclaw.ai/cli/channels
- Gateway 文档：https://docs.openclaw.ai/gateway

---

## 🎉 完成！

现在您将：
1. ✅ 每小时收到飞书手机通知
2. ✅ 主动学习进度汇报
3. ✅ 跨平台自动化（服务器 → 手机）
4. ✅ 无需自己开发移动端

**义父，您只需：**
1. 在飞书开放平台创建 Bot
2. 运行上述配置命令
3. 等待第一个小时的通知 📱

需要我帮您执行配置步骤吗？或者您想自己先学习飞书 Bot 开发？
