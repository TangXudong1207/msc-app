### msc_viz_3d.py ###
import streamlit as st
import streamlit.components.v1 as components
import json
import random
import msc_config as config
import msc_viz_core as core

# ==========================================
# 🎨 色彩暗淡算法
# ==========================================
def dim_color(hex_color, factor=0.3):
    """
    让颜色变得暗淡、失去光泽，用于沉淀物。
    """
    if not hex_color.startswith('#'): return "#333333"
    hex_color = hex_color.lstrip('#')
    try:
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        # 向深灰色(30,30,30)靠拢，降低亮度
        r = int(r * factor + 30 * (1-factor))
        g = int(g * factor + 30 * (1-factor))
        b = int(b * factor + 30 * (1-factor))
        return '#{:02x}{:02x}{:02x}'.format(r, g, b)
    except: return "#333333"

# ==========================================
# 🌍 沉淀位置逻辑
# ==========================================
def get_location_data(node_data):
    loc = None
    try:
        if isinstance(node_data.get('location'), str): loc = json.loads(node_data['location'])
        elif isinstance(node_data.get('location'), dict): loc = node_data['location']
    except: pass
    
    # 如果没有位置，给一个随机经纬度
    if not loc or not loc.get('lat'):
        lat, lon = core.get_random_coordinate()
    else:
        lat, lon = loc.get('lat'), loc.get('lon')
        
    return lat, lon

# ==========================================
# 🌌 WebGL 3D 地球渲染器 (Globe.gl)
# ==========================================
def render_3d_particle_map(nodes, current_user):
    """
    使用 Globe.gl (Three.js) 生成真实的 3D 悬浮卫星视图。
    """
    if not nodes:
        st.info("The universe is empty.")
        return

    # 1. 准备数据 (Python -> JSON)
    viz_data = []
    
    for node in nodes:
        # 基础属性
        raw_color = core.get_spectrum_color(str(node.get('keywords', '')))
        mode = node.get('mode', 'Active')
        lat, lon = get_location_data(node)
        
        # 逻辑分流
        if mode == 'Sediment':
            # 沉淀物：贴地 (alt=0.01), 颜色暗淡, 尺寸小
            viz_data.append({
                "lat": lat, "lng": lon,
                "alt": 0.005,             # 紧贴地表
                "radius": 0.3,            # 很小
                "color": dim_color(raw_color),
                "label": f"Sediment: {node['care_point']}"
            })
        else:
            # 活跃卫星：悬浮 (alt > 0.1), 颜色鲜亮
            # 增加随机高度，制造层次感
            altitude = random.uniform(0.15, 0.45) 
            
            # 判断是否是自己
            if node['username'] == current_user:
                # 自己：更大，更高亮
                viz_data.append({
                    "lat": lat, "lng": lon,
                    "alt": altitude,
                    "radius": 1.5,        # 大尺寸
                    "color": raw_color,   # 原色
                    "label": f"ME: {node['care_point']}",
                    "isUser": True        # 标记，用于JS做特效
                })
            else:
                # 别人：正常尺寸
                viz_data.append({
                    "lat": lat, "lng": lon,
                    "alt": altitude,
                    "radius": 0.6,        # 中等尺寸
                    "color": raw_color,
                    "label": f"{node['care_point']}",
                    "isUser": False
                })

    # 将数据转为 JSON 字符串注入 HTML
    json_data = json.dumps(viz_data)

    # 2. 编写 HTML/JS (Globe.gl)
    # 使用 unpkg 加载库，确保无背景色
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style> body {{ margin: 0; padding: 0; overflow: hidden; background: transparent; }} </style>
        <script src="//unpkg.com/globe.gl"></script>
    </head>
    <body>
    <div id="globeViz"></div>
    <script>
        const data = {json_data};
        
        // 初始化地球
        const world = Globe()
            (document.getElementById('globeViz'))
            .backgroundColor('rgba(0,0,0,0)') // 关键：透明背景
            .globeImageUrl('//unpkg.com/three-globe/example/img/earth-night.jpg') // 夜景贴图
            .width(window.innerWidth)
            .height(650) // 高度适配
            
            // 粒子配置 (Points)
            .pointsData(data)
            .pointAltitude('alt')    // 绑定高度：实现漂浮
            .pointColor('color')     // 绑定颜色：实现光谱色
            .pointRadius('radius')   // 绑定大小：区分自己和他人
            .pointResolution(16)     // 粒子圆滑度
            .pointLabel('label')     // 鼠标悬停文字
            
            // 氛围光效
            .atmosphereColor('#3a228a')
            .atmosphereAltitude(0.15);

        // 设置更具戏剧性的视角 (Cyber-Zen Angle)
        world.pointOfView({{ lat: 20, lng: 100, altitude: 2.0 }});

        // 自动旋转 (慢速)
        world.controls().autoRotate = true;
        world.controls().autoRotateSpeed = 0.6;
        
        // 交互设置
        world.controls().enableZoom = true;
    </script>
    </body>
    </html>
    """

    # 3. 渲染组件
    # height 必须与 HTML 中的 height 匹配或略大
    components.html(html_code, height=660, scrolling=False)

# 保留接口
def render_3d_galaxy(nodes):
    pass
