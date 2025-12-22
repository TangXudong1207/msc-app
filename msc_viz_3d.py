### msc_viz_3d.py ###
import streamlit as st
import plotly.graph_objects as go
import json
import random
import msc_config as config
import msc_viz_core as core

# ==========================================
# 🎨 视觉辅助：色彩暗淡化算法
# ==========================================
def dim_color(hex_color, factor=0.4):
    """
    将鲜艳的 HEX 颜色变暗，模拟时间沉淀的效果。
    factor: 0~1，越小越暗
    """
    if not hex_color.startswith('#'): return "#333333"
    hex_color = hex_color.lstrip('#')
    try:
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        # 混合灰色背景 (RGB 20, 20, 20)
        r = int(r * factor + 20 * (1-factor))
        g = int(g * factor + 20 * (1-factor))
        b = int(b * factor + 20 * (1-factor))
        return '#{:02x}{:02x}{:02x}'.format(r, g, b)
    except: return "#333333"

# ==========================================
# 🌍 城市坐标库 (用于沉淀锚定)
# ==========================================
CITY_ANCHORS = {
    "China": [35.8617, 104.1954], "USA": [37.0902, -95.7129], 
    "UK": [55.3781, -3.4360], "Other": [0, 0],
    "Tokyo": [35.6762, 139.6503], "London": [51.5074, -0.1278],
    "New York": [40.7128, -74.0060], "Shanghai": [31.2304, 121.4737]
}

def get_sediment_location(node_data):
    """
    沉淀逻辑：尝试找回该节点的'根'（注册地），如果找不到则保持原位但锁死在地面
    """
    # 既然数据库目前没存每次节点的 IP，我们用一个简化的逻辑：
    # Active 的时候是随机漂浮的，Sediment 的时候回到一个固定的'家'。
    # 这里我们简单化：Sediment 依然使用原坐标，但视觉上'变重'。
    # 如果你想强行回到城市，需要去 users 表查这个用户的 country/city。
    # 为了视觉美感，我们让它就在原地下沉，变暗。
    
    loc = None
    try:
        if isinstance(node_data.get('location'), str): loc = json.loads(node_data['location'])
        elif isinstance(node_data.get('location'), dict): loc = node_data['location']
    except: pass
    
    if not loc or not loc.get('lat'):
        return core.get_random_coordinate() # 实在没有就随机丢海里
        
    return loc.get('lat'), loc.get('lon')

# ==========================================
# 🛰️ 伪3D 地球 (卫星漂浮版 v2.0)
# ==========================================
def render_3d_particle_map(nodes, current_user):
    if not nodes: 
        st.info("The universe is empty.")
        return

    # 分组容器
    # 1. 漂浮卫星 (Active Satellites) - 鲜亮，空心，大
    sat_lats, sat_lons, sat_colors, sat_texts = [], [], [], []
    
    # 2. 沉淀遗迹 (Sediment Dust) - 暗淡，实心，小
    sed_lats, sed_lons, sed_colors = [], [], []

    for node in nodes:
        # 获取基础颜色
        raw_color = core.get_spectrum_color(str(node.get('keywords', '')))
        mode = node.get('mode', 'Active')
        
        # 获取位置
        lat, lon = get_sediment_location(node)
        
        # --- 逻辑分流 ---
        if mode == 'Sediment':
            # 沉淀态：位置固定，颜色变暗
            sed_lats.append(lat)
            sed_lons.append(lon)
            sed_colors.append(dim_color(raw_color, factor=0.3)) # 变暗
            
        else:
            # 活跃态：像卫星一样漂浮
            # 为了模拟'漂浮'，我们在原始坐标上加一点微小的随机抖动，
            # 让它看起来不像是一个固定的地理点。
            jitter = 0.5 
            f_lat = lat + random.uniform(-jitter, jitter)
            f_lon = lon + random.uniform(-jitter, jitter)
            
            sat_lats.append(f_lat)
            sat_lons.append(f_lon)
            sat_colors.append(raw_color) # 保持原色
            
            # 构建 Hover 文本
            is_mine = (node['username'] == current_user)
            user_label = "ME" if is_mine else "SIGNAL"
            sat_texts.append(f"<b>[{user_label}]</b> {node['care_point']}<br><span style='color:#ccc'>{node.get('insight','')}</span>")

    fig = go.Figure()

    # --- Layer 1: 沉淀层 (Sediment) ---
    # 就像地表的尘埃，暗淡且密集
    if sed_lats:
        fig.add_trace(go.Scattergeo(
            lon=sed_lons, lat=sed_lats, mode='markers',
            marker=dict(
                size=3,               # 极小
                color=sed_colors, 
                opacity=0.5,          # 低透明度
                symbol='circle',      # 实心圆
            ),
            hoverinfo='skip',         # 沉淀物不显示信息，仅仅是背景
            name='Sediment'
        ))

    # --- Layer 2: 卫星层 (Satellites) ---
    # 正在发生的意义，悬浮于高空
    if sat_lats:
        fig.add_trace(go.Scattergeo(
            lon=sat_lons, lat=sat_lats, mode='markers',
            text=sat_texts, hoverinfo='text',
            marker=dict(
                size=10,                # 较大，模拟'近'
                color=sat_colors, 
                opacity=1.0, 
                symbol='diamond-open',  # 空心菱形 (线性风格)
                line=dict(width=1.5, color=sat_colors) # 自身颜色的描边
            ),
            name='Active Signals'
        ))

    # --- 视觉配置 ---
    fig.update_layout(
        geo=dict(
            scope='world', 
            projection_type='orthographic', # 3D 球体投影
            showland=True, landcolor='rgb(15, 15, 15)',   # 极黑陆地
            showocean=True, oceancolor='rgb(5, 5, 8)',    # 近乎黑色的海洋
            showlakes=False, 
            showcountries=True, countrycolor='rgb(30, 30, 30)', # 极淡的国界线
            showcoastlines=True, coastlinecolor='rgb(40, 40, 40)',
            projection_rotation=dict(lon=120, lat=20),
            bgcolor='rgba(0,0,0,0)' # 透明背景
        ),
        paper_bgcolor='rgba(0,0,0,0)', 
        margin={"r":0,"t":0,"l":0,"b":0}, 
        height=600, 
        showlegend=False # 隐藏图例，保持极简
    )
    st.plotly_chart(fig, use_container_width=True)

# 暂时保留 Galaxy 函数接口以免报错，虽然目前没用
def render_3d_galaxy(nodes):
    pass
