### msc_news.py ###

import streamlit as st
import msc_lib as msc
import random
import time

# 模拟热点
HOTSPOTS = [
    {"loc": "Silicon Valley", "lat": 37.38, "lon": -122.08, "topic": "AI Consciousness"},
    {"loc": "Middle East", "lat": 31.04, "lon": 34.85, "topic": "Border Conflict"},
    {"loc": "Scandinavia", "lat": 60.47, "lon": 8.46, "topic": "Climate Anxiety"},
    {"loc": "East Asia", "lat": 35.86, "lon": 104.19, "topic": "Work-Life Balance"},
    {"loc": "Africa", "lat": 9.10, "lon": 18.28, "topic": "Resource Justice"}
]

def fetch_and_digest_news():
    logs = []
    for spot in HOTSPOTS:
        raw_news = f"Breaking news from {spot['loc']} about {spot['topic']}..."
        
        # 提取张力
        analysis = msc.analyze_tension(raw_news)
        
        if analysis and "tension_pair" in analysis:
            tension = analysis['tension_pair']
            color = analysis.get('emotional_color', 'Blue')
            
            content = f"Tension: {tension[0]} vs {tension[1]}"
            insight = f"Global reflection on {spot['topic']}"
            
            node_data = {
                "c_score": 0.8, "n_score": 0.8, "m_score": 0.8,
                "care_point": f"{tension[0]} vs {tension[1]}",
                "insight": insight,
                "meaning_layer": "Global Tension",
                "keywords": [spot['topic'], color],
                "location": {"lat": spot['lat'], "lon": spot['lon']}
            }
            
            # 存入数据库
            vec = msc.get_embedding(content)
            msc.save_node("World_Observer", content, node_data, "News", vec)
            
            logs.append(f"🌍 {spot['loc']}: [{tension[0]} vs {tension[1]}] ({color})")
            
        time.sleep(0.5)
    return logs
