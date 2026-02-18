#!/usr/bin/env python3
"""
智能信息聚合简报 - 极简可靠版
抓取 Hacker News + arXiv AI论文
"""

import json
import urllib.request
import urllib.parse
import socket
from datetime import datetime, timedelta
from pathlib import Path

# 全局超时
socket.setdefaulttimeout(15)

def fetch_hn(limit=8):
    """获取 Hacker News"""
    print("🔍 获取 Hacker News...")
    try:
        url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            story_ids = json.loads(r.read())[:limit * 2]
        
        stories = []
        ai_kw = ['ai', 'llm', 'gpt', 'claude', 'openai', 'machine learning', 'investment', 'trading', 'crypto']
        
        for sid in story_ids[:limit]:
            try:
                surl = f"https://hacker-news.firebaseio.com/v0/item/{sid}.json"
                req = urllib.request.Request(surl, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=5) as r:
                    story = json.loads(r.read())
                
                if story and story.get('title'):
                    title = story['title'].lower()
                    score = story.get('score', 0)
                    
                    # AI/投资相关优先
                    is_ai = any(k in title for k in ai_kw)
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
        return stories[:8]
    except Exception as e:
        print(f"   ❌ {e}")
        return []

def fetch_arxiv():
    """获取 arXiv AI论文 - 10家顶级厂商"""
    print("🔍 获取 arXiv AI论文...")
    
    companies = [
        ("Google DeepMind", "Google OR DeepMind"),
        ("OpenAI", "OpenAI"),
        ("Anthropic", "Anthropic"),
        ("Meta AI", '"Meta AI" OR "FAIR"'),
        ("Microsoft Research", '"Microsoft Research"'),
        ("NVIDIA", "NVIDIA"),
        ("Stanford", "Stanford"),
        ("UC Berkeley", '"UC Berkeley" OR "Berkeley"'),
        ("MIT", "MIT CSAIL"),
        ("CMU", '"Carnegie Mellon"')
    ]
    
    papers = []
    yesterday = (datetime.now() - timedelta(days=2)).strftime('%Y%m%d')
    
    for company, query in companies:
        try:
            url = f"http://export.arxiv.org/api/query?search_query=au:{urllib.parse.quote(query)}+OR+all:{urllib.parse.quote(query)}&start=0&max_results=3&sortBy=submittedDate&sortOrder=descending"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as r:
                data = r.read().decode('utf-8')
            
            # 简单解析
            entries = data.split('<entry>')[1:]
            for entry in entries[:2]:
                try:
                    title_start = entry.find('<title>') + 7
                    title_end = entry.find('</title>')
                    title = entry[title_start:title_end].strip()
                    title = title.replace('\n', ' ')
                    
                    url_start = entry.find('<id>http') + 4
                    url_end = entry.find('</id>')
                    paper_url = entry[url_start:url_end].strip()
                    
                    date_start = entry.find('<published>') + 11
                    date_end = entry.find('</published>')
                    pub_date = entry[date_start:date_end].strip()[:10]
                    
                    if 'T' in pub_date:
                        pub_date = pub_date.replace('-', '')
                        if int(pub_date) >= int(yesterday):
                            papers.append({
                                'title': title,
                                'url': paper_url,
                                'company': company,
                                'date': pub_date
                            })
                except:
                    continue
        except Exception as e:
            print(f"   {company}: {str(e)[:30]}")
            continue
    
    print(f"   ✅ {len(papers)} 篇")
    return papers

def generate_briefing(hn_stories, arxiv_papers):
    """生成简报"""
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    md = f"""# 📰 AI简报 - {date_str}

> 来源: Hacker News + arXiv (10家顶级厂商)
> 生成时间: {datetime.now().strftime('%H:%M')}

---

## 🔥 Hacker News 热门

"""
    
    ai_stories = [s for s in hn_stories if s.get('is_ai')]
    other_stories = [s for s in hn_stories if not s.get('is_ai')]
    
    if ai_stories:
        md += "### AI/投资相关\n\n"
        for s in ai_stories:
            md += f"- **[{s['title']}]({s['url']})**  ")
            md += f"  💬 {s['comments']} | ⬆️ {s['score']}\n\n"
    
    if other_stories:
        md += "### 其他热门\n\n"
        for s in other_stories[:5]:
            md += f"- [{s['title']}]({s['url']})  ")
            md += f"  💬 {s['comments']} | ⬆️ {s['score']}\n\n"
    
    md += "\n## 📄 最新 arXiv 论文\n\n"
    
    if arxiv_papers:
        # 按公司分组
        by_company = {}
        for p in arxiv_papers:
            c = p['company']
            if c not in by_company:
                by_company[c] = []
            by_company[c].append(p)
        
        for company, papers in sorted(by_company.items()):
            md += f"### {company}\n\n"
            for p in papers[:2]:
                md += f"- [{p['title'][:80]}...]({p['url']})\n"
            md += "\n"
    else:
        md += "暂无新论文\n\n"
    
    md += f"""---

*生成时间: {datetime.now().isoformat()}*
*来源: Hacker News API + arXiv API*
"""
    
    return md

def main():
    print("=" * 60)
    print("🤖 AI信息聚合简报生成器")
    print("=" * 60)
    print()
    
    hn = fetch_hn()
    papers = fetch_arxiv()
    
    print()
    print("=" * 60)
    print(f"📊 总计: HN {len(hn)} 条, 论文 {len(papers)} 篇")
    print("=" * 60)
    
    briefing = generate_briefing(hn, papers)
    
    # 保存
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f"info-briefing-{datetime.now().strftime('%Y-%m-%d')}.md"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(briefing)
    
    print(f"\n💾 已保存: {output_path}")

if __name__ == "__main__":
    main()
