### msc_soul_viz.py ###
import streamlit as st
from streamlit_echarts import st_echarts
import streamlit_antd_components as sac
import msc_viz as viz
import msc_soul_gen as gen

def render_soul_scene(radar_dict, user_nodes=None):
    if user_nodes is None: user_nodes = []
    
    nodes, edges, physics_config, p_attr, s_attr = gen.generate_soul_network(radar_dict, user_nodes)
    
    lang = st.session_state.get('language', 'en')
    
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
    
    background_color = "#FFFFFF"

    # 🟢 [修改点]：缩小坐标范围，收紧粒子雾
    axis_range = 180 
    axis_common = {
        "show": False,
        "min": -axis_range, "max": axis_range,
        "axisLine": {"show": False},
        "axisLabel": {"show": False},
        "splitLine": {"show": False}
    }

    option = {
        "backgroundColor": background_color,
        "tooltip": {
            "show": True,
            "formatter": "{b}<br/>{c}", 
            "backgroundColor": "rgba(50,50,50,0.8)",
            "textStyle": {"color": "#fff"},
            "borderColor": "#333"
        },
        
        "xAxis3D": axis_common,
        "yAxis3D": axis_common,
        "zAxis3D": axis_common,

        "grid3D": {
            "show": False,
            "viewControl": {
                "projection": 'perspective',
                "autoRotate": True,
                "autoRotateSpeed": 2, 
                # 🟢 [修改点]：拉近相机 (400 -> 220)，配合更小的视窗高度
                "distance": 220,
                "minDistance": 100, "maxDistance": 400,
                "alpha": 20, "beta": 40
            },
            "light": {
                "main": {"intensity": 1.2, "alpha": 30, "beta": 30},
                "ambient": {"intensity": 0.8}
            },
            "postEffect": {
                "enable": True,
                "bloom": {
                    "enable": True,
                    "bloomIntensity": 0.3 
                }
            },
            "environment": background_color
        },

        "series": [{
            "type": 'graphGL',
            "layout": 'force',
            "force": {
                "repulsion": physics_config["repulsion"],
                "gravity": physics_config["gravity"],
                "friction": physics_config["friction"],
                "edgeLength": physics_config["edgeLength"],
                "initLayout": 'spherical'
            },
            "data": nodes,
            "links": edges,
            "itemStyle": {"opacity": 1},
            "lineStyle": {"width": 0.5, "opacity": 0.1},
            "emphasis": {
                "itemStyle": {"borderColor": "#000", "borderWidth": 1},
                "lineStyle": {"width": 2, "opacity": 0.8},
                "label": {"show": True}
            }
        }]
    }
    
    # 🟢 [修改点]：高度改为 450px，视窗变小
    st_echarts(options=option, height="450px")
    viz.render_spectrum_legend()
