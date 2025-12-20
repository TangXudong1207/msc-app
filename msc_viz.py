### msc_viz.py ###
import streamlit as st
# 1. 导入核心算法
from msc_viz_core import (
    get_spectrum_color, 
    get_cluster_color, 
    compute_clusters
)

# 2. 导入 3D 地球与星河 (Plotly)
from msc_viz_3d import (
    render_3d_particle_map, 
    render_3d_galaxy
)

# 3. 导入 2D 图表与弹窗 (ECharts / Dialogs)
from msc_viz_graph import (
    render_radar_chart, 
    render_cyberpunk_map, 
    view_fullscreen_map, 
    view_radar_details
)

import msc_config as config

# ==========================================
# 🎨 通用组件：光谱图例 (Spectrum Legend)
# ==========================================
def render_spectrum_legend():
    """
    在当前位置渲染一个折叠的颜色说明板
    """
    lang = st.session_state.get('language', 'en')
    title = "🎨 SPECTRUM LEGEND" if lang == 'en' else "🎨 意义光谱解码"
    
    with st.expander(title, expanded=False):
        st.markdown("""
        <style>
            .legend-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
                gap: 10px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.8em;
            }
            .legend-item {
                display: flex;
                align-items: center;
                padding: 4px;
                background: #FAFAFA;
                border: 1px solid #EEE;
                border-radius: 4px;
            }
            .legend-dot {
                width: 12px; height: 12px; border-radius: 50%; margin-right: 8px;
                flex-shrink: 0;
            }
            .legend-text { color: #555; }
        </style>
        <div class='legend-grid'>
        """, unsafe_allow_html=True)
        
        # 遍历 16 色
        html_content = ""
        for name, color in config.SPECTRUM.items():
            # 简单的翻译映射 (可扩展)
            CN_MAP = {
                "Conflict": "冲突", "Hubris": "狂热", "Vitality": "生命力",
                "Rationality": "理性", "Structure": "建制", "Truth": "真理",
                "Curiosity": "好奇", "Mystery": "神秘",
                "Nihilism": "虚无", "Mortality": "死亡", "Consciousness": "觉知",
                "Empathy": "共情", "Heritage": "传承", "Melancholy": "忧郁",
                "Aesthetic": "美学", "Entropy": "熵"
            }
            display_name = name if lang == 'en' else CN_MAP.get(name, name)
            
            html_content += f"""
            <div class='legend-item'>
                <div class='legend-dot' style='background-color: {color};'></div>
                <div class='legend-text'>{display_name}</div>
            </div>
            """
            
        st.markdown(html_content + "</div>", unsafe_allow_html=True)
