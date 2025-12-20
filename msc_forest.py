### msc_forest.py ###
import streamlit as st
import streamlit_antd_components as sac 
from streamlit_echarts import st_echarts
import random
import math
import msc_viz as viz

# ==========================================
# 📐 1. 数学骨架：基础几何组件 (v2.0)
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

def gen_void(n, r=12, center=(0,0,0)):
    pts = []
    for _ in range(n):
        theta = random.uniform(0, 2*math.pi)
        phi = random.uniform(0, math.pi)
        rad = r + random.uniform(0, 5) 
        x = center[0] + rad * math.sin(phi) * math.cos(theta)
        y = center[1] + rad * math.sin(phi) * math.sin(theta)
        z = center[2] + rad * math.cos(phi)
        pts.append([x,y,z])
    return pts

def gen_pulse(n, r=8, center=(0,0,0)):
    pts = []
    for _ in range(n):
        theta = random.uniform(0, 2*math.pi)
        phi = random.uniform(0, math.pi)
        rad = r * (random.uniform(0, 0.1) ** (1/3))
        x = center[0] + rad * math.sin(phi) * math.cos(theta)
        y = center[1] + rad * math.sin(phi) * math.sin(theta)
        z = center[2] + rad * math.cos(phi)
        pts.append([x,y,z])
    return pts

# ==========================================
# 🧬 2. 混合算法 (v2.0)
# ==========================================
def synthesize_creature_data(radar, user_nodes):
    if not radar: radar = {"Care": 3.0, "Agency": 3.0}
    sorted_attr = sorted(radar.items(), key=lambda x: x[1], reverse=True)
    primary_attr, p_score = sorted_attr[0]
    secondary_attr, s_score = sorted_attr[1]
    
    base_count = max(600, len(user_nodes) * 4) 
    raw_points = []
    
    body_pts = []
    if primary_attr == "Coherence": body_pts = gen_sphere(int(base_count*0.6), r=8)
    elif primary_attr == "Agency": body_pts = gen_pillar(int(base_count*0.6), h=25, r=4, taper=0.3)
    elif primary_attr == "Care": body_pts = gen_sphere(int(base_count*0.6), r=9, distortion=1.2)
    elif primary_attr == "Transcendence": body_pts = gen_void(int(base_count*0.6), r=8)
    elif primary_attr == "Curiosity": body_pts = gen_halo(int(base_count*0.6), r=10)
    elif primary_attr == "Reflection": body_pts = gen_sphere(int(base_count*0.6), r=7, distortion=0.5)
    else: p1 = gen_sphere(int(base_count*0.3), r=5, center=(0,0,-4)); p2 = gen_sphere(int(base_count*0.3), r=5, center=(0,0,4)); body_pts = p1 + p2
    raw_points.extend(body_pts)

    mod_pts = []
    if secondary_attr == "Agency": mod_pts = gen_wings(int(base_count*0.4), span=25, center=(0,0,5))
    elif secondary_attr == "Transcendence": mod_pts = gen_pulse(int(base_count*0.4), r=5, center=(0,0,0))
    elif secondary_attr == "Curiosity": mod_pts = gen_halo(int(base_count*0.4), r=14)
    elif secondary_attr == "Aesthetic": mod_pts = gen_antlers(int(base_count*0.4), spread=15, center=(0,0,6))
    else: mod_pts = gen_sphere(int(base_count*0.4), r=10, distortion=0.8)
    raw_points.extend(mod_pts)
    
    random.shuffle(raw_points)

    echarts_series_data = []
    c_map = {
        "Care": "#FF4081", "Agency": "#FFD700", "Reflection": "#536DFE",
        "Coherence": "#00CCFF", "Aesthetic": "#AB47BC", "Curiosity": "#00E676",
        "Transcendence": "#607D8B"
    }
    spirit_color = c_map.get(primary_attr, "#FFFFFF")
    
    for i, pt in enumerate(raw_points):
        if i < len(user_nodes):
            node = user_nodes[i]
            try:
                kw_str = str(node.get('keywords', ''))
                real_color = viz.get_spectrum_color(kw_str)
            except: 
                real_color = spirit_color
            
            content_preview = node.get('care_point', 'Thought')
            full_content = node.get('content', '')
            
            echarts_series_data.append({
                "name": content_preview, "value": pt,
                "itemStyle": {"color": real_color, "opacity": 1.0},
                "symbolSize": 5, "raw_content": full_content
            })
        else:
            echarts_series_data.append({
                "name": "Soul Essence", "value": pt,
                "itemStyle": {"color": spirit_color, "opacity": 0.3},
                "symbolSize": 2, "raw_content": "Structural Energy"
            })
            
    return echarts_series_data, primary_attr, secondary_attr

# ==========================================
# 🌲 3. 渲染主程序 (v2.0 with Legend)
# ==========================================
def render_forest_scene(radar_dict, user_nodes=None):
    if user_nodes is None: user_nodes = []
    
    required_keys = ["Care", "Curiosity", "Reflection", "Coherence", "Agency", "Aesthetic", "Transcendence"]
    for k in required_keys:
        if k not in radar_dict: radar_dict[k] = 3.0
            
    echarts_data, p_attr, s_attr = synthesize_creature_data(radar_dict, user_nodes)
    
    lang = st.session_state.get('language', 'en')
    
    TERM_MAP = {
        "Reflection": {"en": "Reflection", "zh": "深思"},
        "Coherence": {"en": "Coherence", "zh": "连贯"},
        "Agency": {"en": "Agency", "zh": "能动"},
        "Curiosity": {"en": "Curiosity", "zh": "好奇"},
        "Care": {"en": "Care", "zh": "关怀"},
        "Aesthetic": {"en": "Aesthetic", "zh": "美学"},
        "Transcendence": {"en": "Transcendence", "zh": "超越"},
        "Hybrid": {"en": "Hybrid", "zh": "复合体"},
        "Proto-Consciousness": {"en": "Proto-Consciousness", "zh": "原生意识体"},
        "Soul Form": {"en": "SOUL_FORM", "zh": "灵魂形态"}
    }
    
    def t(key): return TERM_MAP.get(key, {}).get(lang, key)
    
    if len(user_nodes) < 5: creature_name = t("Proto-Consciousness")
    else:
        p_str = t(p_attr); s_str = t(s_attr); suffix = t("Hybrid")
        creature_name = f"{p_str}-{s_str} {suffix}"
    
    label_title = t("Soul Form")
    sac.divider(label=label_title, icon='layers', align='center', color='gray')
    st.caption(f"**{creature_name}**")
    
    grid_color = "#333333"; split_color = "#222222"
    option = {
        "backgroundColor": "transparent",
        "tooltip": { "show": True, "trigger": 'item', "formatter": "{b}", "backgroundColor": "rgba(50,50,50,0.9)", "textStyle": {"color": "#fff"}, "borderColor": "#777" },
        "xAxis3D": { "show": True, "name": "", "axisLine": {"lineStyle": {"color": grid_color, "width": 3}}, "axisLabel": {"show": False}, "splitLine": {"show": True, "lineStyle": {"color": split_color, "width": 1}} },
        "yAxis3D": { "show": True, "name": "", "axisLine": {"lineStyle": {"color": grid_color, "width": 3}}, "axisLabel": {"show": False}, "splitLine": {"show": True, "lineStyle": {"color": split_color, "width": 1}} },
        "zAxis3D": { "show": True, "name": "", "axisLine": {"lineStyle": {"color": grid_color, "width": 3}}, "axisLabel": {"show": False}, "splitLine": {"show": True, "lineStyle": {"color": split_color, "width": 1}} },
        "grid3D": { "boxWidth": 110, "boxDepth": 110, "boxHeight": 110, "viewControl": { "projection": 'orthographic', "autoRotate": True, "autoRotateSpeed": 8, "distance": 220, "alpha": 25, "beta": 45 }, "light": { "main": {"intensity": 1.5, "shadow": False}, "ambient": {"intensity": 0.5} }, "environment": "transparent" },
        "series": [{ "type": 'scatter3D', "data": echarts_data, "shading": 'lambert', "emphasis": { "label": { "show": True, "formatter": "{b}", "position": "top", "textStyle": {"color": "#fff", "fontSize": 12, "backgroundColor": "#000", "padding": [2,5]} }, "itemStyle": {"color": "#fff", "opacity": 1} } }]
    }
    st_echarts(options=option, height="350px")
    
    # 新增：添加颜色说明 (Expander 形式，折叠)
    viz.render_spectrum_legend()
