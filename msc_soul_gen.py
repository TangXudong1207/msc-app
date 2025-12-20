import random
import math
import numpy as np

# ==========================================
# 🌌 0. 场域与采样工具 (Field & Sampling Helpers)
# ==========================================
def jitter_vec(vec, intensity=1.0):
    """向量加噪"""
    return vec + np.random.normal(0, intensity, 3)

def gaussian_blob(x, y, z, center, sigma):
    """计算点在三维高斯团中的密度值"""
    cx, cy, cz = center
    sx, sy, sz = sigma
    exponent = -((x-cx)**2/(2*sx**2) + (y-cy)**2/(2*sy**2) + (z-cz)**2/(2*sz**2))
    return np.exp(exponent)

def cat_field_density(x, y, z):
    """定义灵猫形态的概率密度场"""
    # 1. 身体能量团 (大而扁)
    body_density = gaussian_blob(x, y, z, center=(0, 0, -2), sigma=(12, 5, 6))
    
    # 2. 头部能量团 (小而圆，位置靠前上)
    head_density = gaussian_blob(x, y, z, center=(10, 0, 4), sigma=(4, 4, 4))
    
    # 3. 尾部流场区域 (用一个宽泛的区域定义，具体形状靠流场生成)
    # 在身体后方定义一个密度较低但范围广的区域
    tail_area_density = gaussian_blob(x, y, z, center=(-15, 0, 2), sigma=(10, 8, 8)) * 0.6
    
    # 总密度是各部分密度的叠加
    total_density = body_density + head_density * 1.2 + tail_area_density
    # 归一化到 [0, 1] 区间 (大致)
    return min(1.0, total_density)

def apply_tail_flow(x, y, z):
    """对尾部区域的粒子应用旋转流场，制造动态感"""
    # 只对身体后方的粒子应用流场
    if x > -5: return np.array([x, y, z])
    
    # 简单的涡旋流场：围绕 X 轴旋转
    angle = x * 0.05 # 旋转角度随位置变化
    c = math.cos(angle)
    s = math.sin(angle)
    # 旋转 y 和 z
    new_y = y * c - z * s
    new_z = y * s + z * c
    
    # 加上一点向后和向上的趋势
    new_x = x - 0.5
    new_z += 0.2
    
    return np.array([new_x, new_y, new_z])

# ==========================================
# 🐉 1. 具象化基底生成器 (Archetype Generators)
# ==========================================

def gen_spirit_cat_field(n):
    """灵猫：基于场域和流动的伪3D形态"""
    points = []
    
    # 1. 核心能量 (高密度采样)
    n_core = int(n * 0.25)
    for _ in range(n_core):
        # 在核心区域附近高斯采样
        pt = np.random.normal(loc=[2, 0, 0], scale=[6, 3, 3])
        points.append(pt)

    # 2. 场域形态 (拒绝采样法)
    n_field = int(n * 0.6)
    count = 0
    # 设置采样边界盒 (Bounding Box)
    bx, by, bz = 40, 20, 20
    while count < n_field:
        # 在边界盒内随机撒点
        rx = random.uniform(-bx, bx)
        ry = random.uniform(-by, by)
        rz = random.uniform(-bz, bz)
        
        # 计算该点的密度概率
        prob = cat_field_density(rx, ry, rz)
        
        # 拒绝采样
        if random.random() < prob:
            # 采样成功，应用尾部流场
            final_pt = apply_tail_flow(rx, ry, rz)
            # 加一点随机扰动，让粒子更自然
            final_pt = jitter_vec(final_pt, intensity=0.5)
            points.append(final_pt)
            count += 1
            
    # 3. 稀疏环境氛围 (大范围均匀分布)
    n_aura = int(n * 0.15)
    for _ in range(n_aura):
        # 在更大的球体内均匀采样
        r = random.uniform(30, 60)
        theta = random.uniform(0, 2*math.pi)
        phi = math.acos(random.uniform(-1, 1))
        x = r * math.sin(phi) * math.cos(theta)
        y = r * math.sin(phi) * math.sin(theta)
        z = r * math.cos(phi)
        # 压扁一点，更有环绕感
        points.append(np.array([x, y, z * 0.6]))
        
    return np.vstack(points)

# (其他形态使用旧的结构壳体函数占位，后续可以用同样的方法改造)
def get_random_point_on_ellipsoid(a, b, c, jitter=0.0):
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

def gen_placeholder(n): return gen_structure_shell((0,0,0), n, 20, 10, 10)
def gen_dragon_form(n): return gen_placeholder(n)
def gen_mountain_forest_form(n): return gen_placeholder(n)
def gen_whale_form(n): return gen_placeholder(n)
def gen_book_form(n): return gen_placeholder(n)
def gen_gateway_form(n): return gen_placeholder(n)
def gen_tree_form(n): return gen_placeholder(n)

# ==========================================
# 🌪️ 2. 氛围特效应用器 (Aspect Applicators)
# ==========================================
# (特效函数保持不变，它们与新的场域生成完美兼容)
def apply_thunder_aspect(points): return jitter_vec(points, intensity=2.0)
def apply_foundation_aspect(points): return points 
def apply_warmth_aspect(points): return points
def apply_stardust_aspect(points): 
    stardust = []
    n_star = int(len(points) * 0.3)
    for _ in range(n_star):
        theta = random.uniform(0, 2*math.pi)
        phi = random.uniform(0, math.pi)
        r = random.uniform(50, 80) 
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
    if not radar: radar = {"Care": 3.0, "Reflection": 3.0}
    valid_keys = ["Care", "Curiosity", "Reflection", "Coherence", "Agency", "Aesthetic", "Transcendence"]
    clean_radar = {k: v for k, v in radar.items() if k in valid_keys}
    if not clean_radar: clean_radar = {"Care": 3.0, "Reflection": 3.0}
    
    sorted_attr = sorted(clean_radar.items(), key=lambda x: x[1], reverse=True)
    primary_attr = sorted_attr[0][0] if sorted_attr else "Care"
    secondary_attr = sorted_attr[1][0] if len(sorted_attr) > 1 else primary_attr

    # 粒子数量
    base_count = max(1000, len(user_nodes) * 5)

    generator_map = {
        "Agency": gen_dragon_form,
        "Coherence": gen_mountain_forest_form,
        "Care": gen_whale_form,
        "Curiosity": gen_spirit_cat_field, # 使用新的场域生成器
        "Reflection": gen_book_form,
        "Transcendence": gen_gateway_form,
        "Aesthetic": gen_tree_form
    }
    # 强制使用灵猫进行演示
    # 🔴 修复点：这里把 gen_spirit_cat 改成了 gen_spirit_cat_field
    generator = gen_spirit_cat_field 

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
        "Transcendence": "#888888"
    }
    spirit_color = c_map.get(primary_attr, "#888888")
    is_prismatic = (secondary_attr == "Aesthetic")

    for i, pt in enumerate(final_points):
        # 透明度逻辑调整：基于场域密度的自然衰减
        # 简单用距离中心的距离来模拟
        dist_to_center = np.linalg.norm(pt - np.array([5,0,0]))
        # 核心更实，边缘更虚
        base_opacity = max(0.1, 0.9 - (dist_to_center / 30.0)**1.5)

        if is_prismatic:
            hue = (pt[0]*2 + pt[1]*3 + pt[2]*4) % 360
            prism_colors = ["#FF0000", "#FF7F00", "#FFFF00", "#00FF00", "#0000FF", "#4B0082"]
            point_color = prism_colors[int(hue) % len(prism_colors)]
            opacity = base_opacity * 0.8
        else:
            point_color = spirit_color
            opacity = base_opacity * 0.7

        symbol_size = random.uniform(2.5, 5.0)

        if i < len(user_nodes):
            node = user_nodes[i]
            echarts_series_data.append({
                "name": node.get('care_point', 'Thought'), "value": pt,
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
