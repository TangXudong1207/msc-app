import streamlit as st
from streamlit_echarts import st_echarts
import streamlit_antd_components as sac
import msc_viz as viz
# 导入新的生成器模块
import msc_soul_gen as gen

def render_soul_scene(radar_dict, user_nodes=None):
    if user_nodes is None: user_nodes = []
    
    # 调用生成器获取数据
    echarts_data, p_attr, s_attr = gen.synthesize_creature_data(radar_dict, user_nodes)
    
    lang = st.session_state.get('language', 'en')
    
    # 翻译字典 (保持不变)
    ARCHETYPE_NAMES = {
        "Agency": {"en": "Ascending Dragon", "zh": "腾空之龙"},
        "Coherence": {"en": "Mountain & Forest", "zh": "高山森林"},
        "Care": {"en": "Celestial Whale", "zh": "天海之鲸"},
        "Curiosity": {"en": "Spirit Cat", "zh": "灵猫"},
        "Reflection": {"en": "Ancient Book", "zh": "智慧古书"},
        "Transcendence": {"en": "Gateway of Light", "zh": "光之门扉"},
        "Aesthetic": {"en": "Crystalline Tree", "zh": "结晶生命树"}
    }
    ASPECT_NAMES = {
        "Agency": {"en": "Thunder Aspect", "zh": "雷霆氛围"},
        "Coherence": {"en": "Foundation Aspect", "zh": "基石氛围"},
        "Care": {"en": "Warmth Aspect", "zh": "暖流氛围"},
        "Curiosity": {"en": "Stardust Aspect", "zh": "星尘氛围"},
        "Reflection": {"en": "Abyss Aspect", "zh": "深渊氛围"},
        "Transcendence": {"en": "Ascension Aspect", "zh": "升腾氛围"},
        "Aesthetic": {"en": "Prismatic Aspect", "zh": "幻彩氛围"}
    }

    p_name = ARCHETYPE_NAMES.get(p_attr, {}).get(lang, p_attr)
    s_name = ASPECT_NAMES.get(s_attr, {}).get(lang, s_attr)
    
    if len(user_nodes) < 3:
        creature_title = "Proto-Form" if lang=='en' else "初生形态"
        creature_desc = "Gathering energy..." if lang=='en' else "能量汇聚中..."
    else:
        creature_title = p_name
        creature_desc = f"with {s_name}" if lang=='en' else f"伴随 {s_name}"

    label_title = "SOUL FORM" if lang=='en' else "灵魂形态"
    sac.divider(label=label_title, icon='layers', align='center', color='gray')
    st.markdown(f"<div style='text-align:center; margin-bottom: -20px;'><b>{creature_title}</b><br><span style='font-size:0.8em;color:gray'>{creature_desc}</span></div>", unsafe_allow_html=True)
    
    # ==========================================
    # 🎯 核心修改：白色背景 & 中灰色坐标系
    # ==========================================
    
    # 定义新的颜色风格
    axis_line_color = "#AAAAAA" # 中灰色轴线
    split_line_color = "#DDDDDD" # 浅灰色网格
    background_color = "#FFFFFF" # 纯白背景
    axis_label_color = "#666666" # 深灰色标签文字

    # 通用的轴配置
    # 扩大坐标轴范围以容纳更大的图形
    axis_range = 80 
    axis_config = {
        "show": True, 
        "min": -axis_range, "max": axis_range, 
        "axisLine": {"lineStyle": {"color": axis_line_color, "width": 1.5}}, 
        "axisLabel": {"show": True, "textStyle": {"color": axis_label_color, "fontSize": 10, "fontFamily": "JetBrains Mono"}},
        "splitLine": {"show": True, "lineStyle": {"color": split_line_color, "width": 1, "type": "solid"}},
        "nameTextStyle": {"color": axis_label_color, "fontSize": 12, "fontWeight": "bold"}
    }

    option = {
        "backgroundColor": background_color, # 设置背景为白色
        "tooltip": { "show": True, "formatter": "{b}", "backgroundColor": "rgba(255,255,255,0.9)", "textStyle": {"color": "#333"}, "borderColor": "#EEE", "borderWidth": 1 },
        
        "xAxis3D": { **axis_config, "name": "X" },
        "yAxis3D": { **axis_config, "name": "Y" },
        "zAxis3D": { **axis_config, "name": "Z" },

        "grid3D": { 
            "boxWidth": 100, "boxDepth": 100, "boxHeight": 100, 
            "viewControl": { 
                "projection": 'perspective',
                "autoRotate": True, "autoRotateSpeed": 4,
                "distance": 150, # 调整视角
                "alpha": 25, "beta": 45,
                "minDistance": 100, "maxDistance": 250,
                "panMouseButton": 'left', "rotateMouseButton": 'right'
            }, 
            # 调整光照以适应白色背景，更明亮
            "light": { 
                "main": {"intensity": 1.5, "alpha": 40, "beta": 40}, 
                "ambient": {"intensity": 1.0} 
            }, 
            "environment": background_color,
            "splitLine": {"show": True, "lineStyle": {"color": split_line_color, "width": 1}}
        },
        "series": [{ 
            "type": 'scatter3D', "data": echarts_data, 
            "shading": 'lambert',
            # 调整粒子样式以适应白背景
            "itemStyle": {
                # 去掉发光效果，改为更实体的质感
                # "borderColor": "rgba(255,255,255,0.3)", 
                # "borderWidth": 0.5,
                # "shadowBlur": 8
            },
            "emphasis": { 
                "itemStyle": {"color": "#333", "opacity": 1, "borderColor": "#000", "borderWidth": 1},
                "label": {"show": True, "formatter": "{b}", "position": "top", "textStyle": {"color": "#fff", "backgroundColor": "#333", "padding": [2,4], "borderRadius": 2}}
            } 
        }]
    }
    st_echarts(options=option, height="550px")
    viz.render_spectrum_legend()
