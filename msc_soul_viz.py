### msc_soul_viz.py ###
import streamlit as st
import plotly.graph_objects as go
import streamlit_antd_components as sac
import msc_viz as viz
import msc_soul_gen as gen
import itertools

def render_soul_scene(radar_dict, user_nodes=None):
    if user_nodes is None: user_nodes = []
    
    # 1. 计算数据
    plot_data, p_attr, s_attr = gen.generate_soul_network(radar_dict, user_nodes)
    lang = st.session_state.get('language', 'en')
    
    # --- 文案 ---
    ARCHETYPE_NAMES = {
        "Agency": {"en": "Starburst Structure", "zh": "爆发结构"},
        "Care": {"en": "Dense Cluster", "zh": "凝聚结构"},
        "Curiosity": {"en": "Wide Web", "zh": "发散网络"},
        "Coherence": {"en": "Crystalline Grid", "zh": "晶格结构"},
        "Reflection": {"en": "Deep Swirl", "zh": "深旋结构"},
        "Transcendence": {"en": "Ascending Cloud", "zh": "升腾云结构"},
        "Aesthetic": {"en": "Harmonic Sphere", "zh": "和谐球体"}
    }
    # ... (此处省略 ASPECT_NAMES 以节省空间，逻辑不变，保持之前的映射即可) ... 
    # 为了防止报错，这里简写，实际上你应该保留原来完整的字典
    ASPECT_NAMES = {"Agency": "Volatile", "Care": "Gentle", "Curiosity": "Flowing", "Coherence": "Stable", "Reflection": "Breathing", "Transcendence": "Drifting", "Aesthetic": "Elegant"} 
    
    p_name = ARCHETYPE_NAMES.get(p_attr, {}).get(lang, p_attr)
    s_text = s_attr # 简化显示，或者保留原有的多语言逻辑
    
    label_title = "SOUL FORM" if lang=='en' else "灵魂形态"
    sac.divider(label=label_title, icon='layers', align='center', color='gray')
    st.markdown(f"<div style='text-align:center; margin-top:-15px; margin-bottom:10px; font-family:JetBrains Mono; font-size:0.8em; color:#888;'>MODE: {s_text.upper()} // TYPE: {p_name}</div>", unsafe_allow_html=True)
    
    # 2. 数据分离
    thought_indices = [i for i, t in enumerate(plot_data['type']) if t == 'thought']
    atmos_indices = [i for i, t in enumerate(plot_data['type']) if t == 'atmos']
    
    def get_subset(idx):
        return {k: [plot_data[k][i] for i in idx] for k in ["x","y","z","color","size","text"]}

    thoughts = get_subset(thought_indices)
    atmos = get_subset(atmos_indices)

    fig = go.Figure()

    # ==========================================
    # 🟢 视觉层 1: 容器线框 (Cyber Cube)
    # 模拟参考图中的外部轮廓
    # ==========================================
    box_range = [-1.1, 1.1]
    for x in box_range:
        for y in box_range:
            fig.add_trace(go.Scatter3d(
                x=[x, x], y=[y, y], z=[-1.1, 1.1],
                mode='lines', line=dict(color='#222', width=1), hoverinfo='none'
            ))
            fig.add_trace(go.Scatter3d(
                x=[x, x], y=[-1.1, 1.1], z=[y, y],
                mode='lines', line=dict(color='#222', width=1), hoverinfo='none'
            ))
            fig.add_trace(go.Scatter3d(
                x=[-1.1, 1.1], y=[x, x], z=[y, y],
                mode='lines', line=dict(color='#222', width=1), hoverinfo='none'
            ))

    # ==========================================
    # 🟢 视觉层 2: 结构连线 (Web Structure)
    # 连接思想粒子，形成参考图中的网格感
    # ==========================================
    if len(thoughts['x']) > 1:
        # 简单策略：按顺序连接，或者连接到最近的邻居（这里用简单的顺序闭环模拟结构）
        # 为了美观，我们只画几条淡线
        fig.add_trace(go.Scatter3d(
            x=thoughts['x'], y=thoughts['y'], z=thoughts['z'],
            mode='lines',
            line=dict(color='white', width=1, dash='dot'), # 虚线网格
            opacity=0.3,
            hoverinfo='skip'
        ))

    # ==========================================
    # 🟢 视觉层 3: 氛围尘埃 (Data Dust)
    # 样式：极小(1/10)、正方形(Square)、高密度
    # ==========================================
    if atmos['x']:
        fig.add_trace(go.Scatter3d(
            x=atmos["x"], y=atmos["y"], z=atmos["z"],
            mode='markers',
            marker=dict(
                symbol='square',  # 🔷 改为方形像素点
                size=1.5,         # 🔷 极小尺寸 (思想粒子的 1/10)
                color=atmos["color"],
                opacity=0.6,      # 半透明，叠加产生光感
                line=dict(width=0)
            ),
            hoverinfo='none'
        ))

    # ==========================================
    # 🟢 视觉层 4: 思想晶体 (Thought Crystals)
    # 样式：大、菱形(Diamond)、高亮
    # ==========================================
    if thoughts['x']:
        # 内核
        fig.add_trace(go.Scatter3d(
            x=thoughts["x"], y=thoughts["y"], z=thoughts["z"],
            mode='markers',
            marker=dict(
                symbol='diamond', # 🔷 改为菱形晶体
                size=15,          # 🔷 大尺寸
                color=thoughts["color"],
                opacity=1.0,      # 实心
                line=dict(color='white', width=1.5) # 强轮廓
            ),
            text=thoughts["text"],
            hoverinfo='text'
        ))
        # 辉光 (复用坐标，低透明度)
        fig.add_trace(go.Scatter3d(
            x=thoughts["x"], y=thoughts["y"], z=thoughts["z"],
            mode='markers',
            marker=dict(
                symbol='diamond',
                size=30,          # 辉光范围
                color=thoughts["color"],
                opacity=0.15,
            ),
            hoverinfo='skip'
        ))

    # ==========================================
    # 场景配置
    # ==========================================
    fig.update_layout(
        height=450,
        margin=dict(l=0, r=0, b=0, t=0),
        paper_bgcolor='black',
        scene=dict(
            xaxis=dict(visible=False, range=[-1.5, 1.5]),
            yaxis=dict(visible=False, range=[-1.5, 1.5]),
            zaxis=dict(visible=False, range=[-1.5, 1.5]),
            aspectmode='cube',
            bgcolor='black',
            camera=dict(
                eye=dict(x=1.8, y=1.8, z=1.2) # 赛博朋克视角
            ),
            dragmode='orbit'
        ),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True, config={
        'scrollZoom': True,      
        'displayModeBar': False, 
        'staticPlot': False,     
        'responsive': True       
    })
    
    viz.render_spectrum_legend()
