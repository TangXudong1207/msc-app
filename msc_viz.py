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

# 优化后的连线逻辑 (V72.1)
    for i in range(start_idx, node_count):
        for j in range(i + 1, node_count):
            na, nb = graph_nodes[i], graph_nodes[j]
            
            score = 0
            
            # 1. 标签重叠 (Tag Overlap) - 提升权重到 0.7
            # 这是目前最准确的指标。只要有共同关键词，就应该建立连接。
            shared_tags = 0
            if na['keywords'] and nb['keywords']:
                shared_tags = len(set(na['keywords']).intersection(set(nb['keywords'])))
                if shared_tags > 0:
                    # 有1个共同标签得0.5分，2个得0.8分，3个以上直接满分
                    score += min(0.5 + (shared_tags * 0.15), 0.9)

            # 2. 向量相似度 (Vector Similarity) - 降低权重到 0.3
            # (仅当 vector 有效且不是随机生成时才有意义，这里作为辅助)
            if na['vector'] and nb['vector'] and score < 0.9:
                try:
                    vec1, vec2 = np.array(na['vector']), np.array(nb['vector'])
                    # 防止除以零
                    norm = np.linalg.norm(vec1) * np.linalg.norm(vec2)
                    if norm > 0:
                        sim = np.dot(vec1, vec2) / norm
                        # 只有相似度非常高时才加分，避免随机噪声
                        if sim > 0.8: score += 0.2
                except: pass
            
            # 3. 阈值分级
            # 强连接 (Strong): 亮青色实线
            if score >= 0.65: 
                graph_links.append({
                    "source": na['name'], 
                    "target": nb['name'], 
                    "lineStyle": {"width": 2.5, "color": "#00fff2", "curveness": 0.2}
                })
            # 弱连接 (Weak): 灰色虚线
            elif score >= 0.4: 
                graph_links.append({
                    "source": na['name'], 
                    "target": nb['name'], 
                    "lineStyle": {"width": 1, "color": "#555", "type": "dashed", "curveness": 0.2}
                })
    option = {
        "backgroundColor": "#0e1117",
        "series": [{"type": "graph", "layout": "force", "data": graph_nodes, "links": graph_links, "roam": True, "force": {"repulsion": 500 if is_fullscreen else 200}, "itemStyle": {"shadowBlur": 10}}]
    }
    st_echarts(options=option, height=height)
# === 补全缺失的视图函数 ===
@st.dialog("🔭 浩荡宇宙", width="large")
def view_fullscreen_map(nodes, user_name):
    st.markdown(f"### 🌌 {user_name} 的浩荡宇宙")
    # 调用已有的渲染函数，开启全屏模式
    render_cyberpunk_map(nodes, height="600px", is_fullscreen=True)
