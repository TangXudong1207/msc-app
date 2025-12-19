### msc_sim.py ###
import streamlit as st
import msc_lib as msc
import random
import time
import json
import numpy as np

# ==========================================
# 🌍 0. 地理创世纪：文明坐标库
# ==========================================
GLOBAL_CITIES = {
    "Tokyo": [35.6762, 139.6503],
    "New York": [40.7128, -74.0060],
    "London": [51.5074, -0.1278],
    "Paris": [48.8566, 2.3522],
    "Shanghai": [31.2304, 121.4737],
    "Berlin": [52.5200, 13.4050],
    "Reykjavik": [64.1466, -21.9426], # 冰岛，适合孤独的灵魂
    "Buenos Aires": [-34.6037, -58.3816],
    "Cape Town": [-33.9249, 18.4241],
    "Sydney": [-33.8688, 151.2093],
    "Mumbai": [19.0760, 72.8777],
    "Moscow": [55.7558, 37.6173],
    "Cairo": [30.0444, 31.2357],
    "Lhasa": [29.6520, 91.1721]       # 拉萨，适合神秘主义者
}

# ==========================================
# 🎭 1. 设定：灵魂原型 (Archetypes)
# ==========================================
ARCHETYPES = [
    {
        "nickname": "Kafka_Bot", 
        "style": "Existence is bureaucracy. Anxiety. The absurdity of modern life.", 
        "radar": {"Care": 8, "Reflection": 9, "Agency": 2, "Curiosity": 5, "Coherence": 4, "Empathy": 7, "Aesthetic": 6}
    },
    {
        "nickname": "Elon_Bot", 
        "style": "Mars, Rockets, Future, Engineering, Accelerationism, Cold Logic.", 
        "radar": {"Care": 3, "Agency": 10, "Curiosity": 9, "Coherence": 8, "Reflection": 5, "Empathy": 2, "Aesthetic": 5}
    },
    {
        "nickname": "Rumi_Bot", 
        "style": "Sufi poet. Love, Soul, Divine connection, The moon, The heart.", 
        "radar": {"Care": 9, "Empathy": 10, "Aesthetic": 9, "Reflection": 8, "Coherence": 6, "Agency": 4, "Curiosity": 5}
    },
    {
        "nickname": "Nietzsche_Bot", 
        "style": "Will to Power. God is dead. Overman. Sharp critique of weakness.", 
        "radar": {"Care": 4, "Agency": 9, "Reflection": 8, "Coherence": 7, "Empathy": 1, "Aesthetic": 8, "Curiosity": 7}
    },
    {
        "nickname": "Alice_Sim", 
        "style": "A normal observer. Likes coffee, rain, and simple observations.", 
        "radar": {"Care": 6, "Empathy": 6, "Agency": 5, "Reflection": 5, "Curiosity": 6, "Aesthetic": 7, "Coherence": 5}
    }
]

TOPICS = [
    "The meaning of work", "Loneliness in digital age", "The cost of freedom",
    "Artificial Consciousness", "The beauty of decay", "True Love", "Urban isolation"
]

# ==========================================
# 🛠️ 2. 造人逻辑 (Genesis)
# ==========================================
def create_virtual_citizens():
    created_count = 0
    logs = []
    
    for char in ARCHETYPES:
        username = f"sim_{char['nickname'].lower()}"
        # 随机分配一个城市
        city_name, coords = random.choice(list(GLOBAL_CITIES.items()))
        
        # 尝试注册
        if msc.add_user(username, "123456", char['nickname'], city_name):
            # 注入灵魂参数 (Radar)
            msc.update_radar_score(username, char['radar'])
            created_count += 1
            logs.append(f"✅ Created: {char['nickname']} in {city_name}")
        else:
            # 如果已存在，也要更新一下 Radar，防止是旧数据
            msc.update_radar_score(username, char['radar'])
            logs.append(f"🔄 Updated: {char['nickname']} (Already exists)")
            
    return logs

# ==========================================
# 💉 3. 思想注入 (Thought Injection)
# ==========================================
def inject_thoughts(count=1):
    logs = []
    # 获取所有以 sim_ 开头的用户
    all_users = msc.get_all_users("admin")
    sim_users = [u for u in all_users if u['username'].startswith("sim_")]
    
    if not sim_users:
        return ["⚠️ No simulation users found. Run 'Genesis' first."]

    # 循环生成
    for i in range(count):
        # 随机选一个虚拟人
        user_record = random.choice(sim_users)
        username = user_record['username']
        nickname = user_record['nickname']
        
        # 找到他的设定
        archetype = next((a for a in ARCHETYPES if a['nickname'] == nickname), ARCHETYPES[0])
        
        # 1. 确定地理位置 (在他所在的城市附近稍微随机偏移一点，模拟他在城市里移动)
        # 这里需要查一下他的城市，简化起见，我们随机选一个城市
        city_name, center_coords = random.choice(list(GLOBAL_CITIES.items()))
        lat = center_coords[0] + random.uniform(-0.05, 0.05)
        lon = center_coords[1] + random.uniform(-0.05, 0.05)
        location_data = {"lat": lat, "lon": lon, "city": city_name}
        
        # 2. AI 生成内容
        topic = random.choice(TOPICS)
        # 注意：这里强制要求 AI 输出 JSON
        prompt = f"""
        Role: {archetype['style']}
        Topic: {topic}
        Task: Write a short, profound thought (Max 20 words).
        Output JSON: {{ "content": "..." }}
        """
        
        response = msc.call_ai_api(prompt)
        content = response.get('content', '')
        
        if content:
            # 3. 分析 + 向量化
            analysis = msc.analyze_meaning_background(content)
            analysis['location'] = location_data # 注入位置
            if "care_point" not in analysis: analysis['care_point'] = content[:10]
            analysis['valid'] = True # 强制有效

            vec = msc.get_embedding(content)
            
            # 4. 存入数据库
            success, msg = msc.save_node(username, content, analysis, "Genesis_Sim", vec)
            
            if success:
                logs.append(f"🧠 {nickname}: \"{content[:30]}...\"")
            else:
                logs.append(f"❌ Failed: {msg}")
        
    return logs
