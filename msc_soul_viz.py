### msc_soul_viz.py ###
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import streamlit_antd_components as sac
import msc_viz as viz
import msc_soul_gen as gen

# ==========================================
# 🧮 物理引擎 (NumPy Accelerated)
# ==========================================
def calculate_physics_frame(particles, mode, t_step, global_rot):
    """
    计算某一帧的所有粒子位置
    particles: 列表数据
    mode: 物理模式 (Agency, Reflection...)
    t_step: 当前时间步 (0.0 - 2PI)
    global_rot: 全局旋转角度
    """
    # 1. 转换为 NumPy 数组以便批量计算
    N = len(particles)
    X = np.array([p['x'] for p in particles])
    Y = np.array([p['y'] for p in particles])
    Z = np.array([p['z'] for p in particles])
    Phase = np.array([p['phase'] for p in particles])
    Speed = np.array([p['speed'] for p in particles])

    # 2. 应用局部物理 (Local Physics)
    if mode == "Agency": 
        # 💥 呼吸/爆发：沿径向伸缩
        # R_new = R_old * (1 + 0.2 * sin(t * speed + phase))
        factor = 1 + 0.15 * np.sin(t_step * 2 * Speed + Phase)
        X = X * factor
        Y = Y * factor
        Z = Z * factor

    elif mode == "Reflection":
        # 🌀 漩涡：绕Z轴旋转，内快外慢
        R = np.sqrt(X**2 + Y**2 + 0.1) # 半径
        angle = t_step * (2.0 / R) * Speed * 0.5 # 核心旋转快
        X_new = X * np.cos(angle) - Y * np.sin(angle)
        Y_new = X * np.sin(angle) + Y * np.cos(angle)
        X, Y = X_new, Y_new

    elif mode == "Transcendence":
        # ☁️ 升腾：Z轴向上流动，循环
        Z = Z + (t_step * Speed * 0.5) 
        # 边界循环：如果超过 2.5，回到 -2.5
        # 这里的 t_step 是单调增的，我们需要取模逻辑
        # 简易模拟：Z = (Z_init + t * speed) % range - offset
        cycle_height = 5.0
        Z = ((Z + 2.5) % cycle_height) - 2.5

    elif mode == "Curiosity":
        # 🕸️ 脉冲：随机游走/闪烁感
        # 使用高频正弦波模拟抖动
        jitter = 0.05 * np.sin(t_step * 10 + Phase)
        X += jitter
        Y += jitter
        Z += jitter

    elif mode == "Aesthetic":
        # 🪐 轨道：在球面上滑动
        # 简单模拟：绕任意轴微转
        angle = t_step * 0.5 * Speed
        X_new = X * np.cos(angle) - Z * np.sin(angle)
        Z_new = X * np.sin(angle) + Z * np.cos(angle)
        X, Z = X_new, Z_new

    # Coherence & Care & Structure: 保持相对静止，只有微动
    else: 
        offset = 0.02 * np.sin(t_step * 3 + Phase)
        X += offset
        Y += offset
        Z += offset

    # 3. 应用全局旋转 (Global Rotation)
    # 绕 Z 轴整体缓慢旋转
    cos_g = np.cos(global_rot)
    sin_g = np.sin(global_rot)
    X_final = X * cos_g - Y * sin_g
    Y_final = X * sin_g + Y * cos_g
    
    return X_final, Y_final, Z

# ==========================================
# 🎨 渲染主逻辑
# ==========================================
def render_soul_scene(radar_dict, user_nodes=None):
    if user_nodes is None: user_nodes = []
    
    # 1. 生成初始种子数据
    raw_data, p_attr = gen.generate_nebula_data(radar_dict, user_nodes)
    
    lang = st.session_state.get('language', 'en')
    
    # 文案
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
    desc = "Topology of thought based on dialogue meaning structure" if lang=='en' else "基于对话意义结构生成的思想拓扑图"

    # UI 头部
    label_title = "SOUL FORM" if lang=='en' else "灵魂形态"
    sac.divider(label=label_title, icon='layers', align='center', color='gray')
    st.markdown(f"""
    <div style='text-align:center; margin-bottom: 20px;'>
        <div style='font-size: 1.1em; font-weight: 600; letter-spacing: 1px;'>{title}</div>
        <div style='font-size: 0.75em; color: #888; margin-top: 4px;'>{desc}</div>
    </div>
    """, unsafe_allow_html=True)

    # 2. 预计算动画帧 (Pre-calculate Frames)
    # 帧数越多越细腻，但数据量越大。50帧是一个平衡点。
    num_frames = 50 
    frames = []
    
    # 提取静态属性以复用
    atmos_c = [p['c'] for p in raw_data['atmos']]
    atmos_s = [p['s'] for p in raw_data['atmos']]
    th_c = [p['c'] for p in raw_data['thoughts']]
    th_s = [p['s'] for p in raw_data['thoughts']]
    th_t = [p['t'] for p in raw_data['thoughts']]

    # 循环生成每一帧的数据
    for i in range(num_frames):
        # 时间参数 0 -> 2PI
        t_step = (i / num_frames) * 2 * np.pi
        # 全局旋转：转一圈
        global_rot = (i / num_frames) * 2 * np.pi 
        
        # 计算物理位置
        ax, ay, az = calculate_physics_frame(raw_data['atmos'], p_attr, t_step, global_rot)
        tx, ty, tz = calculate_physics_frame(raw_data['thoughts'], p_attr, t_step, global_rot)
        
        frames.append(go.Frame(
            data=[
                # Update Atmos
                go.Scatter3d(x=ax, y=ay, z=az),
                # Update Thoughts
                go.Scatter3d(x=tx, y=ty, z=tz)
            ],
            traces=[0, 1]
        ))

    # 3. 初始帧 (Frame 0)
    ax0, ay0, az0 = calculate_physics_frame(raw_data['atmos'], p_attr, 0, 0)
    tx0, ty0, tz0 = calculate_physics_frame(raw_data['thoughts'], p_attr, 0, 0)

    trace_atmos = go.Scatter3d(
        x=ax0, y=ay0, z=az0,
        mode='markers',
        marker=dict(size=atmos_s, color=atmos_c, opacity=0.5, line=dict(width=0)),
        hoverinfo='none', name='Atmosphere'
    )
    
    trace_thoughts = go.Scatter3d(
        x=tx0, y=ty0, z=tz0,
        mode='markers',
        marker=dict(size=th_s, color=th_c, opacity=1.0, symbol='circle', line=dict(width=1, color='rgba(255,255,255,0.8)')),
        text=th_t, hoverinfo='text', name='Thoughts'
    )

    # 4. 布局与自动播放
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
            dragmode='orbit', 
            # 摄像机固定，让粒子动
            camera=dict(eye=dict(x=1.6, y=0, z=0.6))
        ),
        # ⚡ 自动播放配置
        updatemenus=[dict(
            type='buttons',
            showactive=False,
            y=0, x=0, 
            xanchor='left', yanchor='bottom',
            pad=dict(t=0, r=0),
            bgcolor='rgba(0,0,0,0)',
            buttons=[dict(
                label='⚡ LIVE',
                method='animate',
                args=[None, dict(
                    frame=dict(duration=80, redraw=True), # 80ms/帧
                    fromcurrent=True, 
                    transition=dict(duration=0), # 硬切，避免平滑插值带来的延迟
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
