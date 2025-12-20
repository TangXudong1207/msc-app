import streamlit as st
from streamlit_echarts import st_echarts
import random
import math
import numpy as np
import msc_viz as viz
import streamlit_antd_components as sac

# ==========================================
# 🌫️ 0. 数学与场域工具 (Math & Field Helpers)
# ==========================================
def get_random_point_in_sphere(radius):
    """在球体内生成一个随机点 (用于迷雾)"""
    u = random.random()
    v = random.random()
    theta = u * 2.0 * math.pi
    phi = math.acos(2.0 * v - 1.0)
    r = radius * math.cbrt(random.random())
    sin_phi = math.sin(phi)
    x = r * sin_phi * math.cos(theta)
    y = r * sin_phi * math.sin(theta)
    z = r * math.cos(phi)
    return np.array([x, y, z])

def jitter_vec(vec, intensity=1.0):
    """向量加噪"""
    return vec + np.random.normal(0, intensity, 3)

def gen_flow_curve(start_pt, end_pt, control_pt, n_points, jitter=0.5):
    """生成一条带有噪点的贝塞尔流动曲线 (用于尾巴、身体流线)"""
    t = np.linspace(0, 1, n_points)
    # 二阶贝塞尔曲线公式
    curve = (1-t)**2 * start_pt[:, None] + 2*(1-t)*t * control_pt[:, None] + t**2 * end_pt[:, None]
    curve = curve.T
    # 添加噪点，两端少，中间多
    noise_scale = np.sin(t * math.pi) * jitter
    noise = np.random.normal(0, 1, (n_points, 3)) * noise_scale[:, None]
    return curve + noise

def gen_ethereal_cloud(center, n_points, radius_x, radius_y, radius_z, core_density=0.6):
    """生成虚无的椭球云雾 (用于身体主体)"""
    points = []
    for _ in range(n_points):
        # 使用高斯分布，让粒子集中在核心，边缘稀疏
        x = random.gauss(0, radius_x * core_density)
        y = random.gauss(0, radius_y * core_density)
        z = random.gauss(0, radius_z * core_density)
        points.append(np.array(center) + np.array([x, y, z]))
    return np.array(points)

# ==========================================
# 🐉 1. 灵性基底生成器 (Ethereal Generators)
# ==========================================

def gen_spirit_cat(n):
    """灵猫：由能量流和迷雾构成的灵体"""
    # 1. 身体迷雾 (Ethereal Body Cloud)
    # 不再是实体椭球，而是一团拉长的能量云
    body_pts = gen_ethereal_cloud(center=(0, 0, 0), n_points=int(n*0.4), 
                                  radius_x=8, radius_y=4, radius_z=4, core_density=0.5)
    
    # 2. 头部能量团 (Head Energy Orb)
    head_pts = gen_ethereal_cloud(center=(8, 0, 2), n_points=int(n*0.15),
                                  radius_x=3, radius_y=3, radius_z=3, core_density=0.4)
    
    # 3. 灵动双尾 (Flowing Twin Tails)
    # 使用贝塞尔曲线生成流动的粒子束，而非管道
    tail_start = np.array([-6, 0, 1])
    
    # 尾巴1：向左后方飘动
    t1_end = np.array([-20, 8, 5])
    t1_ctrl = np.array([-12, 15, 10])
    tail1_pts = gen_flow_curve(tail_start, t1_end, t1_ctrl, n_points=int(n*0.15), jitter=1.5)

    # 尾巴2：向右后方飘动
    t2_end = np.array([-20, -8, 2])
    t2_ctrl = np.array([-12, -15, -5])
    tail2_pts = gen_flow_curve(tail_start, t2_end, t2_ctrl, n_points=int(n*0.15), jitter=1.5)
    
    # 4. 基础环绕场 (Base Aura Field)
    # 在整体周围生成非常稀疏的大范围粒子
    aura_pts = []
    for _ in range(int(n*0.15)):
        pt = get_random_point_in_sphere(radius=25)
        # 将其压扁一点，使其更有环绕感
        pt[2] *= 0.6
        aura_pts.append(pt)
        
    return np.vstack([body_pts, head_pts, tail1_pts, tail2_pts, np.array(aura_pts)])

# (其他生物的生成函数占位，逻辑类似，重点是"虚无感")
def gen_dragon_form(n): return gen_ethereal_cloud((0,0,0), n, 20, 5, 5) # 占位
def gen_mountain_forest_form(n): return gen_ethereal_cloud((0,0,0), n, 15, 15, 20) # 占位
def gen_whale_form(n): return gen_ethereal_cloud((0,0,0), n, 25, 8, 10) # 占位
def gen_book_form(n): return gen_ethereal_cloud((0,0,0), n, 10, 2, 8) # 占位
def gen_gateway_form(n): return gen_ethereal_cloud((0,0,0), n, 5, 15, 20) # 占位
def gen_tree_form(n): return gen_ethereal_cloud((0,0,0), n, 8, 8, 25) # 占位

# ==========================================
# 🌪️ 2. 氛围特效应用器 (Aspect Applicators)
# ==========================================
# (特效函数保持不变，它们在这个新的粒子基础上效果会更好)
def apply_thunder_aspect(points): return jitter_vec(points, intensity=1.5)
def apply_foundation_aspect(points): 
    # ... (保持原有逻辑，篇幅原因省略，下同)
    return points 
def apply_warmth_aspect(points): return points
def apply_stardust_aspect(points): 
    # 星尘特效在稀疏粒子上会更明显
    stardust = []
    n_star = int(len(points) * 0.3)
    for _ in range(n_star):
        theta = random.uniform(0, 2*math.pi)
        phi = random.uniform(0, math.pi)
        r = random.uniform(25, 40) # 更远的轨道
        x = r * math.sin(phi) * math.cos(theta)
        y = r * math.sin(phi) * math.sin(theta)
        z = r * math.cos(phi)
        stardust.append([x, y, z])
    return np.vstack([points, jitter_vec(np.array(stardust), intensity=1.0)])
def apply_abyss_aspect(points): return points
def apply_ascension_aspect(points): return points
def apply_prismatic_aspect(points): return points

# ==========================================
# 🧬 3. 核心合成逻辑 (Synthesizer)
# ==========================================
def synthesize_creature_data(radar, user_nodes):
    # ... (保持原有数据处理逻辑)
    if not radar: radar = {"Care": 3.0, "Reflection": 3.0}
    valid_keys = ["Care", "Curiosity", "Reflection", "Coherence", "Agency", "Aesthetic", "Transcendence"]
    clean_radar = {k: v for k, v in radar.items() if k in valid_keys}
    if not clean_radar: clean_radar = {"Care": 3.0, "Reflection": 3.0}
    
    sorted_attr = sorted(clean_radar.items(), key=lambda x: x[1], reverse=True)
    primary_attr = sorted_attr[0][0] if sorted_attr else "Care"
    secondary_attr = sorted_attr[1][0] if len(sorted_attr) > 1 else primary_attr

    # 粒子数量稍微减少，以增加稀疏感
    base_count = max(500, len(user_nodes) * 4)

    # 映射表
    generator_map = {
        "Agency": gen_dragon_form,
        "Coherence": gen_mountain_forest_form,
        "Care": gen_whale_form,
        "Curiosity": gen_spirit_cat, # 使用新的灵猫生成器
        "Reflection": gen_book_form,
        "Transcendence": gen_gateway_form,
        "Aesthetic": gen_tree_form
    }
    # 暂时全部导向灵猫进行测试
    generator = gen_spirit_cat 
    # generator = generator_map.get(primary_attr, gen_whale_form)

    aspect_map = {
        "Agency": apply_thunder_aspect,
        "Coherence": apply_foundation_aspect,
        "Care": apply_warmth_aspect,
        "Curiosity": apply_stardust_aspect,
        "Reflection": apply_abyss_aspect,
        "Transcendence": apply_ascension_aspect,
        "Aesthetic": apply_prismatic_aspect
    }
    applicator = aspect_map.get(secondary_attr, lambda x: x)
    
    raw_points_np = generator(base_count)
    processed_points_np = applicator(raw_points_np)
    final_points = processed_points_np.tolist()
    random.shuffle(final_points)

    # 5. 颜色与透明度处理 (关键!)
    echarts_series_data = []
    c_map = {
        "Care": "#FF4081", "Agency": "#FFD700", "Reflection": "#536DFE",
        "Coherence": "#00CCFF", "Aesthetic": "#AB47BC", "Curiosity": "#00E676",
        "Transcendence": "#FFFFFF"
    }
    spirit_color = c_map.get(primary_attr, "#FFFFFF")
    is_prismatic = (secondary_attr == "Aesthetic")

    for i, pt in enumerate(final_points):
        # 计算点到中心的距离，用于控制透明度
        dist_to_center = np.linalg.norm(pt)
        # 核心粒子更不透明，边缘粒子非常透明
        base_opacity = max(0.1, 1.0 - (dist_to_center / 25.0))

        if is_prismatic:
            hue = (pt[0]*2 + pt[1]*3 + pt[2]*4) % 360
            prism_colors = ["#FF0000", "#FF7F00", "#FFFF00", "#00FF00", "#0000FF", "#4B0082"]
            point_color = prism_colors[int(hue) % len(prism_colors)]
            opacity = base_opacity * 0.8
        else:
            point_color = spirit_color
            opacity = base_opacity * 0.5 # 整体更透明，制造迷雾感

        # 随机大小，增加层次感
        symbol_size = random.uniform(1.5, 4.0)

        if i < len(user_nodes):
            # 用户的意义节点：更大、更亮、不透明
            node = user_nodes[i]
            echarts_series_data.append({
                "name": node.get('care_point', 'Thought'), "value": pt,
                "itemStyle": {"color": point_color, "opacity": 1.0, "borderColor": "#FFF", "borderWidth": 0.5},
                "symbolSize": symbol_size * 2.0, "raw_content": node.get('content', '')
            })
        else:
            # 结构/迷雾粒子
            echarts_series_data.append({
                "name": "Spirit Mist", "value": pt,
                "itemStyle": {"color": point_color, "opacity": opacity},
                "symbolSize": symbol_size, "raw_content": ""
            })
            
    return echarts_series_data, primary_attr, secondary_attr

# ==========================================
# 🌲 4. 渲染主程序 (Renderer)
# ==========================================
def render_forest_scene(radar_dict, user_nodes=None):
    # ... (保持原有标题和翻译逻辑)
    if user_nodes is None: user_nodes = []
    echarts_data, p_attr, s_attr = synthesize_creature_data(radar_dict, user_nodes)
    lang = st.session_state.get('language', 'en')
    # ... (省略翻译字典)
    ARCHETYPE_NAMES = {
        "Agency": {"en": "Ascending Dragon", "zh": "腾空之龙"},
        "Coherence": {"en": "Mountain & Forest", "zh": "高山森林"},
        "Care": {"en": "Celestial Whale", "zh": "天海之鲸"},
        "Curiosity": {"en": "Spirit Cat", "zh": "灵猫"},
        "Reflection": {"en": "Ancient Book", "zh": "智慧古书"},
        "Transcendence": {"en": "Gateway of Light", "zh": "光之门扉"},
        "Aesthetic": {"en": "Crystalline Tree", "zh": "结晶生命树"}
    }
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
        creature_title = "Proto-Mist" if lang=='en' else "初生迷雾"
        creature_desc = "Gathering energy..." if lang=='en' else "能量汇聚中..."
    else:
        creature_title = p_name
        creature_desc = f"with {s_name}" if lang=='en' else f"伴随 {s_name}"

    label_title = "SOUL FORM" if lang=='en' else "灵魂形态"
    sac.divider(label=label_title, icon='layers', align='center', color='gray')
    st.markdown(f"<div style='text-align:center; margin-bottom: -20px;'><b>{creature_title}</b><br><span style='font-size:0.8em;color:gray'>{creature_desc}</span></div>", unsafe_allow_html=True)
    
    # ECharts 3D 配置 (关键调整：视角和光照)
    option = {
        "backgroundColor": "transparent",
        "tooltip": { "show": True, "formatter": "{b}" },
        # 隐藏坐标轴网格线，只保留底板提示
        "xAxis3D": { "show": False, "min": -30, "max": 30, "splitLine": {"show": False}},
        "yAxis3D": { "show": False, "min": -30, "max": 30, "splitLine": {"show": False}},
        "zAxis3D": { "show": False, "min": -20, "max": 40, "splitLine": {"show": False}},
        "grid3D": { 
            "boxWidth": 100, "boxDepth": 100, "boxHeight": 100, 
            "viewControl": { 
                "projection": 'perspective',
                "autoRotate": True, "autoRotateSpeed": 5, # 转慢点，更优雅
                "distance": 140, # 拉近镜头，放大主体
                "alpha": 20, # 更平视的视角
                "beta": 30,
                "minDistance": 100, "maxDistance": 250,
                "panMouseButton": 'left',
                "rotateMouseButton": 'right'
            }, 
            # 柔和的光照
            "light": { 
                "main": {"intensity": 0.8, "alpha": 30, "beta": 30}, 
                "ambient": {"intensity": 0.6} 
            }, 
            # 极简环境
            "environment": "#000000",
            "splitLine": {"show": False}, # 再次确保隐藏网格
            "axisPointer": {"show": False}
        },
        "series": [{ 
            "type": 'scatter3D', "data": echarts_data, 
            # 使用 'lambert' 着色，配合半透明粒子，更有体积感
            "shading": 'lambert',
            # 让粒子有一种发光的感觉
            "itemStyle": {
                "borderColor": "rgba(255,255,255,0.1)",
                "borderWidth": 0.5
            },
            "emphasis": { 
                "itemStyle": {"color": "#fff", "opacity": 1, "borderColor": "#fff", "borderWidth": 2},
                "label": {"show": True, "formatter": "{b}", "position": "top", "textStyle": {"color": "#000", "backgroundColor": "#fff", "padding": [2,4], "borderRadius": 2}}
            } 
        }]
    }
    # 增加高度，让画面更舒展
    st_echarts(options=option, height="450px")
    viz.render_spectrum_legend()
