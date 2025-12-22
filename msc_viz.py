### msc_viz.py ###
import streamlit as st
import streamlit_antd_components as sac

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

# 🟢 修复：补回被误删的图例函数
def render_spectrum_legend():
    # 使用 sac 的 tag 组件来做极简图例
    legend_items = []
    
    # 只选几个核心维度展示，避免太乱
    CORE_DIMS = ["Rationality", "Vitality", "Empathy", "Mystery", "Void"]
    
    st.markdown("<div style='text-align:center; margin-top:10px; margin-bottom:10px;'>", unsafe_allow_html=True)
    
    # 手动用 HTML/CSS 渲染极简的小圆点图例
    html_parts = []
    for dim in CORE_DIMS:
        # 注意：这里做个容错，如果 config 里的 key 不完全匹配就跳过
        color = config.SPECTRUM.get(dim, "#888")
        # 如果找不到 Void，可能叫 Nihilism
        if dim == "Void": color = config.SPECTRUM.get("Nihilism", "#888")
            
        html_parts.append(
            f"<span style='margin: 0 10px; font-size: 0.8em; color: #666;'>"
            f"<span style='display:inline-block; width:8px; height:8px; border-radius:50%; background-color:{color}; margin-right:4px;'></span>"
            f"{dim}</span>"
        )
    
    st.markdown("".join(html_parts) + "</div>", unsafe_allow_html=True)
