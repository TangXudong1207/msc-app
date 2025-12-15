### msc_viz.py (v74.0 Spectrum Edition) ###

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
# 🎨 12维光谱颜色匹配器
# ==========================================
def get_spectrum_color(keywords_str):
    """
    根据关键词字符串匹配 MSC 12 维光谱颜色。
    如果没匹配到，返回默认科技蓝。
    """
    if not keywords_str: return "#00CCFF"
    
    # 优先匹配 Dimension Name
    for dim, color in config.SPECTRUM.items():
        if dim in keywords_str:
            return color
            
    # 其次匹配 Color Hex (有时候 keywords 里直接存了颜色)
    for color in config.SPECTRUM.values():
        if color in keywords_str:
            return color
            
    return "#00CCFF"

# 用于聚类的简单色盘 (Fallback)
CLUSTER_COLORS = list(config.SPECTRUM.values())
def get_cluster_color(cluster_id):
    return CLUSTER_COLORS[cluster_id % len(CLUSTER_COLORS)]

# ==========================================
# 🧠 核心算法：聚类 (带数据清洗)
# ==========================================
def compute_clusters(nodes, n_clusters=5):
    raw_vectors = []
    raw_meta = []
    
    # 1. 提取所有原始数据
    for node in nodes:
        if node['vector']:
            try:
                v = json.loads(node['vector'])
                # 确保是列表且不为空
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
# 🌍 3D 粒子地球 (双层宇宙 + 飞行连线)
# ==========================================
def render_3d_particle_map(nodes):
    if not nodes: 
        st.info("The universe is empty.")
        return

    # 数据容器
    news_nodes = []
    user_nodes = []
    arcs = [] # 连线数据
    
    for node in nodes:
        # 解析数据
        loc = None
        target_loc = None
        try:
            if isinstance(node.get('location'), str): loc = json.loads(node['location'])
            elif isinstance(node.get('location'), dict): loc = node['location']
            
            # 解析连线目标 (新闻特有)
            if 'target_location' in node: 
                 t = node['target_location']
                 if isinstance(t, str): target_loc = json.loads(t)
                 elif isinstance(t, dict): target_loc = t
        except: pass
        
        # 补全向量
        vec = None
        if node['vector']:
            try: vec = json.loads(node['vector'])
            except: pass
        node['_vec'] = vec
        
        # 兜底坐标
        if not loc and node['username'] == 'World_Observer':
             loc = {'lat': np.random.uniform(-40, 60), 'lon': np.random.uniform(-150, 150)}
        node['_loc'] = loc
        node['_target'] = target_loc

        # 分类
        if node['username'] == 'World_Observer':
            news_nodes.append(node)
            # 如果有目标地，且不同于原点，添加到连线列表
            if loc and target_loc:
                if abs(loc['lat'] - target_loc['lat']) > 1 or abs(loc['lon'] - target_loc['lon']) > 1:
                    k = str(node.get('keywords', ''))
                    color = get_spectrum_color(k)
                    arcs.append({
                        'start_lat': loc['lat'], 'start_lon': loc['lon'],
                        'end_lat': target_loc['lat'], 'end_lon': target_loc['lon'],
                        'color': color
                    })
        else:
            user_nodes.append(node)

    # 计算引力吸附 (User -> News)
    for u_node in user_nodes:
        if not u_node['_vec']: continue
        best_news = None
        best_sim = 0
        for n_node in news_nodes:
            if not n_node['_vec']: continue
            try:
                v1 = np.array(u_node['_vec']); v2 = np.array(n_node['_vec'])
                sim = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
                if sim > best_sim: best_sim = sim; best_news = n_node
            except: pass
        
        if best_news and best_sim > 0.75:
            target = best_news['_loc']
            # 吸附在新闻上方
            u_node['_loc']['lat'] = target['lat'] + np.random.normal(0, 2)
            u_node['_loc']['lon'] = target['lon'] + np.random.normal(0, 2)
            u_node['_attracted'] = True
        else:
            u_node['_attracted'] = False

    fig = go.Figure()

    # 1. 地球基底
    fig.add_trace(go.Scattergeo(
        lon=[], lat=[], mode='lines', line=dict(width=1, color='#222'),
    ))

    # 2. 绘制连线 (Arcs)
    for arc in arcs:
        fig.add_trace(go.Scattergeo(
            lon=[arc['start_lon'], arc['end_lon']],
            lat=[arc['start_lat'], arc['end_lat']],
            mode='lines',
            line=dict(width=1, color=arc['color']),
            opacity=0.6,
            hoverinfo='skip',
            name='Impact Arc'
        ))

    # 3. 绘制新闻 (Active & Sediment)
    act_lats, act_lons, act_txts, act_cols, act_sizes = [], [], [], [], []
    sed_lats, sed_lons, sed_cols = [], [], []
    
    for n in news_nodes:
        if not n['_loc']: continue
        lat, lon = n['_loc']['lat'], n['_loc']['lon']
        color_hex = get_spectrum_color(str(n.get('keywords', '')))
        
        if n.get('mode') == 'Sediment':
            sed_lats.append(lat); sed_lons.append(lon)
            # 简单变暗处理：此处保持原色但高透明度
            sed_cols.append(color_hex)
        else:
            act_lats.append(lat); act_lons.append(lon)
            act_txts.append(f"<b>{n['care_point']}</b><br>{n.get('insight','')}")
            act_cols.append(color_hex)
            # 大小基于 intensity，默认 15
            size = float(n.get('intensity', 0.5)) * 20 + 5
            act_sizes.append(size)

    if sed_lats:
        fig.add_trace(go.Scattergeo(
            lon=sed_lons, lat=sed_lats, mode='markers',
            marker=dict(size=4, color=sed_cols, opacity=0.4, symbol='square'),
            hoverinfo='skip', name='History Layer'
        ))
    
    if act_lats:
        fig.add_trace(go.Scattergeo(
            lon=act_lons, lat=act_lats, mode='markers',
            text=act_txts, hoverinfo='text',
            marker=dict(size=act_sizes, color=act_cols, opacity=1.0, line=dict(width=2, color='white')),
            name='Active Pulse'
        ))
        # 光晕
        fig.add_trace(go.Scattergeo(
            lon=act_lons, lat=act_lats, mode='markers',
            marker=dict(size=[s*2.5 for s in act_sizes], color=act_cols, opacity=0.3, line=dict(width=0)),
            hoverinfo='skip', name='Glow'
        ))

    # 4. 用户思想 (金色星辰)
    usr_lats, usr_lons, usr_txts, usr_syms = [], [], [], []
    for u in user_nodes:
        if not u['_loc']: continue
        usr_lats.append(u['_loc']['lat'])
        usr_lons.append(u['_loc']['lon'])
        usr_txts.append(f"@{u['username']}: {u['care_point']}")
        usr_syms.append('star' if u.get('_attracted') else 'circle')

    if usr_lats:
        fig.add_trace(go.Scattergeo(
            lon=usr_lons, lat=usr_lats, mode='markers',
            text=usr_txts, hoverinfo='text',
            marker=dict(size=5, color='#FFD700', symbol=usr_syms, opacity=0.9, line=dict(width=0.5, color='white')),
            name='Human Thought'
        ))

    fig.update_layout(
        geo=dict(
            scope='world', projection_type='orthographic',
            showland=True, landcolor='rgb(10, 10, 10)',
            showocean=True, oceancolor='rgb(5, 5, 5)',
            bgcolor='black', showlakes=False, showcountries=True, countrycolor='#333'
        ),
        paper_bgcolor='black', margin={"r":0,"t":0,"l":0,"b":0}, height=600, showlegend=True,
        legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0)")
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 🕸️ 雷达图 (Echarts)
# ==========================================
def render_radar_chart(radar_dict, height="200px"):
    keys = ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]
    scores = [radar_dict.get(k, 3.0) for k in keys]
    option = {"backgroundColor": "transparent", "radar": {"indicator": [{"name": k, "max": 10} for k in keys], "splitArea": {"show": False}}, "series": [{"type": "radar", "data": [{"value": scores, "areaStyle": {"color": "rgba(0,255,242,0.4)"}, "lineStyle": {"color": "#00fff2"}}]}]}
    st_echarts(options=option, height=height)

# ==========================================
# 🌌 3D 星河 (Abstract Galaxy)
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
        color_continuous_scale=list(config.SPECTRUM.values()), # 使用12维色盘
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
# 🔮 赛博朋克关系图 (Echarts)
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
