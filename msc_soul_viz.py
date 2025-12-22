### msc_soul_viz.py ###
import streamlit as st
import plotly.graph_objects as go
import streamlit_antd_components as sac
import msc_viz as viz
import msc_soul_gen as gen

def render_soul_scene(radar_dict, user_nodes=None):
    if user_nodes is None: user_nodes = []
    
    # 1. 获取基于“形状数学”生成的粒子数据
    data, p_attr, s_attr = gen.generate_nebula_data(radar_dict, user_nodes)
    
    lang = st.session_state.get('language', 'en')
    
    # 文案：根据形状命名
    ARCHETYPE_NAMES = {
        "Agency":        {"en": "Starburst Nebula", "zh": "爆发星云 · Agency"},
        "Care":          {"en": "Dense Cluster",    "zh": "致密星团 · Care"},
        "Curiosity":     {"en": "Wide Web",         "zh": "发散网状云 · Curiosity"},
        "Coherence":     {"en": "Crystalline Grid", "zh": "晶格结构 · Coherence"},
        "Reflection":    {"en": "Deep Swirl",       "zh": "深旋星系 · Reflection"},
        "Transcendence": {"en": "Ascending Cloud",  "zh": "升腾云层 · Transcendence"},
        "Aesthetic":     {"en": "Harmonic Sphere",  "zh": "和谐球体 · Aesthetic"}
    }
    p_name = ARCHETYPE_NAMES.get(p_attr, {}).get(lang, p_attr)
    
    if len(user_nodes) == 0:
        title = "Proto-Field" if lang=='en' else "初生场域"
        desc = "Awaiting thought injection..." if lang=='en' else "等待思想注入..."
    else:
        title = p_name
        desc = f"Structure based on your {p_attr} tendency" if lang=='en' else f"基于 [{p_attr}] 倾向生成的思维拓扑"

    # UI 标题
    label_title = "SOUL FORM" if lang=='en' else "灵魂形态"
    sac.divider(label=label_title, icon='layers', align='center', color='gray')
    st.markdown(f"<div style='text-align:center; margin-bottom: -10px;'><b>{title}</b><br><span style='font-size:0.8em;color:gray'>{desc}</span></div>", unsafe_allow_html=True)

    # ==========================================
    # 🌌 Plotly 3D 静态高画质渲染
    # ==========================================
    
    fig = go.Figure()

    # Layer 1: 氛围尘埃 (Atmosphere)
    # 小、半透明、作为背景烘托
    fig.add_trace(go.Scatter3d(
        x=data["atmos"]["x"], 
        y=data["atmos"]["y"], 
        z=data["atmos"]["z"],
        mode='markers',
        marker=dict(
            size=data["atmos"]["s"],
            color=data["atmos"]["c"],
            opacity=0.5,      # 关键：半透明制造雾气感
            symbol='circle',
            line=dict(width=0) # 无边框，柔和
        ),
        hoverinfo='none',     # 氛围不可点击，纯视觉
        name='Atmosphere'
    ))
    
    # Layer 2: 思想恒星 (Thoughts)
    # 大、不透明、带发光边框、可点击交互
    fig.add_trace(go.Scatter3d(
        x=data["thoughts"]["x"], 
        y=data["thoughts"]["y"], 
        z=data["thoughts"]["z"],
        mode='markers',
        marker=dict(
            size=data["thoughts"]["s"],
            color=data["thoughts"]["c"],
            opacity=1.0,
            symbol='circle',
            # ✨ 发光效果：白色边框
            line=dict(width=1, color='rgba(255,255,255,0.8)') 
        ),
        text=data["thoughts"]["t"],
        hoverinfo='text',
        name='Thoughts'
    ))

    # 布局配置
    fig.update_layout(
        height=350, # 正方形视窗
        margin=dict(l=0, r=0, b=0, t=0), # 零边距
        paper_bgcolor='black', # 画布背景黑
        showlegend=False,
        scene=dict(
            # 🌑 隐藏所有参考系，让它像悬浮在太空中
            xaxis=dict(visible=False, showbackground=False, showgrid=False, showline=False, title=''),
            yaxis=dict(visible=False, showbackground=False, showgrid=False, showline=False, title=''),
            zaxis=dict(visible=False, showbackground=False, showgrid=False, showline=False, title=''),
            bgcolor='black',
            
            # 📷 交互模式：轨道旋转
            # 这允许用户像旋转地球仪一样旋转你的灵魂结构，非常丝滑
            dragmode='orbit', 
            
            # 初始视角
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=0.8), # 45度角俯视
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0)
            )
        )
    )

    # 渲染
    # config 中 scrollZoom: True 允许缩放
    # displayModeBar: False 保持极简
    st.plotly_chart(
        fig, 
        use_container_width=True, 
        config={'displayModeBar': False, 'scrollZoom': True}
    )
    
    # 图例
    viz.render_spectrum_legend()
