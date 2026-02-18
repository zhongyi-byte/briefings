#!/usr/bin/env python3
"""
Hacker News 简报生成器
抓取 Top Stories，优先 AI/投资相关话题
"""

import json
import urllib.request
import socket
from datetime import datetime
from pathlib import Path

socket.setdefaulttimeout(15)

AI_KEYWORDS = [
    'ai', 'llm', 'gpt', 'claude', 'openai', 'anthropic', 'gemini', 
    'machine learning', 'deep learning', 'neural',
    'investment', 'trading', 'crypto', 'stock', 'market',
    'startup', 'venture', 'funding'
]

def fetch_hn(limit=10):
    """获取 Hacker News Top Stories"""
    print("🔍 获取 Hacker News...")
    
    try:
        url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            story_ids = json.loads(r.read())[:limit * 2]
        
        stories = []
        for sid in story_ids[:limit]:
            try:
                surl = f"https://hacker-news.firebaseio.com/v0/item/{sid}.json"
                req = urllib.request.Request(surl, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=5) as r:
                    story = json.loads(r.read())
                
                if story and story.get('title'):
                    title = story['title'].lower()
                    score = story.get('score', 0)
                    
                    is_ai = any(kw in title for kw in AI_KEYWORDS)
                    priority = 1 if is_ai else 2
                    
                    stories.append({
                        'title': story['title'],
                        'url': story.get('url', f"https://news.ycombinator.com/item?id={sid}"),
                        'score': score,
                        'comments': story.get('descendants', 0),
                        'priority': priority,
                        'is_ai': is_ai
                    })
            except:
                continue
        
        stories.sort(key=lambda x: (x['priority'], -x['score']))
        print(f"   ✅ {len(stories)} 条")
        return stories
    
    except Exception as e:
        print(f"   ❌ {e}")
        return []

def generate_briefing(stories):
    """生成 HN 简报"""
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    md = f"""# 🔥 Hacker News 简报 - {date_str}

> 来源: Hacker News Top Stories
> 生成时间: {datetime.now().strftime('%H:%M')}
> 共 {len(stories)} 条

---

"""
    
    ai_stories = [s for s in stories if s.get('is_ai')]
    other_stories = [s for s in stories if not s.get('is_ai')]
    
    if ai_stories:
        md += "## 🤖 AI/投资相关\n\n"
        for s in ai_stories:
            md += f"- **[{s['title']}]({s['url']})**  \n"
            md += f"  💬 {s['comments']} | ⬆️ {s['score']}\n\n"
    
    if other_stories:
        md += "## 📰 其他热门\n\n"
        for s in other_stories[:6]:
            md += f"- [{s['title']}]({s['url']})  \n"
            md += f"  💬 {s['comments']} | ⬆️ {s['score']}\n\n"
    
    md += f"""---

*生成时间: {datetime.now().isoformat()}*
*来源: [Hacker News](https://news.ycombinator.com)*
"""
    return md

def main():
    print("=" * 60)
    print("🔥 Hacker News 简报生成器")
    print("=" * 60)
    print()
    
    stories = fetch_hn()
    
    if not stories:
        print("❌ 未获取到数据")
        return
    
    briefing = generate_briefing(stories)
    
    # 保存
    output_dir = Path(__file__).parent.parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f"hn-briefing-{datetime.now().strftime('%Y-%m-%d')}.md"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(briefing)
    
    print(f"\n💾 已保存: {output_path}")
    print(f"📊 AI相关: {len([s for s in stories if s['is_ai']])} 条")

if __name__ == "__main__":
    main()
