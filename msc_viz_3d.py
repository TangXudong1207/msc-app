### msc_viz_3d.py ###
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import json
import msc_config as config
import msc_viz_core as core

# ==========================================
# 🌍 1. 伪3D 地球 (卫星漂浮版)
# ==========================================
def render_3d_particle_map(nodes, current_user):
    if not nodes: 
        st.info("The universe is empty.")
        return

    # 数据容器
    # 1. 地面层 (Lights) - 其他人的信号
    sig_lats, sig_lons, sig_colors, sig_texts = [], [], [], []
    
    # 2. 轨道层 (Satellites) - 我的信号
    my_lats, my_lons, my_colors, my_texts = [], [], [], []
    
    # 3. 沉淀层 (Sediment) - 过期信号
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
            # 这里的坐标其实是一样的，但我们将用样式把它“提”起来
            my_lats.append(lat); my_lons.append(lon)
            my_colors.append(color)
            my_texts.append(f"<b>{node['care_point']}</b><br><span style='font-size:0.8em; color:#ccc'>{node.get('insight','')}</span>")
        else:
            sig_lats.append(lat); sig_lons.append(lon)
            sig_colors.append(color)
            sig_texts.append(f"Signal: {node['care_point']}")

    fig = go.Figure()

    # --- Layer 1: 历史沉淀 (暗淡背景) ---
    if sed_lats:
        fig.add_trace(go.Scattergeo(
            lon=sed_lons, lat=sed_lats, mode='markers',
            marker=dict(size=2, color=sed_colors, opacity=0.2, symbol='circle'),
            hoverinfo='skip', name='Sediment'
        ))

    # --- Layer 2: 地面灯光 (City Lights) ---
    # 其他用户的节点：处理为发光点，半透明，贴地
    if sig_lats:
        fig.add_trace(go.Scattergeo(
            lon=sig_lons, lat=sig_lats, mode='markers',
            text=sig_texts, hoverinfo='text',
            marker=dict(
                size=5,             # 较小
                color=sig_colors, 
                opacity=0.6,        # 半透明
                symbol='circle',    # 圆点
                line=dict(width=0)  # 无边框，柔和
            ),
            name='Signals'
        ))

    # --- Layer 3: 轨道卫星 (Satellites) ---
    # 用户的节点：处理为高科技感的几何体，看起来像漂浮在上方
    if my_lats:
        fig.add_trace(go.Scattergeo(
            lon=my_lons, lat=my_lats, mode='markers',
            text=my_texts, hoverinfo='text',
            marker=dict(
                size=12,                # 很大，产生“近大远小”的错觉
                color=my_colors, 
                opacity=1.0, 
                symbol='diamond-open',  # 空心菱形，像瞄准框或卫星
                line=dict(width=2, color='white') # 强烈的白色边框，高亮
            ),
            name='My Orbit'
        ))

    # --- 视觉配置 ---
    fig.update_layout(
        geo=dict(
            scope='world', 
            projection_type='orthographic',
            showland=True, landcolor='rgb(10, 10, 10)',   # 极黑的陆地
            showocean=True, oceancolor='rgb(5, 5, 12)',   # 深蓝黑色海洋
            showlakes=False, 
            showcountries=True, countrycolor='rgb(30, 30, 30)', # 隐约的国界
            showcoastlines=True, coastlinecolor='rgb(40, 40, 50)',
            projection_rotation=dict(lon=120, lat=20),
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
