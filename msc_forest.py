import streamlit as st
from streamlit_echarts import st_echarts
import random
import math
import numpy as np
import msc_viz as viz
import streamlit_antd_components as sac

# ==========================================
# 📐 0. 数学工具库 (Math Helpers)
# ==========================================
def jitter_points(points, intensity=1.0):
    """为点云添加随机噪点"""
    noisy_points = []
    for p in points:
        # 简单的正态分布噪音
        nx = p[0] + random.gauss(0, intensity)
        ny = p[1] + random.gauss(0, intensity)
        nz = p[2] + random.gauss(0, intensity)
        noisy_points.append([nx, ny, nz])
    return np.array(noisy_points)

def gen_helix_tube(n, turns=3, height=30, radius=5, tube_radius=2):
    """生成螺旋管状结构 (用于龙、树干)"""
    t = np.linspace(0, turns * 2 * np.pi, n)
    # 螺旋中心线
    x_c = radius * np.cos(t)
    y_c = radius * np.sin(t)
    z_c = np.linspace(-height/2, height/2, n)
    
    points = []
    for i in range(n):
        # 在中心线周围生成管壁粒子
        for _ in range(int(n/turns/5)): # 密度控制
            theta_tube = random.uniform(0, 2*math.pi)
            r_tube = random.uniform(0, tube_radius)
            # 简化的法向偏移 (不够严谨但视觉够用)
            x = x_c[i] + r_tube * np.cos(theta_tube) * np.cos(t[i])
            y = y_c[i] + r_tube * np.cos(theta_tube) * np.sin(t[i])
            z = z_c[i] + r_tube * np.sin(theta_tube)
            points.append([x, y, z])
    return np.array(points)

def gen_ellipsoid(n, a=10, b=5, c=5, center=(0,0,0)):
    """生成椭球体 (用于鲸鱼、猫身体)"""
    points = []
    for _ in range(n):
        theta = random.uniform(0, 2*math.pi)
        phi = random.uniform(0, math.pi)
        rad = random.uniform(0.8, 1.0) ** (1/3) # 稍微实心一点
        x = center[0] + a * rad * math.sin(phi) * math.cos(theta)
        y = center[1] + b * rad * math.sin(phi) * math.sin(theta)
        z = center[2] + c * rad * math.cos(phi)
        points.append([x, y, z])
    return np.array(points)

def gen_cone_layered(n, radius=15, height=30, layers=10):
    """生成分层圆锥体 (用于山峰)"""
    points = []
    points_per_layer = n // layers
    for i in range(layers):
        h_ratio = i / (layers - 1) # 0 to 1
        current_h = height * h_ratio - height/2
        current_r = radius * (1 - h_ratio)
        for _ in range(points_per_layer):
            theta = random.uniform(0, 2*math.pi)
            r = current_r * math.sqrt(random.uniform(0, 1))
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            z = current_h + random.uniform(-0.5, 0.5) # 层间微扰
            points.append([x, y, z])
    return np.array(points)

def gen_angled_planes(n, width=15, height=20, angle_deg=30):
    """生成成角度的两个平面 (用于书本)"""
    points = []
    angle_rad = math.radians(angle_deg)
    n_half = n // 2
    # 左页
    for _ in range(n_half):
        w_local = random.uniform(0, width)
        h_local = random.uniform(-height/2, height/2)
        # 绕Y轴旋转 -angle
        x = -w_local * math.cos(angle_rad)
        z = w_local * math.sin(angle_rad) + random.uniform(-0.5, 0.5) #书页厚度
        y = h_local
        points.append([x, y, z])
    # 右页
    for _ in range(n_half):
        w_local = random.uniform(0, width)
        h_local = random.uniform(-height/2, height/2)
        # 绕Y轴旋转 +angle
        x = w_local * math.cos(angle_rad)
        z = w_local * math.sin(angle_rad) + random.uniform(-0.5, 0.5)
        y = h_local
        points.append([x, y, z])
    return np.array(points)

# ==========================================
# 🐉 1. 基底形象生成器 (Primary Generators)
# ==========================================
def gen_dragon_form(n):
    # S形上升的身体
    body = gen_helix_tube(n=int(n*0.7), turns=2.5, height=40, radius=8, tube_radius=3)
    # 头部 (简单的球状聚集)
    head_center = body[-1] if len(body) > 0 else (0,0,20)
    head = gen_ellipsoid(n=int(n*0.2), a=5, b=4, c=4, center=head_center)
    # 爪子/须 (少量散点)
    claws = jitter_points(body[::20], intensity=4.0)
    return np.vstack([body, head, claws])

def gen_mountain_forest_form(n):
    # 主山峰
    mountain = gen_cone_layered(n=int(n*0.6), radius=20, height=35, layers=15)
    # 底部森林 (扁平的散点圆盘)
    forest_base = []
    base_z = -18
    for _ in range(int(n*0.4)):
        theta = random.uniform(0, 2*math.pi)
        r = random.uniform(15, 28) # 比山底更宽
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        z = base_z + random.uniform(0, 3) # 森林高度
        forest_base.append([x, y, z])
    return np.vstack([mountain, np.array(forest_base)])

def gen_whale_form(n):
    # 巨大的流线型身体
    body = gen_ellipsoid(n=int(n*0.8), a=25, b=8, c=10, center=(0,0,0))
    # 尾鳍 (扁平结构)
    tail_center = (-25, 0, 0)
    tail = gen_ellipsoid(n=int(n*0.2), a=2, b=10, c=6, center=tail_center)
    # 简单的旋转使尾巴看起来像尾巴
    tail[:, 0] += random.uniform(-2, 2, size=len(tail)) #稍微扭曲
    return np.vstack([body, tail])

def gen_cat_form(n):
    # 身体
    body = gen_ellipsoid(n=int(n*0.5), a=8, b=6, c=6, center=(0, -2, 0))
    # 头部 (较高位置)
    head = gen_ellipsoid(n=int(n*0.3), a=5, b=5, c=5, center=(0, 6, 4))
    # 双尾 (两条曲线)
    tail1 = gen_helix_tube(n=int(n*0.1), turns=1, height=15, radius=2, tube_radius=1)
    tail1[:, 1] -= 8 # 移到身后
    tail1[:, 0] += 3 # 偏左
    tail2 = gen_helix_tube(n=int(n*0.1), turns=1, height=15, radius=2, tube_radius=1)
    tail2[:, 1] -= 8
    tail2[:, 0] -= 3 # 偏右
    
    return np.vstack([body, head, tail1, tail2])

def gen_book_form(n):
    # 书页本体
    pages = gen_angled_planes(n=int(n*0.7), width=18, height=22, angle_deg=25)
    # 飘散的文字粒子 (从中心缝隙向上)
    words = []
    for _ in range(int(n*0.3)):
        x = random.gauss(0, 1) # 中心附近
        z = random.uniform(0, 5) # 缝隙深度
        y = random.uniform(0, 25) # 向上飘散的高度
        # 越高越散
        spread = y / 5.0
        x += random.uniform(-spread, spread)
        z += random.uniform(-spread, spread)
        words.append([x, y, z])
    return np.vstack([pages, np.array(words)])

def gen_gateway_form(n):
    # 两根柱子
    pillar_h = 30
    pillar_r = 3
    p1 = gen_helix_tube(n=int(n*0.4), turns=0.5, height=pillar_h, radius=1, tube_radius=pillar_r)
    p1[:, 0] -= 10 # 左柱
    p2 = gen_helix_tube(n=int(n*0.4), turns=0.5, height=pillar_h, radius=1, tube_radius=pillar_r)
    p2[:, 0] += 10 # 右柱
    
    # 顶部连接弧 (半圆散点)
    arch = []
    top_z = pillar_h / 2
    for _ in range(int(n*0.2)):
        theta = random.uniform(0, math.pi) # 半圆
        r_arch = 10 # 半径等于柱间距一半
        x = r_arch * math.cos(theta)
        z = r_arch * math.sin(theta) + top_z
        y = random.uniform(-2, 2) # 厚度
        arch.append([x, y, z])

    return np.vstack([p1, p2, np.array(arch)])

def gen_tree_form(n):
    # 主干
    trunk = gen_helix_tube(n=int(n*0.4), turns=0.5, height=25, radius=1, tube_radius=4)
    trunk[:, 2] -= 5 # 底部扎根
    
    # 几个主要分枝 (简化的粗糙实现)
    branches = []
    branch_pts = int(n*0.15)
    # 分枝1
    b1 = gen_helix_tube(n=branch_pts, turns=0.5, height=15, radius=1, tube_radius=2.5)
    # 简单的旋转和位移模拟分枝
    theta_b1 = math.radians(45)
    rot_mat = np.array([[math.cos(theta_b1), 0, math.sin(theta_b1)], [0, 1, 0], [-math.sin(theta_b1), 0, math.cos(theta_b1)]])
    b1 = b1.dot(rot_mat)
    b1[:, 2] += 10 # 移到树干中上部
    branches.append(b1)
    
    # 分枝2 (反向)
    b2 = gen_helix_tube(n=branch_pts, turns=0.5, height=15, radius=1, tube_radius=2.5)
    theta_b2 = math.radians(-45)
    rot_mat2 = np.array([[math.cos(theta_b2), 0, math.sin(theta_b2)], [0, 1, 0], [-math.sin(theta_b2), 0, math.cos(theta_b2)]])
    b2 = b2.dot(rot_mat2)
    b2[:, 2] += 12 
    branches.append(b2)
    
    # 树冠/花朵 (顶部散点)
    crown = []
    for _ in range(int(n*0.3)):
        p = random.choice(np.vstack(branches)) # 从分枝末端附近生成
        crown.append(jitter_points([p], intensity=5.0)[0])
        
    return np.vstack([trunk, *branches, np.array(crown)])

# ==========================================
# 🌪️ 2. 氛围特效应用器 (Secondary Aspects)
# ==========================================
def apply_thunder_aspect(points, intensity=1.5):
    """雷霆: 强烈的随机抖动，增加尖刺感"""
    return jitter_points(points, intensity=intensity)

def apply_foundation_aspect(points):
    """基石: 在底部增加一个稳定的环"""
    min_z = np.min(points[:, 2]) if len(points) > 0 else 0
    base_ring = []
    n_base = int(len(points) * 0.2)
    for _ in range(n_base):
        theta = random.uniform(0, 2*math.pi)
        r = random.uniform(18, 25)
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        z = min_z - 2 + random.uniform(0, 1)
        base_ring.append([x, y, z])
    return np.vstack([points, np.array(base_ring)])

def apply_warmth_aspect(points):
    """暖流: 应用柔和的正弦波扭曲"""
    warmed_points = []
    for p in points:
        # 基于高度Z应用简单的波动
        offset_x = math.sin(p[2] * 0.2) * 2.0
        offset_y = math.cos(p[2] * 0.2) * 2.0
        warmed_points.append([p[0]+offset_x, p[1]+offset_y, p[2]])
    return np.array(warmed_points)

def apply_stardust_aspect(points):
    """星尘: 在周围增加快速环绕的散点"""
    stardust = []
    n_star = int(len(points) * 0.3)
    for _ in range(n_star):
        theta = random.uniform(0, 2*math.pi)
        phi = random.uniform(0, math.pi)
        r = random.uniform(25, 35) # 较远轨道
        x = r * math.sin(phi) * math.cos(theta)
        y = r * math.sin(phi) * math.sin(theta)
        z = r * math.cos(phi)
        stardust.append([x, y, z])
    # 合并但让星尘看起来更散
    return np.vstack([points, jitter_points(np.array(stardust), intensity=2.0)])

def apply_abyss_aspect(points):
    """深渊: 使核心更致密，外部更稀疏 (向心收缩)"""
    abyss_points = []
    center = np.mean(points, axis=0) if len(points) > 0 else np.array([0,0,0])
    for p in points:
        vec = p - center
        dist = np.linalg.norm(vec)
        # 距离越远，收缩越少；距离近，收缩多。模拟深水压力。
        shrink_factor = 0.8 + (dist / 50.0) * 0.2 
        abyss_points.append(center + vec * shrink_factor)
    return np.array(abyss_points)

def apply_ascension_aspect(points):
    """升腾: 整体向上的趋势，顶部更散"""
    ascend_points = []
    for p in points:
        # Z轴越高，向上的偏移量越大
        z_bias = max(0, p[2] + 20) * 0.2 
        ascend_points.append([p[0], p[1], p[2] + z_bias])
    return jitter_points(np.array(ascend_points), intensity=0.5) # 加一点点抖动

def apply_prismatic_aspect(points):
    """幻彩: 不改变形状，只在数据结构中标记，在渲染时处理颜色"""
    # 这里只需返回原点集，颜色逻辑在 synthesize 中处理
    return points

# ==========================================
# 🧬 3. 核心合成逻辑 (Synthesizer)
# ==========================================
def synthesize_creature_data(radar, user_nodes):
    if not radar: radar = {"Care": 3.0, "Reflection": 3.0}
    # 1. 数据清洗与排序
    valid_keys = ["Care", "Curiosity", "Reflection", "Coherence", "Agency", "Aesthetic", "Transcendence"]
    clean_radar = {k: v for k, v in radar.items() if k in valid_keys}
    if not clean_radar: clean_radar = {"Care": 3.0, "Reflection": 3.0}
    
    sorted_attr = sorted(clean_radar.items(), key=lambda x: x[1], reverse=True)
    primary_attr = sorted_attr[0][0] if sorted_attr else "Care"
    secondary_attr = sorted_attr[1][0] if len(sorted_attr) > 1 else primary_attr

    # 2. 确定粒子数量基数
    base_count = max(800, len(user_nodes) * 5)

    # 3. 【核心】根据最高分选择基底形象生成器
    generator_map = {
        "Agency": gen_dragon_form,
        "Coherence": gen_mountain_forest_form,
        "Care": gen_whale_form,
        "Curiosity": gen_cat_form,
        "Reflection": gen_book_form,
        "Transcendence": gen_gateway_form,
        "Aesthetic": gen_tree_form
    }
    generator = generator_map.get(primary_attr, gen_whale_form) # 默认鲸鱼
    raw_points_np = generator(base_count)

    # 4. 【核心】根据第二高分应用氛围特效
    aspect_map = {
        "Agency": apply_thunder_aspect,
        "Coherence": apply_foundation_aspect,
        "Care": apply_warmth_aspect,
        "Curiosity": apply_stardust_aspect,
        "Reflection": apply_abyss_aspect,
        "Transcendence": apply_ascension_aspect,
        "Aesthetic": apply_prismatic_aspect
    }
    applicator = aspect_map.get(secondary_attr, lambda x: x) # 默认无特效
    processed_points_np = applicator(raw_points_np)
    
    # 转回列表以便后续处理
    final_points = processed_points_np.tolist()
    random.shuffle(final_points)

    # 5. 颜色与数据封装
    echarts_series_data = []
    # 颜色映射 (与 config.SPECTRUM 的主色调对应)
    c_map = {
        "Care": "#FF4081", "Agency": "#FFD700", "Reflection": "#536DFE",
        "Coherence": "#00CCFF", "Aesthetic": "#AB47BC", "Curiosity": "#00E676",
        "Transcendence": "#FFFFFF" # Transcendence 用白色/亮色
    }
    spirit_color = c_map.get(primary_attr, "#FFFFFF")
    is_prismatic = (secondary_attr == "Aesthetic")

    for i, pt in enumerate(final_points):
        # 颜色逻辑
        if is_prismatic:
            # 幻彩特效：基于点的位置生成彩虹色
            hue = (pt[0] + pt[1] + pt[2]) % 360
            # 这里简单模拟，ECharts不直接支持HSL，用几个预设彩色随机顶替
            prism_colors = ["#FF0000", "#FF7F00", "#FFFF00", "#00FF00", "#0000FF", "#4B0082", "#9400D3"]
            point_color = prism_colors[int(hue) % len(prism_colors)]
            opacity = 0.8
        else:
            point_color = spirit_color
            opacity = 0.4 # 默认半透明，更有灵体感

        # 内容映射逻辑 (将用户的真实节点嵌入粒子)
        if i < len(user_nodes):
            node = user_nodes[i]
            content_preview = node.get('care_point', 'Thought')
            full_content = node.get('content', '')
            # 节点粒子稍微大一点，不透明一点
            echarts_series_data.append({
                "name": content_preview, "value": pt,
                "itemStyle": {"color": point_color, "opacity": 1.0},
                "symbolSize": 4, "raw_content": full_content
            })
        else:
            # 结构粒子
            echarts_series_data.append({
                "name": "Spirit Particle", "value": pt,
                "itemStyle": {"color": point_color, "opacity": opacity},
                "symbolSize": 2, "raw_content": "Structure Essence"
            })
            
    return echarts_series_data, primary_attr, secondary_attr

# ==========================================
# 🌲 4. 渲染主程序 (Renderer)
# ==========================================
def render_forest_scene(radar_dict, user_nodes=None):
    if user_nodes is None: user_nodes = []
    
    echarts_data, p_attr, s_attr = synthesize_creature_data(radar_dict, user_nodes)
    
    lang = st.session_state.get('language', 'en')
    
    # 原型名称翻译
    ARCHETYPE_NAMES = {
        "Agency": {"en": "Ascending Dragon", "zh": "腾空之龙"},
        "Coherence": {"en": "Mountain & Forest", "zh": "高山森林"},
        "Care": {"en": "Celestial Whale", "zh": "天海之鲸"},
        "Curiosity": {"en": "Spirit Cat", "zh": "灵猫"},
        "Reflection": {"en": "Ancient Book", "zh": "智慧古书"},
        "Transcendence": {"en": "Gateway of Light", "zh": "光之门扉"},
        "Aesthetic": {"en": "Crystalline Tree", "zh": "结晶生命树"}
    }
    # 氛围名称翻译
    ASPECT_NAMES = {
        "Agency": {"en": "Thunder Aspect", "zh": "雷霆氛围"},
        "Coherence": {"en": "Foundation Aspect", "zh": "基石氛围"},
        "Care": {"en": "Warmth Aspect", "zh": "暖流氛围"},
        "Curiosity": {"en": "Stardust Aspect", "zh": "星尘氛围"},
        "Reflection": {"en": "Abyss Aspect", "zh": "深渊氛围"},
        "Transcendence": {"en": "Ascension Aspect", "zh": "升腾氛围"},
        "Aesthetic": {"en": "Prismatic Aspect", "zh": "幻彩氛围"}
    }

    p_name = ARCHETYPE_NAMES.get(p_attr, {}).get(lang, p_attr)
    s_name = ASPECT_NAMES.get(s_attr, {}).get(lang, s_attr)
    
    if len(user_nodes) < 3:
        creature_title = "Proto-Form" if lang=='en' else "初生形态"
        creature_desc = "Gathering meaning..." if lang=='en' else "意义汇聚中..."
    else:
        creature_title = p_name
        creature_desc = f"with {s_name}" if lang=='en' else f"伴随 {s_name}"

    label_title = "SOUL FORM" if lang=='en' else "灵魂形态"
    sac.divider(label=label_title, icon='layers', align='center', color='gray')
    st.markdown(f"<div style='text-align:center'><b>{creature_title}</b><br><span style='font-size:0.8em;color:gray'>{creature_desc}</span></div>", unsafe_allow_html=True)
    
    # ECharts 3D 配置 (保持深色背景以突出光感)
    grid_color = "#333333"; split_color = "#222222"
    option = {
        "backgroundColor": "transparent",
        "tooltip": { "show": True, "trigger": 'item', "formatter": "{b}" },
        "xAxis3D": { "show": False, "min": -40, "max": 40 }, # 隐藏坐标轴，固定范围
        "yAxis3D": { "show": False, "min": -40, "max": 40 },
        "zAxis3D": { "show": False, "min": -40, "max": 40 },
        "grid3D": { 
            "boxWidth": 120, "boxDepth": 120, "boxHeight": 120, 
            "viewControl": { 
                "projection": 'perspective', # 透视投影更有立体感
                "autoRotate": True, "autoRotateSpeed": 10, 
                "distance": 200, "alpha": 30, "beta": 40,
                "minDistance": 150, "maxDistance": 300
            }, 
            "light": { "main": {"intensity": 1.2}, "ambient": {"intensity": 0.8} }, 
            "environment": "#000000" # 纯黑环境背景
        },
        "series": [{ 
            "type": 'scatter3D', "data": echarts_data, 
            "shading": 'lambert', #更加真实的光照
            "emphasis": { "itemStyle": {"color": "#fff", "opacity": 1} } 
        }]
    }
    st_echarts(options=option, height="400px")
    viz.render_spectrum_legend()
