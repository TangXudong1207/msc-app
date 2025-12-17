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
    "Reykjavik": [64.1466, -21.9426], # 孤独之地
    "Buenos Aires": [-34.6037, -58.3816],
    "Cape Town": [-33.9249, 18.4241],
    "Sydney": [-33.8688, 151.2093],
    "Mumbai": [19.0760, 72.8777],
    "Moscow": [55.7558, 37.6173],
    "Cairo": [30.0444, 31.2357],
    "Istanbul": [41.0082, 28.9784],
    "Lhasa": [29.6520, 91.1721]       # 精神高地
}

# ==========================================
# 🎭 1. 设定：灵魂原型 (Archetypes)
# ==========================================
ARCHETYPES = [
    {
        "nickname": "Kafka_AI",
        "style": "存在主义，焦虑，敏感，觉得世界是荒谬的",
        "radar": {"Care": 8, "Reflection": 9, "Agency": 3, "Curiosity": 5, "Coherence": 4, "Empathy": 7, "Aesthetic": 6}
    },
    {
        "nickname": "Elon_AI",
        "style": "极客，未来主义，理性，相信技术救赎，反感无病呻吟",
        "radar": {"Care": 4, "Agency": 10, "Curiosity": 9, "Coherence": 8, "Reflection": 5, "Empathy": 2, "Aesthetic": 5}
    },
    {
        "nickname": "Rumi_AI",
        "style": "神秘主义，诗人，温暖，谈论爱与灵魂，治愈系",
        "radar": {"Care": 9, "Empathy": 10, "Aesthetic": 9, "Reflection": 8, "Coherence": 6, "Agency": 4, "Curiosity": 5}
    },
    {
        "nickname": "Camus_AI",
        "style": "反抗者，冷静，西西弗斯精神，在绝望中寻找力量",
        "radar": {"Care": 7, "Agency": 8, "Reflection": 9, "Coherence": 9, "Empathy": 5, "Aesthetic": 4, "Curiosity": 6}
    },
    {
        "nickname": "Alice_Sim",
        "style": "普通的现代都市青年，迷茫，想躺平又不敢，寻找生活小确幸",
        "radar": {"Care": 6, "Empathy": 6, "Agency": 4, "Reflection": 5, "Curiosity": 6, "Aesthetic": 7, "Coherence": 5}
    },
    {
        "nickname": "Nietzsche_Bot",
        "style": "激进，权力意志，批判现代性的虚弱，崇尚超越",
        "radar": {"Care": 9, "Agency": 9, "Reflection": 8, "Coherence": 7, "Empathy": 2, "Aesthetic": 8, "Curiosity": 7}
    }
]

TOPICS = [
    "工作的意义是什么？是异化还是实现？",
    "我们在数字时代是否更孤独了？",
    "自由的代价是什么？",
    "由于AI的发展，人类的创造力还重要吗？",
    "死亡是否赋予了生命意义？",
    "什么是真正的爱？",
    "未来的城市会是什么样？"
]

# ==========================================
# 🧬 2. 核心功能：批量造人 (带地理分配)
# ==========================================
def create_virtual_citizens(count=5):
    """
    count: 想要尝试生成的数量
    """
    created_count = 0
    # 随机打乱原型列表，避免每次都按顺序生成
    shuffled_archetypes = random.sample(ARCHETYPES, len(ARCHETYPES))
    
    for i in range(min(count, len(shuffled_archetypes))):
        char = shuffled_archetypes[i]
        username = f"sim_{char['nickname'].lower()}"
        
        # 1. 分配家乡
        city_name, coords = random.choice(list(GLOBAL_CITIES.items()))
        
        # 检查是否已存在
        if not msc.get_user_profile(username).get('radar_profile'):
            # 注册用户：密码默认123456，国家填城市名
            if msc.add_user(username, "123456", char['nickname'], city_name):
                # 更新雷达
                msc.update_radar_score(username, char['radar'])
                # 更新地理位置到 User 表 (存为 JSON [lon, lat] 注意顺序)
                # supabase 里我们通常存 location 字段，这里我们假设 add_user 只是存了基础，
                # 我们需要在逻辑里确保位置被利用。目前 add_user 里虽然写了 location，但这里我们可以通过更新来确保。
                # 注意：World地图通常用 [lon, lat] 或 {lat, lon}，这里我们为了sim简单，暂不强行更新User表坐标，
                # 而是确保下面 inject_thoughts 时使用这个坐标。
                created_count += 1
                
    return created_count

# ==========================================
# 💉 3. 核心功能：思想注入 (带地理抖动)
# ==========================================
def inject_thoughts(count=3):
    """
    让虚拟人针对话题发言，并携带地理坐标
    """
    logs = []
    
    # 获取所有以 sim_ 开头的用户 (模拟获取)
    # 由于 msc_db 只有 get_all_users，我们先获取所有，然后过滤
    all_users = msc.get_all_users("admin")
    sim_users = [u for u in all_users if u['username'].startswith("sim_")]
    
    if not sim_users:
        return ["⚠️ No simulation users found. Run 'Summon' first."]

    for i in range(count):
        # 1. 随机选人
        user_record = random.choice(sim_users)
        username = user_record['username']
        nickname = user_record['nickname']
        
        # 2. 查找原型设定
        # 简单匹配：从 nickname 匹配 ARCHETYPES
        archetype = next((a for a in ARCHETYPES if a['nickname'] == nickname), ARCHETYPES[0])
        
        # 3. 确定坐标 (从城市列表中反向查找，或者随机分配一个)
        # 这里为了演示效果，我们重新给这次发言分配一个城市（模拟漫游）或固定城市
        city_name, center_coords = random.choice(list(GLOBAL_CITIES.items()))
        # 添加抖动 (Jitter)：模拟在城市的不同街区 (+- 0.05 度)
        lat = center_coords[0] + random.uniform(-0.05, 0.05)
        lon = center_coords[1] + random.uniform(-0.05, 0.05)
        location_data = {"lat": lat, "lon": lon, "city": city_name}
        
        # 4. 生成内容
        topic = random.choice(TOPICS)
        prompt = f"""
        角色设定：{archetype['style']}
        话题：{topic}
        任务：请用符合你角色设定的口吻，说一句简短深刻的话（30字以内）。
        不要解释，不要引用，直接输出内容。
        """
        
        # 调用 AI
        response = msc.call_ai_api(f"{prompt} 输出 JSON: {{'content': '...'}}")
        content = response.get('content', '')
        
        if content:
            # 5. 分析 & 存入 (带 Location)
            analysis = msc.analyze_meaning_background(content)
            # 强制补全 location 到 analysis 结果中，以便 save_node 存入
            analysis['location'] = location_data
            
            if analysis.get("valid", False):
                vec = msc.get_embedding(content)
                msc.save_node(username, content, analysis, "Genesis_Sim", vec)
                logs.append(f"🌍 [{city_name}] {nickname}: {content[:15]}... (Care: {analysis.get('m_score',0):.2f})")
            else:
                logs.append(f"⚪ {nickname}: (Meaning too weak to manifest)")
        
        time.sleep(1.0) # 避免速率限制
        
    return logs
