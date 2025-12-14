### msc_forest.py ###

import streamlit as st
from streamlit_echarts import st_echarts
import random
import numpy as np

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
            
            if dist < size/2: z += (agency / 2.0) * (1 - dist/(size/2))
            z = z * (0.5 + coherence/20.0)
            if z < (empathy / 2.5): z = -1 * (empathy / 5.0) 
            
            data.append([x, y, round(z, 2)])
    return data

def render_forest_scene(radar_dict):
    st.markdown("### 🏔️ Mind Topography")
    data = generate_heightmap(radar_dict, size=16)
    
    option = {
        "backgroundColor": "transparent",
        "visualMap": {
            "show": False, "dimension": 2, "min": -5, "max": 10,
            "inRange": {"color": ['#0d47a1', '#2196f3', '#c8e6c9', '#2e7d32', '#5d4037', '#eceff1']}
        },
        "xAxis3D": {"type": 'category', "show": False},
        "yAxis3D": {"type": 'category', "show": False},
        "zAxis3D": {"type": 'value', "show": False},
        "grid3D": {
            "boxHeight": 80,
            "viewControl": {"autoRotate": True, "alpha": 45, "beta": 30},
            "light": {"main": {"intensity": 1.2, "shadow": True}, "ambient": {"intensity": 0.3}}
        },
        "series": [{"type": 'bar3D', "data": data, "shading": 'lambert'}]
    }
    
    st_echarts(options=option, height="350px")
    avg = sum(radar_dict.values()) / 7
    status = "Stable" if avg > 5 else "Unstable"
    st.caption(f"Terrain Status: **{status}**")
