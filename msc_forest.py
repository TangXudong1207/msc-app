### msc_forest.py (英雄无敌3 风格致敬版) ###

import streamlit as st
import random

# ==========================================
# 🏰 阵营风格定义 (Factions)
# ==========================================
FACTIONS = {
    # 森林/壁垒 (Rampart) - 对应 Care/Aesthetic
    "Rampart": {
        "ground": "#2d4c1e", "border": "#1a2e11",
        "tiles": ["🌲", "🌳", "🌿", "🍀", "🏡"],
        "landmark": "🦄" # 独角兽花园
    },
    # 塔楼/雪山 (Tower) - 对应 Agency/Logic
    "Tower": {
        "ground": "#e3f2fd", "border": "#90caf9",
        "tiles": ["🏔️", "❄️", "🧊", "🏛️", "🌨️"],
        "landmark": "⚡" # 泰坦云殿
    },
    # 地下城 (Dungeon) - 对应 Reflection/Curiosity
    "Dungeon": {
        "ground": "#212121", "border": "#424242",
        "tiles": ["🍄", "👁️", "🔮", "🕳️", "🕯️"],
        "landmark": "🐉" # 黑龙洞穴
    },
    # 城堡 (Castle) - 对应 Coherence/Order
    "Castle": {
        "ground": "#8d6e63", "border": "#5d4037",
        "tiles": ["🏰", "🛡️", "🧱", "🌾", "🐎"],
        "landmark": "👑" # 天使之门
    },
    # 海洋 (Cove) - 对应 Empathy
    "Cove": {
        "ground": "#01579b", "border": "#0d47a1",
        "tiles": ["🌊", "⛵", "🐚", "🏝️", "⚓"],
        "landmark": "🧜" # 亚特兰蒂斯
    }
}

def get_faction(radar):
    # 根据雷达图最高的维度，决定地图的种族风格
    top = max(radar, key=radar.get)
    val = radar[top]
    
    if top == "Agency": return "Tower"
    elif top == "Empathy": return "Cove"
    elif top == "Reflection": return "Dungeon"
    elif top == "Coherence": return "Castle"
    else: return "Rampart" # 默认壁垒

# ==========================================
# 🗺️ 核心算法：生成等轴地图数据
# ==========================================
def generate_homm_map(radar, size=8):
    faction_name = get_faction(radar)
    style = FACTIONS[faction_name]
    
    # 核心分数决定了地图的“繁荣度”
    # 分数越高，地块越丰富，建筑越多
    avg_score = sum(radar.values()) / len(radar)
    richness = avg_score / 10.0 
    
    grid = []
    for y in range(size):
        row = []
        for x in range(size):
            # 基础噪音
            noise = random.random()
            
            # 中心点放奇迹建筑
            if x == size//2 and y == size//2 and avg_score > 6.0:
                tile = style["landmark"]
                opacity = 1.0
                scale = 1.8 # 奇迹要大
            else:
                scale = 1.0
                # 边缘迷雾 (Fog)
                dist = ((x-size/2)**2 + (y-size/2)**2)**0.5
                if dist > (size/2 * richness + 1):
                    tile = "☁️" # 迷雾
                    opacity = 0.3
                elif noise < richness:
                    tile = random.choice(style["tiles"])
                    opacity = 0.9 + noise * 0.1
                else:
                    tile = "・" # 空地
                    opacity = 0.2
            
            row.append({"char": tile, "op": opacity, "scale": scale})
        grid.append(row)
        
    return grid, style, faction_name

# ==========================================
# 🎨 渲染器：CSS Isometic Grid
# ==========================================
def render_forest_scene(radar_dict):
    st.markdown("### 🏰 Mind Kingdom")
    
    grid, style, faction = generate_homm_map(radar_dict)
    
    # CSS 魔法：让它看起来像一块游戏地图
    # 使用 grid 布局，加上背景色和边框
    html = f"""
    <style>
        .homm-map {{
            display: grid;
            grid-template-columns: repeat({len(grid)}, 1fr);
            gap: 2px;
            background-color: {style['ground']};
            border: 4px solid {style['border']};
            border-radius: 8px;
            padding: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            width: 100%;
            aspect-ratio: 1/1;
        }}
        .homm-cell {{
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            transition: all 0.3s;
            cursor: default;
        }}
        .homm-cell:hover {{
            transform: scale(1.3);
            filter: brightness(1.2);
        }}
    </style>
    
    <div class="homm-map">
    """
    
    for row in grid:
        for cell in row:
            # 动态生成每个格子的样式
            cell_style = f"opacity: {cell['op']}; transform: scale({cell['scale']});"
            html += f'<div class="homm-cell" style="{cell_style}">{cell["char"]}</div>'
            
    html += "</div>"
    
    st.markdown(html, unsafe_allow_html=True)
    
    # 底部说明
    st.caption(f"当前领地：**{faction}** (Based on your dominant trait)")
    if sum(radar_dict.values())/7 < 4.0:
        st.warning("⚠️ 领地贫瘠：你需要更多的深度思考来驱散迷雾。")
