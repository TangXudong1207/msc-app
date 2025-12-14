### msc_forest.py (ECharts 3D 地形版) ###

import streamlit as st
from streamlit_echarts import st_echarts
import random
import numpy as np

# ==========================================
# 🗺️ 核心算法：雷达转高度图 (Radar to Heightmap)
# ==========================================
def generate_heightmap(radar_dict, size=20):
    """
    将7维雷达数据，转化为 20x20 的高度矩阵 (x, y, z)
    """
    data = []
    
    # 提取核心参数作为地形因子
    agency = radar_dict.get("Agency", 3.0)     # 山峰高度
    empathy = radar_dict.get("Empathy", 3.0)   # 水位线 (负高度)
    coherence = radar_dict.get("Coherence", 3.0) # 地形平滑度
    
    # 随机种子，保证同一个人的地形是固定的
    rng = np.random.default_rng(seed=int(sum(radar_dict.values()) * 100))
    
    for y in range(size):
        for x in range(size):
            # 1. 基础高度 (Base Noise)
            z = rng.uniform(0, 2)
            
            # 2. 造山运动 (Agency)
            # 距离中心越近，受 Agency 影响越大
            dist = ((x - size/2)**2 + (y - size/2)**2) ** 0.5
            if dist < size/2:
                z += (agency / 2.0) * (1 - dist/(size/2))
            
            # 3. 侵蚀作用 (Coherence)
            # Coherence 越高，地形越平滑；越低越破碎
            z = z * (0.5 + coherence/20.0)
            
            # 4. 水位切割 (Empathy)
            # Empathy 越高，低地越容易变成深海
            if z < (empathy / 2.5):
                z = -1 * (empathy / 5.0) # 变成负值，表示水下
            
            # 格式化为 ECharts 需要的 [x, y, z]
            data.append([x, y, round(z, 2)])
            
    return data

# ==========================================
# 🎨 渲染器：3D Bar Chart (伪装成像素地形)
# ==========================================
def render_forest_scene(radar_dict):
    st.markdown("### 🏔️ Mind Topography")
    
    data = generate_heightmap(radar_dict, size=16)
    
    # 动态配色逻辑
    # 根据 Z 轴高度决定颜色 (模拟海拔)
    color_logic = """
    function(params) {
        var z = params.value[2];
        if (z < 0) return '#0d47a1';       // 深海 (Deep Ocean)
        if (z < 1) return '#2196f3';       // 浅海 (Shallow Water)
        if (z < 3) return '#c8e6c9';       // 沙滩/平原 (Sand/Plains)
        if (z < 5) return '#2e7d32';       // 森林 (Forest)
        if (z < 7) return '#5d4037';       // 岩石 (Rock)
        return '#eceff1';                  // 雪顶 (Snow)
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
                # 备用渐变色，虽然主要靠上面的 function
                "color": ['#0d47a1', '#2196f3', '#c8e6c9', '#2e7d32', '#5d4037', '#eceff1']
            }
        },
        "xAxis3D": {"type": 'category', "show": False},
        "yAxis3D": {"type": 'category', "show": False},
        "zAxis3D": {"type": 'value', "show": False, "min": -5, "max": 12},
        "grid3D": {
            "boxWidth": 200,
            "boxDepth": 200,
            "boxHeight": 80, # 压扁一点，更有地图感
            "viewControl": {
                "projection": 'orthographic', # 等轴视图 (Isometric)
                "autoRotate": True,           # 自动旋转展示
                "autoRotateSpeed": 10,
                "alpha": 45,                  # 俯视角度
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
            "shading": 'lambert', # 真实光影渲染
            "label": {"show": False},
            "itemStyle": {
                "color":  JsCode(color_logic) # 使用 JS 代码动态上色
            }
        }]
    }
    
    # 渲染图表
    # 注意：需要引入 JsCode 才能让颜色函数生效
    from streamlit_echarts import JsCode
    st_echarts(options=option, height="350px")
    
    # 底部状态栏
    avg = sum(radar_dict.values()) / 7
    status = "Stable" if avg > 5 else "Unstable"
    st.caption(f"Terrain Status: **{status}** | Grid: 16x16")
