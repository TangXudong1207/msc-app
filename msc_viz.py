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

# 🟢 已移除 render_spectrum_legend 函数，保持界面纯净
