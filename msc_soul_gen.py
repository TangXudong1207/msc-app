import random
import math
import numpy as np

# ==========================================
# 📐 0. 数学与结构工具 (Math & Structure Helpers)
# ==========================================
def get_random_point_on_ellipsoid(a, b, c, jitter=0.0):
    """在椭球体表面生成随机点，并附加噪点"""
    theta = random.uniform(0, 2 * math.pi)
    phi = math.acos(random.uniform(-1, 1))
    x = a * math.sin(phi) * math.cos(theta)
    y = b * math.sin(phi) * math.sin(theta)
    z = c * math.cos(phi)
    if jitter > 0:
        x += random.gauss(0, jitter)
        y += random.gauss(0, jitter)
        z += random.gauss(0, jitter)
    return np.array([x, y, z])

def gen_structure_shell(center, n_points, a, b, c, jitter_surface=0.3, fill_density=0.2):
    """生成带有稀疏内部填充的结构壳体"""
    points = []
    n_surface = int(n_points * (1 - fill_density))
    for _ in range(n_surface):
        pt = get_random_point_on_ellipsoid(a, b, c, jitter_surface)
        points.append(np.array(center) + pt)
    n_fill = n_points - n_surface
    for _ in range(n_fill):
        r_scale = random.uniform(0.3, 0.8)
        pt = get_random_point_on_ellipsoid(a*r_scale, b*r_scale, c*r_scale, jitter_surface*2)
        points.append(np.array(center) + pt)
    return np.array(points)

def gen_flow_curve_tight(start_pt, end_pt, control_pt, n_points, jitter=0.3):
    """生成紧凑清晰的贝塞尔流动曲线"""
    t = np.linspace(0, 1, n_points)
    curve = (1-t)**2 * start_pt[:, None] + 2*(1-t)*t * control_pt[:, None] + t**2 * end_pt[:, None]
    curve = curve.T
    noise = np.random.normal(0, jitter, (n_points, 3))
    return curve + noise

# ==========================================
# 🐉 1. 具象化基底生成器 (Archetype Generators)
# ==========================================
# 🎯 核心修改：大幅放大尺寸参数，使其充满坐标系

def gen_spirit_cat(n):
    """灵猫：放大版"""
    # 1. 身体 (放大约 2.5 倍)
    body_pts = gen_structure_shell(center=(0, 0, 0), n_points=int(n*0.35), 
                                   a=28, b=12, c=14, jitter_surface=0.8)
    
    # 2. 头部 (放大并调整位置)
    head_center = np.array([28, 0, 5])
    head_pts = gen_structure_shell(center=head_center, n_points=int(n*0.15),
                                   a=10, b=10, c=9, jitter_surface=0.6)
    
    # 3. 耳朵 (放大并调整位置)
    ear_pts = []
    # 左耳
    e1_start = head_center + np.array([0, 4, 6])
    e1_top = head_center + np.array([-3, 9, 15])
    e1_end = head_center + np.array([4, 7, 6])
    ear_pts.append(gen_flow_curve_tight(e1_start, e1_top, (e1_start+e1_top)/2, int(n*0.02), jitter=0.4))
    ear_pts.append(gen_flow_curve_tight(e1_top, e1_end, (e1_top+e1_end)/2, int(n*0.02), jitter=0.4))
    # 右耳
    e2_start = head_center + np.array([0, -4, 6])
    e2_top = head_center + np.array([-3, -9, 15])
    e2_end = head_center + np.array([4, -7, 6])
    ear_pts.append(gen_flow_curve_tight(e2_start, e2_top, (e2_start+e2_top)/2, int(n*0.02), jitter=0.4))
    ear_pts.append(gen_flow_curve_tight(e2_top, e2_end, (e2_top+e2_end)/2, int(n*0.02), jitter=0.4))
    ear_pts_np = np.vstack(ear_pts)

    # 4. 灵动双尾 (放大并调整路径)
    tail_start = np.array([-26, 0, 2])
    # 尾巴1
    t1_end = np.array([-60, 25, 20])
    t1_ctrl = np.array([-40, 40, 12])
    tail1_pts = gen_flow_curve_tight(tail_start, t1_end, t1_ctrl, n_points=int(n*0.12), jitter=1.2)
    # 尾巴2
    t2_end = np.array([-60, -25, 10])
    t2_ctrl = np.array([-40, -40, 5])
    tail2_pts = gen_flow_curve_tight(tail_start, t2_end, t2_ctrl, n_points=int(n*0.12), jitter=1.2)
    
    # 5. 基础微光环绕 (范围扩大)
    aura_pts = []
    for _ in range(int(n*0.08)):
        theta = random.uniform(0, 2*math.pi)
        r = random.uniform(40, 70)
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        z = random.uniform(-15, 25)
        aura_pts.append(np.array([x,y,z]))
        
    return np.vstack([body_pts, head_pts, ear_pts_np, tail1_pts, tail2_pts, np.array(aura_pts)])

# (其他形态暂时使用空函数占位，确保代码可运行)
def gen_placeholder(n): return gen_structure_shell((0,0,0), n, 20, 20, 20)
def gen_dragon_form(n): return gen_placeholder(n)
def gen_mountain_forest_form(n): return gen_placeholder(n)
def gen_whale_form(n): return gen_placeholder(n)
def gen_book_form(n): return gen_placeholder(n)
def gen_gateway_form(n): return gen_placeholder(n)
def gen_tree_form(n): return gen_placeholder(n)

# ==========================================
# 🌪️ 2. 氛围特效应用器 (Aspect Applicators)
# ==========================================
def jitter_vec(vec, intensity=1.0): return vec + np.random.normal(0, intensity, 3)
def apply_thunder_aspect(points): return jitter_vec(points, intensity=2.5) # 增强特效强度
def apply_foundation_aspect(points): return points 
def apply_warmth_aspect(points): return points
def apply_stardust_aspect(points): 
    stardust = []
    n_star = int(len(points) * 0.25)
    for _ in range(n_star):
        theta = random.uniform(0, 2*math.pi)
        phi = random.uniform(0, math.pi)
        r = random.uniform(60, 90) # 扩大星尘轨道
        x = r * math.sin(phi) * math.cos(theta)
        y = r * math.sin(phi) * math.sin(theta)
        z = r * math.cos(phi)
        stardust.append([x, y, z])
    return np.vstack([points, jitter_vec(np.array(stardust), intensity=1.5)])
def apply_abyss_aspect(points): return points
def apply_ascension_aspect(points): return points
def apply_prismatic_aspect(points): return points

# ==========================================
# 🧬 3. 核心合成逻辑 (Synthesizer)
# ==========================================
def synthesize_creature_data(radar, user_nodes):
    if not radar: radar = {"Care": 3.0, "Reflection": 3.0}
    valid_keys = ["Care", "Curiosity", "Reflection", "Coherence", "Agency", "Aesthetic", "Transcendence"]
    clean_radar = {k: v for k, v in radar.items() if k in valid_keys}
    if not clean_radar: clean_radar = {"Care": 3.0, "Reflection": 3.0}
    
    sorted_attr = sorted(clean_radar.items(), key=lambda x: x[1], reverse=True)
    primary_attr = sorted_attr[0][0] if sorted_attr else "Care"
    secondary_attr = sorted_attr[1][0] if len(sorted_attr) > 1 else primary_attr

    # 增加粒子总数以适应更大的体积
    base_count = max(1200, len(user_nodes) * 6)

    generator_map = {
        "Agency": gen_dragon_form,
        "Coherence": gen_mountain_forest_form,
        "Care": gen_whale_form,
        "Curiosity": gen_spirit_cat,
        "Reflection": gen_book_form,
        "Transcendence": gen_gateway_form,
        "Aesthetic": gen_tree_form
    }
    # 强制使用灵猫进行演示
    generator = gen_spirit_cat 

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

    echarts_series_data = []
    c_map = {
        "Care": "#FF4081", "Agency": "#FFD700", "Reflection": "#536DFE",
        "Coherence": "#00CCFF", "Aesthetic": "#AB47BC", "Curiosity": "#00E676",
        "Transcendence": "#888888" # 在白背景下，Transcendence 改为中灰色
    }
    spirit_color = c_map.get(primary_attr, "#888888")
    is_prismatic = (secondary_attr == "Aesthetic")

    for i, pt in enumerate(final_points):
        # 调整透明度计算，适应白背景
        dist_to_center = np.linalg.norm(pt - np.array([10,0,0]))
        base_opacity = max(0.3, 1.0 - (dist_to_center / 60.0))

        if is_prismatic:
            hue = (pt[0]*2 + pt[1]*3 + pt[2]*4) % 360
            prism_colors = ["#FF0000", "#FF7F00", "#FFFF00", "#00FF00", "#0000FF", "#4B0082"]
            point_color = prism_colors[int(hue) % len(prism_colors)]
            opacity = base_opacity * 0.9
        else:
            point_color = spirit_color
            opacity = base_opacity * 0.8

        symbol_size = random.uniform(2.5, 5.5)

        if i < len(user_nodes):
            node = user_nodes[i]
            echarts_series_data.append({
                "name": node.get('care_point', 'Thought'), "value": pt,
                # 在白背景下，去掉白色描边，改为深色描边增加对比度
                "itemStyle": {"color": point_color, "opacity": 1.0, "borderColor": "#555", "borderWidth": 0.5},
                "symbolSize": symbol_size * 2.0, "raw_content": node.get('content', '')
            })
        else:
            echarts_series_data.append({
                "name": "Spirit Particle", "value": pt,
                "itemStyle": {"color": point_color, "opacity": opacity},
                "symbolSize": symbol_size, "raw_content": ""
            })
            
    return echarts_series_data, primary_attr, secondary_attr
