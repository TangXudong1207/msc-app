### msc_viz.py ###
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import numpy as np
import random
import math
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

def get_random_ocean_coordinate():
    """太平洋/大西洋随机坐标"""
    oceans = [
        {"lat_min": -30, "lat_max": 30, "lon_min": 160, "lon_max": -140},
        {"lat_min": -40, "lat_max": 40, "lon_min": -45, "lon_max": -15}
    ]
    ocean = random.choice(oceans)
    if ocean["lon_min"] > ocean["lon_max"]:
        if random.random() > 0.5: lon = random.uniform(ocean["lon_min"], 180)
        else: lon = random.uniform(-180, ocean["lon_max"])
    else:
        lon = random.uniform(ocean["lon_min"], ocean["lon_max"])
    lat = random.uniform(ocean["lat_min"], ocean["lat_max"])
    return lat, lon

# ==========================================
# 📐 1. 真·3D 坐标转换 (Spherical to Cartesian)
# ==========================================
def ll2xyz(lat, lon, radius=1.0):
    """
    将经纬度转换为 3D 空间坐标 (x, y, z)
    lat: -90 ~ 90
    lon: -180 ~ 180
    radius: 球体半径
    """
    phi = (90 - lat) * (math.pi / 180)
    theta = (lon + 180) * (math.pi / 180)
    
    x = -(radius * math.sin(phi) * math.cos(theta))
    y = (radius * math.sin(phi) * math.sin(theta))
    z = (radius * math.cos(phi))
    
    return x, y, z

# ==========================================
# 🌍 2. 3D 轨道地球 (The Orbital Earth)
# ==========================================
def render_3d_particle_map(nodes, current_user):
    if not nodes: 
        st.info("The universe is empty.")
        return

    # 半径定义
    R_EARTH = 100
    R_ORBIT = 135 # 您的意义卡悬浮高度 (1.35倍地球半径)

    # 容器初始化
    traces = []
    
    # 数据分类容器
    # 地表层
    sed_x, sed_y, sed_z, sed_c = [], [], [], []
    sig_x, sig_y, sig_z, sig_c = [], [], [], []
    # 轨道层 (我的)
    my_x, my_y, my_z, my_c, my_t = [], [], [], [], []
    # 牵引线 (连接地表和轨道)
    line_x, line_y, line_z = [], [], [] 

    for node in nodes:
        # 1. 坐标解析
        loc = None
        is_drift = False
        try:
            if isinstance(node.get('location'), str): loc = json.loads(node['location'])
            elif isinstance(node.get('location'), dict): loc = node['location']
        except: pass
        
        # 漂流瓶逻辑
        if not loc or not loc.get('lat'): 
            d_lat, d_lon = get_random_ocean_coordinate()
            loc = {"lat": d_lat, "lon": d_lon}
            is_drift = True

        lat, lon = loc.get('lat'), loc.get('lon')
        color = get_spectrum_color(str(node.get('keywords', '')))
        mode = node.get('mode', 'Active')
        
        # 2. 分层逻辑
        
        # === A. 我的意义卡 (My Orbit) ===
        if node['username'] == current_user:
            # 计算悬浮坐标
            ox, oy, oz = ll2xyz(lat, lon, R_ORBIT)
            # 计算地表锚点坐标
            gx, gy, gz = ll2xyz(lat, lon, R_EARTH)
            
            # 添加点
            my_x.append(ox); my_y.append(oy); my_z.append(oz)
            my_c.append(color)
            my_t.append(f"<b>{node['care_point']}</b><br><i>{node.get('insight','')}</i>")
            
            # 添加牵引线 (Tether)
            line_x.extend([gx, ox, None]) # None 用于断开线段
            line_y.extend([gy, oy, None])
            line_z.extend([gz, oz, None])
            
            # 同时也画一个地表的小点，表示根基
            sig_x.append(gx); sig_y.append(gy); sig_z.append(gz)
            sig_c.append(color)

        # === B. 历史沉淀 (Sediment) ===
        elif mode == 'Sediment':
            sx, sy, sz = ll2xyz(lat, lon, R_EARTH)
            sed_x.append(sx); sed_y.append(sy); sed_z.append(sz)
            sed_c.append(color)
            
        # === C. 他人信号/漂流 (Signals) ===
        else:
            sx, sy, sz = ll2xyz(lat, lon, R_EARTH)
            sig_x.append(sx); sig_y.append(sy); sig_z.append(sz)
            sig_c.append(color)

    # 3. 构建 Plotly Traces
    
    # [Layer 0] 黑体球 (遮挡背面的点，制造实体感)
    # 使用网格构建一个黑球
    u = np.linspace(0, 2 * np.pi, 20)
    v = np.linspace(0, np.pi, 20)
    x_sphere = R_EARTH * 0.98 * np.outer(np.cos(u), np.sin(v))
    y_sphere = R_EARTH * 0.98 * np.outer(np.sin(u), np.sin(v))
    z_sphere = R_EARTH * 0.98 * np.outer(np.ones(np.size(u)), np.cos(v))
    
    traces.append(go.Surface(
        x=x_sphere, y=y_sphere, z=z_sphere,
        colorscale=[[0, 'black'], [1, 'black']], 
        opacity=1.0, showscale=False, hoverinfo='skip',
        name="Planet Body"
    ))

    # [Layer 1] 经纬网 (Wireframe Grid) - 帮助定位中东/巴黎等位置
    # 简单画几条线作为地球骨架
    
    # [Layer 2] 历史沉淀 (暗淡地表)
    if sed_x:
        traces.append(go.Scatter3d(
            x=sed_x, y=sed_y, z=sed_z,
            mode='markers',
            marker=dict(size=2, color=sed_c, opacity=0.3, symbol='circle'),
            hoverinfo='skip', name='History'
        ))
        
    # [Layer 3] 他人信号 (地表亮灯)
    if sig_x:
        traces.append(go.Scatter3d(
            x=sig_x, y=sig_y, z=sig_z,
            mode='markers',
            marker=dict(size=4, color=sig_c, opacity=0.8, symbol='circle'),
            text=["Signal"]*len(sig_x), hoverinfo='text',
            name='Collective'
        ))

    # [Layer 4] 牵引线 (Tethers) - 连接地表与高空
    if line_x:
        traces.append(go.Scatter3d(
            x=line_x, y=line_y, z=line_z,
            mode='lines',
            line=dict(color='rgba(255,255,255,0.3)', width=1),
            hoverinfo='skip', name='Links'
        ))

    # [Layer 5] 我的轨道 (My Orbit) - 悬浮高空
    if my_x:
        traces.append(go.Scatter3d(
            x=my_x, y=my_y, z=my_z,
            mode='markers+text',
            # 只有鼠标移上去才显示文字
            text=my_t, hoverinfo='text', 
            marker=dict(
                size=8, color=my_c, opacity=1.0, 
                symbol='diamond', line=dict(width=1, color='white')
            ),
            name='My Orbit'
        ))

    # 4. 布局设置
    layout = go.Layout(
        scene=dict(
            xaxis=dict(visible=False, showgrid=False),
            yaxis=dict(visible=False, showgrid=False),
            zaxis=dict(visible=False, showgrid=False),
            bgcolor='black',
            dragmode='orbit', # 允许旋转
            aspectmode='data' # 保持球体比例
        ),
        paper_bgcolor='black',
        margin={"r":0,"t":0,"l":0,"b":0},
        height=600,
        showlegend=True,
        legend=dict(x=0, y=0, font=dict(color="#666"))
    )

    fig = go.Figure(data=traces, layout=layout)
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 3. 聚类 (Helper)
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

# ==========================================
# 🌌 4. 星河 (Galaxy View)
# ==========================================
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

# ==========================================
# 🕸️ 5. 雷达图
# ==========================================
def render_radar_chart(radar_dict, height="200px"):
    keys = ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]
    scores = [radar_dict.get(k, 3.0) for k in keys]
    option = {"backgroundColor": "transparent", "radar": {"indicator": [{"name": k, "max": 10} for k in keys], "splitArea": {"show": False}}, "series": [{"type": "radar", "data": [{"value": scores, "areaStyle": {"color": "rgba(0,255,242,0.4)"}, "lineStyle": {"color": "#00fff2"}}]}]}
    st_echarts(options=option, height=height)

# ==========================================
# 🔮 6. 赛博朋克关系图
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
            score = 0 # 简化连线逻辑
            graph_links.append({"source": na['name'], "target": nb['name'], "lineStyle": {"width": 1, "color": "#555", "curveness": 0.2, "opacity": 0.3}})
    option = {"backgroundColor": "#0e1117", "tooltip": {"formatter": "{b}"}, "series": [{"type": "graph", "layout": "force", "data": graph_nodes, "links": graph_links, "roam": True, "force": {"repulsion": 800 if is_fullscreen else 200, "gravity": 0.1, "edgeLength": 50}, "itemStyle": {"shadowBlur": 10}, "lineStyle": {"color": "source", "curveness": 0.2}}]}
    events = {"click": "function(params) { return params.name }"}
    clicked_id = st_echarts(options=option, height=height, events=events, key=f"map_{height}")
    if clicked_id:
        target_node = next((n for n in graph_nodes if n['name'] == clicked_id), None)
        if target_node: return target_node['full_data']
    return None

# ==========================================
# 🔭 7. 弹窗组件
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
