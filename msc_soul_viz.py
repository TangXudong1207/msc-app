import streamlit as st
from streamlit_echarts import st_echarts
import streamlit_antd_components as sac
import msc_viz as viz
import msc_soul_gen as gen

def render_soul_scene(radar_dict, user_nodes=None):
    if user_nodes is None: user_nodes = []
    
    # 1. 调用生成器获取网络数据和物理配置
    nodes, edges, physics_config, p_attr, s_attr = gen.generate_soul_network(radar_dict, user_nodes)
    
    lang = st.session_state.get('language', 'en')
    
    # --- 标题和描述的翻译映射 (基于新的物理隐喻) ---
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

    p_name = ARCHETYPE_NAMES.get(p_attr, {}).get(lang, p_attr)
    s_name = ASPECT_NAMES.get(s_attr, {}).get(lang, s_attr)
    
    if len(user_nodes) == 0:
        creature_title = "Proto-Field" if lang=='en' else "初生场域"
        creature_desc = "Awaiting thought injection..." if lang=='en' else "等待思想注入..."
    else:
        creature_title = p_name
        creature_desc = f"operating in {s_name}" if lang=='en' else f"运行于 {s_name}"

    label_title = "SOUL FORM" if lang=='en' else "灵魂形态"
    sac.divider(label=label_title, icon='layers', align='center', color='gray')
    st.markdown(f"<div style='text-align:center; margin-bottom: -20px;'><b>{creature_title}</b><br><span style='font-size:0.8em;color:gray'>{creature_desc}</span></div>", unsafe_allow_html=True)
    
    # ==========================================
    # 🎯 ECharts GraphGL 配置
    # ==========================================
    
    background_color = "#FFFFFF" # 纯白背景

    # 2. 坐标轴配置 (调整大小)
    # 对于 graphGL，坐标轴更多是参考背景。
    # 我们设置一个适中的范围，让网络在其中自然生长。
    axis_range = 50 
    axis_common = {
        "show": True,
        "min": -axis_range, "max": axis_range,
        "axisLine": {"lineStyle": {"color": "#EEEEEE", "width": 1}}, # 非常淡的轴线
        "axisLabel": {"show": False}, # 不显示标签，保持干净
        "splitLine": {"show": True, "lineStyle": {"color": "#F5F5F5", "width": 1}} # 非常淡的网格
    }

    option = {
        "backgroundColor": background_color,
        # 提示框组件
        "tooltip": {
            "show": True,
            "formatter": lambda params: f"<b>{params.name}</b><br>{params.value}" if params.value else params.name,
            "backgroundColor": "rgba(50,50,50,0.8)",
            "textStyle": {"color": "#fff"},
            "borderColor": "#333"
        },
        
        "xAxis3D": axis_common,
        "yAxis3D": axis_common,
        "zAxis3D": axis_common,

        "grid3D": {
            # 调整视野深度，让巨大的节点看起来更震撼
            "viewControl": {
                "projection": 'perspective',
                "autoRotate": True,
                "autoRotateSpeed": 5, # 缓慢旋转展示动态
                "distance": 250,
                "minDistance": 150, "maxDistance": 400,
                "alpha": 20, "beta": 40
            },
            # 明亮、干净的光照
            "light": {
                "main": {"intensity": 1.2, "alpha": 30, "beta": 30},
                "ambient": {"intensity": 0.8}
            },
            "environment": background_color
        },

        "series": [{
            "type": 'graphGL', # 核心：使用 WebGL 加速的关系图
            "layout": 'force', # 核心：使用力引导布局
            "force": {
                # 3. 注入物理引擎参数
                "repulsion": physics_config["repulsion"],
                "gravity": physics_config["gravity"],
                "friction": physics_config["friction"],
                "edgeLength": physics_config["edgeLength"],
                "initLayout": 'spherical' # 初始呈球状分布，然后炸开
            },
            "data": nodes,
            "links": edges,
            # 节点和边的通用样式已在数据生成时定义，这里设置全局默认
            "itemStyle": {"opacity": 1},
            "lineStyle": {"width": 0.5, "opacity": 0.1},
            # 高亮样式
            "emphasis": {
                "itemStyle": {"borderColor": "#000", "borderWidth": 1},
                "lineStyle": {"width": 2, "opacity": 0.8},
                "label": {"show": True}
            }
        }]
    }
    
    # 增加组件高度，提供更有沉浸感的视野
    st_echarts(options=option, height="600px")
    viz.render_spectrum_legend()
