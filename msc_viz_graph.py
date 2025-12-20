### msc_viz_graph.py ###import streamlit as st
import streamlit as st
from streamlit_echarts import st_echarts
import json
import numpy as np
import msc_viz_core as core
import msc_lib as msc 
# 注意：这里需要延迟导入 viz 以避免循环引用，或者直接在函数内导入
# 为了安全，我们不在这里 import msc_viz，而是手动实现或重构
# 最佳实践：把 render_spectrum_legend 放在 main 或者独立的 UI 库里。
# 但为了简单，我们在函数内部 import。

# ==========================================
# 🕸️ 1. 雷达图 (Radar)
# ==========================================
def render_radar_chart(radar_dict, height="200px"):
    keys = ["Care", "Curiosity", "Reflection", "Coherence", "Agency", "Aesthetic", "Transcendence"]
    safe_scores = []
    for k in keys:
        safe_scores.append(radar_dict.get(k, 3.0))

    option = {
        "backgroundColor": "transparent", 
        "radar": {
            "indicator": [{"name": k, "max": 10} for k in keys], 
            "splitArea": {"show": False}
        }, 
        "series": [{
            "type": "radar", 
            "data": [{
                "value": safe_scores, 
                "areaStyle": {"color": "rgba(255, 75, 75, 0.4)"}, 
                "lineStyle": {"color": "#FF4B4B"}
            }]
        }]
    }
    st_echarts(options=option, height=height)

# ==========================================
# 🔮 2. 赛博朋克关系图 (Network Graph)
# ==========================================
def render_cyberpunk_map(nodes, height="250px", is_fullscreen=False, key_suffix="map"):
    if not nodes: return None
    
    cluster_df = core.compute_clusters(nodes, n_clusters=5)
    id_to_color = {}
    default_color = "#00fff2"
    
    if not cluster_df.empty:
        for i, color in enumerate(cluster_df['color']):
            if i < len(nodes): id_to_color[str(nodes[i]['id'])] = color

    graph_nodes, graph_links = [], []
    symbol_base = 30 if is_fullscreen else 15
    
    for i, node in enumerate(nodes):
        logic = node.get('logic_score') or 0.5
        nid = str(node['id'])
        node_color = id_to_color.get(nid, default_color)
        label_text = node['care_point']
        if len(label_text) > 6: label_text = label_text[:5] + "..."

        graph_nodes.append({
            "name": nid, "id": nid, "symbolSize": symbol_base * (0.8 + logic),
            "value": node['care_point'], 
            "label": {"show": is_fullscreen, "formatter": label_text, "color": "#fff", "fontSize": 10},
            "full_data": {
                "insight": node.get('insight', ''), "content": node['content'], 
                "layer": node.get('meaning_layer', ''), "username": node['username']
            },
            "itemStyle": {"color": node_color}
        })

    node_count = len(graph_nodes)
    start_idx = max(0, node_count - 50)
    for i in range(start_idx, node_count):
        for j in range(i + 1, node_count):
            na, nb = graph_nodes[i], graph_nodes[j]
            graph_links.append({
                "source": na['name'], "target": nb['name'], 
                "lineStyle": {"width": 1, "color": "#555", "curveness": 0.2, "opacity": 0.3}
            })

    option = {
        "backgroundColor": "#0e1117", 
        "tooltip": {"formatter": "{b}"}, 
        "series": [{
            "type": "graph", "layout": "force", "data": graph_nodes, "links": graph_links, "roam": True, 
            "force": {"repulsion": 800 if is_fullscreen else 200, "gravity": 0.1, "edgeLength": 50}, 
            "itemStyle": {"shadowBlur": 10}, "lineStyle": {"color": "source", "curveness": 0.2}
        }]
    }
    
    events = {"click": "function(params) { return params.name }"}
    clicked_id = st_echarts(options=option, height=height, events=events, key=f"echart_{key_suffix}")
    
    if clicked_id:
        target_node = next((n for n in graph_nodes if n['name'] == clicked_id), None)
        if target_node: return target_node['full_data']
    return None

# ==========================================
# 🔭 3. 弹窗组件 (Dialogs)
# ==========================================
@st.dialog("🔭 小宇宙 (Microcosm)", width="large")
def view_fullscreen_map(nodes, user_name):
    # 延迟导入以避免循环引用
    import msc_viz as viz_facade
    
    lang = st.session_state.get('language', 'en')
    title = f"{user_name}'s Microcosm" if lang == 'en' else f"{user_name} 的小宇宙"
    st.markdown(f"### 🌌 {title}")
    
    clicked_data = render_cyberpunk_map(nodes, height="500px", is_fullscreen=True, key_suffix="fullscreen_dlg")
    
    if clicked_data:
        st.divider()
        st.markdown(f"#### ✨ {clicked_data.get('layer', 'Selected Node')}")
        c1, c2 = st.columns([0.7, 0.3])
        with c1:
            st.info(f"**Insight:** {clicked_data['insight']}")
            st.caption(f"> \"{clicked_data['content']}\"")
        with c2:
            if st.button("📍 Locate", use_container_width=True): st.toast("Time travel initiated...", icon="⏳")
    
    st.divider()
    # 添加图例
    viz_facade.render_spectrum_legend()

@st.dialog("🧬 MSC 深度基因解码", width="large")
def view_radar_details(radar_dict, username):
    c1, c2 = st.columns([1, 1])
    with c1: render_radar_chart(radar_dict, height="350px")
    with c2:
        st.markdown(f"### {username} 的核心参数")
        required_keys = ["Care", "Curiosity", "Reflection", "Coherence", "Agency", "Aesthetic", "Transcendence"]
        for key in required_keys:
            val = radar_dict.get(key, 3.0)
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
