#!/usr/bin/env python3
"""
arXiv AI论文简报生成器
抓取10家顶级厂商的最新论文
"""

import urllib.request
import urllib.parse
import socket
import re
from datetime import datetime, timedelta
from pathlib import Path

socket.setdefaulttimeout(15)

# 10家顶级厂商
TOP_COMPANIES = [
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

def fetch_arxiv_company(company, query):
    """获取单个公司的论文"""
    papers = []
    yesterday = (datetime.now() - timedelta(days=2)).strftime('%Y%m%d')
    
    try:
        url = f"http://export.arxiv.org/api/query?search_query=au:{urllib.parse.quote(query)}+OR+all:{urllib.parse.quote(query)}&start=0&max_results=3&sortBy=submittedDate&sortOrder=descending"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = r.read().decode('utf-8')
        
        entries = data.split('<entry>')[1:]
        for entry in entries[:2]:
            try:
                # 提取标题
                title_match = re.search(r'<title>(.+?)</title>', entry, re.DOTALL)
                if not title_match:
                    continue
                title = title_match.group(1).strip()
                title = title.replace('\n', ' ').replace('  ', ' ')
                
                # 提取URL
                url_match = re.search(r'<id>(http://arxiv.org/abs/\d+\.\d+)</id>', entry)
                paper_url = url_match.group(1) if url_match else ""
                
                # 提取日期
                date_match = re.search(r'<published>(\d{4}-\d{2}-\d{2})', entry)
                pub_date = date_match.group(1) if date_match else ""
                
                # 提取作者
                authors = re.findall(r'<name>(.+?)</name>', entry)
                
                if pub_date:
                    papers.append({
                        'title': title,
                        'url': paper_url,
                        'company': company,
                        'date': pub_date,
                        'authors': authors[:3]
                    })
            except:
                continue
        
        return papers
    
    except Exception as e:
        print(f"   {company}: {str(e)[:30]}")
        return []

def fetch_arxiv():
    """获取所有公司论文"""
    print("🔍 获取 arXiv AI论文...")
    print(f"   监控 {len(TOP_COMPANIES)} 家机构")
    
    all_papers = []
    for company, query in TOP_COMPANIES:
        papers = fetch_arxiv_company(company, query)
        if papers:
            print(f"   ✅ {company}: {len(papers)} 篇")
            all_papers.extend(papers)
        else:
            print(f"   ⚠️ {company}: 无新论文")
    
    print(f"\n   总计: {len(all_papers)} 篇")
    return all_papers

def generate_briefing(papers):
    """生成 arXiv 简报"""
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    md = f"""# 📄 arXiv AI论文简报 - {date_str}

> 来源: arXiv (10家顶级厂商)
> 生成时间: {datetime.now().strftime('%H:%M')}
> 共 {len(papers)} 篇新论文

---

"""
    
    if not papers:
        md += "今日暂无新论文\n\n"
    else:
        # 按公司分组
        by_company = {}
        for p in papers:
            c = p['company']
            if c not in by_company:
                by_company[c] = []
            by_company[c].append(p)
        
        for company, company_papers in sorted(by_company.items()):
            md += f"## {company}\n\n"
            for p in company_papers:
                md += f"- **[{p['title'][:80]}]({p['url']})**\n"
                if p['authors']:
                    md += f"  👤 {', '.join(p['authors'])}\n"
                md += f"  📅 {p['date']}\n\n"
    
    md += f"""---

*生成时间: {datetime.now().isoformat()}*
*来源: [arXiv](https://arxiv.org)*

监控机构:
"""
    for company, _ in TOP_COMPANIES:
        md += f"- {company}\n"
    
    return md

def main():
    print("=" * 60)
    print("📄 arXiv AI论文简报生成器")
    print("=" * 60)
    print()
    
    papers = fetch_arxiv()
    briefing = generate_briefing(papers)
    
    # 保存
    output_dir = Path(__file__).parent.parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f"arxiv-briefing-{datetime.now().strftime('%Y-%m-%d')}.md"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(briefing)
    
    print(f"\n💾 已保存: {output_path}")

if __name__ == "__main__":
    main()
