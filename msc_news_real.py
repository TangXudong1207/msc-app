### msc_news_real.py (RSS Grounding Edition) ###

import msc_lib as msc
import msc_config as config
import feedparser
import json
import time
import random

# ==========================================
# 📡 真实信号源 (RSS Feeds)
# ==========================================
# 选取全球最具代表性的英文 RSS 源 (中文源容易有反爬虫)
RSS_SOURCES = {
    "World_General": "http://feeds.bbci.co.uk/news/world/rss.xml", # BBC World
    "Tech_Frontier": "https://feeds.feedburner.com/TheHackersNews", # Tech
    "Science_Nature": "https://www.sciencedaily.com/rss/matter_energy.xml", # Science
    "Global_Economy": "https://www.cnbc.com/id/10000664/device/rss/rss.html", # Finance
    "Middle_East": "https://www.aljazeera.com/xml/rss/all.xml" # Al Jazeera
}

# ==========================================
# 🗺️ 坐标字典 (Geo-Mapping)
# ==========================================
GEO_DB = {
    "USA": {"lat": 38.90, "lon": -77.03}, "China": {"lat": 39.90, "lon": 116.40},
    "Russia": {"lat": 55.75, "lon": 37.61}, "UK": {"lat": 51.50, "lon": -0.12},
    "France": {"lat": 48.85, "lon": 2.35}, "Germany": {"lat": 52.52, "lon": 13.40},
    "Japan": {"lat": 35.67, "lon": 139.65}, "India": {"lat": 28.61, "lon": 77.20},
    "Brazil": {"lat": -15.82, "lon": -47.92}, "Canada": {"lat": 45.42, "lon": -75.69},
    "Australia": {"lat": -35.28, "lon": 149.13}, "South Korea": {"lat": 37.56, "lon": 126.97},
    "Italy": {"lat": 41.90, "lon": 12.49}, "Turkey": {"lat": 39.93, "lon": 32.85},
    "Saudi Arabia": {"lat": 24.71, "lon": 46.67}, "South Africa": {"lat": -25.74, "lon": 28.22},
    "Argentina": {"lat": -34.60, "lon": -58.38}, "Mexico": {"lat": 19.43, "lon": -99.13},
    "Indonesia": {"lat": -6.20, "lon": 106.84}, "Israel": {"lat": 31.76, "lon": 35.21},
    "Iran": {"lat": 35.68, "lon": 51.38}, "Ukraine": {"lat": 50.45, "lon": 30.52},
    "Gaza": {"lat": 31.50, "lon": 34.46}, "Taiwan": {"lat": 25.03, "lon": 121.56},
    "Global": {"lat": 0, "lon": 0}
}

def get_coords(name):
    for k, v in GEO_DB.items():
        if k.lower() in name.lower() or name.lower() in k.lower(): return v
    return {"lat": random.uniform(-40, 60), "lon": random.uniform(-150, 150)} # 兜底

def fetch_real_news_auto():
    """
    1. 爬取真实 RSS
    2. 让 AI 阅读并提取张力
    3. 存入数据库
    """
    all_logs = []
    
    # 1. 采集阶段
    raw_articles = []
    for src_name, url in RSS_SOURCES.items():
        try:
            feed = feedparser.parse(url)
            # 每个源取前 2 条最新新闻
            for entry in feed.entries[:2]:
                raw_articles.append({
                    "title": entry.title,
                    "summary": entry.get('summary', '')[:150], # 截断
                    "source": src_name
                })
        except: continue
        
    if not raw_articles:
        return ["⚠️ RSS Fetch Failed. Check internet connection."]

    # 2. 分析阶段 (批量处理，省 Token)
    # 把所有标题打包发给 AI
    titles_text = "\n".join([f"- {a['title']}" for a in raw_articles])
    
    prompt = f"""
    [Task: Analyze Real News Tension]
    Below are real-time news headlines. 
    For each, identify the Key Country/Location and the underlying Value Tension.
    
    News List:
    {titles_text}
    
    Output JSON List:
    [
      {{
        "title": "Exact headline from input",
        "tension": "Value A vs Value B",
        "dimension": "Conflict/Rationality/etc (Pick from MSC Spectrum)",
        "origin": "Country Name",
        "intensity": 0.8
      }}
    ]
    """
    
    # 调用 AI (优先 Google)
    response = msc.call_ai_api(prompt, use_google=True)
    
    # 3. 解析与存储
    analyzed_list = response if isinstance(response, list) else response.get('news', [])
    # 兼容处理
    if not analyzed_list and isinstance(response, dict):
        for v in response.values(): 
            if isinstance(v, list): analyzed_list = v; break
            
    for item in analyzed_list:
        try:
            title = item.get('title', 'Unknown')
            tension = item.get('tension', 'Unknown')
            dim = item.get('dimension', 'Structure')
            origin = item.get('origin', 'Global')
            
            color = config.SPECTRUM.get(dim, "#E0E0E0")
            origin_loc = get_coords(origin)
            
            content = f"[{dim}] {title}"
            node_data = {
                "c_score": 0.9,
                "care_point": tension,
                "insight": f"{title} ({origin})",
                "meaning_layer": "RSS_Real",
                "keywords": [dim, color, "RealNews"],
                "location": origin_loc,
                "intensity": item.get('intensity', 0.5)
            }
            
            # 向量化
            vec = msc.get_embedding(content)
            msc.save_node("World_Observer", content, node_data, "News_Stream", vec)
            
            all_logs.append(f"📡 {origin}: {tension} ({dim})")
            
        except: continue
        
    return all_logs

# 保留旧接口兼容性
def scan_grid_tier(a,b): return []
