### msc_viz_3d.py ###
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import json
import msc_config as config
import msc_viz_core as core # 引用核心库

# ==========================================
# 🌍 1. 伪3D 地球 (高光效版)
# ==========================================
def render_3d_particle_map(nodes, current_user):
    if not nodes: 
        st.info("The universe is empty.")
        return

    # 数据容器
    sig_lats, sig_lons, sig_colors, sig_texts = [], [], [], []
    glow_lats, glow_lons, glow_colors = [], [], []
    my_lats, my_lons, my_colors, my_texts = [], [], [], []
    sed_lats, sed_lons, sed_colors = [], [], []

    for node in nodes:
        # --- 位置解析 ---
        loc = None
        try:
            if isinstance(node.get('location'), str): loc = json.loads(node['location'])
            elif isinstance(node.get('location'), dict): loc = node['location']
        except: pass
        
        # 如果没有位置，随机飞在天上
        if not loc or not loc.get('lat'): 
            d_lat, d_lon = core.get_random_coordinate()
            loc = {"lat": d_lat, "lon": d_lon}

        lat, lon = loc.get('lat'), loc.get('lon')
        color = core.get_spectrum_color(str(node.get('keywords', '')))
        mode = node.get('mode', 'Active')

        # --- 分层逻辑 ---
        if mode == 'Sediment':
            sed_lats.append(lat); sed_lons.append(lon)
            sed_colors.append(color) 
        elif node['username'] == current_user:
            my_lats.append(lat); my_lons.append(lon)
            my_colors.append(color)
            my_texts.append(f"<b>{node['care_point']}</b><br><span style='font-size:0.8em; color:#ccc'>{node.get('insight','')}</span>")
        else:
            sig_lats.append(lat); sig_lons.append(lon)
            sig_colors.append(color)
            sig_texts.append(f"Signal: {node['care_point']}")
            # 光晕层
            glow_lats.append(lat); glow_lons.append(lon)
            glow_colors.append(color)

    fig = go.Figure()

    # --- Layer 1: 历史沉淀 ---
    if sed_lats:
        fig.add_trace(go.Scattergeo(
            lon=sed_lons, lat=sed_lats, mode='markers',
            marker=dict(size=2, color=sed_colors, opacity=0.3, symbol='circle'),
            hoverinfo='skip', name='Sediment'
        ))

    # --- Layer 2: 城市光晕 ---
    if glow_lats:
        fig.add_trace(go.Scattergeo(
            lon=glow_lons, lat=glow_lats, mode='markers',
            marker=dict(size=8, color=glow_colors, opacity=0.2, symbol='circle'),
            hoverinfo='skip', showlegend=False
        ))

    # --- Layer 3: 信号核心 ---
    if sig_lats:
        fig.add_trace(go.Scattergeo(
            lon=sig_lons, lat=sig_lats, mode='markers',
            text=sig_texts, hoverinfo='text',
            marker=dict(size=3, color=sig_colors, opacity=0.9, symbol='circle', line=dict(width=0)),
            name='Signals'
        ))

    # --- Layer 4: 我的卫星 ---
    if my_lats:
        fig.add_trace(go.Scattergeo(
            lon=my_lons, lat=my_lats, mode='markers',
            text=my_texts, hoverinfo='text',
            marker=dict(size=10, color=my_colors, opacity=1.0, symbol='diamond', line=dict(width=1, color='white')),
            name='My Orbit'
        ))

    # --- 视觉配置 ---
    fig.update_layout(
        geo=dict(
            scope='world', projection_type='orthographic',
            showland=True, landcolor='rgb(15, 15, 15)',
            showocean=True, oceancolor='rgb(5, 5, 10)',
            showlakes=False, showcountries=True, countrycolor='rgb(40, 40, 40)',
            showcoastlines=True, coastlinecolor='rgb(50, 50, 50)',
            projection_rotation=dict(lon=120, lat=20),
            showatmosphere=True, atmospherecolor='rgb(0, 30, 60)', atmospherewidth=5,
            bgcolor='black'
        ),
        paper_bgcolor='black', margin={"r":0,"t":0,"l":0,"b":0}, height=600, 
        showlegend=True, legend=dict(x=0, y=0, font=dict(color="#666"), bgcolor="rgba(0,0,0,0)", orientation="h")
    )
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 🌌 2. 星河 (Galaxy View)
# ==========================================
def render_3d_galaxy(nodes):
    if len(nodes) < 3: 
        st.info("🌌 星河汇聚中...")
        return
    df = core.compute_clusters(nodes, n_clusters=6)
    if df.empty: return
    df['size'] = 6
    fig = px.scatter_3d(
        df, x='x', y='y', z='z', 
        color='cluster', 
        color_continuous_scale=list(config.SPECTRUM.values()), 
        hover_name='care_point', 
        template="plotly_dark", opacity=0.9
    )
    fig.update_layout(
        scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False), bgcolor='black'), 
        paper_bgcolor="black", margin={"r":0,"t":0,"l":0,"b":0}, height=600, showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)
