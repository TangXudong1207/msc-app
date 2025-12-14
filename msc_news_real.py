### msc_news_real.py (真实新闻张力引擎) ###

import feedparser
import msc_lib as msc
import time
import random
from geopy.geocoders import Nominatim

# 1. 真实数据源 (可扩充)
RSS_FEEDS = {
    "Tech_Anxiety": "https://feeds.feedburner.com/TheHackersNews", # 技术与安全
    "Global_Conflict": "http://feeds.bbci.co.uk/news/world/rss.xml", # 全球局势
    "Human_Condition": "https://www.psychologytoday.com/us/feed/essential-reads", # 心理状态
}

# 初始化地理编码器 (用于把 'London' 变成坐标)
geolocator = Nominatim(user_agent="msc_agent")

def get_coordinates(location_name):
    try:
        # 为了不频繁调用 API 被封，这里加个随机缓存或简化处理
        # 实际生产环境应建立缓存库
        loc = geolocator.geocode(location_name, timeout=5)
        if loc: return [loc.longitude, loc.latitude]
    except: pass
    # 如果失败，随机一个坐标 (MVP 阶段兜底)
    return [random.uniform(-150, 150), random.uniform(-40, 60)]

def fetch_real_news(limit=3):
    """
    抓取并分析新闻，返回日志
    """
    logs = []
    
    for category, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        
        # 只取前 N 条
        for entry in feed.entries[:limit]:
            title = entry.title
            summary = entry.get('summary', '')[:200] # 截断摘要
            
            # 1. AI 分析张力 (调用 msc_lib)
            # prompt = f"Analyze tension in: {title}. {summary}"
            analysis = msc.analyze_tension(f"{title}\n{summary}")
            
            if analysis and "tension_pair" in analysis:
                pair = analysis['tension_pair']
                color = analysis.get('emotional_color', 'Blue') # AI 决定的颜色
                intensity = analysis.get('intensity', 0.5)
                
                # 2. 确定地点 (让 AI 从新闻里提取地点，如果没有则归属到 'Cyberspace')
                # 这里简化处理，让 AI 返回 location 名字，然后我们转坐标
                # 暂时用随机坐标模拟分布，以免 geopy 报错卡顿
                coords = [random.uniform(-150, 150), random.uniform(-40, 60)]
                
                # 3. 存入数据库 (World_Observer)
                content = f"[{category}] {title}"
                node_data = {
                    "c_score": 0.9, # 新闻权重高
                    "care_point": f"{pair[0]} vs {pair[1]}", # 核心张力
                    "insight": f"Real-world tension detected: {title}",
                    "meaning_layer": "Global Pulse",
                    "keywords": [category, color, "RealNews"],
                    "location": {"lat": coords[1], "lon": coords[0]}, # 存入坐标
                    "intensity": intensity # 粒子大小
                }
                
                # 生成向量 (Vertex / Mock)
                vec = msc.get_embedding(content)
                msc.save_node("World_Observer", content, node_data, "News_Stream", vec)
                
                logs.append(f"📡 {category}: {pair[0]} <--> {pair[1]} ({color})")
                
            time.sleep(0.5) # 礼貌爬取
            
    return logs
