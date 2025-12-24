### msc_viz_3d.py ###
import streamlit as st
import streamlit.components.v1 as components
import json
import random
import msc_config as config
import msc_transformer as trans

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
    
    if not loc or not loc.get('lat'): return trans.get_random_coordinate()
    return loc.get('lat'), loc.get('lon')

def render_3d_particle_map(nodes, current_user):
    if not nodes:
        st.info("The universe is empty.")
        return

    ground_data = []
    satellite_data = []
    rings_data = []
    
    for node in nodes:
        raw_color = trans.get_spectrum_color(str(node.get('keywords', '')))
        mode = node.get('mode', 'Active')
        lat, lon = get_location_data(node)
        
        if mode == 'Sediment':
            ground_data.append({
                "lat": lat, "lng": lon, "alt": 0.0, "radius": 0.2,
                "color": dim_color(raw_color, 0.4), "label": f"History: {node['care_point']}"
            })
        else:
            if node['username'] != current_user:
                ground_data.append({
                    "lat": lat, "lng": lon, "alt": 0.005, "radius": 0.6,
                    "color": raw_color, "label": f"Light: {node['care_point']}"
                })
            else:
                altitude = random.uniform(0.15, 0.4)
                satellite_data.append({
                    "lat": lat, "lng": lon, "alt": altitude, "radius": 0.6,
                    "color": raw_color, "label": f"ME: {node['care_point']}"
                })
                rings_data.append({
                    "lat": lat, "lng": lon, "alt": altitude, "color": raw_color,
                    "maxR": 3, "prop": 0.4
                })

    json_ground = json.dumps(ground_data)
    json_sat = json.dumps(satellite_data)
    json_rings = json.dumps(rings_data)

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style> body {{ margin: 0; background: #000; overflow: hidden; }} </style>
        <script src="//unpkg.com/globe.gl"></script>
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
            .globeImageUrl('//unpkg.com/three-globe/example/img/earth-night.jpg')
            .backgroundColor('#000000')
            .atmosphereColor('#2222ff')
            .atmosphereAltitude(0.15)
            .pointsData(groundData)
            .pointAltitude('alt')
            .pointColor('color')
            .pointRadius('radius')
            .pointResolution(12)
            .pointLabel('label')
            .customLayerData(satData)
            .customThreeObject(d => {{
                const geometry = new THREE.SphereGeometry(d.radius * 2); 
                const material = new THREE.MeshLambertMaterial({{ color: d.color }});
                return new THREE.Mesh(geometry, material);
            }})
            .customThreeObjectUpdate((obj, d) => {{
                Object.assign(obj.position, world.getCoords(d.lat, d.lng, d.alt));
            }})
            .ringsData(ringsData)
            .ringColor('color')
            .ringAltitude('alt')
            .ringMaxRadius('maxR')
            .ringPropagationSpeed('prop')
            .ringRepeatPeriod(1000);

        world.controls().autoRotate = true;
        world.controls().autoRotateSpeed = 0.4;
        world.pointOfView({{ lat: 20, lng: 100, altitude: 2.5 }});
    </script>
    </body>
    </html>
    """
    components.html(html_code, height=700, scrolling=False)

def render_3d_galaxy(nodes): pass
2. 修复 msc_viz.py (确保导入语句正确)
有时候 Python 的括号换行如果不小心删了逗号，就会报错 SyntaxError。

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
