### msc_soul_viz.py ###
import streamlit as st
from streamlit_echarts import st_echarts
import streamlit_antd_components as sac
import msc_viz as viz
import msc_soul_gen as gen
import time

def render_soul_scene(radar_dict, user_nodes=None):
    if user_nodes is None: user_nodes = []
    
    nodes, edges, physics_config, p_attr, s_attr = gen.generate_soul_network(radar_dict, user_nodes)
    
    lang = st.session_state.get('language', 'en')
    
    # ... (省略翻译字典，保持不变) ...
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
    
    # 🎨 [背景色]：改为黑色 (#000000) 才能看到发光效果 (Bloom)
    background_color = "#000000"

    # 📏 [边界范围]：控制粒子活动的隐形盒子大小
    # 值越小，粒子越容易跑出屏幕；值越大，粒子看起来越小。
    axis_range = 250 
    
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
            # 📷 [相机控制]
            "viewControl": {
                "projection": 'perspective',
                # 🔄 [自动旋转]：True 为开启。如果没转，尝试刷新页面。
                "autoRotate": True,
                
                # 🚀 [转速]：数值越大转得越快。比如设为 10 或 20 试试。
                "autoRotateSpeed": 10, 
                
                # 🔭 [相机距离]：数值越大，相机离粒子越远（画面缩小）。
                # 如果你想把所有粒子都放进去，就把这个数字调大 (比如 500, 600)。
                "distance": 500,
                
                "minDistance": 200, "maxDistance": 800,
                "alpha": 20, "beta": 40
            },
            "light": {
                "main": {"intensity": 1.5, "alpha": 30, "beta": 30},
                "ambient": {"intensity": 0.5}
            },
            # ✨ [发光特效] (Post Processing)
            "postEffect": {
                "enable": True,
                "bloom": {
                    "enable": True,
                    # 💡 [发光强度]：0.1 (微弱) ~ 1.0 (极强)。
                    "bloomIntensity": 0.6
                }
            },
            "environment": background_color
        },

        "series": [{
            "type": 'graphGL',
            "layout": 'force',
            "roam": True, # 允许平移和缩放
            
            # ⚛️ [物理引擎参数]：来自 msc_soul_gen.py
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
            "lineStyle": {"width": 0.5, "opacity": 0.2},
            "emphasis": {
                "itemStyle": {"borderColor": "#FFF", "borderWidth": 2},
                "lineStyle": {"width": 2, "opacity": 1.0},
                "label": {"show": True}
            }
        }]
    }
    
    # 📺 [视窗高度]：350px (正方形)
    # 🔑 [强制刷新 Key]：添加 key 参数，确保每次参数修改后组件都会重绘
    st_echarts(options=option, height="350px", key=f"soul_viz_{int(time.time())}")
    viz.render_spectrum_legend()
