### msc_soul_viz.py ###
import streamlit as st
import plotly.graph_objects as go
import streamlit_antd_components as sac
import msc_viz as viz
import msc_soul_gen as gen

def render_soul_scene(radar_dict, user_nodes=None):
    if user_nodes is None: user_nodes = []
    
    plot_data, p_attr, s_attr = gen.generate_soul_network(radar_dict, user_nodes)
    lang = st.session_state.get('language', 'en')
    
    # --- 文案映射保持不变 ---
    ARCHETYPE_NAMES = {
        "Agency": {"en": "Starburst Structure", "zh": "爆发结构"},
        "Care": {"en": "Dense Cluster", "zh": "凝聚结构"},
        "Curiosity": {"en": "Wide Web", "zh": "发散网络"},
        "Coherence": {"en": "Crystalline Grid", "zh": "晶格结构"},
        "Reflection": {"en": "Deep Swirl", "zh": "深旋结构"},
        "Transcendence": {"en": "Ascending Cloud", "zh": "升腾云结构"},
        "Aesthetic": {"en": "Harmonic Sphere", "zh": "和谐球体"}
    }
    ASPECT_NAMES = {
        "Agency": {"en": "Volatile Mode", "zh": "躁动模式"},
        "Care": {"en": "Gentle Mode", "zh": "柔缓模式"},
        "Curiosity": {"en": "Flowing Mode", "zh": "流转模式"},
        "Coherence": {"en": "Stable Mode", "zh": "稳定模式"},
        "Reflection": {"en": "Breathing Mode", "zh": "呼吸模式"},
        "Transcendence": {"en": "Drifting Mode", "zh": "漂浮模式"},
        "Aesthetic": {"en": "Elegant Mode", "zh": "优雅模式"}
    }

    p_name = ARCHETYPE_NAMES.get(p_attr, {}).get(lang, p_attr)
    s_name = ASPECT_NAMES.get(s_attr, {}).get(lang, s_attr)
    
    creature_title = p_name if len(user_nodes) > 0 else ("Proto-Field" if lang=='en' else "初生场域")
    creature_desc = (f"operating in {s_name}" if lang=='en' else f"运行于 {s_name}") if len(user_nodes) > 0 else ("Awaiting thought injection..." if lang=='en' else "等待思想注入...")

    label_title = "SOUL FORM" if lang=='en' else "灵魂形态"
    sac.divider(label=label_title, icon='layers', align='center', color='gray')
    st.markdown(f"<div style='text-align:center; margin-top:-15px; margin-bottom:10px;'><b>{creature_title}</b><br><span style='font-size:0.8em;color:gray'>{creature_desc}</span></div>", unsafe_allow_html=True)
    
    # ==========================================
    # 🟢 核心修改：分离数据源
    # ==========================================
    # 1. 拆分主星 (Thought) 和 背景星 (Atmos)
    thought_indices = [i for i, t in enumerate(plot_data['type']) if t == 'thought']
    atmos_indices = [i for i, t in enumerate(plot_data['type']) if t == 'atmos']

    def get_subset(indices):
        return {
            "x": [plot_data["x"][i] for i in indices],
            "y": [plot_data["y"][i] for i in indices],
            "z": [plot_data["z"][i] for i in indices],
            "color": [plot_data["color"][i] for i in indices],
            "size": [plot_data["size"][i] for i in indices],
            "text": [plot_data["text"][i] for i in indices]
        }

    thoughts = get_subset(thought_indices)
    atmos = get_subset(atmos_indices)

    fig = go.Figure()

    # ==========================================
    # Layer 1: 背景星海 (Star Field)
    # 特点：小、锐利、无光晕、半透明
    # ==========================================
    if atmos['x']:
        fig.add_trace(go.Scatter3d(
            x=atmos["x"], y=atmos["y"], z=atmos["z"],
            mode='markers',
            marker=dict(
                size=atmos["size"], # 使用 gen.py 中生成的极小尺寸
                color=atmos["color"],
                opacity=0.8, # 较高不透明度，像星星一样亮
                line=dict(width=0) # 无描边
            ),
            hoverinfo='none' # 背景星不交互
        ))

    # ==========================================
    # Layer 2: 核心思想 - 光晕层 (Aura)
    # 特点：大、虚、淡
    # ==========================================
    if thoughts['x']:
        fig.add_trace(go.Scatter3d(
            x=thoughts["x"], y=thoughts["y"], z=thoughts["z"],
            mode='markers',
            marker=dict(
                size=[s * 3.0 for s in thoughts["size"]], 
                color=thoughts["color"],
                opacity=0.2, 
            ),
            hoverinfo='none'
        ))

    # ==========================================
    # Layer 3: 核心思想 - 实体层 (Core)
    # 特点：中等、实、亮、有描边
    # ==========================================
    if thoughts['x']:
        fig.add_trace(go.Scatter3d(
            x=thoughts["x"], y=thoughts["y"], z=thoughts["z"],
            mode='markers',
            marker=dict(
                size=thoughts["size"],
                color=thoughts["color"],
                opacity=1.0,
                line=dict(color='white', width=1.5) # 强白色描边
            ),
            text=thoughts["text"],
            hoverinfo='text'
        ))

    # ==========================================
    # 布局配置
    # ==========================================
    fig.update_layout(
        height=400,
        margin=dict(l=0, r=0, b=0, t=0),
        paper_bgcolor='black',
        scene=dict(
            # 硬边框 + 黑色背景
            xaxis=dict(visible=False, range=[-1.4, 1.4]),
            yaxis=dict(visible=False, range=[-1.4, 1.4]),
            zaxis=dict(visible=False, range=[-1.4, 1.4]),
            aspectmode='cube',
            bgcolor='black',
            camera=dict(
                eye=dict(x=1.6, y=1.6, z=1.2)
            ),
            # 🟢 关键：Orbit 模式让鼠标拨动像地球仪一样丝滑
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
