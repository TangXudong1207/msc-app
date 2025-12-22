### msc_viz_3d.py ###
import streamlit as st
import streamlit.components.v1 as components
import json
import random
import msc_config as config
import msc_viz_core as core

# ==========================================
# 🎨 视觉辅助
# ==========================================
def dim_color(hex_color, factor=0.5):
    """
    让颜色变得暗淡，用于沉淀物。
    """
    if not hex_color.startswith('#'): return "#444444"
    hex_color = hex_color.lstrip('#')
    try:
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        # 混合深色
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
        return '#{:02x}{:02x}{:02x}'.format(r, g, b)
    except: return "#444444"

def get_location_data(node_data):
    loc = None
    try:
        if isinstance(node_data.get('location'), str): loc = json.loads(node_data['location'])
        elif isinstance(node_data.get('location'), dict): loc = node_data['location']
    except: pass
    
    if not loc or not loc.get('lat'):
        return core.get_random_coordinate()
    return loc.get('lat'), loc.get('lon')

# ==========================================
# 🌌 WebGL 3D 渲染器 (Globe.gl - Starry Night Edition)
# ==========================================
def render_3d_particle_map(nodes, current_user):
    if not nodes:
        st.info("The universe is empty.")
        return

    points_data = [] # 静态点（沉淀+活跃）
    rings_data = []  # 动态波纹（仅限我的活跃点）
    
    for node in nodes:
        raw_color = core.get_spectrum_color(str(node.get('keywords', '')))
        mode = node.get('mode', 'Active')
        lat, lon = get_location_data(node)
        
        # --- 沉淀层 (城市微光) ---
        if mode == 'Sediment':
            points_data.append({
                "lat": lat, "lng": lon,
                "alt": 0.002,             # 紧贴地面
                "radius": 0.15,           # 极小的光点
                "color": dim_color(raw_color),
                "label": f"Sediment: {node['care_point']}"
            })
            
        # --- 活跃层 (漂浮卫星) ---
        else:
            # 随机漂浮高度 (0.1 ~ 0.35)
            # 地球半径是1，0.1 相当于离地表 600km，很有卫星感
            altitude = random.uniform(0.1, 0.35)
            
            # 基础卫星点
            points_data.append({
                "lat": lat, "lng": lon,
                "alt": altitude,
                "radius": 0.5,            # 明显的亮点 (之前太大了变成了柱子)
                "color": raw_color,
                "label": f"{node['care_point']}"
            })
            
            # 如果是当前用户，增加一个动态波纹圈
            if node['username'] == current_user:
                rings_data.append({
                    "lat": lat, "lng": lon,
                    "alt": altitude,      # 波纹也在空中
                    "color": raw_color,
                    "maxR": 5,            # 波纹扩散半径
                    "prop": 0.5           # 波纹速度
                })

    # 注入数据
    json_points = json.dumps(points_data)
    json_rings = json.dumps(rings_data)

    # 生成 HTML (强制黑色背景)
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style> 
            body {{ margin: 0; padding: 0; background-color: #000000; overflow: hidden; }} 
            #globeViz {{ width: 100vw; height: 100vh; }}
        </style>
        <script src="//unpkg.com/globe.gl"></script>
    </head>
    <body>
    <div id="globeViz"></div>
    <script>
        const pointsData = {json_points};
        const ringsData = {json_rings};
        
        const world = Globe()
            (document.getElementById('globeViz'))
            
            // 1. 核心外观：黑夜模式
            .globeImageUrl('//unpkg.com/three-globe/example/img/earth-night.jpg')
            .backgroundColor('#000000') // 强制纯黑背景
            .atmosphereColor('#4444ff') // 幽蓝大气层
            .atmosphereAltitude(0.2)
            
            // 2. 粒子层 (Points)
            .pointsData(pointsData)
            .pointAltitude('alt')    // 高度
            .pointColor('color')     // 颜色
            .pointRadius('radius')   // 半径 (已缩小，不会变成柱子了)
            .pointResolution(16)     // 圆度
            .pointLabel('label')
            
            // 3. 波纹层 (Rings - 仅我的节点)
            .ringsData(ringsData)
            .ringColor('color')
            .ringAltitude('alt')
            .ringMaxRadius('maxR')
            .ringPropagationSpeed('prop')
            .ringRepeatPeriod(800);  // 波纹频率

        // 4. 视角与控制
        world.controls().autoRotate = true;
        world.controls().autoRotateSpeed = 0.5;
        world.pointOfView({{ lat: 20, lng: 100, altitude: 2.2 }}); // 稍微拉远一点视角

    </script>
    </body>
    </html>
    """

    components.html(html_code, height=700, scrolling=False)

def render_3d_galaxy(nodes):
    pass
