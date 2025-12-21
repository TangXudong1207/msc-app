### msc_soul_viz.py ###
import streamlit as st
import plotly.graph_objects as go
import streamlit_antd_components as sac
import msc_viz as viz
import msc_soul_gen as gen

def render_soul_scene(radar_dict, user_nodes=None):
    if user_nodes is None: user_nodes = []
    
    # 1. 获取 Plotly 格式的数据
    plot_data, p_attr, s_attr = gen.generate_soul_network(radar_dict, user_nodes)
    
    lang = st.session_state.get('language', 'en')
    
    # ... (保留文案映射) ...
    ARCHETYPE_NAMES = {
        "Agency":        {"en": "Starburst Structure", "zh": "爆发结构"},
        "Care":          {"en": "Dense Cluster",      "zh": "凝聚结构"},
        "Curiosity":     {"en": "Wide Web",           "zh": "发散网络"},
        "Coherence":     {"en": "Crystalline Grid",   "zh": "晶格结构"},
        "Reflection":    {"en": "Deep Swirl",         "zh": "深旋结构"},
        "Transcendence": {"en": "Ascending Cloud",    "zh": "升腾云结构"},
        "Aesthetic":     {"en": "Harmonic Sphere",    "zh": "和谐球体"}
    }
    ASPECT_NAMES = {
        "Agency":        {"en": "Volatile Mode",   "zh": "躁动模式"},
        "Care":          {"en": "Gentle Mode",     "zh": "柔缓模式"},
        "Curiosity":     {"en": "Flowing Mode",    "zh": "流转模式"},
        "Coherence":     {"en": "Stable Mode",     "zh": "稳定模式"},
        "Reflection":    {"en": "Breathing Mode",  "zh": "呼吸模式"},
        "Transcendence": {"en": "Drifting Mode",   "zh": "漂浮模式"},
        "Aesthetic":     {"en": "Elegant Mode",    "zh": "优雅模式"}
    }

    p_name = ARCHETYPE_NAMES.get(p_attr, {}).get(lang, p_attr)
    s_name = ASPECT_NAMES.get(s_attr, {}).get(lang, s_attr)
    
    if len(user_nodes) == 0:
        creature_title = "Proto-Field" if lang=='en' else "初生场域"
        creature_desc = "Awaiting thought injection..." if lang=='en' else "等待思想注入..."
    else:
        creature_title = p_name
        creature_desc = f"operating in {s_name}" if lang=='en' else f"运行于 {s_name}"

    label_title = "SOUL FORM" if lang=='en' else "灵魂形态"
    sac.divider(label=label_title, icon='layers', align='center', color='gray')
    st.markdown(f"<div style='text-align:center; margin-bottom: -20px;'><b>{creature_title}</b><br><span style='font-size:0.8em;color:gray'>{creature_desc}</span></div>", unsafe_allow_html=True)
    
    # ==========================================
    # 🟢 Plotly 3D 渲染
    # ==========================================
    fig = go.Figure()

    # 1. 画连线 (Lines) - 淡淡的网格
    fig.add_trace(go.Scatter3d(
        x=plot_data["lines_x"],
        y=plot_data["lines_y"],
        z=plot_data["lines_z"],
        mode='lines',
        line=dict(color='#444444', width=1), # 深灰色的线
        hoverinfo='none',
        opacity=0.3
    ))

    # 2. 画节点 (Nodes)
    fig.add_trace(go.Scatter3d(
        x=plot_data["x"],
        y=plot_data["y"],
        z=plot_data["z"],
        mode='markers',
        marker=dict(
            size=plot_data["size"],
            color=plot_data["color"],
            opacity=0.9,
            # ✨ 模拟发光：给点加一个白色的边框
            line=dict(color='white', width=1)
        ),
        text=plot_data["text"], # Tooltip 内容
        hoverinfo='text'
    ))

    # 3. 样式配置 (全黑背景，隐藏坐标轴)
    fig.update_layout(
        height=350, # 正方形视窗
        margin=dict(l=0, r=0, b=0, t=0), # 零边距
        paper_bgcolor='black', # 画布背景黑
        scene=dict(
            # 🌑 隐藏所有轴、网格、背景
            xaxis=dict(visible=False, showbackground=False, showgrid=False, showline=False),
            yaxis=dict(visible=False, showbackground=False, showgrid=False, showline=False),
            zaxis=dict(visible=False, showbackground=False, showgrid=False, showline=False),
            bgcolor='black', # 3D 场景背景黑
            
            # 📷 相机初始视角
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5) # 稍微拉远一点
            ),
            # 禁用默认的旋转惯性，让拖拽更精准 (或者开启以获得滑行感)
            dragmode='orbit'
        )
    )
    
    # 渲染！
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    viz.render_spectrum_legend()
