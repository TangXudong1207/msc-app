import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import numpy as np
# 🌟 核心修复：必须引入这两个库
from sklearn.decomposition import PCA 
from sklearn.cluster import KMeans
from streamlit_echarts import st_echarts

# --- 2D 地图 ---
def render_2d_world_map(nodes):
    # ... (代码与之前相同，略) ...
    # 确保 map_data 不为空
    map_data = [{"lat": 39.9, "lon": 116.4, "size": 10, "label": "HQ"}]
    for _ in range(len(nodes) + 15): 
        lon = np.random.uniform(-150, 150)
        lat = np.random.uniform(-40, 60)
        map_data.append({"lat": float(lat), "lon": float(lon), "size": 5, "label": "Node"})
    
    df = pd.DataFrame(map_data)
    fig = go.Figure(data=go.Scattergeo(
        lon = df["lon"], lat = df["lat"],
        mode = 'markers',
        marker = dict(size=5, color='#ffd60a', opacity=0.8)
    ))
    fig.update_layout(
        geo = dict(scope='world', projection_type='natural earth', showland=True, landcolor="rgb(20, 20, 20)", bgcolor="black"),
        margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="black", height=500
    )
    st.plotly_chart(fig, use_container_width=True)

# --- 3D 星河 ---
def render_3d_galaxy(nodes):
    if len(nodes) < 3: st.info("🌌 星河汇聚中..."); return
    vectors, labels, colors = [], [], []
    for i, node in enumerate(nodes):
        if node['vector']:
            try:
                v = json.loads(node['vector'])
                vectors.append(v)
                labels.append(node['care_point'])
                colors.append(i % 3)
            except: pass
    if not vectors: return
    
    # 🌟 PCA 调用现在安全了
    pca = PCA(n_components=3)
    coords = pca.fit_transform(vectors)
    
    df = pd.DataFrame(coords, columns=['x', 'y', 'z'])
    df['label'] = labels
    df['cluster'] = colors
    
    fig = px.scatter_3d(df, x='x', y='y', z='z', color='cluster', hover_name='label', template="plotly_dark", opacity=0.8)
    fig.update_layout(scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False), bgcolor='black'), paper_bgcolor="black", margin={"r":0,"t":0,"l":0,"b":0}, height=600, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# --- 雷达图 ---
def render_radar_chart(radar_dict, height="200px"):
    keys = ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]
    scores = [radar_dict.get(k, 3.0) for k in keys]
    option = {
        "backgroundColor": "transparent",
        "radar": {"indicator": [{"name": k, "max": 10} for k in keys], "splitArea": {"show": False}},
        "series": [{"type": "radar", "data": [{"value": scores, "areaStyle": {"color": "rgba(0,255,242,0.4)"}, "lineStyle": {"color": "#00fff2"}}]}]
    }
    st_echarts(options=option, height=height)

# --- 拓扑图 ---
def render_cyberpunk_map(nodes, height="250px", is_fullscreen=False):
    if not nodes: return
    graph_nodes = []
    symbol_base = 30 if is_fullscreen else 15
    for i, node in enumerate(nodes):
        logic = node.get('m_score') if node.get('m_score') is not None else 0.5
        graph_nodes.append({
            "name": str(node['id']), 
            "symbolSize": symbol_base * (0.8 + logic),
            "value": node['care_point'],
            "label": {"show": is_fullscreen, "formatter": node['care_point'][:5], "color": "#fff"}
        })
    option = {
        "backgroundColor": "#0e1117",
        "series": [{"type": "graph", "layout": "force", "data": graph_nodes, "force": {"repulsion": 1000 if is_fullscreen else 300}, "itemStyle": {"shadowBlur": 10}}]
    }
    st_echarts(options=option, height=height)

@st.dialog("🔭 全屏", width="large")
def view_fullscreen_map(nodes, user_name):
    render_cyberpunk_map(nodes, height="600px", is_fullscreen=True)
