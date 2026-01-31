#!/bin/bash

# AI 领域热门项目每日推送脚本
# 每天早上 10 点自动运行，发送到飞书

CLAWDBOT_DIR="/root/clawd"
OUTPUT_FILE="$CLAWDBOT_DIR/memory/ai-trending-$(date +%Y-%m-%d).md"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始获取 AI 热门项目..." >> "$OUTPUT_FILE"

# 获取 GitHub AI 热门项目
RESULT=$(curl -s "https://api.github.com/search/repositories?q=topic:artificial-intelligence+language:python&sort=stars&order=desc&per_page=5" \
  -H "Accept: application/vnd.github.v3+json" \
  | jq -r '
    "🔥 今日 AI 热门项目 ($(date +%Y-%m-%d))\n\n",
    (if .items then
      .items[:5] | map(
        "## \(.name | ascii_upcase)\n" +
        "📝 \(.description // "暂无简介")\n" +
        "⭐ \(.stargazers_count) stars | 🍴 \(.forks_count) forks\n" +
        "🔗 \(.html_url)\n" +
        "🏷️ 语言: \(.language // "未知")\n" +
        "📅 更新: \(.updated_at | split("T")[0])\n"
      ) | join("\n---\n")
    else
      "获取失败，请稍后重试"
    end)
  ')

# 保存到文件
echo -e "$RESULT" > "$OUTPUT_FILE"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 结果已保存到 $OUTPUT_FILE" >> "$OUTPUT_FILE"
echo -e "$RESULT"

# 输出结果，供 Clawdbot 读取
echo -e "$RESULT"
