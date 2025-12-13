## msc_viz.py (星河创世纪版：聚类与染色) ###

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import numpy as np
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans  # 引入聚类算法
from streamlit_echarts import st_echarts
import msc_config as config
import msc_lib as msc 

# ==========================================
# 🎨 智能配色盘 (Intelligent Palette)
# ==========================================
# 为不同的星团分配具有哲学意味的颜色
CLUSTER_COLORS = [
    '#FF4B4B', # Red: 激情/冲突/焦虑 (Passion/Conflict)
    '#1A73E8', # Blue: 理性/结构/冷静 (Reason/Structure)
    '#FFA421', # Orange: 创造/活力/混乱 (Creativity/Chaos)
    '#00C853', # Green: 生长/治愈/自然 (Growth/Nature)
    '#9C27B0', # Purple: 灵性/神秘/超越 (Spirituality/Mystery)
    '#00BCD4', # Cyan: 自由/未来/科技 (Freedom/Future)
]

def get_cluster_color(cluster_id):
    return CLUSTER_COLORS[cluster_id % len(CLUSTER_COLORS)]

# ==========================================
# 🧠 核心算法：星团引力计算
# ==========================================
def compute_clusters(nodes, n_clusters=5):
    """
    计算节点的聚类，返回带有 'cluster' 和 'color' 的 DataFrame
    """
    vectors = []
    meta_data = []
    
    # 1. 提取有效向量
    for node in nodes:
        if node['vector']:
            try:
                v = json.loads(node['vector'])
                vectors.append(v)
                meta_data.append({
                    "care_point": node['care_point'],
                    "insight": node.get('insight', ''),
                    "lat": np.random.uniform(-40, 60), # 暂用随机坐标模拟 2D 投影
                    "lon": np.random.uniform(-150, 150)
                })
            except: pass
    
    if not vectors: return pd.DataFrame()

    # 2. 动态决定星团数量 (不能超过节点总数)
    n_clusters = min(n_clusters, len(vectors))
    if n_clusters < 2: n_clusters = 1

    # 3. K-Means 聚类 (寻找引力中心)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(vectors)
    
    # 4. 降维 (为了 3D 展示)
    pca = PCA(n_components=3)
    coords_3d = pca.fit_transform(vectors)

    # 5. 组装数据
    df = pd.DataFrame(meta_data)
    df['cluster'] = labels
    df['color'] = [get_cluster_color(l) for l in labels]
    df['x'] = coords_3d[:, 0]
    df['y'] = coords_3d[:, 1]
    df['z'] = coords_3d[:, 2]
    
    return df

# ==========================================
# 🌍 2D 世界地图 (彩色版)
# ==========================================
def render_2d_world_map(nodes):
    if not nodes: return
    
    # 计算聚类
    df = compute_clusters(nodes, n_clusters=5)
    
    if df.empty:
        st.info("🌑 暂无足够的意义数据来形成星图。")
        return

    # 添加总部
    hq_df = pd.DataFrame([{"lat": 39.9, "lon": 116.4, "care_point": "HQ", "color": "#FFFFFF", "size": 10}])
    
    # 绘制散点
    fig = go.Figure()
    
    # 绘制普通节点 (按颜色分类)
    fig.add_trace(go.Scattergeo(
        lon = df["lon"], lat = df["lat"],
        mode = 'markers',
        text = df["care_point"], # 鼠标悬停显示
        marker = dict(
            size=6, 
            color=df['color'], # 智能染色
            opacity=0.8,
            line=dict(width=0)
        ),
        name='Meaning Nodes'
    ))
    
    # 绘制 HQ
    fig.add_trace(go.Scattergeo(
        lon = hq_df["lon"], lat = hq_df["lat"],
        mode = 'markers',
        marker = dict(size=10, color='white', symbol='diamond'),
        name='Origin'
    ))

    fig.update_layout(
        geo = dict(scope='world', projection_type='natural earth', showland=True, landcolor="#111", bgcolor="black"), 
        margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="black", height=500,
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 🌌 3D 星河 (彩色涌现版)
# ==========================================
def render_3d_galaxy(nodes):
    if len(nodes) < 3: 
        st.info("🌌 星河汇聚中... (需要至少3个节点才能计算空间)")
        return
        
    df = compute_clusters(nodes, n_clusters=6) # 尝试分出 6 个星系
    
    if df.empty: return
    
    df['size'] = 6
    
    # 使用 Plotly Express 自动按 Cluster 染色
    fig = px.scatter_3d(
        df, x='x', y='y', z='z', 
        color='cluster', # 按聚类ID染色
        color_continuous_scale=CLUSTER_COLORS, # 使用我们的哲学色盘
        hover_name='care_point', 
        hover_data={'insight': True, 'cluster': False, 'x':False, 'y':False, 'z':False},
        template="plotly_dark", 
        opacity=0.9
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
    option = {"backgroundColor": "transparent", "radar": {"indicator": [{"name": k, "max": 10} for k in keys], "splitArea": {"show": False}}, "series": [{"type": "radar", "data": [{"value": scores, "areaStyle": {"color": "rgba(0,255,242,0.4)"}, "lineStyle": {"color": "#00fff2"}}]}]}
    st_echarts(options=option, height=height)

# ==========================================
# 🔮 赛博朋克关系图 (Echarts - 连线染色版)
# ==========================================
def render_cyberpunk_map(nodes, height="250px", is_fullscreen=False):
    if not nodes: return
    
    # 预计算聚类，为了给节点染色
    cluster_df = compute_clusters(nodes, n_clusters=5)
    # 建立 id -> color 映射
    id_to_color = {}
    if not cluster_df.empty:
        # 假设 nodes 顺序和 cluster_df 顺序一致 (这是个简化假设，严谨需用 ID 匹配)
        # 这里为了演示简单，直接按顺序给色
        for i, color in enumerate(cluster_df['color']):
            if i < len(nodes):
                id_to_color[str(nodes[i]['id'])] = color

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
        # 获取该节点的星团颜色，如果没有则默认为白色
        node_color = id_to_color.get(nid, "#ffffff")

        graph_nodes.append({
            "name": nid, "id": nid,
            "symbolSize": symbol_base * (0.8 + logic),
            "value": node['care_point'],
            "label": {"show": is_fullscreen, "formatter": node['care_point'][:5], "color": "#fff"},
            "vector": vector, "keywords": keywords,
            "itemStyle": {"color": node_color} # === 节点染色 ===
        })

    # 连线逻辑 (标签优先)
    node_count = len(graph_nodes)
    start_idx = max(0, node_count - 50)
    
    for i in range(start_idx, node_count):
        for j in range(i + 1, node_count):
            na, nb = graph_nodes[i], graph_nodes[j]
            score = 0
            
            # 标签重叠
            if na['keywords'] and nb['keywords']:
                shared = len(set(na['keywords']).intersection(set(nb['keywords'])))
                if shared > 0: score += min(0.4 + (shared * 0.15), 0.9)
            
            # 向量相似
            if na['vector'] and nb['vector'] and score < 0.9:
                try:
                    vec1, vec2 = np.array(na['vector']), np.array(nb['vector'])
                    norm = np.linalg.norm(vec1) * np.linalg.norm(vec2)
                    if norm > 0:
                        sim = np.dot(vec1, vec2) / norm
                        if sim > 0.8: score += 0.2
                except: pass
            
            # 连线染色：如果两个节点同色，连线也用那个颜色；否则用青色
            line_color = "#00fff2"
            if na.get("itemStyle", {}).get("color") == nb.get("itemStyle", {}).get("color"):
                line_color = na["itemStyle"]["color"]

            if score >= 0.65: 
                graph_links.append({"source": na['name'], "target": nb['name'], "lineStyle": {"width": 2.5, "color": line_color, "curveness": 0.2}})
            elif score >= 0.45: 
                graph_links.append({"source": na['name'], "target": nb['name'], "lineStyle": {"width": 1, "color": "#555", "type": "dashed", "curveness": 0.2}})

    option = {
        "backgroundColor": "#0e1117",
        "tooltip": {},
        "animationDurationUpdate": 1500,
        "animationEasingUpdate": "quinticInOut",
        "series": [{
            "type": "graph", "layout": "force", "data": graph_nodes, "links": graph_links, "roam": True, 
            "force": {"repulsion": 800 if is_fullscreen else 200, "gravity": 0.1, "edgeLength": 50}, 
            "itemStyle": {"shadowBlur": 10}, "lineStyle": {"color": "source", "curveness": 0.2}
        }]
    }
    st_echarts(options=option, height=height)

@st.dialog("🔭 浩荡宇宙", width="large")
def view_fullscreen_map(nodes, user_name):
    st.markdown(f"### 🌌 {user_name} 的浩荡宇宙")
    render_cyberpunk_map(nodes, height="600px", is_fullscreen=True)

@st.dialog("🧬 MSC 深度基因解码", width="large")
def view_radar_details(radar_dict, username):
    c1, c2 = st.columns([1, 1])
    with c1: render_radar_chart(radar_dict, height="350px")
    with c2:
        st.markdown(f"### {username} 的核心参数")
        for key, val in radar_dict.items():
            color = "green" if val > 6 else ("orange" if val > 4 else "gray")
            st.progress(val / 10, text=f"**{key}**: {val}")
    st.divider()
    st.markdown("### 🧠 AI Analysis")
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
