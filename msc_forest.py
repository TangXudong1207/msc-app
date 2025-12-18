### msc_forest.py ###

import streamlit as st
from streamlit_echarts import st_echarts
import random
import numpy as np
import math
import msc_viz as viz  # 必须引用，用于获取光谱颜色

# ==========================================
# 📐 1. 数学骨架：基础几何组件 (保持不变)
# ==========================================
def gen_sphere(n, r=10, center=(0,0,0), distortion=0):
    pts = []
    for _ in range(n):
        theta = random.uniform(0, 2*math.pi)
        phi = random.uniform(0, math.pi)
        rad = r * (random.uniform(0.3, 1) ** (1/3)) 
        if distortion > 0: rad += random.gauss(0, distortion)
        x = center[0] + rad * math.sin(phi) * math.cos(theta)
        y = center[1] + rad * math.sin(phi) * math.sin(theta)
        z = center[2] + rad * math.cos(phi)
        pts.append([x,y,z])
    return pts

def gen_pillar(n, h=20, r=5, center=(0,0,0), taper=0.5):
    pts = []
    for _ in range(n):
        z_local = random.uniform(0, h)
        h_ratio = z_local / h
        current_r = r * (1 - (1-taper)*h_ratio)
        theta = random.uniform(0, 2*math.pi)
        rad = current_r * math.sqrt(random.uniform(0.2, 1))
        x = center[0] + rad * math.cos(theta)
        y = center[1] + rad * math.sin(theta)
        z = center[2] + z_local - h/2
        pts.append([x,y,z])
    return pts

def gen_wings(n, span=20, curve=0.5, center=(0,0,0)):
    pts = []
    for _ in range(n):
        side = random.choice([-1, 1])
        t = random.uniform(0, 1)
        x = side * (2 + span * t)
        y = -5 * t + random.gauss(0, 1)
        z = (10 * curve) * math.sin(t * 3) + random.gauss(0, 1)
        pts.append([center[0]+x, center[1]+y, center[2]+z])
    return pts

def gen_antlers(n, spread=10, center=(0,0,0)):
    pts = []
    for _ in range(n):
        side = random.choice([-1, 1])
        t = random.uniform(0, 1)
        x = side * (2 + spread * 0.5 * t) + random.gauss(0, 0.5)
        y = random.gauss(0, 1)
        z = 5 + spread * t + random.gauss(0, 0.5)
        if t > 0.6 and random.random() > 0.5:
            x += random.uniform(-2, 2)
            z += random.uniform(0, 3)
        pts.append([center[0]+x, center[1]+y, center[2]+z])
    return pts

def gen_halo(n, r=15, center=(0,0,0)):
    pts = []
    for _ in range(n):
        theta = random.uniform(0, 2*math.pi)
        rad = r + random.gauss(0, 0.5)
        x = center[0] + rad * math.cos(theta)
        y = center[1] + rad * math.sin(theta)
        z = center[2] + random.uniform(-1, 1)
        pts.append([x,y,z])
    return pts

# ==========================================
# 🧬 2. 混合算法：形态与数据映射
# ==========================================
def synthesize_creature_data(radar, user_nodes):
    """
    核心升级：将真实节点数据注入几何形态
    """
    if not radar: radar = {"Care": 3.0, "Agency": 3.0}
    
    sorted_attr = sorted(radar.items(), key=lambda x: x[1], reverse=True)
    primary_attr, p_score = sorted_attr[0]
    secondary_attr, s_score = sorted_attr[1]
    
    # 基础粒子数：保证形态完整
    base_count = max(600, len(user_nodes) * 4) 
    
    # --- 1. 生成纯几何坐标 ---
    raw_points = []
    
    # A. 躯干 (占 60%)
    body_pts = []
    if primary_attr in ["Reflection", "Coherence"]:
        body_pts = gen_sphere(int(base_count*0.6), r=8)
    elif primary_attr in ["Agency", "Curiosity"]:
        body_pts = gen_pillar(int(base_count*0.6), h=25, r=4, taper=0.3)
    elif primary_attr in ["Care", "Empathy"]:
        body_pts = gen_sphere(int(base_count*0.6), r=8, distortion=1.5)
    else:
        p1 = gen_sphere(int(base_count*0.3), r=5, center=(0,0,-5))
        p2 = gen_sphere(int(base_count*0.3), r=5, center=(0,0,5))
        body_pts = p1 + p2
    raw_points.extend(body_pts)

    # B. 组件 (占 40%)
    mod_pts = []
    if secondary_attr in ["Agency", "Aesthetic"]:
        mod_pts = gen_wings(int(base_count*0.4), span=25, center=(0,0,5))
    elif secondary_attr in ["Care", "Reflection"]:
        mod_pts = gen_antlers(int(base_count*0.4), spread=12, center=(0,0,8))
    elif secondary_attr == "Curiosity":
        mod_pts = gen_halo(int(base_count*0.4), r=12)
    else:
        mod_pts = gen_sphere(int(base_count*0.4), r=10, distortion=1)
    raw_points.extend(mod_pts)
    
    # 随机打乱坐标，避免真实节点全部集中在躯干头部
    random.shuffle(raw_points)

    # --- 2. 注入数据 (Data Injection) ---
    echarts_series_data = []
    
    # 颜色映射表 (用于灵能粒子)
    c_map = {
        "Care": "#00FF88", "Agency": "#FFD700", "Reflection": "#9D00FF",
        "Conflict": "#FF2B2B", "Empathy": "#FF69B4", "Structure": "#E0E0E0",
        "Curiosity": "#00CCFF", "Aesthetic": "#FF00FF", "Mystery": "#9D00FF"
    }
    spirit_color = c_map.get(primary_attr, "#FFFFFF")
    
    for i, pt in enumerate(raw_points):
        # 如果还有真实节点，就把这个坐标分配给真实节点
        if i < len(user_nodes):
            node = user_nodes[i]
            # 获取真实光谱颜色
            try:
                kw_str = str(node.get('keywords', ''))
                real_color = viz.get_spectrum_color(kw_str)
            except: 
                real_color = spirit_color
            
            # 构造带交互的数据项
            # Tooltip 会显示 name 和 value
            # 我们把 content 放进 name 里，或者用 formatter
            content_preview = node.get('care_point', 'Thought')
            full_content = node.get('content', '')
            
            echarts_series_data.append({
                "name": content_preview, # 鼠标悬停显示的标题
                "value": pt,
                "itemStyle": {
                    "color": real_color,
                    "opacity": 1.0 # 真实节点不透明，很亮
                },
                "symbolSize": 5, # 真实节点大一点
                # 自定义数据，供 tooltip 使用
                "raw_content": full_content
            })
        else:
            # 灵能粒子 (Spirit Dust) - 维持形状
            echarts_series_data.append({
                "name": "Soul Essence",
                "value": pt,
                "itemStyle": {
                    "color": spirit_color,
                    "opacity": 0.3 # 灵能粒子半透明，作为背景
                },
                "symbolSize": 2, # 灵能粒子小一点
                "raw_content": "Structural Energy"
            })
            
    return echarts_series_data, primary_attr, secondary_attr

# ==========================================
# 🌲 3. 渲染主程序 (Data-Hologram Edition)
# ==========================================
def render_forest_scene(radar_dict, user_nodes=None):
    if user_nodes is None: user_nodes = []
    
    # 1. 计算形态与数据
    echarts_data, p_attr, s_attr = synthesize_creature_data(radar_dict, user_nodes)
    
    creature_name = f"{p_attr}-{s_attr} Hybrid"
    if len(user_nodes) < 5: creature_name = "Proto-Consciousness"
    
    st.markdown(f"### 🧬 Soul Form: **{creature_name}**")
    
    # 2. 视觉升级：重工业全息网格
    # 颜色定义
    grid_color = "#333333" # 轴线
    split_color = "#222222" # 网格线
    
    option = {
        "backgroundColor": "transparent",
        # 💡 Tooltip 配置：显示真实内容
        "tooltip": {
            "show": True,
            "trigger": 'item',
            "formatter": "{b}", # 这里简单显示 name，如果需要更复杂内容，Streamlit中传函数较麻烦
            "backgroundColor": "rgba(50,50,50,0.9)",
            "textStyle": {"color": "#fff"},
            "borderColor": "#777"
        },
        # 💡 三维坐标轴：加粗，加重
        "xAxis3D": {
            "show": True, "name": "", 
            "axisLine": {"lineStyle": {"color": grid_color, "width": 3}}, # 粗轴
            "axisLabel": {"show": False},
            "splitLine": {"show": True, "lineStyle": {"color": split_color, "width": 1}}
        },
        "yAxis3D": {
            "show": True, "name": "",
            "axisLine": {"lineStyle": {"color": grid_color, "width": 3}},
            "axisLabel": {"show": False},
            "splitLine": {"show": True, "lineStyle": {"color": split_color, "width": 1}}
        },
        "zAxis3D": {
            "show": True, "name": "",
            "axisLine": {"lineStyle": {"color": grid_color, "width": 3}},
            "axisLabel": {"show": False},
            "splitLine": {"show": True, "lineStyle": {"color": split_color, "width": 1}}
        },
        "grid3D": {
            "boxWidth": 110, "boxDepth": 110, "boxHeight": 110,
            "viewControl": {
                "projection": 'orthographic',
                "autoRotate": True,
                "autoRotateSpeed": 8, # 稍微慢一点，显出厚重感
                "distance": 220,
                "alpha": 25, 
                "beta": 45,
                "rotateSensitivity": 1,
                "zoomSensitivity": 1
            },
            "light": {
                "main": {
                    "intensity": 1.5, # 增强亮度
                    "shadow": False,
                    "alpha": 40,
                    "beta": 40
                },
                "ambient": {
                    "intensity": 0.5
                }
            },
            # 让环境变暗一点点，突出全息感
            "environment": "transparent",
        },
        "series": [{
            "type": 'scatter3D',
            "data": echarts_data,
            "shading": 'lambert', # 开启光影，让粒子有体积感
            # 开启高亮交互
            "emphasis": {
                "label": {
                    "show": True,
                    "formatter": "{b}", # 鼠标移上去显示文字
                    "position": "top",
                    "textStyle": {"color": "#fff", "fontSize": 12, "backgroundColor": "#000", "padding": [2,5]}
                },
                "itemStyle": {
                    "color": "#fff", # 高亮变白
                    "opacity": 1
                }
            }
        }]
    }
    
    st_echarts(options=option, height="350px")
