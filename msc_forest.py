import streamlit as st
from streamlit_echarts import st_echarts
import random
import numpy as np
import math
import msc_viz as viz  # 用于取色

# ==========================================
# 📐 1. 数学骨架：基础几何组件
# ==========================================
# 这些函数是“积木”，用于拼凑出任何形态

def gen_sphere(n, r=10, center=(0,0,0), distortion=0):
    """生成球体/核心"""
    pts = []
    for _ in range(n):
        theta = random.uniform(0, 2*math.pi)
        phi = random.uniform(0, math.pi)
        rad = r * (random.uniform(0.1, 1) ** (1/3)) # 实心分布
        
        # 畸变逻辑：如果 distortion > 0，球体会变得不规则
        if distortion > 0:
            rad += random.gauss(0, distortion)
            
        x = center[0] + rad * math.sin(phi) * math.cos(theta)
        y = center[1] + rad * math.sin(phi) * math.sin(theta)
        z = center[2] + rad * math.cos(phi)
        pts.append([x,y,z])
    return pts

def gen_pillar(n, h=20, r=5, center=(0,0,0), taper=0.5):
    """生成柱体/躯干 (taper控制锥度, <1为上细下粗)"""
    pts = []
    for _ in range(n):
        z_local = random.uniform(0, h)
        h_ratio = z_local / h
        # 半径随高度变化
        current_r = r * (1 - (1-taper)*h_ratio)
        
        theta = random.uniform(0, 2*math.pi)
        rad = current_r * math.sqrt(random.uniform(0, 1))
        
        x = center[0] + rad * math.cos(theta)
        y = center[1] + rad * math.sin(theta)
        z = center[2] + z_local - h/2 # 居中
        pts.append([x,y,z])
    return pts

def gen_wings(n, span=20, curve=0.5, center=(0,0,0)):
    """生成双翼 (粒子流)"""
    pts = []
    for _ in range(n):
        side = random.choice([-1, 1])
        t = random.uniform(0, 1) # 翼展进度
        
        # 翼展曲线方程
        x = side * (2 + span * t)
        y = -5 * t + random.gauss(0, 1) # 后掠
        z = (10 * curve) * math.sin(t * 3) + random.gauss(0, 1) # 弯曲
        
        # 加上中心偏移
        pts.append([center[0]+x, center[1]+y, center[2]+z])
    return pts

def gen_antlers(n, spread=10, center=(0,0,0)):
    """生成鹿角/触须 (分形结构)"""
    pts = []
    for _ in range(n):
        side = random.choice([-1, 1])
        t = random.uniform(0, 1)
        
        # 树枝状生长
        x = side * (2 + spread * 0.5 * t) + random.gauss(0, 0.5)
        y = random.gauss(0, 1)
        z = 5 + spread * t + random.gauss(0, 0.5)
        
        # 简单的分叉模拟
        if t > 0.6 and random.random() > 0.5:
            x += random.uniform(-2, 2)
            z += random.uniform(0, 3)
            
        pts.append([center[0]+x, center[1]+y, center[2]+z])
    return pts

def gen_halo(n, r=15, center=(0,0,0)):
    """生成光环/气场"""
    pts = []
    for _ in range(n):
        theta = random.uniform(0, 2*math.pi)
        # 环状分布
        rad = r + random.gauss(0, 0.5)
        x = center[0] + rad * math.cos(theta)
        y = center[1] + rad * math.sin(theta)
        z = center[2] + random.uniform(-1, 1)
        pts.append([x,y,z])
    return pts

# ==========================================
# 🧬 2. 混合算法：形态合成器 (Morph-Synthesizer)
# ==========================================
def synthesize_creature(radar, node_count):
    """
    根据雷达数据合成生物形态。
    返回: 粒子坐标列表, 颜色列表
    """
    # 1. 解析 DNA (雷达数据)
    # 排序属性，找出主导因子(Primary)和次级因子(Secondary)
    sorted_attr = sorted(radar.items(), key=lambda x: x[1], reverse=True)
    primary_attr, p_score = sorted_attr[0]
    secondary_attr, s_score = sorted_attr[1]
    
    # 计算总粒子数 (基于节点数，但这只是为了展示，可以放大)
    base_count = max(200, node_count * 2) # 至少200个点
    
    particles = []
    colors = []
    
    # --- A. 构建躯干 (Base Body) ---
    # 根据主导属性决定躯干形状
    body_pts = []
    
    if primary_attr == "Reflection" or primary_attr == "Coherence":
        # 核心型：球体 (Reflection) 或 立方体/致密球 (Coherence)
        body_pts = gen_sphere(int(base_count*0.5), r=8)
        
    elif primary_attr == "Agency" or primary_attr == "Curiosity":
        # 冲量型：流线型柱体 (Agency) 或 细长流体 (Curiosity)
        body_pts = gen_pillar(int(base_count*0.5), h=25, r=4, taper=0.3) # 锥形
        # Agency 特殊处理：旋转一下变成水平冲刺状? Echarts 旋转麻烦，这里先保持垂直
        
    elif primary_attr == "Care" or primary_attr == "Empathy":
        # 包容型：圆润的有机体
        body_pts = gen_sphere(int(base_count*0.5), r=8, distortion=2.0) # 柔软的云团
        
    else: # Aesthetic / Structure
        # 结构型：对称双球 (哑铃状)
        p1 = gen_sphere(int(base_count*0.25), r=5, center=(0,0,-5))
        p2 = gen_sphere(int(base_count*0.25), r=5, center=(0,0,5))
        body_pts = p1 + p2
        
    particles.extend(body_pts)
    # 给躯干上色 (主色)
    # 这里应该用 viz 里的色盘，这里简化硬编码演示逻辑
    # 实际应用中，这里应该混合用户真实节点的颜色
    base_color = "#FFFFFF" # 默认
    if primary_attr == "Care": base_color = "#00FF88"
    elif primary_attr == "Agency": base_color = "#FFD700"
    elif primary_attr == "Reflection": base_color = "#9D00FF"
    elif primary_attr == "Conflict": base_color = "#FF2B2B"
    # ... 其他颜色省略，保持简洁
    
    colors.extend([base_color] * len(body_pts))

    # --- B. 挂载组件 (Modifiers) ---
    # 根据次级属性决定外挂器官
    mod_pts = []
    mod_color = "#CCCCCC"
    
    if secondary_attr == "Agency" or secondary_attr == "Aesthetic":
        # 长翅膀
        mod_pts = gen_wings(int(base_count*0.4), span=25, center=(0,0,5))
        mod_color = "#FF7F00" if secondary_attr == "Agency" else "#FF00FF"
        
    elif secondary_attr == "Care" or secondary_attr == "Reflection":
        # 长角/触须
        mod_pts = gen_antlers(int(base_count*0.3), spread=12, center=(0,0,8))
        mod_color = "#00FF88" if secondary_attr == "Care" else "#00CCFF"
        
    elif secondary_attr == "Curiosity":
        # 尾迹/光环
        mod_pts = gen_halo(int(base_count*0.3), r=12)
        mod_color = "#00CCFF"
        
    else:
        # 默认强化躯干 (加厚)
        mod_pts = gen_sphere(int(base_count*0.2), r=10, distortion=1)
        mod_color = base_color
        
    particles.extend(mod_pts)
    colors.extend([mod_color] * len(mod_pts))
    
    # --- C. 进化状态 (Phase Check) ---
    # 如果总分很高 (>50)，添加 "Ascension" 特效 (顶部粒子流)
    total_score = sum(radar.values())
    if total_score > 50:
        ascension_pts = gen_pillar(int(base_count*0.2), h=30, r=1, center=(0,0,10))
        particles.extend(ascension_pts)
        colors.extend(["#FFFFFF"] * len(ascension_pts)) # 纯白光柱

    return particles, colors, primary_attr, secondary_attr

# ==========================================
# 🌲 3. 渲染主程序
# ==========================================
def render_forest_scene(radar_dict, user_nodes=None):
    if user_nodes is None: user_nodes = []
    
    # 1. 计算形态
    particles, colors, p_attr, s_attr = synthesize_creature(radar_dict, len(user_nodes))
    
    # 2. 生成描述文案
    creature_name = f"{p_attr}-{s_attr} Hybrid"
    if len(user_nodes) < 5: creature_name = "Proto-Consciousness (Sprout)"
    
    st.markdown(f"### 🧬 Soul Form: **{creature_name}**")
    
    # 3. 构造 ECharts 数据
    echarts_data = []
    for i, pt in enumerate(particles):
        echarts_data.append({
            "value": pt,
            "itemStyle": {"color": colors[i]}
        })
        
    # 4. 渲染
    option = {
        "backgroundColor": "transparent",
        "tooltip": {},
        "xAxis3D": {"show": False, "min": -20, "max": 20},
        "yAxis3D": {"show": False, "min": -20, "max": 20},
        "zAxis3D": {"show": False, "min": -20, "max": 20},
        "grid3D": {
            "boxWidth": 120, "boxDepth": 120, "boxHeight": 120,
            "viewControl": {
                "autoRotate": True,
                "autoRotateSpeed": 6,
                "distance": 220,
                "alpha": 30, # 视角倾斜
                "beta": 10
            },
            "environment": "#000",
            "axisLine": {"show": False},
            "splitLine": {"show": False}
        },
        "series": [{
            "type": 'scatter3D',
            "data": echarts_data,
            "symbolSize": 3.5, # 粒子大小
            "itemStyle": {
                "opacity": 0.8
            },
            # 开启泛光效果 (Bloom) - 如果支持的话，会让粒子发光
            "blendMode": 'lighter'
        }]
    }
    
    st_echarts(options=option, height="350px")
