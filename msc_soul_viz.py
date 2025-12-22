### msc_soul_viz.py ###
import streamlit as st
import plotly.graph_objects as go
import streamlit_antd_components as sac
import msc_viz as viz
import msc_soul_gen as gen

def render_soul_scene(radar_dict, user_nodes=None):
    if user_nodes is None: user_nodes = []
    
    # 1. 获取数据
    plot_data, p_attr, s_attr = gen.generate_soul_network(radar_dict, user_nodes)
    lang = st.session_state.get('language', 'en')
    
    # ==========================================
    # 🟢 恢复双维度文案映射 (Archetype + Aspect)
    # ==========================================
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

    # 获取对应语言的文本
    p_name = ARCHETYPE_NAMES.get(p_attr, {}).get(lang, p_attr)
    s_name = ASPECT_NAMES.get(s_attr, {}).get(lang, s_attr)
    
    # 构造标题和描述
    if len(user_nodes) == 0:
        creature_title = "Proto-Field" if lang=='en' else "初生场域"
        creature_desc = "Awaiting thought injection..." if lang=='en' else "等待思想注入..."
    else:
        creature_title = p_name
        creature_desc = f"operating in {s_name}" if lang=='en' else f"运行于 {s_name}"

    label_title = "SOUL FORM" if lang=='en' else "灵魂形态"
    sac.divider(label=label_title, icon='layers', align='center', color='gray')
    st.markdown(f"<div style='text-align:center; margin-top:-15px; margin-bottom:10px;'><b>{creature_title}</b><br><span style='font-size:0.8em;color:gray'>{creature_desc}</span></div>", unsafe_allow_html=True)
    
    # ==========================================
    # 🟢 渲染策略：双层粒子 (光晕 + 核心)
    # ==========================================
    fig = go.Figure()

    # 第一层：外部光晕 (Aura) - 大尺寸、低透明度
    fig.add_trace(go.Scatter3d(
        x=plot_data["x"], y=plot_data["y"], z=plot_data["z"],
        mode='markers',
        marker=dict(
            size=[s * 3.5 for s in plot_data["size"]], # 光晕放大
            color=plot_data["color"],
            opacity=0.15, # 产生雾感
        ),
        hoverinfo='none'
    ))

    # 第二层：内部核心 (Core) - 小尺寸、高亮度、带边框
    fig.add_trace(go.Scatter3d(
        x=plot_data["x"], y=plot_data["y"], z=plot_data["z"],
        mode='markers',
        marker=dict(
            size=plot_data["size"],
            color=plot_data["color"],
            opacity=0.9,
            line=dict(color='white', width=1) # 白色描边增加质感
        ),
        text=plot_data["text"],
        hoverinfo='text'
    ))

    # ==========================================
    # 🟢 布局配置：解决边框和交互问题
    # ==========================================
    fig.update_layout(
        height=400,
        margin=dict(l=0, r=0, b=0, t=0),
        paper_bgcolor='black', # 视窗背景
        scene=dict(
            # 硬边框逻辑：
            # 粒子坐标归一化在 [-1, 1]，坐标轴范围锁定在 [-1.4, 1.4]
            # 这样粒子永远在画面中央，不会飞出去
            xaxis=dict(visible=False, range=[-1.4, 1.4]),
            yaxis=dict(visible=False, range=[-1.4, 1.4]),
            zaxis=dict(visible=False, range=[-1.4, 1.4]),
            
            aspectmode='cube', # 锁定立方体比例
            bgcolor='black',   # 场景背景
            camera=dict(
                eye=dict(x=1.7, y=1.7, z=1.3) # 调整相机距离
            ),
            dragmode='orbit' # 确保开启旋转
        ),
        showlegend=False
    )
    
    # 🟢 交互配置：显式开启配置
    st.plotly_chart(fig, use_container_width=True, config={
        'scrollZoom': True,      # 允许缩放
        'displayModeBar': False, # 隐藏工具栏
        'staticPlot': False,     # 关键：必须为 False 才能旋转
        'responsive': True       # 适配移动端
    })
    
    viz.render_spectrum_legend()
