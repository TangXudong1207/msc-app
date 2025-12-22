### msc_viz_3d.py ###
import streamlit as st
import streamlit.components.v1 as components
import json
import random
import msc_config as config
import msc_viz_core as core

def dim_color(hex_color, factor=0.5):
    if not hex_color.startswith('#'): return "#444444"
    hex_color = hex_color.lstrip('#')
    try:
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = int(r * factor); g = int(g * factor); b = int(b * factor)
        return '#{:02x}{:02x}{:02x}'.format(r, g, b)
    except: return "#444444"

def get_location_data(node_data):
    loc = None
    try:
        if isinstance(node_data.get('location'), str): loc = json.loads(node_data['location'])
        elif isinstance(node_data.get('location'), dict): loc = node_data['location']
    except: pass
    
    if not loc or not loc.get('lat'): return core.get_random_coordinate()
    return loc.get('lat'), loc.get('lon')

# ==========================================
# 🌌 WebGL 3D 渲染器 (Pure Sphere Edition)
# ==========================================
def render_3d_particle_map(nodes, current_user):
    if not nodes:
        st.info("The universe is empty.")
        return

    # 数据分流
    # 1. 地面点数据 (Ground Dots): 用于地幔和地面灯光
    ground_data = []
    
    # 2. 悬浮球数据 (Floating Spheres): 用于用户的漂浮卫星 (彻底消除巨塔感)
    satellite_data = []
    
    # 3. 波纹数据 (Rings): 仅限当前用户
    rings_data = []
    
    for node in nodes:
        raw_color = core.get_spectrum_color(str(node.get('keywords', '')))
        mode = node.get('mode', 'Active')
        lat, lon = get_location_data(node)
        
        # --- Layer 1 & 2: 沉淀与地面灯光 ---
        if mode == 'Sediment':
            # 沉淀：极暗，贴地
            ground_data.append({
                "lat": lat, "lng": lon,
                "alt": 0.0,              # 贴地
                "radius": 0.1,           # 极小
                "color": dim_color(raw_color, 0.4),
                "label": f"History: {node['care_point']}"
            })
        else:
            # 这里的"非我的活跃点"，我们也可以视为"地面灯光"
            if node['username'] != current_user:
                ground_data.append({
                    "lat": lat, "lng": lon,
                    "alt": 0.005,        # 微微离地
                    "radius": 0.25,      # 稍大
                    "color": raw_color,
                    "label": f"Light: {node['care_point']}"
                })
            
            # --- Layer 3: 我的漂浮卫星 (My Satellite) ---
            else:
                # 只有"我"的节点才是真正的悬浮卫星
                # 这样既突出了自我，也解决了满屏柱子的问题
                altitude = random.uniform(0.15, 0.4)
                
                satellite_data.append({
                    "lat": lat, "lng": lon,
                    "alt": altitude,
                    "radius": 0.4,       # 卫星大小
                    "color": raw_color,
                    "label": f"ME: {node['care_point']}"
                })
                
                # 增加波纹
                rings_data.append({
                    "lat": lat, "lng": lon,
                    "alt": altitude,
                    "color": raw_color,
                    "maxR": 6,
                    "prop": 0.4
                })

    json_ground = json.dumps(ground_data)
    json_sat = json.dumps(satellite_data)
    json_rings = json.dumps(rings_data)

    # HTML Generator
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style> body {{ margin: 0; background: #000; overflow: hidden; }} </style>
        <script src="//unpkg.com/globe.gl"></script>
        <!-- 引入 Three.js 用于渲染自定义球体 -->
        <script src="//unpkg.com/three"></script>
    </head>
    <body>
    <div id="globeViz"></div>
    <script>
        const groundData = {json_ground};
        const satData = {json_sat};
        const ringsData = {json_rings};
        
        const world = Globe()
            (document.getElementById('globeViz'))
            
            // 基础环境
            .globeImageUrl('//unpkg.com/three-globe/example/img/earth-night.jpg')
            .backgroundColor('#000000')
            .atmosphereColor('#2222ff')
            .atmosphereAltitude(0.15)
            
            // Layer 1 & 2: 地面点 (使用 pointsData，因为高度低，不会像塔)
            .pointsData(groundData)
            .pointAltitude('alt')
            .pointColor('color')
            .pointRadius('radius')
            .pointResolution(12)
            .pointLabel('label')
            
            // Layer 3: 悬浮卫星 (使用 customLayer 渲染纯粹的 Sphere)
            // 这是消除"巨塔"的关键：手动创建 Three.js Mesh，完全悬空
            .customLayerData(satData)
            .customThreeObject(d => {{
                // 创建一个发光球体
                const geometry = new THREE.SphereGeometry(d.radius * 2); // 放大一点视觉比例
                const material = new THREE.MeshLambertMaterial({{ color: d.color }});
                const sphere = new THREE.Mesh(geometry, material);
                
                // 提升位置到高度
                // Globe.gl 会自动处理经纬度位置，我们只需要处理高度
                // 但在 customLayer 中，我们需要把物体放到对应的 altitude 上
                
                // 更新：customThreeObjectUpdate 会处理位置
                // 这里只返回物体
                return sphere;
            }})
            .customThreeObjectUpdate((obj, d) => {{
                // 将经纬度+高度转换为 Three.js 坐标
                // world.getGlobeRadius() 获取地球半径
                const altitude = d.alt * 100 + 100; // 这里的单位转换需要根据库的比例
                
                // 简便方法：Globe.gl 会自动把 obj 放在经纬度表面。
                // 我们只需要沿法线方向(也就是现在的坐标方向)向外移动
                
                Object.assign(obj.position, world.getCoords(d.lat, d.lng, d.alt));
            }})
            
            // Layer 4: 波纹
            .ringsData(ringsData)
            .ringColor('color')
            .ringAltitude('alt')
            .ringMaxRadius('maxR')
            .ringPropagationSpeed('prop')
            .ringRepeatPeriod(1000);

        // 视角
        world.controls().autoRotate = true;
        world.controls().autoRotateSpeed = 0.4;
        world.pointOfView({{ lat: 20, lng: 100, altitude: 2.5 }});
    </script>
    </body>
    </html>
    """
    components.html(html_code, height=700, scrolling=False)

def render_3d_galaxy(nodes): pass
