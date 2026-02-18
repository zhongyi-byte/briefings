#!/bin/bash
# 简报自动部署脚本
# 部署到 briefing.zyi.info (Cloudflare Pages)

set -e

echo "🚀 部署简报到 briefing.zyi.info"
echo "================================="
echo ""

# 配置
BRIEFINGS_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LIFE_BRIEFING_DIR="/home/ubuntu/workspace/life-briefing"
TODAY=$(date '+%Y-%m-%d')

# 从环境变量读取 GitHub Token
if [ -z "$GITHUB_TOKEN" ]; then
    # 尝试从 .env 文件读取
    if [ -f "$HOME/.openclaw/.env" ]; then
        export $(grep -v '^#' "$HOME/.openclaw/.env" | xargs 2>/dev/null)
    fi
fi

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ 错误: GITHUB_TOKEN 未设置"
    exit 1
fi

echo "📅 今日日期: $TODAY"
echo "📁 源目录: $BRIEFINGS_DIR"
echo ""

# 查找简报文件的优先级顺序
echo "🔍 查找简报文件..."

TODAY_BRIEFING=""

# 优先级 1: info-briefing-$TODAY.md (完整简报含 arXiv)
if [ -f "$BRIEFINGS_DIR/output/info-briefing-$TODAY.md" ]; then
    TODAY_BRIEFING="$BRIEFINGS_DIR/output/info-briefing-$TODAY.md"
    echo "   ✅ 使用完整简报: info-briefing-$TODAY.md"

# 优先级 2: rss-briefing-$TODAY.md (RSS简报)
elif [ -f "$BRIEFINGS_DIR/output/rss-briefing-$TODAY.md" ]; then
    TODAY_BRIEFING="$BRIEFINGS_DIR/output/rss-briefing-$TODAY.md"
    echo "   ⚠️ 使用 RSS 简报: rss-briefing-$TODAY.md"

# 优先级 3: 任意日期的简报
else
    INFO_BRIEFING=$(ls -t $BRIEFINGS_DIR/output/info-briefing-*.md 2>/dev/null | head -1)
    if [ -n "$INFO_BRIEFING" ]; then
        TODAY_BRIEFING="$INFO_BRIEFING"
        echo "   ⚠️ 使用历史完整简报: $(basename $INFO_BRIEFING)"
    else
        RSS_BRIEFING=$(ls -t $BRIEFINGS_DIR/output/rss-briefing-*.md 2>/dev/null | head -1)
        if [ -n "$RSS_BRIEFING" ]; then
            TODAY_BRIEFING="$RSS_BRIEFING"
            echo "   ⚠️ 使用历史 RSS 简报: $(basename $RSS_BRIEFING)"
        else
            echo "   ❌ 未找到简报文件"
            exit 1
        fi
    fi
fi

echo ""
echo "📄 选定简报: $(basename $TODAY_BRIEFING)"

# 进入 life-briefing 目录
cd "$LIFE_BRIEFING_DIR"

# 配置 Git
git config user.email "zhong4092@gmail.com"
git config user.name "zhongyi-byte"
git remote set-url origin "https://zhongyi-byte:${GITHUB_TOKEN}@github.com/zhongyi-byte/life-briefing.git"

# 拉取最新代码
echo ""
echo "1️⃣ 拉取最新代码..."
git pull origin main

# 复制简报到项目目录
echo ""
echo "2️⃣ 复制简报文件..."

# 统一复制为 $TODAY.md (方便网站访问)
cp "$TODAY_BRIEFING" "briefings/$TODAY.md"
echo "   ✅ 已复制为 briefings/$TODAY.md"

# 同时保留原始文件名
if [ "$(basename $TODAY_BRIEFING)" != "$TODAY.md" ]; then
    cp "$TODAY_BRIEFING" "briefings/$(basename $TODAY_BRIEFING)"
    echo "   ✅ 已保留原始文件: briefings/$(basename $TODAY_BRIEFING)"
fi

# 提交并推送
echo ""
echo "3️⃣ 提交到 GitHub..."
git add briefings/
git commit -m "Add briefing: $TODAY - $(date '+%H:%M')" || echo "   无变更需要提交"
git push origin main

echo ""
echo "✅ 简报已部署！"
echo ""
echo "🌐 访问地址:"
echo "   https://briefing.zyi.info"
echo "   https://life-briefing.pages.dev"
echo ""
echo "⏰ 部署时间: $(date '+%H:%M:%S')"
