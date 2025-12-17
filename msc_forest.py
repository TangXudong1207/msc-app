import streamlit as st
from streamlit_echarts import st_echarts
import random
import numpy as np
import math
import msc_viz as viz  # 用于取色

# ==========================================
# 📐 1. 数学骨架：基础几何组件 (保持不变)
# ==========================================
def gen_sphere(n, r=10, center=(0,0,0), distortion=0):
    pts = []
    for _ in range(n):
        theta = random.uniform(0, 2*math.pi)
        phi = random.uniform(0, math.pi)
        rad = r * (random.uniform(0.1, 1) ** (1/3))
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
        rad = current_r * math.sqrt(random.uniform(0, 1))
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
# 🧬 2. 混合算法：形态合成器
# ==========================================
def synthesize_creature(radar, node_count):
    # 如果没有数据，给个默认值防止报错
    if not radar: radar = {"Care": 3.0, "Agency": 3.0}
    
    sorted_attr = sorted(radar.items(), key=lambda x: x[1], reverse=True)
    primary_attr, p_score = sorted_attr[0]
    secondary_attr, s_score = sorted_attr[1]
    
    # 粒子基数：放大显示，让形态更扎实
    base_count = max(300, node_count * 3) 
    
    particles = []
    colors = []
    
    # --- A. 躯干 ---
    body_pts = []
    if primary_attr in ["Reflection", "Coherence"]:
        body_pts = gen_sphere(int(base_count*0.5), r=8)
    elif primary_attr in ["Agency", "Curiosity"]:
        body_pts = gen_pillar(int(base_count*0.5), h=25, r=4, taper=0.3)
    elif primary_attr in ["Care", "Empathy"]:
        body_pts = gen_sphere(int(base_count*0.5), r=8, distortion=1.5)
    else:
        p1 = gen_sphere(int(base_count*0.25), r=5, center=(0,0,-5))
        p2 = gen_sphere(int(base_count*0.25), r=5, center=(0,0,5))
        body_pts = p1 + p2
        
    particles.extend(body_pts)
    
    # 躯干颜色映射
    c_map = {
        "Care": "#00FF88", "Agency": "#FFD700", "Reflection": "#9D00FF",
        "Conflict": "#FF2B2B", "Empathy": "#FF69B4", "Structure": "#E0E0E0",
        "Curiosity": "#00CCFF", "Aesthetic": "#FF00FF"
    }
    base_color = c_map.get(primary_attr, "#FFFFFF")
    colors.extend([base_color] * len(body_pts))

    # --- B. 组件 ---
    mod_pts = []
    mod_color = "#CCCCCC"
    
    if secondary_attr in ["Agency", "Aesthetic"]:
        mod_pts = gen_wings(int(base_count*0.4), span=25, center=(0,0,5))
        mod_color = "#FF7F00" if secondary_attr == "Agency" else "#FF00FF"
    elif secondary_attr in ["Care", "Reflection"]:
        mod_pts = gen_antlers(int(base_count*0.3), spread=12, center=(0,0,8))
        mod_color = "#00FF88" if secondary_attr == "Care" else "#00CCFF"
    elif secondary_attr == "Curiosity":
        mod_pts = gen_halo(int(base_count*0.3), r=12)
        mod_color = "#00CCFF"
    else:
        mod_pts = gen_sphere(int(base_count*0.2), r=10, distortion=1)
        mod_color = base_color
        
    particles.extend(mod_pts)
    colors.extend([mod_color] * len(mod_pts))
    
    # --- C. 飞升光效 ---
    total_score = sum(radar.values())
    if total_score > 40:
        ascension_pts = gen_pillar(int(base_count*0.1), h=40, r=0.5, center=(0,0,0))
        particles.extend(ascension_pts)
        colors.extend(["#FFFFFF"] * len(ascension_pts))

    return particles, colors, primary_attr, secondary_attr

# ==========================================
# 🌲 3. 渲染主程序 (Holographic Edition)
# ==========================================
def render_forest_scene(radar_dict, user_nodes=None):
    if user_nodes is None: user_nodes = []
    
    # 1. 计算形态
    particles, colors, p_attr, s_attr = synthesize_creature(radar_dict, len(user_nodes))
    
    creature_name = f"{p_attr}-{s_attr} Hybrid"
    if len(user_nodes) < 5: creature_name = "Proto-Consciousness"
    
    st.markdown(f"### 🧬 Soul Form: **{creature_name}**")
    
    echarts_data = []
    for i, pt in enumerate(particles):
        echarts_data.append({
            "value": pt,
            "itemStyle": {"color": colors[i]}
        })
        
    # 2. 核心升级：Holographic View Settings
    option = {
        "backgroundColor": "transparent",
        "tooltip": {},
        # 隐藏坐标轴刻度，但保留空间感
        "xAxis3D": {"show": False, "min": -25, "max": 25},
        "yAxis3D": {"show": False, "min": -25, "max": 25},
        "zAxis3D": {"show": False, "min": -25, "max": 25},
        "grid3D": {
            "boxWidth": 120, "boxDepth": 120, "boxHeight": 120,
            # 💡 关键修改：正交投影 + 特定角度 = 纪念碑谷风格的立体感
            "viewControl": {
                "projection": 'orthographic', 
                "autoRotate": True,
                "autoRotateSpeed": 10,
                "distance": 200, 
                "alpha": 20, # 稍微俯视
                "beta": 40   # 侧视角度
            },
            # 💡 关键修改：光照系统
            "light": {
                "main": {
                    "intensity": 1.2,
                    "shadow": True,  # 开启阴影
                    "shadowQuality": 'high',
                    "alpha": 30,
                    "beta": 30
                },
                "ambient": {
                    "intensity": 0.3
                }
            },
            "environment": "#000",
            # 隐藏网格线，让它悬浮
            "axisLine": {"show": False},
            "splitLine": {"show": False}
        },
        "series": [{
            "type": 'scatter3D',
            "data": echarts_data,
            # 💡 关键修改：增加粒子大小，开启 Lambert 光影材质
            "symbolSize": 5, 
            "shading": 'lambert', # 真实光照材质，让点变成球
            "itemStyle": {
                "opacity": 1.0 # 不透明，质感更强
            },
            # 强调色
            "emphasis": {
                "itemStyle": {
                    "color": "#fff",
                    "opacity": 1
                }
            }
        }]
    }
    
    st_echarts(options=option, height="350px")
