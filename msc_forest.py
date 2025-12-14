### msc_forest.py (ECharts 3D 纯净版：修复 JSON 序列化错误) ###

import streamlit as st
from streamlit_echarts import st_echarts
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
    
    rng = np.random.default_rng(seed=int(sum(radar_dict.values()) * 100))
    
    for y in range(size):
        for x in range(size):
            z = rng.uniform(0, 2)
            dist = ((x - size/2)**2 + (y - size/2)**2) ** 0.5
            
            if dist < size/2:
                z += (agency / 2.0) * (1 - dist/(size/2))
            
            z = z * (0.5 + coherence/20.0)
            
            if z < (empathy / 2.5):
                z = -1 * (empathy / 5.0) 
            
            data.append([x, y, round(z, 2)])
            
    return data

# ==========================================
# 🎨 渲染器：3D Bar Chart (VisualMap 版)
# ==========================================
def render_forest_scene(radar_dict):
    st.markdown("### 🏔️ Mind Topography")
    
    data = generate_heightmap(radar_dict, size=16)
    
    option = {
        "backgroundColor": "transparent",
        "tooltip": {},
        # === 修复点：使用 VisualMap 代替 JsCode ===
        # 根据 Z 轴 (高度) 自动映射颜色，无需 JS 函数
        "visualMap": {
            "show": False,
            "dimension": 2, # 绑定到 Z 轴
            "min": -5,
            "max": 10,
            "inRange": {
                # 这是一个从深海到雪山的渐变色带
                "color": [
                    '#0d47a1', # 深蓝 (深海)
                    '#2196f3', # 浅蓝 (浅海)
                    '#c8e6c9', # 浅绿 (平原)
                    '#2e7d32', # 深绿 (森林)
                    '#5d4037', # 褐色 (岩石)
                    '#eceff1'  # 白色 (雪顶)
                ]
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
            "label": {"show": False}
            # itemStyle 里的 color: JsCode 已经被删除了
        }]
    }
    
    st_echarts(options=option, height="350px")
    
    avg = sum(radar_dict.values()) / 7
    status = "Stable" if avg > 5 else "Unstable"
    st.caption(f"Terrain Status: **{status}** | Grid: 16x16")
