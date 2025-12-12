import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import numpy as np
from sklearn.decomposition import PCA # 🌟 核心修复：必须引入
from streamlit_echarts import st_echarts
import msc_config as config # 引入配置以读取阈值(如果有的话)

# ... (2D 地图代码保持不变，为省空间略) ...
def render_2d_world_map(nodes):
    map_data = [{"lat": 39.9, "lon": 116.4, "size": 10, "label": "HQ"}]
    for _ in range(len(nodes) + 15): 
        lon = np.random.uniform(-150, 150); lat = np.random.uniform(-40, 60)
        map_data.append({"lat": float(lat), "lon": float(lon), "size": 5, "label": "Node"})
    df = pd.DataFrame(map_data)
    fig = go.Figure(data=go.Scattergeo(lon = df["lon"], lat = df["lat"], mode = 'markers', marker = dict(size=5, color='#ffd60a', opacity=0.8)))
    fig.update_layout(geo = dict(scope='world', projection_type='natural earth', showland=True, landcolor="rgb(20, 20, 20)", bgcolor="black"), margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="black", height=500)
    st.plotly_chart(fig, use_container_width=True)

# ... (3D 星河代码保持不变，为省空间略) ...
def render_3d_galaxy(nodes):
    if len(nodes) < 3: st.info("🌌 星河汇聚中..."); return
    vectors, labels = [], []
    for i, node in enumerate(nodes):
        if node['vector']:
            try:
                v = json.loads(node['vector']); vectors.append(v); labels.append(node['care_point'])
            except: pass
    if not vectors: return
    pca = PCA(n_components=3); coords = pca.fit_transform(vectors)
    df = pd.DataFrame(coords, columns=['x','y','z']); df['label']=labels; df['size']=8
    fig = px.scatter_3d(df, x='x', y='y', z='z', size='size', hover_name='label', template="plotly_dark", opacity=0.8)
    fig.update_layout(scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False), bgcolor='black'), paper_bgcolor="black", margin={"r":0,"t":0,"l":0,"b":0}, height=600, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

def render_radar_chart(radar_dict, height="200px"):
    keys = ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]
    scores = [radar_dict.get(k, 3.0) for k in keys]
    option = {"backgroundColor": "transparent", "radar": {"indicator": [{"name": k, "max": 10} for k in keys], "splitArea": {"show": False}}, "series": [{"type": "radar", "data": [{"value": scores, "areaStyle": {"color": "rgba(0,255,242,0.4)"}, "lineStyle": {"color": "#00fff2"}}]}]}
    st_echarts(options=option, height=height)

# 🌟 修复：连线逻辑
def render_cyberpunk_map(nodes, height="250px", is_fullscreen=False):
    if not nodes: return
    graph_nodes, graph_links = [], []
    symbol_base = 30 if is_fullscreen else 15
    
    # 1. 生成节点
    for i, node in enumerate(nodes):
        logic = node.get('logic_score') or 0.5
        keywords = json.loads(node['keywords']) if node.get('keywords') else []
        vector = json.loads(node['vector']) if node.get('vector') else None
        
        graph_nodes.append({
            "name": str(node['id']), "id": str(node['id']),
            "symbolSize": symbol_base * (0.8 + logic),
            "value": node['care_point'],
            "label": {"show": is_fullscreen, "formatter": node['care_point'][:5], "color": "#fff"},
            "vector": vector, "keywords": keywords
        })

    # 2. 生成连线 (Relaxed Logic)
    # 我们降低了相似度阈值，并加入了 Tag 匹配
    node_count = len(graph_nodes)
    # 为了性能，只比较最近的 30 个节点
    start_idx = max(0, node_count - 30)
    
    for i in range(start_idx, node_count):
        for j in range(i + 1, node_count):
            na, nb = graph_nodes[i], graph_nodes[j]
            
            score = 0
            # A. 向量相似度
            if na['vector'] and nb['vector']:
                vec1, vec2 = np.array(na['vector']), np.array(nb['vector'])
                sim = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
                score += sim * 0.6
                
            # B. 标签重叠度 (Meaning Overlap)
            if na['keywords'] and nb['keywords']:
                overlap = len(set(na['keywords']).intersection(set(nb['keywords'])))
                if overlap > 0: score += 0.4 # 只要有共同标签就加分
            
            # C. 阈值判断
            if score > 0.75: # 强连接
                graph_links.append({"source": na['name'], "target": nb['name'], "lineStyle": {"width": 2, "color": "#00fff2"}})
            elif score > 0.55: # 弱连接 (降低门槛)
                graph_links.append({"source": na['name'], "target": nb['name'], "lineStyle": {"width": 0.5, "color": "#555", "type": "dashed"}})

    option = {
        "backgroundColor": "#0e1117",
        "series": [{"type": "graph", "layout": "force", "data": graph_nodes, "links": graph_links, "roam": True, "force": {"repulsion": 500 if is_fullscreen else 200}, "itemStyle": {"shadowBlur": 10}}]
    }
    st_echarts(options=option, height=height)
