### msc_viz.py (完整无删减版：含交互地图、雷达、考古卡片) ###

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import numpy as np
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from streamlit_echarts import st_echarts, JsCode # 引入 JsCode
import msc_config as config
import msc_lib as msc 

# ==========================================
# 🎨 智能配色盘 (Intelligent Palette)
# ==========================================
CLUSTER_COLORS = [
    '#FF4B4B', # Red: 激情/冲突
    '#1A73E8', # Blue: 理性/结构
    '#FFA421', # Orange: 创造/活力
    '#00C853', # Green: 生长/治愈
    '#9C27B0', # Purple: 灵性/神秘
    '#00BCD4', # Cyan: 自由/未来
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
    
    for node in nodes:
        if node['vector']:
            try:
                v = json.loads(node['vector'])
                vectors.append(v)
                meta_data.append({
                    "care_point": node['care_point'],
                    "insight": node.get('insight', ''),
                    "lat": np.random.uniform(-40, 60),
                    "lon": np.random.uniform(-150, 150)
                })
            except: pass
    
    if not vectors: return pd.DataFrame()

    n_clusters = min(n_clusters, len(vectors))
    if n_clusters < 2: n_clusters = 1

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(vectors)
    
    pca = PCA(n_components=3)
    coords_3d = pca.fit_transform(vectors)

    df = pd.DataFrame(meta_data)
    df['cluster'] = labels
    df['color'] = [get_cluster_color(l) for l in labels]
    df['x'] = coords_3d[:, 0]
    df['y'] = coords_3d[:, 1]
    df['z'] = coords_3d[:, 2]
    
    return df

# ==========================================
# 🌍 2D 世界地图 (Plotly)
# ==========================================
def render_2d_world_map(nodes):
    if not nodes: return
    
    df = compute_clusters(nodes, n_clusters=5)
    
    if df.empty:
        st.info("🌑 暂无足够的意义数据来形成星图。")
        return

    hq_df = pd.DataFrame([{"lat": 39.9, "lon": 116.4, "care_point": "HQ", "color": "#FFFFFF", "size": 10}])
    
    fig = go.Figure()
    
    fig.add_trace(go.Scattergeo(
        lon = df["lon"], lat = df["lat"],
        mode = 'markers',
        text = df["care_point"], 
        marker = dict(size=6, color=df['color'], opacity=0.8, line=dict(width=0)),
        name='Meaning Nodes'
    ))
    
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
# 🌌 3D 星河 (Plotly)
# ==========================================
def render_3d_galaxy(nodes):
    if len(nodes) < 3: 
        st.info("🌌 星河汇聚中... (需要至少3个节点才能计算空间)")
        return
        
    df = compute_clusters(nodes, n_clusters=6)
    
    if df.empty: return
    
    df['size'] = 6
    
    fig = px.scatter_3d(
        df, x='x', y='y', z='z', 
        color='cluster', 
        color_continuous_scale=CLUSTER_COLORS, 
        hover_name='care_point', 
        hover_data={'insight': True, 'cluster': False, 'x':False, 'y':False, 'z':False},
        template="plotly_dark", 
        opacity=0.9
    )
    
    fig.update_layout(
        scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False), bgcolor='black'), 
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
    
    option = {
        "backgroundColor": "transparent", 
        "radar": {
            "indicator": [{"name": k, "max": 10} for k in keys], 
            "splitArea": {"show": False}
        }, 
        "series": [{
            "type": "radar", 
            "data": [{
                "value": scores, 
                "areaStyle": {"color": "rgba(0,255,242,0.4)"}, 
                "lineStyle": {"color": "#00fff2"}
            }]
        }]
    }
    st_echarts(options=option, height=height)

# ==========================================
# 🔮 赛博朋克关系图 (交互升级版)
# ==========================================
def render_cyberpunk_map(nodes, height="250px", is_fullscreen=False):
    if not nodes: return
    
    # 1. 聚类染色
    cluster_df = compute_clusters(nodes, n_clusters=5)
    id_to_color = {}
    if not cluster_df.empty:
        # 这里做一个简单的顺序映射 (简化版)，实际应根据ID映射
        for i, color in enumerate(cluster_df['color']):
            if i < len(nodes): id_to_color[str(nodes[i]['id'])] = color

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
        node_color = id_to_color.get(nid, "#ffffff")

        # === 优化点：Label 只显示精简的 Care Point ===
        # 如果 Care Point 太长，截断显示
        label_text = node['care_point']
        if len(label_text) > 6: label_text = label_text[:5] + "..."

        graph_nodes.append({
            "name": nid, 
            "id": nid,
            "symbolSize": symbol_base * (0.8 + logic),
            "value": node['care_point'], # 鼠标悬停显示完整 Care Point
            "label": {
                "show": is_fullscreen, 
                "formatter": label_text, # 只显示精简文字
                "color": "#fff",
                "fontSize": 10
            },
            # 存下完整数据供点击使用
            "full_data": {
                "insight": node.get('insight', 'No Insight'),
                "content": node['content'],
                "layer": node.get('meaning_layer', ''),
                "username": node['username']
            },
            "vector": vector, "keywords": keywords,
            "itemStyle": {"color": node_color}
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
            
            # 连线染色
            line_color = "#00fff2"
            if na.get("itemStyle", {}).get("color") == nb.get("itemStyle", {}).get("color"):
                line_color = na["itemStyle"]["color"]

            if score >= 0.65: 
                graph_links.append({"source": na['name'], "target": nb['name'], "lineStyle": {"width": 2.5, "color": line_color, "curveness": 0.2}})
            elif score >= 0.45: 
                graph_links.append({"source": na['name'], "target": nb['name'], "lineStyle": {"width": 1, "color": "#555", "type": "dashed", "curveness": 0.2}})

    # === 关键：点击事件配置 ===
    option = {
        "backgroundColor": "#0e1117",
        "tooltip": {"formatter": "{b}: {c}"}, # 悬停显示简单信息
        "series": [{
            "type": "graph", "layout": "force", "data": graph_nodes, "links": graph_links, "roam": True, 
            "force": {"repulsion": 800 if is_fullscreen else 200, "gravity": 0.1, "edgeLength": 50}, 
            "itemStyle": {"shadowBlur": 10}, "lineStyle": {"color": "source", "curveness": 0.2}
        }]
    }
    
    # 监听点击事件，返回被点击节点的 name (即 id)
    events = {"click": "function(params) { return params.name }"}
    
    # 渲染图表
    clicked_node_id = st_echarts(options=option, height=height, events=events, key=f"map_{height}")
    
    # 如果用户点击了节点，弹出详情卡片
    if clicked_node_id:
        target_node = next((n for n in graph_nodes if n['name'] == clicked_node_id), None)
        if target_node:
            view_node_card(target_node['full_data'])

# === 新增：意义详情卡片 (Dialog) ===
@st.dialog("✨ 意义晶体", width="large")
def view_node_card(node_data):
    # 1. 核心洞察区
    st.markdown(f"### {node_data.get('layer', 'Core Meaning')}")
    st.info(f"**Insight:** {node_data['insight']}")
    
    st.divider()
    
    # 2. 原始语境区 (考古)
    st.caption("📜 原始对话回溯 (Original Context)")
    
    # 调用 lib 去找当时的聊天记录
    original_chat = msc.get_node_context(node_data['username'], node_data['content'])
    
    if original_chat:
        timestamp = str(original_chat.get('created_at', ''))[:16].replace('T', ' ')
        st.markdown(f"""
        <div style="background:#f0f2f6; padding:15px; border-radius:10px; border-left: 4px solid #1A73E8;">
            <div style="font-size:12px; color:#666; margin-bottom:5px;">{timestamp}</div>
            <div style="font-size:16px; font-weight:500;">"{node_data['content']}"</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔗 定位到聊天上下文"):
            st.toast("已定位到历史坐标 (模拟跳转)", icon="📍")
    else:
        st.markdown(f"> \"{node_data['content']}\"")
        st.caption("无法追溯确切的时间戳")

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
