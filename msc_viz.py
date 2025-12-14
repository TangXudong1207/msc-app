### msc_viz.py (修复版：含粒子地图) ###

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from streamlit_echarts import st_echarts
import msc_config as config
import msc_lib as msc 

# ==========================================
# 🎨 智能配色盘
# ==========================================
CLUSTER_COLORS = [
    '#FF4B4B', '#1A73E8', '#FFA421', '#00C853', '#9C27B0', '#00BCD4'
]

def get_cluster_color(cluster_id):
    return CLUSTER_COLORS[cluster_id % len(CLUSTER_COLORS)]

# ==========================================
# 🌍 3D 粒子地球 (核心函数：必须存在！)
# ==========================================
def render_3d_particle_map(nodes):
    """
    使用 Plotly 3D Scatter 渲染地球上的发光粒子
    """
    if not nodes: 
        st.info("No geospatial signals detected yet.")
        return

    lats, lons, texts, colors, sizes = [], [], [], [], []
    
    for node in nodes:
        # 尝试提取坐标
        loc = None
        try:
            if isinstance(node.get('location'), str): loc = json.loads(node['location'])
            elif isinstance(node.get('location'), dict): loc = node['location']
        except: pass
        
        # 如果有坐标，或者是 News 节点
        if loc:
            lat = loc.get('lat', 0)
            lon = loc.get('lon', 0)
        elif node['username'] == 'World_Observer':
            # 如果新闻没解析出坐标，随机撒点 (兜底)
            lat = np.random.uniform(-40, 60)
            lon = np.random.uniform(-150, 150)
        else:
            continue # 普通无坐标节点不显示在地球上

        lats.append(lat)
        lons.append(lon)
        texts.append(f"<b>{node['care_point']}</b><br>{node.get('insight','')}")
        
        # 颜色映射 (新闻根据 Tension 变色)
        keywords = str(node.get('keywords', ''))
        if 'Red' in keywords: c = '#ff2b2b'   # 冲突红
        elif 'Green' in keywords: c = '#00ff88' # 希望绿
        else: c = '#00ccff' # 默认科技蓝
        colors.append(c)
        
        # 大小映射 (模拟张力强度)
        sizes.append(np.random.randint(8, 18))

    if not lats:
        st.info("No geospatial signals detected yet.")
        return

    fig = go.Figure()

    # 1. 绘制地球基底 (暗黑线框风格)
    fig.add_trace(go.Scattergeo(
        lon=[], lat=[],
        mode='lines',
        line=dict(width=1, color='#333'),
    ))

    # 2. 绘制发光粒子 (核心层)
    fig.add_trace(go.Scattergeo(
        lon=lons, lat=lats,
        mode='markers',
        text=texts,
        hoverinfo='text',
        marker=dict(
            size=sizes,
            color=colors,
            opacity=1.0,
            line=dict(width=2, color='white') # 白芯制造发光感
        ),
        name='Tension Core'
    ))
    
    # 3. 绘制光晕 (外层 - 制造霓虹感)
    fig.add_trace(go.Scattergeo(
        lon=lons, lat=lats,
        mode='markers',
        marker=dict(
            size=[s*2.5 for s in sizes], # 光晕大
            color=colors,
            opacity=0.3, # 半透明
            line=dict(width=0)
        ),
        hoverinfo='skip',
        name='Glow'
    ))

    fig.update_layout(
        geo=dict(
            scope='world',
            projection_type='orthographic', # 3D 球体
            showland=True,
            landcolor='rgb(15, 15, 15)',
            showocean=True,
            oceancolor='rgb(5, 5, 5)',
            bgcolor='black',
            showlakes=False,
            showcountries=True,
            countrycolor='#333'
        ),
        paper_bgcolor='black',
        margin={"r":0,"t":0,"l":0,"b":0},
        height=600,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 聚类计算 (辅助)
# ==========================================
def compute_clusters(nodes, n_clusters=5):
    raw_vectors = []
    raw_meta = []
    
    for node in nodes:
        if node['vector']:
            try:
                v = json.loads(node['vector'])
                if isinstance(v, list) and len(v) > 0:
                    raw_vectors.append(v)
                    raw_meta.append({
                        "care_point": node['care_point'],
                        "insight": node.get('insight', ''),
                        "id": str(node['id'])
                    })
            except: pass
    
    if not raw_vectors: return pd.DataFrame()

    lengths = [len(v) for v in raw_vectors]
    if not lengths: return pd.DataFrame()
    from collections import Counter
    target_len = Counter(lengths).most_common(1)[0][0]
    
    clean_vectors, clean_meta = [], []
    for i, v in enumerate(raw_vectors):
        if len(v) == target_len:
            clean_vectors.append(v)
            clean_meta.append(raw_meta[i])
            
    if len(clean_vectors) < 2: return pd.DataFrame()

    real_n_clusters = min(n_clusters, len(clean_vectors))
    try:
        kmeans = KMeans(n_clusters=real_n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(clean_vectors)
        pca = PCA(n_components=3)
        coords_3d = pca.fit_transform(clean_vectors)

        df = pd.DataFrame(clean_meta)
        df['cluster'] = labels
        df['color'] = [get_cluster_color(l) for l in labels]
        df['x'] = coords_3d[:, 0]
        df['y'] = coords_3d[:, 1]
        df['z'] = coords_3d[:, 2]
        return df
    except Exception as e:
        print(f"Cluster Error: {e}")
        return pd.DataFrame()

# ==========================================
# 🌌 3D 星河
# ==========================================
def render_3d_galaxy(nodes):
    if len(nodes) < 3: 
        st.info("🌌 星河汇聚中...")
        return
    df = compute_clusters(nodes, n_clusters=6)
    if df.empty: return
    
    df['size'] = 6
    fig = px.scatter_3d(df, x='x', y='y', z='z', color='cluster', color_continuous_scale=CLUSTER_COLORS, hover_name='care_point', template="plotly_dark", opacity=0.9)
    fig.update_layout(scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False), bgcolor='black'), paper_bgcolor="black", margin={"r":0,"t":0,"l":0,"b":0}, height=600, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 🕸️ 雷达图
# ==========================================
def render_radar_chart(radar_dict, height="200px"):
    keys = ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]
    scores = [radar_dict.get(k, 3.0) for k in keys]
    option = {"backgroundColor": "transparent", "radar": {"indicator": [{"name": k, "max": 10} for k in keys], "splitArea": {"show": False}}, "series": [{"type": "radar", "data": [{"value": scores, "areaStyle": {"color": "rgba(0,255,242,0.4)"}, "lineStyle": {"color": "#00fff2"}}]}]}
    st_echarts(options=option, height=height)

# ==========================================
# 🔮 赛博朋克关系图
# ==========================================
def render_cyberpunk_map(nodes, height="250px", is_fullscreen=False):
    if not nodes: return
    
    cluster_df = compute_clusters(nodes, n_clusters=5)
    id_to_color = {}
    default_color = "#00fff2"
    
    if not cluster_df.empty:
        for i, color in enumerate(cluster_df['color']):
            if i < len(nodes): id_to_color[str(nodes[i]['id'])] = color

    graph_nodes, graph_links = [], []
    symbol_base = 30 if is_fullscreen else 15
    
    for i, node in enumerate(nodes):
        logic = node.get('logic_score') or 0.5
        keywords = []
        try: keywords = json.loads(node.get('keywords', '[]'))
        except: keywords = []
        vector = None
        try: vector = json.loads(node.get('vector', '[]'))
        except: pass
        
        nid = str(node['id'])
        node_color = id_to_color.get(nid, default_color)
        label_text = node['care_point']
        if len(label_text) > 6: label_text = label_text[:5] + "..."

        graph_nodes.append({
            "name": nid, "id": nid,
            "symbolSize": symbol_base * (0.8 + logic),
            "value": node['care_point'],
            "label": {"show": is_fullscreen, "formatter": label_text, "color": "#fff", "fontSize": 10},
            "full_data": {"insight": node.get('insight', ''), "content": node['content'], "layer": node.get('meaning_layer', ''), "username": node['username']},
            "vector": vector, "keywords": keywords,
            "itemStyle": {"color": node_color}
        })

    node_count = len(graph_nodes)
    start_idx = max(0, node_count - 50)
    for i in range(start_idx, node_count):
        for j in range(i + 1, node_count):
            na, nb = graph_nodes[i], graph_nodes[j]
            score = 0
            if na['keywords'] and nb['keywords']:
                shared = len(set(na['keywords']).intersection(set(nb['keywords'])))
                if shared > 0: score += min(0.4 + (shared * 0.15), 0.9)
            if na['vector'] and nb['vector'] and score < 0.9:
                try:
                    vec1, vec2 = np.array(na['vector']), np.array(nb['vector'])
                    norm = np.linalg.norm(vec1) * np.linalg.norm(vec2)
                    if norm > 0:
                        sim = np.dot(vec1, vec2) / norm
                        if sim > 0.8: score += 0.2
                except: pass
            
            line_color = "#00fff2"
            if na.get("itemStyle", {}).get("color") == nb.get("itemStyle", {}).get("color"):
                line_color = na["itemStyle"]["color"]

            if score >= 0.65: 
                graph_links.append({"source": na['name'], "target": nb['name'], "lineStyle": {"width": 2.5, "color": line_color, "curveness": 0.2}})
            elif score >= 0.45: 
                graph_links.append({"source": na['name'], "target": nb['name'], "lineStyle": {"width": 1, "color": "#555", "type": "dashed", "curveness": 0.2}})

    option = {"backgroundColor": "#0e1117", "tooltip": {"formatter": "{b}"}, "series": [{"type": "graph", "layout": "force", "data": graph_nodes, "links": graph_links, "roam": True, "force": {"repulsion": 800 if is_fullscreen else 200, "gravity": 0.1, "edgeLength": 50}, "itemStyle": {"shadowBlur": 10}, "lineStyle": {"color": "source", "curveness": 0.2}}]}
    events = {"click": "function(params) { return params.name }"}
    clicked_id = st_echarts(options=option, height=height, events=events, key=f"map_{height}")
    if clicked_id:
        target_node = next((n for n in graph_nodes if n['name'] == clicked_id), None)
        if target_node: return target_node['full_data']
    return None

@st.dialog("🔭 浩荡宇宙", width="large")
def view_fullscreen_map(nodes, user_name):
    st.markdown(f"### 🌌 {user_name} 的浩荡宇宙")
    clicked_data = render_cyberpunk_map(nodes, height="500px", is_fullscreen=True)
    if clicked_data:
        st.divider()
        st.markdown(f"#### ✨ {clicked_data.get('layer', 'Selected Node')}")
        c1, c2 = st.columns([0.7, 0.3])
        with c1:
            st.info(f"**Insight:** {clicked_data['insight']}")
            st.caption(f"> \"{clicked_data['content']}\"")
        with c2:
            if st.button("📍 定位上下文", use_container_width=True): st.toast("Time travel initiated...", icon="⏳")

@st.dialog("🧬 MSC 深度基因解码", width="large")
def view_radar_details(radar_dict, username):
    c1, c2 = st.columns([1, 1])
    with c1: render_radar_chart(radar_dict, height="350px")
    with c2:
        st.markdown(f"### {username} 的核心参数")
        for key, val in radar_dict.items():
            st.progress(val / 10, text=f"**{key}**: {val}")
    st.divider()
    
    report_key = f"report_{username}_{sum(radar_dict.values())}"
    if report_key not in st.session_state:
        with st.spinner("正在连接潜意识层，解析精神底色..."):
            report = msc.analyze_persona_report(radar_dict)
            st.session_state[report_key] = report
    report = st.session_state[report_key]
    with st.container(border=True):
        st.markdown("#### 🌊 现状 · Status Quo")
        st.info(report.get("status_quo", "分析中..."))
    with st.container(border=True):
        st.markdown("#### 🌱 成长 · Evolution")
        st.success(report.get("growth_path", "分析中..."))
