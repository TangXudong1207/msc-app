### msc_viz_3d.py ###
import streamlit as st
import streamlit.components.v1 as components
import json
import random
import msc_config as config
import msc_transformer as trans # <--- 变动在这里

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
    
    # 使用新文件的方法
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
        # 使用新文件的方法
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
                const sphere = new THREE.Mesh(geometry, material);
                return sphere;
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
4. [修改] msc_viz_graph.py
变动： 引用 msc_transformer 替代 msc_viz_core。

### msc_viz_graph.py ###
import streamlit as st
from streamlit_echarts import st_echarts
import json
import msc_transformer as trans # <--- 变动在这里
import msc_lib as msc 

# ==========================================
# 🕸️ 1. 雷达图 (Radar)
# ==========================================
def render_radar_chart(radar_dict, height="200px"):
    keys = ["Care", "Curiosity", "Reflection", "Coherence", "Agency", "Aesthetic", "Transcendence"]
    safe_scores = []
    for k in keys:
        safe_scores.append(radar_dict.get(k, 3.0))

    option = {
        "backgroundColor": "transparent", 
        "radar": {
            "indicator": [{"name": k, "max": 10} for k in keys], 
            "splitArea": {"show": False}
        }, 
        "series": [{
            "type": "radar", 
            "data": [{
                "value": safe_scores, 
                "areaStyle": {"color": "rgba(255, 75, 75, 0.4)"}, 
                "lineStyle": {"color": "#FF4B4B"}
            }]
        }]
    }
    st_echarts(options=option, height=height)

# ==========================================
# 🔮 2. 赛博朋克关系图 (Network Graph)
# ==========================================
def render_cyberpunk_map(nodes, height="250px", is_fullscreen=False, key_suffix="map"):
    if not nodes: return None
    
    # 使用新文件的方法
    cluster_df = trans.compute_clusters(nodes, n_clusters=5)
    id_to_color = {}
    default_color = "#00fff2"
    
    if not cluster_df.empty:
        for i, color in enumerate(cluster_df['color']):
            if i < len(nodes): id_to_color[str(nodes[i]['id'])] = color

    graph_nodes, graph_links = [], []
    symbol_base = 30 if is_fullscreen else 15
    
    for i, node in enumerate(nodes):
        logic = node.get('logic_score') or 0.5
        nid = str(node['id'])
        node_color = id_to_color.get(nid, default_color)
        label_text = node['care_point']
        if len(label_text) > 6: label_text = label_text[:5] + "..."

        graph_nodes.append({
            "name": nid, "id": nid, "symbolSize": symbol_base * (0.8 + logic),
            "value": node['care_point'], 
            "label": {"show": is_fullscreen, "formatter": label_text, "color": "#fff", "fontSize": 10},
            "full_data": {
                "insight": node.get('insight', ''), "content": node['content'], 
                "layer": node.get('meaning_layer', ''), "username": node['username']
            },
            "itemStyle": {"color": node_color}
        })

    node_count = len(graph_nodes)
    start_idx = max(0, node_count - 50)
    for i in range(start_idx, node_count):
        for j in range(i + 1, node_count):
            na, nb = graph_nodes[i], graph_nodes[j]
            graph_links.append({
                "source": na['name'], "target": nb['name'], 
                "lineStyle": {"width": 1, "color": "#555", "curveness": 0.2, "opacity": 0.3}
            })

    option = {
        "backgroundColor": "#0e1117", 
        "tooltip": {"formatter": "{b}"}, 
        "series": [{
            "type": "graph", "layout": "force", "data": graph_nodes, "links": graph_links, "roam": True, 
            "force": {"repulsion": 800 if is_fullscreen else 200, "gravity": 0.1, "edgeLength": 50}, 
            "itemStyle": {"shadowBlur": 10}, "lineStyle": {"color": "source", "curveness": 0.2}
        }]
    }
    
    events = {"click": "function(params) { return params.name }"}
    clicked_id = st_echarts(options=option, height=height, events=events, key=f"echart_{key_suffix}")
    
    if clicked_id:
        target_node = next((n for n in graph_nodes if n['name'] == clicked_id), None)
        if target_node: return target_node['full_data']
    return None

# ==========================================
# 🔭 3. 弹窗组件 (Dialogs)
# ==========================================
@st.dialog("🔭 小宇宙 (Microcosm)", width="large")
def view_fullscreen_map(nodes, user_name):
    import msc_viz as viz_facade
    
    lang = st.session_state.get('language', 'en')
    title = f"{user_name}'s Microcosm" if lang == 'en' else f"{user_name} 的小宇宙"
    st.markdown(f"### 🌌 {title}")
    
    clicked_data = render_cyberpunk_map(nodes, height="500px", is_fullscreen=True, key_suffix="fullscreen_dlg")
    
    if clicked_data:
        st.divider()
        st.markdown(f"#### ✨ {clicked_data.get('layer', 'Selected Node')}")
        c1, c2 = st.columns([0.7, 0.3])
        with c1:
            st.info(f"**Insight:** {clicked_data['insight']}")
            st.caption(f"> \"{clicked_data['content']}\"")
        with c2:
            if st.button("📍 Locate", use_container_width=True): st.toast("Time travel initiated...", icon="⏳")
    
    st.divider()
    viz_facade.render_spectrum_legend()

@st.dialog("🧬 MSC 深度基因解码", width="large")
def view_radar_details(radar_dict, username):
    c1, c2 = st.columns([1, 1])
    with c1: render_radar_chart(radar_dict, height="350px")
    with c2:
        st.markdown(f"### {username} 的核心参数")
        required_keys = ["Care", "Curiosity", "Reflection", "Coherence", "Agency", "Aesthetic", "Transcendence"]
        for key in required_keys:
            val = radar_dict.get(key, 3.0)
            st.progress(val / 10, text=f"**{key}**: {val}")
            
    st.divider()
    report_key = f"report_{username}_{sum(radar_dict.values())}"
    if report_key not in st.session_state:
        with st.spinner("Analyzing..."):
            report = msc.analyze_persona_report(radar_dict)
            st.session_state[report_key] = report
    report = st.session_state[report_key]
    with st.container(border=True):
        st.markdown("#### 🌊 现状 · Status Quo")
        st.info(report.get("status_quo", "分析中..."))
    with st.container(border=True):
        st.markdown("#### 🌱 成长 · Evolution")
        st.success(report.get("growth_path", "分析中..."))
