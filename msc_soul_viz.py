### msc_soul_viz.py ###
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import streamlit_antd_components as sac
import msc_viz as viz
import msc_soul_gen as gen

# ==========================================
# 🌌 物理引擎 (NumPy Vectorized)
# ==========================================
def calculate_physics_frame(particles, mode, t, global_rot):
    # 提取数组
    X = np.array([p['x'] for p in particles])
    Y = np.array([p['y'] for p in particles])
    Z = np.array([p['z'] for p in particles])
    P = np.array([p['phase'] for p in particles])
    S = np.array([p['speed'] for p in particles])

    # 1. 局部物理运动 (Local Motion)
    if mode == "Agency": # 呼吸效应
        factor = 1.0 + 0.1 * np.sin(t * 2 * S + P)
        X *= factor; Y *= factor; Z *= factor
    elif mode == "Reflection": # 漩涡效应
        R = np.sqrt(X**2 + Y**2 + 0.01)
        ang = t * (1.0/R) * S * 0.5
        X_new = X*np.cos(ang) - Y*np.sin(ang)
        Y = X*np.sin(ang) + Y*np.cos(ang)
        X = X_new
    elif mode == "Transcendence": # 上升流
        Z = ((Z + t * S * 0.5 + 2.5) % 5.0) - 2.5
    else: # 默认：布朗微动
        jitter = 0.05 * np.sin(t * 5 + P)
        X += jitter; Y += jitter; Z += jitter

    # 2. 全局公转 (Global Rotation)
    cos_g = np.cos(global_rot); sin_g = np.sin(global_rot)
    X_f = X * cos_g - Y * sin_g
    Y_f = X * sin_g + Y * cos_g
    
    return X_f, Y_f, Z

# ==========================================
# 🎨 渲染主程序
# ==========================================
def render_soul_scene(radar_dict, user_nodes=None):
    if user_nodes is None: user_nodes = []
    
    # 1. 生成基础数据
    raw, p_attr = gen.generate_nebula_data(radar_dict, user_nodes)
    lang = st.session_state.get('language', 'en')
    
    # 文案
    NAMES = {
        "Agency": "Starburst", "Care": "Cluster", "Curiosity": "Nebula",
        "Coherence": "Grid", "Reflection": "Swirl", "Transcendence": "Ascension", "Aesthetic": "Sphere"
    }
    title = NAMES.get(p_attr, "Nebula")
    desc = "Topology of thought based on dialogue meaning structure" if lang=='en' else "基于对话意义结构生成的思想拓扑图"

    sac.divider(label="SOUL FORM", icon='layers', align='center', color='gray')
    st.markdown(f"<div style='text-align:center; margin-bottom:15px;'><div style='font-size:1.1em;font-weight:600;'>{title}</div><div style='font-size:0.75em;color:#888;'>{desc}</div></div>", unsafe_allow_html=True)

    # 2. 生成动画帧 (30帧循环，性能平衡点)
    frames = []
    n_frames = 30 
    
    # 提取静态属性
    ac = [p['c'] for p in raw['atmos']]; as_ = [p['s'] for p in raw['atmos']]
    tc = [p['c'] for p in raw['thoughts']]; ts = [p['s'] for p in raw['thoughts']]; tt = [p['t'] for p in raw['thoughts']]

    for i in range(n_frames):
        t = (i / n_frames) * 2 * np.pi
        ax, ay, az = calculate_physics_frame(raw['atmos'], p_attr, t, t) # 局部t=全局t
        tx, ty, tz = calculate_physics_frame(raw['thoughts'], p_attr, t, t)
        
        frames.append(go.Frame(
            data=[
                go.Scatter3d(x=ax, y=ay, z=az),
                go.Scatter3d(x=tx, y=ty, z=tz)
            ],
            traces=[0, 1]
        ))

    # 3. 初始帧
    ax0, ay0, az0 = calculate_physics_frame(raw['atmos'], p_attr, 0, 0)
    tx0, ty0, tz0 = calculate_physics_frame(raw['thoughts'], p_attr, 0, 0)

    fig = go.Figure(
        data=[
            go.Scatter3d(x=ax0, y=ay0, z=az0, mode='markers', marker=dict(size=as_, color=ac, opacity=0.6, line=dict(width=0)), hoverinfo='none', name='Atmos'),
            go.Scatter3d(x=tx0, y=ty0, z=tz0, mode='markers', marker=dict(size=ts, color=tc, opacity=1.0, line=dict(width=1, color='white')), text=tt, hoverinfo='text', name='Thoughts')
        ],
        frames=frames
    )

    # 4. 布局 (包含播放按钮)
    fig.update_layout(
        height=350, margin=dict(l=0, r=0, b=0, t=0),
        paper_bgcolor='black', showlegend=False,
        scene=dict(
            xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False),
            bgcolor='black', dragmode='orbit',
            camera=dict(eye=dict(x=1.6, y=0, z=0.6))
        ),
        updatemenus=[dict(
            type='buttons', showactive=False,
            y=0, x=0.5, xanchor='center', yanchor='bottom', # 居中
            pad=dict(t=10, r=10),
            bgcolor='rgba(50,50,50,0.5)', # 灰色半透明背景
            buttons=[dict(
                label='▶ ACTIVATE DYNAMICS', # 明显的按钮
                method='animate',
                args=[None, dict(frame=dict(duration=100, redraw=True), fromcurrent=True, mode='immediate', loop=True)]
            )]
        )]
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'scrollZoom': True})
    viz.render_spectrum_legend()
