### msc_forest.py (个人森林生态生成器) ###

import streamlit as st
import random
import time

# ==========================================
# 🌲 生态元素库 (The Elements)
# ==========================================
ELEMENTS = {
    "mountain": ["🏔️", "⛰️", "🗻", "🗿"],
    "water": ["🌊", "💧", "🟦", "🧊"],
    "forest": ["🌲", "🌳", "🌴", "🌵"],
    "flower": ["🌸", "🌻", "🌹", "🌷", "🍄"],
    "ground": ["🟫", "🟩", "⬜", "⬛"], # 土壤，草地，雪地，虚空
    "life": ["🦋", "🐝", "🐦", "🦌", "🐇"]
}

# ==========================================
# 🎨 核心算法：雷达转地貌
# ==========================================
def generate_forest_map(radar_dict, size=10):
    """
    输入: radar_dict (用户的7维分数, 0-10)
    输出: 一个二维的 emoji 矩阵 (地图)
    """
    # 1. 提取核心参数
    agency = radar_dict.get("Agency", 3.0)
    empathy = radar_dict.get("Empathy", 3.0)
    reflection = radar_dict.get("Reflection", 3.0)
    aesthetic = radar_dict.get("Aesthetic", 3.0)
    care = radar_dict.get("Care", 3.0)
    
    # 2. 决定基调 (Biome Type)
    # 哪个分数最高，就决定了主要的生态类型
    biome = "plains"
    max_trait = max(radar_dict, key=radar_dict.get)
    
    if max_trait == "Agency" and agency > 7: biome = "highland" # 高原
    elif max_trait == "Empathy" and empathy > 7: biome = "wetland" # 湿地
    elif max_trait == "Reflection" and reflection > 7: biome = "dense_forest" # 深林
    elif max_trait == "Aesthetic" and aesthetic > 7: biome = "garden" # 花园
    
    # 3. 生成地图网格
    grid = []
    
    for y in range(size):
        row = []
        for x in range(size):
            # 基础概率噪音
            noise = random.random()
            cell = "🟩" # 默认草地
            
            # --- 规则 A: 造山 (Agency) ---
            # Agency 越高，山越多，且越集中在地图中心
            dist_to_center = ((x - size/2)**2 + (y - size/2)**2) ** 0.5
            mountain_prob = (agency / 20.0) - (dist_to_center / size) * 0.5
            if noise < mountain_prob:
                cell = random.choice(ELEMENTS["mountain"])
            
            # --- 规则 B: 造水 (Empathy) ---
            # Empathy 越高，水越多，倾向于成片
            water_prob = (empathy / 25.0)
            # 简单的元胞模拟：如果旁边有水，我也容易变成水
            if x > 0 and row[x-1] in ELEMENTS["water"]: water_prob += 0.3
            if noise > (1 - water_prob):
                cell = random.choice(ELEMENTS["water"])
                
            # --- 规则 C: 种树 (Reflection) ---
            forest_prob = (reflection / 15.0)
            if cell == "🟩" and noise < forest_prob:
                cell = random.choice(ELEMENTS["forest"])
                
            # --- 规则 D: 开花 (Aesthetic) ---
            # 只有在草地或森林边上开花
            flower_prob = (aesthetic / 20.0)
            if cell in ["🟩", "🌳"] and random.random() < flower_prob:
                cell = random.choice(ELEMENTS["flower"])
            
            # --- 规则 E: 生命力 (Care) ---
            # Care 越高，越容易出现小动物
            life_prob = (care / 50.0)
            if cell not in ELEMENTS["mountain"] + ELEMENTS["water"] and random.random() < life_prob:
                cell = random.choice(ELEMENTS["life"])

            row.append(cell)
        grid.append(row)
        
    return grid, biome

# ==========================================
# 🖼️ 渲染器：Streamlit 组件
# ==========================================
def render_forest_scene(radar_dict):
    st.markdown("### 🌲 Your Inner Ecosystem")
    
    grid, biome = generate_forest_map(radar_dict, size=12) # 生成 12x12 的地图
    
    # 渲染描述
    biome_desc = {
        "highland": "⛰️ 坚毅的高地 (Highland of Will)",
        "wetland": "🌊 包容的湿地 (Wetland of Empathy)",
        "dense_forest": "🌲 深邃的密林 (Forest of Reflection)",
        "garden": "🌸 绚烂的花园 (Garden of Aesthetics)",
        "plains": "🌱 广阔的原野 (Plains of Potential)"
    }
    st.caption(f"当前心灵地貌：**{biome_desc.get(biome, 'Unknown')}**")
    
    # 渲染地图 (用 HTML 保持紧凑)
    map_html = '<div style="font-size: 20px; line-height: 1.2; text-align: center; background: #111; padding: 20px; border-radius: 10px;">'
    for row in grid:
        map_html += "".join(row) + "<br>"
    map_html += "</div>"
    
    st.markdown(map_html, unsafe_allow_html=True)
    
    # 互动反馈
    st.info("💡 你的每一次深度对话，都会改变这片森林的植被。")
