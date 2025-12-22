### msc_soul_viz.py ###
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import streamlit_antd_components as sac
import msc_viz as viz
import msc_soul_gen as gen

def render_soul_scene(radar_dict, user_nodes=None):
    if user_nodes is None: user_nodes = []
    
    # 1. 获取数据
    data, p_attr = gen.generate_nebula_data(radar_dict, user_nodes)
    
    lang = st.session_state.get('language', 'en')
    
    # 2. 文案与名称映射
    ARCHETYPE_NAMES = {
        "Agency":        {"en": "Starburst Nebula", "zh": "爆发星云"},
        "Care":          {"en": "Dense Cluster",    "zh": "致密星团"},
        "Curiosity":     {"en": "Wide Web",         "zh": "发散网状云"},
        "Coherence":     {"en": "Crystalline Grid", "zh": "晶格结构"},
        "Reflection":    {"en": "Deep Swirl",       "zh": "深旋星系"},
        "Transcendence": {"en": "Ascending Cloud",  "zh": "升腾云层"},
        "Aesthetic":     {"en": "Harmonic Sphere",  "zh": "和谐球体"}
    }
    p_name = ARCHETYPE_NAMES.get(p_attr, {}).get(lang, p_attr)
    
    if len(user_nodes) == 0:
        title = "Proto-Field" if lang=='en' else "初生场域"
        desc = "Awaiting thought injection..." if lang=='en' else "等待思想注入..."
    else:
        title = p_name
        # 🟢 恢复说明文案，使用指定内容
        desc = "Topology of thought based on dialogue meaning structure" if lang=='en' else "基于对话意义结构生成的思想拓扑图"

    # 3. UI 标题区域
    label_title = "SOUL FORM" if lang=='en' else "灵魂形态"
    sac.divider(label=label_title, icon='layers', align='center', color='gray')
    
    # 🟢 布局修复：增加底部边距 (margin-bottom: 10px)，防止 3D 画布遮挡文字
    # 使用 font-family: serif 增加隐喻感，灰色小字显示描述
    st.markdown(f"""
    <div style='text-align:center; margin-bottom: 15px;'>
        <div style='font-size: 1.1em; font-weight: 600; letter-spacing: 1px;'>{title}</div>
        <div style='font-size: 0.75em; color: #888; margin-top: 4px;'>{desc}</div>
    </div>
    """, unsafe_allow_html=True)

    # ==========================================
    # 🌌 Plotly 3D 渲染 (摄像机动画版)
    # ==========================================
    
    # Trace 1: 氛围尘埃 (Atmosphere)
    trace_atmos = go.Scatter3d(
        x=data["atmos"]["x"], y=data["atmos"]["y"], z=data["atmos"]["z"],
        mode='markers',
        marker=dict(size=data["atmos"]["s"], color=data["atmos"]["c"], opacity=0.5, line=dict(width=0)),
        hoverinfo='none', name='Atmosphere'
    )
    
    # Trace 2: 思想恒星 (Thoughts)
    trace_thoughts = go.Scatter3d(
        x=data["thoughts"]["x"], y=data["thoughts"]["y"], z=data["thoughts"]["z"],
        mode='markers',
        marker=dict(size=data["thoughts"]["s"], color=data["thoughts"]["c"], opacity=1.0, symbol='circle', line=dict(width=1, color='rgba(255,255,255,0.8)')),
        text=data["thoughts"]["t"], hoverinfo='text', name='Thoughts'
    )

    # 生成动画帧：摄像机环绕路径
    frames = []
    n_frames = 120 
    radius = 1.6   
    
    for i in range(n_frames):
        theta = (2 * np.pi * i) / n_frames
        x_eye = radius * np.cos(theta)
        y_eye = radius * np.sin(theta)
        frames.append(go.Frame(
            layout=dict(
                scene=dict(
                    camera=dict(
                        eye=dict(x=x_eye, y=y_eye, z=0.6) 
                    )
                )
            )
        ))

    # 布局设置
    fig = go.Figure(
        data=[trace_atmos, trace_thoughts],
        frames=frames
    )

    fig.update_layout(
        height=350, # 保持正方形视窗
        margin=dict(l=0, r=0, b=0, t=0), # 画布内部无边距
        paper_bgcolor='black',
        showlegend=False,
        scene=dict(
            xaxis=dict(visible=False, showbackground=False),
            yaxis=dict(visible=False, showbackground=False),
            zaxis=dict(visible=False, showbackground=False),
            bgcolor='black',
            dragmode='orbit', 
            camera=dict(eye=dict(x=1.6, y=0, z=0.6))
        ),
        # 动画控制按钮 (Orbit)
        updatemenus=[dict(
            type='buttons',
            showactive=False,
            y=0, x=0, 
            xanchor='left', yanchor='bottom',
            pad=dict(t=0, r=0),
            bgcolor='rgba(0,0,0,0)',
            buttons=[dict(
                label='🌀 Orbit',
                method='animate',
                args=[None, dict(
                    frame=dict(duration=50, redraw=False), 
                    fromcurrent=True, 
                    transition=dict(duration=0),
                    mode='immediate',
                    loop=True
                )]
            )]
        )]
    )

    st.plotly_chart(
        fig, 
        use_container_width=True, 
        config={'displayModeBar': False, 'scrollZoom': True}
    )
    
    viz.render_spectrum_legend()
