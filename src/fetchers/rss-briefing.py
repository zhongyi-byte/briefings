#!/usr/bin/env python3
"""
RSS 简报生成器
抓取精选私人博客 RSS
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# 精选 RSS 列表
RSS_FEEDS = [
    {"name": "Simon Willison", "url": "https://simonwillison.net/atom/everything/", 
     "category": "技术探索", "priority": 1, "type": "atom"},
    {"name": "antirez", "url": "http://antirez.com/rss", 
     "category": "系统编程", "priority": 1, "type": "rss"},
    {"name": "Rachel by the Bay", "url": "https://rachelbythebay.com/w/atom.xml", 
     "category": "系统故事", "priority": 1, "type": "atom"},
    {"name": "Overreacted", "url": "https://overreacted.io/rss.xml", 
     "category": "编程哲学", "priority": 1, "type": "rss"},
    {"name": "Dynomight", "url": "https://dynomight.net/feed.xml", 
     "category": "深度思考", "priority": 1, "type": "rss"},
    {"name": "Sean Goedecke", "url": "https://www.seangoedecke.com/rss.xml", 
     "category": "软件工程", "priority": 2, "type": "rss"},
    {"name": "Mitchell Hashimoto", "url": "https://mitchellh.com/feed.xml", 
     "category": "产品技术", "priority": 2, "type": "atom"},
    {"name": "Ken Shirriff", "url": "https://www.righto.com/feeds/posts/default", 
     "category": "硬件逆向", "priority": 2, "type": "rss"},
]

def fetch_feed(feed, cutoff):
    """获取单个 feed"""
    try:
        resp = requests.get(feed['url'], timeout=15)
        
        if feed['type'] == 'atom':
            entries = parse_atom(resp.content)
        else:
            entries = parse_rss(resp.content)
        
        articles = []
        for entry in entries:
            if entry.get('published'):
                try:
                    pub_text = entry['published'].replace('Z', '+00:00')
                    pub_date = datetime.fromisoformat(pub_text)
                    if pub_date >= cutoff:
                        articles.append({
                            **entry,
                            'source': feed['name'],
                            'category': feed['category'],
                            'priority': feed['priority'],
                            'date': pub_date
                        })
                except:
                    pass
        
        return {'feed': feed['name'], 'articles': articles, 'error': None}
    
    except Exception as e:
        return {'feed': feed['name'], 'articles': [], 'error': str(e)[:50]}

def parse_atom(content):
    """解析 Atom"""
    root = ET.fromstring(content)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    entries = []
    
    for entry in root.findall('.//atom:entry', ns)[:5]:
        title = entry.find('atom:title', ns)
        published = entry.find('atom:published', ns)
        link = entry.find('atom:link', ns)
        
        if title is not None and published is not None:
            entries.append({
                'title': title.text or 'No title',
                'url': link.get('href', '') if link is not None else '',
                'published': published.text
            })
    return entries

def parse_rss(content):
    """解析 RSS"""
    root = ET.fromstring(content)
    entries = []
    
    for item in root.findall('.//item')[:5]:
        title = item.find('title')
        pub_date = item.find('pubDate')
        link = item.find('link')
        
        if title is not None:
            entries.append({
                'title': title.text or 'No title',
                'url': link.text if link is not None else '',
                'published': pub_date.text if pub_date is not None else ''
            })
    return entries

def generate_briefing(articles):
    """生成简报"""
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    md = f"""# 📰 RSS 简报 - {date_str}

> 来源: 精选私人博客
> 抓取时间: {datetime.now().strftime('%H:%M')}
> 新文章: {len(articles)} 篇

---

## 🌟 最新文章

"""
    
    priority1 = [a for a in articles if a['priority'] == 1]
    for article in priority1[:15]:
        md += f"""### {article['title']}
- **来源**: [{article['source']}]({article['url']}) ({article['category']})
- **日期**: {article['date'].strftime('%Y-%m-%d %H:%M')}

"""
    
    if len(articles) > len(priority1):
        md += "## 🔧 其他文章\n\n"
        for article in articles[len(priority1):10]:
            md += f"- [{article['title']}]({article['url']}) - {article['source']} ({article['date'].strftime('%m-%d')})\n"
    
    md += f"""
---

*生成时间: {datetime.now().isoformat()}*
*来源: 精选私人博客 RSS ({len(RSS_FEEDS)} 个源)*
"""
    return md

def main():
    print("=" * 60)
    print("🤖 RSS 简报生成器 - 并行抓取")
    print("=" * 60)
    
    cutoff = datetime.now(timezone.utc) - timedelta(days=3)
    all_articles = []
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(fetch_feed, feed, cutoff): feed for feed in RSS_FEEDS}
        
        for future in as_completed(futures):
            result = future.result()
            if result['error']:
                print(f"🔍 {result['feed']}... ❌ {result['error']}")
            else:
                print(f"🔍 {result['feed']}... ✅ {len(result['articles'])} 篇")
                all_articles.extend(result['articles'])
    
    all_articles.sort(key=lambda x: x['date'], reverse=True)
    
    print(f"\n📊 找到 {len(all_articles)} 篇新文章")
    
    briefing = generate_briefing(all_articles)
    
    # 保存
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f"rss-briefing-{datetime.now().strftime('%Y-%m-%d')}.md"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(briefing)
    
    print(f"💾 简报已保存: {output_path}")

if __name__ == "__main__":
    main()
