### msc_viz.py (终极完整版：包含光柱、聚类与关系图) ###

import streamlit as st
import pydeck as pdk
import pandas as pd
import json
import numpy as np
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
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
# 🧠 核心算法：星团引力计算 (带数据清洗)
# ==========================================
def compute_clusters(nodes, n_clusters=5):
    raw_vectors = []
    raw_meta = []
    
    # 1. 提取所有原始数据
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

    # 2. 数据清洗 (长度对齐)
    lengths = [len(v) for v in raw_vectors]
    if not lengths: return pd.DataFrame()
    
    from collections import Counter
    target_len = Counter(lengths).most_common(1)[0][0]
    
    clean_vectors = []
    clean_meta = []
    for i, v in enumerate(raw_vectors):
        if len(v) == target_len:
            clean_vectors.append(v)
            clean_meta.append(raw_meta[i])
            
    if len(clean_vectors) < 2: return pd.DataFrame()

    # 3. 聚类计算
    real_n_clusters = min(n_clusters, len(clean_vectors))
    
    try:
        kmeans = KMeans(n_clusters=real_n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(clean_vectors)
        
        df = pd.DataFrame(clean_meta)
        df['cluster'] = labels
        df['color'] = [get_cluster_color(l) for l in labels]
        return df
    except Exception as e:
        print(f"Cluster Error: {e}")
        return pd.DataFrame()

# ==========================================
# 🌍 3D 灯塔地图 (PyDeck - Beacon Map)
# ==========================================
def render_3d_beacon_map(nodes):
    if not nodes: 
        st.info("Waiting for signals...")
        return

    map_data = []
    
    for node in nodes:
        lat, lon = 0, 0
        weight = 1
        color = [100, 100, 100] # 默认灰
        
        # 1. 新闻节点 (High Priority)
        if node['username'] == 'World_Observer':
            keywords = str(node.get('keywords', ''))
            if 'Red' in keywords: color = [255, 50, 50]   # 红色冲突
            elif 'Green' in keywords: color = [50, 255, 50] # 绿色希望
            else: color = [50, 100, 255] # 蓝色焦虑
            
            # 模拟坐标
            lat = np.random.uniform(20, 50)
            lon = np.random.uniform(-120, 120)
            weight = 50 
            
        # 2. 用户节点 (User Thought)
        else:
            # 权重放大 100 倍！
            weight = config.USER_WEIGHT_MULTIPLIER
            color = [255, 215, 0] # 金色
            
            # 模拟用户坐标聚集
            center_lat = np.random.choice([35, 40, 51]) 
            center_lon = np.random.choice([139, -74, -0.1])
            lat = center_lat + np.random.normal(0, 2)
            lon = center_lon + np.random.normal(0, 2)

        map_data.append({
            "lat": lat, "lon": lon, "weight": weight, "color": color,
            "tooltip": node['care_point']
        })

    df = pd.DataFrame(map_data)

    # Layer 1: 六边形光柱
    layer_hex = pdk.Layer(
        "HexagonLayer", df,
        get_position=["lon", "lat"],
        auto_highlight=True,
        elevation_scale=500,
        elevation_range=[0, 3000],
        extruded=True,
        coverage=0.8,
        get_fill_color="color",
        pickable=True
    )
    
    # Layer 2: 散点光晕
    layer_scatter = pdk.Layer(
        "ScatterplotLayer", df,
        get_position=["lon", "lat"],
        get_color="color",
        get_radius=50000,
        opacity=0.3,
        stroked=True,
        filled=True,
        radius_min_pixels=2
    )

    view_state = pdk.ViewState(latitude=30, longitude=0, zoom=1.5, pitch=45)

    deck = pdk.Deck(
        layers=[layer_hex, layer_scatter],
        initial_view_state=view_state,
        tooltip={"text": "{tooltip}"},
        map_style="mapbox://styles/mapbox/dark-v10"
    )
    st.pydeck_chart(deck)

# ==========================================
# 🔮 赛博朋克关系图 (完整版：含聚类染色)
# ==========================================
def render_cyberpunk_map(nodes, height="250px", is_fullscreen=False):
    if not nodes: return
    
    # 1. 预计算聚类颜色
    cluster_df = compute_clusters(nodes, n_clusters=5)
    id_to_color = {}
    
    default_color = "#00fff2"
    
    if not cluster_df.empty:
        # 建立 ID 到颜色的映射
        for _, row in cluster_df.iterrows():
            id_to_color[row['id']] = row['color']

    graph_nodes, graph_links = [], []
    symbol_base = 30 if is_fullscreen else 15
    
    for i, node in enumerate(nodes):
        logic = node.get('logic_score') or 0.5
        keywords = []
        if node.get('keywords'):
            if isinstance(node['keywords'], str):
                try: keywords = json.loads(node['keywords'])
                except: keywords = []
            else: keywords = node['keywords']
        vector = None
        if node.get('vector'):
            if isinstance(node['vector'], str):
                try: vector = json.loads(node['vector'])
                except: pass
            else: vector = node['vector']
        
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

    # 2. 连线逻辑 (标签优先)
    node_count = len(graph_nodes)
    start_idx = max(0, node_count - 50) # 只显示最近50个节点的连线，防止卡顿
    
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
            
            # 连线染色：同色相连
            line_color = "#00fff2"
            if na.get("itemStyle", {}).get("color") == nb.get("itemStyle", {}).get("color"):
                line_color = na["itemStyle"]["color"]

            if score >= 0.65: 
                graph_links.append({"source": na['name'], "target": nb['name'], "lineStyle": {"width": 2.5, "color": line_color, "curveness": 0.2}})
            elif score >= 0.45: 
                graph_links.append({"source": na['name'], "target": nb['name'], "lineStyle": {"width": 1, "color": "#555", "type": "dashed", "curveness": 0.2}})

    option = {"backgroundColor": "#0e1117", "tooltip": {"formatter": "{b}"}, "series": [{"type": "graph", "layout": "force", "data": graph_nodes, "links": graph_links, "roam": True, "force": {"repulsion": 800 if is_fullscreen else 200, "gravity": 0.1, "edgeLength": 50}, "itemStyle": {"shadowBlur": 10}, "lineStyle": {"color": "source", "curveness": 0.2}}]}
    
    # 交互点击事件
    events = {"click": "function(params) { return params.name }"}
    clicked_id = st_echarts(options=option, height=height, events=events, key=f"map_{height}")
    
    if clicked_id:
        target_node = next((n for n in graph_nodes if n['name'] == clicked_id), None)
        if target_node: return target_node['full_data']
    return None

# ==========================================
# 🕸️ 雷达图 (Echarts)
# ==========================================
def render_radar_chart(radar_dict, height="200px"):
    keys = ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]
    scores = [radar_dict.get(k, 3.0) for k in keys]
    option = {"backgroundColor": "transparent", "radar": {"indicator": [{"name": k, "max": 10} for k in keys], "splitArea": {"show": False}}, "series": [{"type": "radar", "data": [{"value": scores, "areaStyle": {"color": "rgba(0,255,242,0.4)"}, "lineStyle": {"color": "#00fff2"}}]}]}
    st_echarts(options=option, height=height)

# ==========================================
# 🧬 深度画像
# ==========================================
@st.dialog("🧬 MSC 深度基因解码", width="large")
def view_radar_details(radar_dict, username):
    c1, c2 = st.columns([1, 1])
    with c1: render_radar_chart(radar_dict, height="350px")
    with c2:
        st.markdown(f"### {username}")
        for key, val in radar_dict.items():
            st.progress(val / 10, text=f"**{key}**: {val}")
    st.divider()
    
    report_key = f"report_{username}_{sum(radar_dict.values())}"
    if report_key not in st.session_state:
        with st.spinner("Analyzing..."):
            report = msc.analyze_persona_report(radar_dict)
            st.session_state[report_key] = report
    
    report = st.session_state[report_key]
    st.info(report.get("status_quo", "..."))
    st.success(report.get("growth_path", "..."))

@st.dialog("🔭 浩荡宇宙", width="large")
def view_fullscreen_map(nodes, user_name):
    st.markdown(f"### 🌌 {user_name} 的浩荡宇宙")
    # 这里调用完整的 cyberpunk map
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
