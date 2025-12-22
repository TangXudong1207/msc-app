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
    
    # 文案：极简隐喻
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
    
    title = p_name
    # 之前那句解释性的 desc 已经被完全移除了

    # UI 标题
    label_title = "SOUL FORM" if lang=='en' else "灵魂形态"
    sac.divider(label=label_title, icon='layers', align='center', color='gray')
    st.markdown(f"<div style='text-align:center; margin-bottom: -10px; font-family:serif; letter-spacing:1px;'><b>{title}</b></div>", unsafe_allow_html=True)

    # ==========================================
    # 🌌 Plotly 3D 渲染 (摄像机动画版)
    # ==========================================
    
    # 1. 静态 Trace (数据本身不动)
    trace_atmos = go.Scatter3d(
        x=data["atmos"]["x"], y=data["atmos"]["y"], z=data["atmos"]["z"],
        mode='markers',
        marker=dict(size=data["atmos"]["s"], color=data["atmos"]["c"], opacity=0.5, line=dict(width=0)),
        hoverinfo='none', name='Atmosphere'
    )
    
    trace_thoughts = go.Scatter3d(
        x=data["thoughts"]["x"], y=data["thoughts"]["y"], z=data["thoughts"]["z"],
        mode='markers',
        marker=dict(size=data["thoughts"]["s"], color=data["thoughts"]["c"], opacity=1.0, symbol='circle', line=dict(width=1, color='rgba(255,255,255,0.8)')),
        text=data["thoughts"]["t"], hoverinfo='text', name='Thoughts'
    )

    # 2. 生成动画帧：只移动摄像机 (Camera Eye)
    # 这种方式极度节省性能，因为点的数据不传输，只传输视角坐标
    frames = []
    n_frames = 120 # 120帧，非常平滑
    radius = 1.6   # 摄像机距离中心的半径
    
    for i in range(n_frames):
        theta = (2 * np.pi * i) / n_frames
        # 计算摄像机位置：在 XY 平面上圆周运动，Z 轴稍微抬高
        x_eye = radius * np.cos(theta)
        y_eye = radius * np.sin(theta)
        frames.append(go.Frame(
            layout=dict(
                scene=dict(
                    camera=dict(
                        eye=dict(x=x_eye, y=y_eye, z=0.6) # z=0.6 保持俯视
                    )
                )
            )
        ))

    # 3. 布局设置
    fig = go.Figure(
        data=[trace_atmos, trace_thoughts],
        frames=frames
    )

    fig.update_layout(
        height=350,
        margin=dict(l=0, r=0, b=0, t=0),
        paper_bgcolor='black',
        showlegend=False,
        scene=dict(
            xaxis=dict(visible=False, showbackground=False),
            yaxis=dict(visible=False, showbackground=False),
            zaxis=dict(visible=False, showbackground=False),
            bgcolor='black',
            dragmode='orbit', # 允许手势旋转
            camera=dict(eye=dict(x=1.6, y=0, z=0.6)) # 初始位置
        ),
        # 动画控制按钮 (这是唯一能让 Plotly 在 Web 上动起来的开关)
        updatemenus=[dict(
            type='buttons',
            showactive=False,
            y=0, x=0, # 按钮位置在左下角
            xanchor='left', yanchor='bottom',
            pad=dict(t=0, r=0),
            bgcolor='rgba(0,0,0,0)', # 透明背景
            buttons=[dict(
                label='🌀 Orbit', # 按钮文案
                method='animate',
                args=[None, dict(
                    frame=dict(duration=50, redraw=False), # 50ms 一帧，redraw=False 是流畅的关键
                    fromcurrent=True, 
                    transition=dict(duration=0),
                    mode='immediate',
                    loop=True # 循环播放
                )]
            )]
        )]
    )

    # 渲染
    st.plotly_chart(
        fig, 
        use_container_width=True, 
        config={'displayModeBar': False, 'scrollZoom': True}
    )
    
    viz.render_spectrum_legend()
