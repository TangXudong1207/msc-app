### msc_soul_viz.py ###
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import streamlit_antd_components as sac
import msc_viz as viz
import msc_soul_gen as gen
import math

def rotate_points(x, y, angle_rad):
    """
    二维旋转算法，用于生成旋转动画帧
    """
    x_new = x * math.cos(angle_rad) - y * math.sin(angle_rad)
    y_new = x * math.sin(angle_rad) + y * math.cos(angle_rad)
    return x_new, y_new

def render_soul_scene(radar_dict, user_nodes=None):
    if user_nodes is None: user_nodes = []
    
    # 1. 获取静态粒子数据
    data, p_attr, s_attr = gen.generate_nebula_data(radar_dict, user_nodes)
    
    lang = st.session_state.get('language', 'en')
    
    # --- 文案映射 (保持原逻辑) ---
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
        creature_title = "Proto-Field" if lang=='en' else "初生场域"
        creature_desc = "Awaiting thought injection..." if lang=='en' else "等待思想注入..."
    else:
        creature_title = p_name
        creature_desc = "Soul Resonance Field" if lang=='en' else "灵魂共鸣场"

    label_title = "SOUL FORM" if lang=='en' else "灵魂形态"
    sac.divider(label=label_title, icon='layers', align='center', color='gray')
    st.markdown(f"<div style='text-align:center; margin-bottom: -10px;'><b>{creature_title}</b><br><span style='font-size:0.8em;color:gray'>{creature_desc}</span></div>", unsafe_allow_html=True)

    # ==========================================
    # 🌌 Plotly 3D 渲染 (带自旋动画)
    # ==========================================
    
    # 1. 初始 Trace (第0帧)
    # Trace 0: 氛围 (Atmos)
    trace_atmos = go.Scatter3d(
        x=data["atmos"]["x"], y=data["atmos"]["y"], z=data["atmos"]["z"],
        mode='markers',
        marker=dict(
            size=data["atmos"]["s"],
            color=data["atmos"]["c"],
            opacity=0.6, # 氛围半透明
            line=dict(width=0) # 无边框
        ),
        hoverinfo='none', # 氛围不显示文字
        name='Atmosphere'
    )
    
    # Trace 1: 思想 (Thoughts)
    trace_thoughts = go.Scatter3d(
        x=data["thoughts"]["x"], y=data["thoughts"]["y"], z=data["thoughts"]["z"],
        mode='markers',
        marker=dict(
            size=data["thoughts"]["s"],
            color=data["thoughts"]["c"],
            opacity=1.0,
            symbol='circle',
            line=dict(width=2, color='white') # 恒星有白边
        ),
        text=data["thoughts"]["t"],
        hoverinfo='text',
        name='Thoughts'
    )

    # 2. 生成动画帧 (Frames)
    # 我们生成 30 帧，旋转 360 度
    frames = []
    num_frames = 60 # 帧数越多越流畅，但加载越慢。60帧对于手机端是合理的权衡。
    
    # 预先转换 numpy array 加速计算
    ax_np = np.array(data["atmos"]["x"])
    ay_np = np.array(data["atmos"]["y"])
    tx_np = np.array(data["thoughts"]["x"])
    ty_np = np.array(data["thoughts"]["y"])
    
    for i in range(num_frames):
        angle = (2 * math.pi * i) / num_frames
        
        # 旋转氛围
        ax_rot, ay_rot = rotate_points(ax_np, ay_np, angle)
        # 旋转思想
        tx_rot, ty_rot = rotate_points(tx_np, ty_np, angle)
        
        frames.append(go.Frame(
            data=[
                go.Scatter3d(x=ax_rot, y=ay_rot), # Update Trace 0
                go.Scatter3d(x=tx_rot, y=ty_rot)  # Update Trace 1
            ],
            traces=[0, 1] 
        ))

    # 3. 布局设置
    fig = go.Figure(
        data=[trace_atmos, trace_thoughts],
        frames=frames
    )

    fig.update_layout(
        height=350, # 正方形视窗
        margin=dict(l=0, r=0, b=0, t=0),
        paper_bgcolor='black',
        showlegend=False,
        scene=dict(
            xaxis=dict(visible=False, showbackground=False),
            yaxis=dict(visible=False, showbackground=False),
            zaxis=dict(visible=False, showbackground=False),
            bgcolor='black',
            dragmode='orbit', # 关键：允许像星球一样旋转
            camera=dict(
                eye=dict(x=1.8, y=1.8, z=0.5), # 稍微俯视
                projection=dict(type='perspective')
            )
        ),
        # 动画按钮配置
        updatemenus=[dict(
            type='buttons',
            showactive=False,
            y=0.1, x=0.1, xanchor='right', yanchor='bottom',
            pad=dict(t=0, r=10),
            buttons=[dict(
                label='⚡ LIVE', # 播放按钮文案
                method='animate',
                args=[None, dict(
                    frame=dict(duration=100, redraw=True), # 每一帧 100ms
                    fromcurrent=True,
                    transition=dict(duration=0),
                    mode='immediate',
                    loop=True # 循环播放
                )]
            )]
        )]
    )

    # 渲染
    # config 中 scrollZoom: True 允许滚轮缩放
    # displayModeBar: False 隐藏讨厌的 Plotly 工具栏，保持极简
    st.plotly_chart(
        fig, 
        use_container_width=True, 
        config={'displayModeBar': False, 'scrollZoom': True}
    )
    
    # 底部图例
    viz.render_spectrum_legend()
