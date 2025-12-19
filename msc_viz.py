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

# ==========================================
# 🎨 0. 辅助工具
# ==========================================
def get_spectrum_color(keywords_str):
    if not keywords_str: return "#00CCFF"
    for dim, color in config.SPECTRUM.items():
        if dim in keywords_str: return color
    for color in config.SPECTRUM.values():
        if color in keywords_str: return color
    return "#00CCFF"

def get_cluster_color(cluster_id):
    CLUSTER_COLORS = list(config.SPECTRUM.values())
    return CLUSTER_COLORS[cluster_id % len(CLUSTER_COLORS)]

def get_random_coordinate():
    """完全随机的全球坐标（模拟卫星巡游）"""
    lat = random.uniform(-60, 70) # 避开极地
    lon = random.uniform(-180, 180)
    return lat, lon

# ==========================================
# 🌍 1. 伪3D 地球 (高光效版)
# ==========================================
def render_3d_particle_map(nodes, current_user):
    if not nodes: 
        st.info("The universe is empty.")
        return

    # 数据容器
    # 1. 别人的信号 (实点)
    sig_lats, sig_lons, sig_colors, sig_texts = [], [], [], []
    # 2. 别人的信号 (光晕 - 用于制造灯光感)
    glow_lats, glow_lons, glow_colors = [], [], []
    
    # 3. 我的卫星 (实点)
    my_lats, my_lons, my_colors, my_texts = [], [], [], []
    
    # 4. 历史沉淀 (暗淡)
    sed_lats, sed_lons, sed_colors = [], [], []

    for node in nodes:
        # --- 位置解析 ---
        loc = None
        is_random = False
        try:
            if isinstance(node.get('location'), str): loc = json.loads(node['location'])
            elif isinstance(node.get('location'), dict): loc = node['location']
        except: pass
        
        # 如果没有位置，随机飞在天上
        if not loc or not loc.get('lat'): 
            d_lat, d_lon = get_random_coordinate()
            loc = {"lat": d_lat, "lon": d_lon}
            is_random = True

        lat, lon = loc.get('lat'), loc.get('lon')
        color = get_spectrum_color(str(node.get('keywords', '')))
        mode = node.get('mode', 'Active')

        # --- 分层逻辑 ---
        
        # A. 历史沉淀 (Sediment) -> 极暗，贴地
        if mode == 'Sediment':
            sed_lats.append(lat); sed_lons.append(lon)
            sed_colors.append(color) 
            
        # B. 我的意义 (My Orbit) -> 卫星
        elif node['username'] == current_user:
            my_lats.append(lat); my_lons.append(lon)
            my_colors.append(color)
            # 只有我的显示具体内容
            my_texts.append(f"<b>{node['care_point']}</b><br><span style='font-size:0.8em; color:#ccc'>{node.get('insight','')}</span>")
            
        # C. 他人信号 (Signals) -> 城市灯光
        else:
            sig_lats.append(lat); sig_lons.append(lon)
            sig_colors.append(color)
            sig_texts.append(f"Signal: {node['care_point']}")
            # 添加到光晕层
            glow_lats.append(lat); glow_lons.append(lon)
            glow_colors.append(color)

    fig = go.Figure()

    # --- Layer 1: 历史沉淀 (Sediment) ---
    if sed_lats:
        fig.add_trace(go.Scattergeo(
            lon=sed_lons, lat=sed_lats, mode='markers',
            marker=dict(size=2, color=sed_colors, opacity=0.3, symbol='circle'),
            hoverinfo='skip', name='Sediment'
        ))

    # --- Layer 2: 城市光晕 (The Glow) ---
    # 这一层画得大一点，透明一点，制造“发光”的错觉
    if glow_lats:
        fig.add_trace(go.Scattergeo(
            lon=glow_lons, lat=glow_lats, mode='markers',
            marker=dict(
                size=8, # 大光晕
                color=glow_colors, 
                opacity=0.2, # 很透明
                symbol='circle'
            ),
            hoverinfo='skip', showlegend=False
        ))

    # --- Layer 3: 信号核心 (The Core) ---
    if sig_lats:
        fig.add_trace(go.Scattergeo(
            lon=sig_lons, lat=sig_lats, mode='markers',
            text=sig_texts, hoverinfo='text',
            marker=dict(
                size=3, # 核心小亮点
                color=sig_colors, 
                opacity=0.9, 
                symbol='circle',
                line=dict(width=0)
            ),
            name='Signals'
        ))

    # --- Layer 4: 我的卫星 (My Orbit) ---
    if my_lats:
        fig.add_trace(go.Scattergeo(
            lon=my_lons, lat=my_lats, mode='markers',
            text=my_texts, hoverinfo='text',
            marker=dict(
                size=10, # 明显大
                color=my_colors, 
                opacity=1.0, 
                symbol='diamond', # 菱形，像人造卫星
                line=dict(width=1, color='white') # 白边，高对比度
            ),
            name='My Orbit'
        ))

    # --- 视觉配置 ---
    fig.update_layout(
        geo=dict(
            scope='world', 
            projection_type='orthographic', # 伪3D球体
            
            # 🌑 暗黑星球风格设置
            showland=True, landcolor='rgb(15, 15, 15)', # 极暗的陆地
            showocean=True, oceancolor='rgb(5, 5, 10)', # 近乎黑色的海洋
            showlakes=False,
            showcountries=True, countrycolor='rgb(40, 40, 40)', # 隐约的国界线
            showcoastlines=True, coastlinecolor='rgb(50, 50, 50)', # 海岸线
            
            # 🌌 大气层效果 (Atmosphere)
            projection_rotation=dict(lon=120, lat=20), # 默认视角
            showatmosphere=True, 
            atmospherecolor='rgb(0, 30, 60)', # 幽蓝的大气层
            atmospherewidth=5,
            
            bgcolor='black'
        ),
        paper_bgcolor='black', 
        margin={"r":0,"t":0,"l":0,"b":0}, 
        height=600, 
        showlegend=True,
        legend=dict(
            x=0, y=0, 
            font=dict(color="#666"), 
            bgcolor="rgba(0,0,0,0)",
            orientation="h"
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ... (保留其他函数: compute_clusters, render_3d_galaxy, render_radar_chart, render_cyberpunk_map, view_fullscreen_map, view_radar_details) ...

# -------------------------------------------------------------------------
# 为了保证文件完整性，以下是必须保留的函数
# -------------------------------------------------------------------------

def compute_clusters(nodes, n_clusters=5):
    raw_vectors = []
    raw_meta = []
    for node in nodes:
        if node['vector']:
            try:
                v = json.loads(node['vector'])
                if isinstance(v, list) and len(v) > 0:
                    raw_vectors.append(v)
                    raw_meta.append({"care_point": node['care_point'], "id": str(node['id'])})
            except: pass
    if not raw_vectors or len(raw_vectors) < 2: return pd.DataFrame()
    target_len = len(raw_vectors[0])
    clean_vectors = [v for v in raw_vectors if len(v) == target_len]
    clean_meta = [m for i, m in enumerate(raw_meta) if len(raw_vectors[i]) == target_len]
    if len(clean_vectors) < 2: return pd.DataFrame()
    try:
        kmeans = KMeans(n_clusters=min(n_clusters, len(clean_vectors)), random_state=42, n_init=10)
        labels = kmeans.fit_predict(clean_vectors)
        pca = PCA(n_components=3)
        coords_3d = pca.fit_transform(clean_vectors)
        df = pd.DataFrame(clean_meta)
        df['cluster'] = labels
        df['color'] = [get_cluster_color(l) for l in labels]
        df['x'] = coords_3d[:, 0]; df['y'] = coords_3d[:, 1]; df['z'] = coords_3d[:, 2]
        return df
    except: return pd.DataFrame()

def render_3d_galaxy(nodes):
    if len(nodes) < 3: 
        st.info("🌌 星河汇聚中...")
        return
    df = compute_clusters(nodes, n_clusters=6)
    if df.empty: return
    df['size'] = 6
    fig = px.scatter_3d(df, x='x', y='y', z='z', color='cluster', color_continuous_scale=list(config.SPECTRUM.values()), hover_name='care_point', template="plotly_dark", opacity=0.9)
    fig.update_layout(scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False), bgcolor='black'), paper_bgcolor="black", margin={"r":0,"t":0,"l":0,"b":0}, height=600, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

def render_radar_chart(radar_dict, height="200px"):
    keys = ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]
    scores = [radar_dict.get(k, 3.0) for k in keys]
    option = {"backgroundColor": "transparent", "radar": {"indicator": [{"name": k, "max": 10} for k in keys], "splitArea": {"show": False}}, "series": [{"type": "radar", "data": [{"value": scores, "areaStyle": {"color": "rgba(0,255,242,0.4)"}, "lineStyle": {"color": "#00fff2"}}]}]}
    st_echarts(options=option, height=height)

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
        nid = str(node['id'])
        node_color = id_to_color.get(nid, default_color)
        label_text = node['care_point']
        if len(label_text) > 6: label_text = label_text[:5] + "..."
        graph_nodes.append({
            "name": nid, "id": nid, "symbolSize": symbol_base * (0.8 + logic),
            "value": node['care_point'], "label": {"show": is_fullscreen, "formatter": label_text, "color": "#fff", "fontSize": 10},
            "full_data": {"insight": node.get('insight', ''), "content": node['content'], "layer": node.get('meaning_layer', ''), "username": node['username']},
            "itemStyle": {"color": node_color}
        })
    node_count = len(graph_nodes)
    start_idx = max(0, node_count - 50)
    for i in range(start_idx, node_count):
        for j in range(i + 1, node_count):
            na, nb = graph_nodes[i], graph_nodes[j]
            score = 0 
            graph_links.append({"source": na['name'], "target": nb['name'], "lineStyle": {"width": 1, "color": "#555", "curveness": 0.2, "opacity": 0.3}})
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
