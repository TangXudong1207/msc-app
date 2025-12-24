### msc_viz.py ###
import streamlit as st
import streamlit_antd_components as sac
import msc_transformer as trans 
import msc_config as config

# 注意这里的导入格式，不要漏掉逗号
from msc_viz_3d import (
    render_3d_particle_map, 
    render_3d_galaxy
)

from msc_viz_graph import (
    render_radar_chart, 
    render_cyberpunk_map, 
    view_fullscreen_map, 
    view_radar_details
)

def render_spectrum_legend():
    CORE_DIMS = ["Rationality", "Vitality", "Empathy", "Mystery", "Void"]
    st.markdown("<div style='text-align:center; margin-top:10px; margin-bottom:10px;'>", unsafe_allow_html=True)
    html_parts = []
    for dim in CORE_DIMS:
        color = config.SPECTRUM.get(dim, "#888")
        if dim == "Void": color = config.SPECTRUM.get("Nihilism", "#888")
        html_parts.append(
            f"<span style='margin: 0 10px; font-size: 0.8em; color: #666;'>"
            f"<span style='display:inline-block; width:8px; height:8px; border-radius:50%; background-color:{color}; margin-right:4px;'></span>"
            f"{dim}</span>"
        )
    st.markdown("".join(html_parts) + "</div>", unsafe_allow_html=True)
