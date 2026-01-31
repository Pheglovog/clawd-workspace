#!/bin/bash

# 获取 GitHub AI 领域热门项目
# 使用 GitHub Trending API

echo "正在获取 AI 领域热门项目..."

# 获取 AI 相关的 trending repos
# 使用 GitHub API 获取 trending repositories
curl -s "https://api.github.com/search/repositories?q=topic:artificial-intelligence+language:python&sort=stars&order=desc&per_page=5" \
  -H "Accept: application/vnd.github.v3+json" \
  | jq -r '
    "🔥 今日 AI 热门项目\n",
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
  '
