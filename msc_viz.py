### msc_viz.py (完整修复版) ###

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import numpy as np
from sklearn.decomposition import PCA
from streamlit_echarts import st_echarts
import msc_config as config

# ==========================================
# 🌍 2D 世界地图 (Plotly)
# ==========================================
def render_2d_world_map(nodes):
    # 模拟一些基础地理数据，加上真实节点
    map_data = [{"lat": 39.9, "lon": 116.4, "size": 10, "label": "HQ"}]
    
    # 这里只是为了演示效果，生成一些随机点
    # 真实逻辑应该是读取 node['location'] (如果有的话)
    for _ in range(len(nodes) + 15): 
        lon = np.random.uniform(-150, 150)
        lat = np.random.uniform(-40, 60)
        map_data.append({"lat": float(lat), "lon": float(lon), "size": 5, "label": "Node"})
        
    df = pd.DataFrame(map_data)
    
    fig = go.Figure(data=go.Scattergeo(
        lon = df["lon"], 
        lat = df["lat"], 
        mode = 'markers', 
        marker = dict(size=5, color='#ffd60a', opacity=0.8)
    ))
    
    fig.update_layout(
        geo = dict(
            scope='world', 
            projection_type='natural earth', 
            showland=True, 
            landcolor="rgb(20, 20, 20)", 
            bgcolor="black"
        ), 
        margin={"r":0,"t":0,"l":0,"b":0}, 
        paper_bgcolor="black", 
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 🌌 3D 星河 (Plotly)
# ==========================================
def render_3d_galaxy(nodes):
    if len(nodes) < 3: 
        st.info("🌌 星河汇聚中... (需要至少3个节点才能计算空间)")
        return
        
    vectors, labels = [], []
    for i, node in enumerate(nodes):
        if node['vector']:
            try:
                v = json.loads(node['vector'])
                vectors.append(v)
                labels.append(node['care_point'])
            except: pass
            
    if not vectors: return
    
    # PCA 降维：把 1536 维降到 3 维
    pca = PCA(n_components=3)
    coords = pca.fit_transform(vectors)
    
    df = pd.DataFrame(coords, columns=['x','y','z'])
    df['label'] = labels
    df['size'] = 8
    
    fig = px.scatter_3d(
        df, x='x', y='y', z='z', 
        size='size', 
        hover_name='label', 
        template="plotly_dark", 
        opacity=0.8
    )
    
    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False), 
            yaxis=dict(visible=False), 
            zaxis=dict(visible=False), 
            bgcolor='black'
        ), 
        paper_bgcolor="black", 
        margin={"r":0,"t":0,"l":0,"b":0}, 
        height=600, 
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 🕸️ 雷达图 (Echarts)
# ==========================================
def render_radar_chart(radar_dict, height="200px"):
    keys = ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]
    scores = [radar_dict.get(k, 3.0) for k in keys]
    
    option = {
        "backgroundColor": "transparent", 
        "radar": {
            "indicator": [{"name": k, "max": 10} for k in keys], 
            "splitArea": {"show": False}
        }, 
        "series": [{
            "type": "radar", 
            "data": [{
                "value": scores, 
                "areaStyle": {"color": "rgba(0,255,242,0.4)"}, 
                "lineStyle": {"color": "#00fff2"}
            }]
        }]
    }
    st_echarts(options=option, height=height)

# ==========================================
# 🔮 赛博朋克关系图 (Echarts - 核心连线逻辑)
# ==========================================
def render_cyberpunk_map(nodes, height="250px", is_fullscreen=False):
    if not nodes: return
    
    graph_nodes, graph_links = [], []
    symbol_base = 30 if is_fullscreen else 15
    
    # 1. 生成节点对象
    for i, node in enumerate(nodes):
        logic = node.get('logic_score') or 0.5
        
        # 安全解析 keywords
        keywords = []
        if node.get('keywords'):
            if isinstance(node['keywords'], str):
                try: keywords = json.loads(node['keywords'])
                except: keywords = []
            else:
                keywords = node['keywords']
                
        # 安全解析 vector
        vector = None
        if node.get('vector'):
            if isinstance(node['vector'], str):
                try: vector = json.loads(node['vector'])
                except: pass
            else:
                vector = node['vector']
        
        graph_nodes.append({
            "name": str(node['id']), 
            "id": str(node['id']),
            "symbolSize": symbol_base * (0.8 + logic),
            "value": node['care_point'],
            "label": {
                "show": is_fullscreen, 
                "formatter": node['care_point'][:5], 
                "color": "#fff"
            },
            "vector": vector, 
            "keywords": keywords
        })

    # 2. 生成连线 (基于标签重叠优先)
    node_count = len(graph_nodes)
    # 性能优化：只比较最近的 40 个节点
    start_idx = max(0, node_count - 40)
    
    for i in range(start_idx, node_count):
        for j in range(i + 1, node_count):
            na, nb = graph_nodes[i], graph_nodes[j]
            
            score = 0
            
            # --- 算法核心：标签重叠 (Tag Overlap) ---
            # 只要有共同关键词，就给分，这是最直接的意义连接
            shared_tags = 0
            if na['keywords'] and nb['keywords']:
                shared_tags = len(set(na['keywords']).intersection(set(nb['keywords'])))
                if shared_tags > 0:
                    # 1个词=0.55, 2个词=0.7, 3个词=0.85
                    score += min(0.4 + (shared_tags * 0.15), 0.9)

            # --- 算法辅助：向量相似度 (Vector Sim) ---
            # 只有当 score 还没满，且向量有效时才计算
            if na['vector'] and nb['vector'] and score < 0.9:
                try:
                    vec1, vec2 = np.array(na['vector']), np.array(nb['vector'])
                    norm = np.linalg.norm(vec1) * np.linalg.norm(vec2)
                    if norm > 0:
                        sim = np.dot(vec1, vec2) / norm
                        if sim > 0.8: score += 0.2
                except: pass
            
            # 3. 连线阈值判断
            if score >= 0.65: # 强连接：亮青色实线
                graph_links.append({
                    "source": na['name'], 
                    "target": nb['name'], 
                    "lineStyle": {"width": 2.5, "color": "#00fff2", "curveness": 0.2}
                })
            elif score >= 0.45: # 弱连接：灰色虚线
                graph_links.append({
                    "source": na['name'], 
                    "target": nb['name'], 
                    "lineStyle": {"width": 1, "color": "#666", "type": "dashed", "curveness": 0.2}
                })

    option = {
        "backgroundColor": "#0e1117",
        "tooltip": {},
        "animationDurationUpdate": 1500,
        "animationEasingUpdate": "quinticInOut",
        "series": [{
            "type": "graph", 
            "layout": "force", 
            "data": graph_nodes, 
            "links": graph_links, 
            "roam": True, 
            "force": {
                "repulsion": 800 if is_fullscreen else 200,
                "gravity": 0.1,
                "edgeLength": 50
            }, 
            "itemStyle": {"shadowBlur": 10},
            "lineStyle": {"color": "source", "curveness": 0.2}
        }]
    }
    st_echarts(options=option, height=height)

# === 补全缺失的视图函数 ===
@st.dialog("🔭 浩荡宇宙", width="large")
def view_fullscreen_map(nodes, user_name):
    st.markdown(f"### 🌌 {user_name} 的浩荡宇宙")
    render_cyberpunk_map(nodes, height="600px", is_fullscreen=True)
