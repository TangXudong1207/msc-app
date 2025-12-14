### msc_forest.py (ECharts 3D 修复版) ###

import streamlit as st
from streamlit_echarts import st_echarts, JsCode # <--- 关键修复：这里直接引用 JsCode
import random
import numpy as np

# ==========================================
# 🗺️ 核心算法：雷达转高度图
# ==========================================
def generate_heightmap(radar_dict, size=20):
    data = []
    agency = radar_dict.get("Agency", 3.0)
    empathy = radar_dict.get("Empathy", 3.0)
    coherence = radar_dict.get("Coherence", 3.0)
    
    # 随机种子保证地貌固定
    rng = np.random.default_rng(seed=int(sum(radar_dict.values()) * 100))
    
    for y in range(size):
        for x in range(size):
            z = rng.uniform(0, 2)
            dist = ((x - size/2)**2 + (y - size/2)**2) ** 0.5
            
            # Agency 造山
            if dist < size/2:
                z += (agency / 2.0) * (1 - dist/(size/2))
            
            # Coherence 平滑
            z = z * (0.5 + coherence/20.0)
            
            # Empathy 造海
            if z < (empathy / 2.5):
                z = -1 * (empathy / 5.0) 
            
            data.append([x, y, round(z, 2)])
            
    return data

# ==========================================
# 🎨 渲染器：3D Bar Chart
# ==========================================
def render_forest_scene(radar_dict):
    st.markdown("### 🏔️ Mind Topography")
    
    data = generate_heightmap(radar_dict, size=16)
    
    # JS 颜色逻辑：根据高度上色
    color_logic = """
    function(params) {
        var z = params.value[2];
        if (z < 0) return '#0d47a1';       // 深海
        if (z < 1) return '#2196f3';       // 浅海
        if (z < 3) return '#c8e6c9';       // 平原
        if (z < 5) return '#2e7d32';       // 森林
        if (z < 7) return '#5d4037';       // 岩石
        return '#eceff1';                  // 雪顶
    }
    """
    
    option = {
        "backgroundColor": "transparent",
        "tooltip": {},
        "visualMap": {
            "show": False,
            "min": -5,
            "max": 10,
            "inRange": {
                "color": ['#0d47a1', '#2196f3', '#c8e6c9', '#2e7d32', '#5d4037', '#eceff1']
            }
        },
        "xAxis3D": {"type": 'category', "show": False},
        "yAxis3D": {"type": 'category', "show": False},
        "zAxis3D": {"type": 'value', "show": False, "min": -5, "max": 12},
        "grid3D": {
            "boxWidth": 200,
            "boxDepth": 200,
            "boxHeight": 80,
            "viewControl": {
                "projection": 'orthographic',
                "autoRotate": True,
                "autoRotateSpeed": 10,
                "alpha": 45,
                "beta": 30
            },
            "light": {
                "main": {"intensity": 1.2, "shadow": True},
                "ambient": {"intensity": 0.3}
            }
        },
        "series": [{
            "type": 'bar3D',
            "data": data,
            "shading": 'lambert',
            "label": {"show": False},
            "itemStyle": {
                "color":  JsCode(color_logic) # 现在这里认识 JsCode 了
            }
        }]
    }
    
    st_echarts(options=option, height="350px")
    
    avg = sum(radar_dict.values()) / 7
    status = "Stable" if avg > 5 else "Unstable"
    st.caption(f"Terrain Status: **{status}** | Grid: 16x16")
