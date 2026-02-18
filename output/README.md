# 📰 Briefings - 每日科技简报系统

自动抓取 Hacker News、arXiv AI论文、精选 RSS 博客，生成每日简报并部署到 Cloudflare Pages。

## 🏗️ 项目结构

```
briefings/
├── src/
│   └── fetchers/
│       ├── info-aggregator.py    # Hacker News + arXiv 抓取
│       └── rss-briefing.py       # RSS 博客抓取
├── scripts/
│   └── deploy.sh                 # 部署脚本
├── output/                       # 生成的简报文件
├── config/                       # 配置文件
└── README.md
```

## 🚀 使用方法

### 1. 生成简报

```bash
# 生成 HN + arXiv 简报
python3 src/fetchers/info-aggregator.py

# 生成 RSS 简报
python3 src/fetchers/rss-briefing.py
```

### 2. 部署到网站

```bash
# 设置 GitHub Token
export GITHUB_TOKEN="ghp_xxx"

# 运行部署脚本
bash scripts/deploy.sh
```

## 📊 数据来源

### Hacker News
- 抓取 Top Stories
- 优先 AI/投资相关话题

### arXiv (10家顶级厂商)
- Google DeepMind
- OpenAI
- Anthropic
- Meta AI
- Microsoft Research
- NVIDIA
- Stanford
- UC Berkeley
- MIT
- CMU

### RSS 博客 (8个精选源)
- Simon Willison
- antirez
- Rachel by the Bay
- Overreacted
- Dynomight
- Sean Goedecke
- Mitchell Hashimoto
- Ken Shirriff

## 🌐 访问地址

- **主站**: https://briefing.zyi.info
- **备用**: https://life-briefing.pages.dev

## 📝 输出文件

生成的简报保存在 `output/` 目录：
- `info-briefing-YYYY-MM-DD.md` - HN + arXiv 简报
- `rss-briefing-YYYY-MM-DD.md` - RSS 博客简报

## ⏰ 自动化

通过 OpenClaw Cron 定时运行：
- 每天 09:00 自动生成并部署

## 🔧 依赖

```bash
pip install requests
```

---

*基于 Karpathy 推荐的私人博客列表构建*
