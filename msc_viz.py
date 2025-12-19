### msc_viz.py ###
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import numpy as np
import random
from streamlit_echarts import st_echarts
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import msc_config as config
import msc_lib as msc

# ==========================================
# 🎨 0. 辅助工具 (颜色与坐标)
# ==========================================
def get_spectrum_color(keywords_str):
    """根据关键词字符串匹配 MSC 12 维光谱颜色"""
    if not keywords_str: return "#00CCFF" # 默认科技蓝
    # 优先匹配 Dimension Name
    for dim, color in config.SPECTRUM.items():
        if dim in keywords_str: return color
    # 其次匹配 Color Hex
    for color in config.SPECTRUM.values():
        if color in keywords_str: return color
    return "#00CCFF"

def get_cluster_color(cluster_id):
    CLUSTER_COLORS = list(config.SPECTRUM.values())
    return CLUSTER_COLORS[cluster_id % len(CLUSTER_COLORS)]

def get_random_ocean_coordinate():
    """生成随机的海洋坐标（太平洋/大西洋），用于展示无地理信息的漂流瓶"""
    oceans = [
        {"lat_min": -30, "lat_max": 30, "lon_min": 160, "lon_max": -140}, # 太平洋带
        {"lat_min": -40, "lat_max": 40, "lon_min": -45, "lon_max": -15}   # 大西洋带
    ]
    ocean = random.choice(oceans)
    
    # 经度处理 (跨越日界线逻辑)
    if ocean["lon_min"] > ocean["lon_max"]:
        if random.random() > 0.5: lon = random.uniform(ocean["lon_min"], 180)
        else: lon = random.uniform(-180, ocean["lon_max"])
    else:
        lon = random.uniform(ocean["lon_min"], ocean["lon_max"])
        
    lat = random.uniform(ocean["lat_min"], ocean["lat_max"])
    return lat, lon

# ==========================================
# 🧠 1. 聚类算法 (Clustering)
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
    
    if not raw_vectors or len(raw_vectors) < 2: return pd.DataFrame()

    # 简单对齐
    target_len = len(raw_vectors[0])
    clean_vectors = [v for v in raw_vectors if len(v) == target_len]
    clean_meta = [m for i, m in enumerate(raw_meta) if len(raw_vectors[i]) == target_len]
    
    if len(clean_vectors) < 2: return pd.DataFrame()

    try:
        real_n_clusters = min(n_clusters, len(clean_vectors))
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
    except: return pd.DataFrame()

# ==========================================
# 🌍 2. 3D 粒子地球 (World Map)
# ==========================================
def render_3d_particle_map(nodes, current_user):
    if not nodes: 
        st.info("The universe is empty.")
        return

    # 分层容器
    my_lats, my_lons, my_texts, my_colors = [], [], [], [] 
    others_lats, others_lons, others_colors = [], [], [] 
    sediment_lats, sediment_lons, sediment_colors = [], [], [] 
    drift_lats, drift_lons, drift_colors = [], [], [] # 海洋漂流层

    for node in nodes:
        loc = None
        is_drift = False
        try:
            if isinstance(node.get('location'), str): loc = json.loads(node['location'])
            elif isinstance(node.get('location'), dict): loc = node['location']
        except: pass
        
        # 🚨 无位置信息 -> 丢入海洋
        if not loc or not loc.get('lat'): 
            d_lat, d_lon = get_random_ocean_coordinate()
            loc = {"lat": d_lat, "lon": d_lon}
            is_drift = True

        lat, lon = loc.get('lat'), loc.get('lon')
        color = get_spectrum_color(str(node.get('keywords', '')))
        mode = node.get('mode', 'Active')

        if mode == 'Sediment':
            sediment_lats.append(lat); sediment_lons.append(lon)
            sediment_colors.append(color) 
        elif node['username'] == current_user:
            my_lats.append(lat); my_lons.append(lon)
            my_texts.append(f"<b>My Thought:</b> {node['care_point']}")
            my_colors.append(color) 
        elif is_drift:
            drift_lats.append(lat); drift_lons.append(lon)
            drift_colors.append(color)
        else:
            others_lats.append(lat); others_lons.append(lon)
            others_colors.append(color)

    fig = go.Figure()

    # Base Earth
    fig.add_trace(go.Scattergeo(lon=[], lat=[], mode='lines', line=dict(width=1, color='#111')))

    # Layers
    if sediment_lats:
        fig.add_trace(go.Scattergeo(
            lon=sediment_lons, lat=sediment_lats, mode='markers',
            marker=dict(size=2, color=sediment_colors, opacity=0.3, symbol='square'),
            hoverinfo='skip', name='Sediment'
        ))
    if others_lats:
        fig.add_trace(go.Scattergeo(
            lon=others_lons, lat=others_lats, mode='markers',
            text=["Signal"] * len(others_lats), hoverinfo='text',
            marker=dict(size=5, color=others_colors, opacity=0.8),
            name='Signals'
        ))
    if drift_lats:
        fig.add_trace(go.Scattergeo(
            lon=drift_lons, lat=drift_lats, mode='markers',
            text=["Drifting Thought"] * len(drift_lats), hoverinfo='text',
            marker=dict(size=4, color=drift_colors, opacity=0.5, symbol='diamond'),
            name='Drift'
        ))
    if my_lats:
        fig.add_trace(go.Scattergeo(
            lon=my_lons, lat=my_lats, mode='markers',
            text=my_texts, hoverinfo='text',
            marker=dict(size=10, color=my_colors, opacity=1.0, symbol='star', line=dict(width=1, color='white')),
            name='Me'
        ))

    fig.update_layout(
        geo=dict(
            scope='world', projection_type='orthographic',
            showland=True, landcolor='rgb(15, 15, 15)',
            showocean=True, oceancolor='rgb(5, 5, 10)',
            bgcolor='black', showlakes=False, showcountries=False
        ),
        paper_bgcolor='black', margin={"r":0,"t":0,"l":0,"b":0}, height=500, 
        showlegend=True, legend=dict(font=dict(color="#888"), bgcolor="rgba(0,0,0,0)", orientation="h", y=0)
    )
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 🌌 3. 3D 星河 (Abstract Galaxy)
# ==========================================
def render_3d_galaxy(nodes):
    if len(nodes) < 3: 
        st.info("🌌 星河汇聚中...")
        return
    df = compute_clusters(nodes, n_clusters=6)
    if df.empty: return
    
    df['size'] = 6
    fig = px.scatter_3d(
        df, x='x', y='y', z='z', 
        color='cluster', 
        color_continuous_scale=list(config.SPECTRUM.values()), 
        hover_name='care_point', 
        template="plotly_dark", 
        opacity=0.9
    )
    fig.update_layout(
        scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False), bgcolor='black'), 
        paper_bgcolor="black", margin={"r":0,"t":0,"l":0,"b":0}, height=600, showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 🕸️ 4. 雷达图 (Radar)
# ==========================================
def render_radar_chart(radar_dict, height="200px"):
    keys = ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]
    scores = [radar_dict.get(k, 3.0) for k in keys]
    option = {"backgroundColor": "transparent", "radar": {"indicator": [{"name": k, "max": 10} for k in keys], "splitArea": {"show": False}}, "series": [{"type": "radar", "data": [{"value": scores, "areaStyle": {"color": "rgba(0,255,242,0.4)"}, "lineStyle": {"color": "#00fff2"}}]}]}
    st_echarts(options=option, height=height)

# ==========================================
# 🔮 5. 赛博朋克关系图 (Network Graph)
# ==========================================
def render_cyberpunk_map(nodes, height="250px", is_fullscreen=False):
    if not nodes: return None
    
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

    # 简单连线逻辑
    node_count = len(graph_nodes)
    start_idx = max(0, node_count - 50) # 只算最近50个，防止卡死
    for i in range(start_idx, node_count):
        for j in range(i + 1, node_count):
            na, nb = graph_nodes[i], graph_nodes[j]
            score = 0
            if na['keywords'] and nb['keywords']:
                shared = len(set(na['keywords']).intersection(set(nb['keywords'])))
                if shared > 0: score += 0.5
            
            line_color = "#00fff2"
            if na.get("itemStyle", {}).get("color") == nb.get("itemStyle", {}).get("color"):
                line_color = na["itemStyle"]["color"]

            if score >= 0.5: 
                graph_links.append({"source": na['name'], "target": nb['name'], "lineStyle": {"width": 1, "color": line_color, "curveness": 0.2, "opacity": 0.3}})

    option = {"backgroundColor": "#0e1117", "tooltip": {"formatter": "{b}"}, "series": [{"type": "graph", "layout": "force", "data": graph_nodes, "links": graph_links, "roam": True, "force": {"repulsion": 800 if is_fullscreen else 200, "gravity": 0.1, "edgeLength": 50}, "itemStyle": {"shadowBlur": 10}, "lineStyle": {"color": "source", "curveness": 0.2}}]}
    
    events = {"click": "function(params) { return params.name }"}
    clicked_id = st_echarts(options=option, height=height, events=events, key=f"map_{height}")
    
    if clicked_id:
        target_node = next((n for n in graph_nodes if n['name'] == clicked_id), None)
        if target_node: return target_node['full_data']
    return None

# ==========================================
# 🔭 6. 弹窗组件 (Dialogs)
# ==========================================
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
        with st.spinner("Analyzing..."):
            report = msc.analyze_persona_report(radar_dict)
            st.session_state[report_key] = report
    report = st.session_state[report_key]
    with st.container(border=True):
        st.markdown("#### 🌊 现状 · Status Quo")
        st.info(report.get("status_quo", "分析中..."))
    with st.container(border=True):
        st.markdown("#### 🌱 成长 · Evolution")
        st.success(report.get("growth_path", "分析中..."))
