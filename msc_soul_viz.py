### msc_soul_viz.py ###
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import streamlit_antd_components as sac
import msc_viz as viz
import msc_soul_gen as gen

# ==========================================
# 🌌 物理引擎 (基于 Secondary Dimension)
# ==========================================
def calculate_physics_frame(particles, motion_mode, t, global_rot):
    """
    motion_mode: 次维度，决定动态行为 (Agency=躁动, Care=柔缓...)
    """
    X = np.array([p['x'] for p in particles])
    Y = np.array([p['y'] for p in particles])
    Z = np.array([p['z'] for p in particles])
    P = np.array([p['phase'] for p in particles])
    S = np.array([p['speed'] for p in particles])

    # 🌟 核心逻辑：次维度动态映射
    
    # 1. Agency -> 躁动 (Volatile)
    # 高频抖动 + 快速脉冲
    if motion_mode == "Agency":
        jitter = 0.08 * np.sin(t * 8 * S + P) # 高频震颤
        pulse = 1.0 + 0.15 * np.sin(t * 3 * S) # 快速呼吸
        X = (X + jitter) * pulse
        Y = (Y + jitter) * pulse
        Z = (Z + jitter) * pulse
        
    # 2. Care -> 柔缓 (Gentle)
    # 极慢的呼吸，像沉睡
    elif motion_mode == "Care":
        pulse = 1.0 + 0.05 * np.sin(t * 1.0 * S + P) # 慢速呼吸
        X *= pulse; Y *= pulse; Z *= pulse
        
    # 3. Curiosity -> 流转 (Flowing)
    # 局部画圈 (李萨如轨迹)
    elif motion_mode == "Curiosity":
        orbit_r = 0.2
        X += orbit_r * np.cos(t * 2 * S + P)
        Y += orbit_r * np.sin(t * 2 * S + P)
        
    # 4. Coherence -> 冻结 (Frozen)
    # 只有极微小的刚性整体移动，强调秩序
    elif motion_mode == "Coherence":
        # 几乎不动，只做极微小的整体浮动
        Z += 0.05 * np.sin(t * 0.5)
        
    # 5. Reflection -> 深旋 (Swirling)
    # 明显的自旋角速度
    elif motion_mode == "Reflection":
        R = np.sqrt(X**2 + Y**2 + 0.01)
        # 内圈快，外圈慢
        ang = t * (0.8 / R) * S 
        X_new = X*np.cos(ang) - Y*np.sin(ang)
        Y = X*np.sin(ang) + Y*np.cos(ang)
        X = X_new
        
    # 6. Transcendence -> 漂浮 (Drifting)
    # 持续向上的流体运动
    elif motion_mode == "Transcendence":
        flow_speed = 0.8
        # Z轴循环流动
        Z = ((Z + t * flow_speed * S + 3.0) % 6.0) - 3.0
        
    # 7. Aesthetic -> 优雅 (Elegant)
    # 完美的简谐波浪
    elif motion_mode == "Aesthetic":
        wave = 0.1 * np.sin(X * 2 + t * 2) # 波动随位置变化
        Z += wave
        
    # Default Fallback
    else:
        X += 0.05 * np.sin(t*2+P)

    # 🌍 全局公转 (Global Rotation)
    # 所有模式都会叠加这个缓慢的整体旋转，为了展示全貌
    rot_speed = 0.5 # 0.5倍速
    cos_g = np.cos(global_rot * rot_speed)
    sin_g = np.sin(global_rot * rot_speed)
    X_f = X * cos_g - Y * sin_g
    Y_f = X * sin_g + Y * cos_g
    
    return X_f, Y_f, Z

# ==========================================
# 🎨 渲染主程序
# ==========================================
def render_soul_scene(radar_dict, user_nodes=None):
    if user_nodes is None: user_nodes = []
    
    # 1. 生成基础数据 (包含 Primary 和 Secondary 属性)
    raw, p_attr, s_attr = gen.generate_nebula_data(radar_dict, user_nodes)
    lang = st.session_state.get('language', 'en')
    
    # 文案映射
    SHAPE_NAMES = {
        "Agency": "Starburst", "Care": "Cluster", "Curiosity": "Nebula",
        "Coherence": "Grid", "Reflection": "Vortex", "Transcendence": "Ascension", "Aesthetic": "Sphere"
    }
    MOTION_NAMES = {
        "Agency": "Volatile", "Care": "Gentle", "Curiosity": "Flowing",
        "Coherence": "Frozen", "Reflection": "Swirling", "Transcendence": "Drifting", "Aesthetic": "Harmonic"
    }
    
    shape_name = SHAPE_NAMES.get(p_attr, "Nebula")
    motion_name = MOTION_NAMES.get(s_attr, "Static")
    
    title = f"{shape_name}"
    # 隐喻描述：形如[主维度]，动如[次维度]
    desc = f"Form of {p_attr} · Rhythm of {s_attr}" if lang=='en' else f"以 [{p_attr}] 为形 · 以 [{s_attr}] 为律"

    sac.divider(label="SOUL FORM", icon='layers', align='center', color='gray')
    st.markdown(f"<div style='text-align:center; margin-bottom:15px;'><div style='font-size:1.1em;font-weight:600;'>{title}</div><div style='font-size:0.75em;color:#888;'>{desc}</div></div>", unsafe_allow_html=True)

    # 2. 预计算 30 帧 (Pre-calculate 30 Frames)
    frames = []
    n_frames = 30
    
    ac = [p['c'] for p in raw['atmos']]; as_ = [p['s'] for p in raw['atmos']]
    tc = [p['c'] for p in raw['thoughts']]; ts = [p['s'] for p in raw['thoughts']]; tt = [p['t'] for p in raw['thoughts']]

    for i in range(n_frames):
        t = (i / n_frames) * 2 * np.pi # 0 -> 2PI
        global_rot = t # 全局旋转周期同步
        
        # 🌟 关键：传入 s_attr (次维度) 控制物理动态
        ax, ay, az = calculate_physics_frame(raw['atmos'], s_attr, t, global_rot)
        tx, ty, tz = calculate_physics_frame(raw['thoughts'], s_attr, t, global_rot)
        
        frames.append(go.Frame(
            data=[
                go.Scatter3d(x=ax, y=ay, z=az),
                go.Scatter3d(x=tx, y=ty, z=tz)
            ],
            traces=[0, 1]
        ))

    # 3. 初始帧
    ax0, ay0, az0 = calculate_physics_frame(raw['atmos'], s_attr, 0, 0)
    tx0, ty0, tz0 = calculate_physics_frame(raw['thoughts'], s_attr, 0, 0)

    fig = go.Figure(
        data=[
            go.Scatter3d(x=ax0, y=ay0, z=az0, mode='markers', marker=dict(size=as_, color=ac, opacity=0.5, line=dict(width=0)), hoverinfo='none', name='Atmos'),
            go.Scatter3d(x=tx0, y=ty0, z=tz0, mode='markers', marker=dict(size=ts, color=tc, opacity=1.0, line=dict(width=1, color='white')), text=tt, hoverinfo='text', name='Thoughts')
        ],
        frames=frames
    )

    # 4. 布局
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
            y=0, x=0.5, xanchor='center', yanchor='bottom',
            pad=dict(t=10, r=10),
            bgcolor='rgba(50,50,50,0.5)',
            buttons=[dict(
                label='▶ ACTIVATE',
                method='animate',
                args=[None, dict(frame=dict(duration=80, redraw=True), fromcurrent=True, mode='immediate', loop=True)]
            )]
        )]
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'scrollZoom': True})
    viz.render_spectrum_legend()
