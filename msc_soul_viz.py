### msc_soul_viz.py ###
import streamlit as st
import plotly.graph_objects as go
import streamlit_antd_components as sac
import msc_viz as viz
import msc_soul_gen as gen

def render_soul_scene(radar_dict, user_nodes=None):
    if user_nodes is None: user_nodes = []
    
    # 获取归一化后的数据
    plot_data, p_attr, s_attr = gen.generate_soul_network(radar_dict, user_nodes)
    lang = st.session_state.get('language', 'en')
    
    # 文案映射 (保持不变)
    ARCHETYPE_NAMES = {
        "Agency": {"en": "Starburst", "zh": "爆发结构"},
        "Care": {"en": "Dense Cluster", "zh": "凝聚结构"},
        "Curiosity": {"en": "Wide Web", "zh": "发散网络"},
        "Coherence": {"en": "Crystalline", "zh": "晶格结构"},
        "Reflection": {"en": "Deep Swirl", "zh": "深旋结构"},
        "Transcendence": {"en": "Ascending Cloud", "zh": "升腾结构"},
        "Aesthetic": {"en": "Harmonic Sphere", "zh": "和谐球体"}
    }
    p_name = ARCHETYPE_NAMES.get(p_attr, {}).get(lang, p_attr)
    
    label_title = "SOUL FORM" if lang=='en' else "灵魂形态"
    sac.divider(label=label_title, icon='layers', align='center', color='gray')
    st.markdown(f"<div style='text-align:center; margin-top:-10px; margin-bottom:10px;'><b style='color:#333;'>{p_name}</b></div>", unsafe_allow_html=True)
    
    # ==========================================
    # 🟢 Plotly 双层发光渲染
    # ==========================================
    fig = go.Figure()

    # 第一层：光晕 (Aura) - 较大，低透明度
    fig.add_trace(go.Scatter3d(
        x=plot_data["x"], y=plot_data["y"], z=plot_data["z"],
        mode='markers',
        marker=dict(
            size=[s * 2.5 for s in plot_data["size"]], # 光晕比核心大
            color=plot_data["color"],
            opacity=0.15, # 非常淡
        ),
        hoverinfo='none'
    ))

    # 第二层：核心 (Core) - 较小，高亮度
    fig.add_trace(go.Scatter3d(
        x=plot_data["x"], y=plot_data["y"], z=plot_data["z"],
        mode='markers',
        marker=dict(
            size=plot_data["size"],
            color=plot_data["color"],
            opacity=0.9,
            line=dict(color='white', width=0.5) # 白色描边增加亮度
        ),
        text=plot_data["text"],
        hoverinfo='text'
    ))

    # 3. 样式配置 (彻底修复旋转与缩放)
    fig.update_layout(
        height=400,
        margin=dict(l=0, r=0, b=0, t=0),
        paper_bgcolor='rgba(0,0,0,0)', # 透明背景适配 Streamlit 主题
        showlegend=False,
        scene=dict(
            xaxis=dict(visible=False, range=[-1.2, 1.2]), # 限制显示范围，形成硬边框感
            yaxis=dict(visible=False, range=[-1.2, 1.2]),
            zaxis=dict(visible=False, range=[-1.2, 1.2]),
            aspectmode='cube', # 强制比例为 1:1:1
            bgcolor='black',   # 内部空间背景黑
            camera=dict(
                eye=dict(x=1.8, y=1.8, z=1.2), # 调整相机距离，确保在手机端能看全
                projection=dict(type='perspective') # 使用透视视图增加深度感
            ),
            dragmode='orbit' # 允许旋转
        ),
        # 针对移动端的特殊配置
        hoverlabel=dict(bgcolor="black", font_size=12, font_family="JetBrains Mono")
    )
    
    # 🟢 关键：config 参数决定了是否可以旋转、缩放
    st.plotly_chart(fig, use_container_width=True, config={
        'displayModeBar': False, # 隐藏上方工具栏
        'scrollZoom': True,      # 开启缩放
        'staticPlot': False,     # 必须为 False 才能旋转
        'responsive': True       # 自适应手机屏幕
    })
    
    viz.render_spectrum_legend()
