import streamlit as st
from streamlit_echarts import st_echarts
import random
import math
import numpy as np
import msc_viz as viz
import streamlit_antd_components as sac

# ==========================================
# 🌫️ 0. 数学与结构工具 (Math & Structure Helpers)
# ==========================================
def get_random_point_on_ellipsoid(a, b, c, jitter=0.0):
    """在椭球体表面生成随机点，并附加噪点 (用于勾勒清晰轮廓)"""
    theta = random.uniform(0, 2 * math.pi)
    phi = math.acos(random.uniform(-1, 1))
    x = a * math.sin(phi) * math.cos(theta)
    y = b * math.sin(phi) * math.sin(theta)
    z = c * math.cos(phi)
    # 添加噪点使表面不那么光滑
    if jitter > 0:
        x += random.gauss(0, jitter)
        y += random.gauss(0, jitter)
        z += random.gauss(0, jitter)
    return np.array([x, y, z])

def gen_structure_shell(center, n_points, a, b, c, jitter_surface=0.3, fill_density=0.2):
    """生成带有稀疏内部填充的结构壳体 (用于身体主体)"""
    points = []
    # 表面粒子 (勾勒轮廓)
    n_surface = int(n_points * (1 - fill_density))
    for _ in range(n_surface):
        pt = get_random_point_on_ellipsoid(a, b, c, jitter_surface)
        points.append(np.array(center) + pt)
    
    # 内部稀疏填充 (增加体积感)
    n_fill = n_points - n_surface
    for _ in range(n_fill):
        # 使用较小的半径在内部生成
        r_scale = random.uniform(0.3, 0.8)
        pt = get_random_point_on_ellipsoid(a*r_scale, b*r_scale, c*r_scale, jitter_surface*2)
        points.append(np.array(center) + pt)
        
    return np.array(points)

def gen_flow_curve_tight(start_pt, end_pt, control_pt, n_points, jitter=0.3):
    """生成更紧凑清晰的贝塞尔流动曲线 (用于尾巴、耳朵轮廓)"""
    t = np.linspace(0, 1, n_points)
    # 二阶贝塞尔曲线
    curve = (1-t)**2 * start_pt[:, None] + 2*(1-t)*t * control_pt[:, None] + t**2 * end_pt[:, None]
    curve = curve.T
    # 噪点显著降低，使线条更清晰
    noise = np.random.normal(0, jitter, (n_points, 3))
    return curve + noise

# (保留旧的云雾函数作为备用或用于其他形态)
def gen_ethereal_cloud(center, n_points, radius_x, radius_y, radius_z, core_density=0.6):
    points = []
    for _ in range(n_points):
        x = random.gauss(0, radius_x * core_density)
        y = random.gauss(0, radius_y * core_density)
        z = random.gauss(0, radius_z * core_density)
        points.append(np.array(center) + np.array([x, y, z]))
    return np.array(points)

# ==========================================
# 🐉 1. 具象化基底生成器 (Archetype Generators)
# ==========================================

def gen_spirit_cat(n):
    """灵猫：具有清晰轮廓和关键特征的灵体"""
    # 1. 身体 (清晰的椭球壳体)
    # 身体拉长，略微压扁
    body_pts = gen_structure_shell(center=(0, 0, 0), n_points=int(n*0.35), 
                                   a=11, b=4.5, c=5, jitter_surface=0.4)
    
    # 2. 头部 (位于身体前端，较圆)
    head_center = np.array([11, 0, 2])
    head_pts = gen_structure_shell(center=head_center, n_points=int(n*0.15),
                                   a=3.8, b=3.8, c=3.6, jitter_surface=0.3)
    
    # 3. 耳朵 (关键特征！用短曲线勾勒三角形)
    ear_pts = []
    # 左耳
    e1_start = head_center + np.array([0, 1.5, 2.5])
    e1_top = head_center + np.array([-1, 3.5, 5.5]) # 耳尖
    e1_end = head_center + np.array([1.5, 2.5, 2.5])
    ear_pts.append(gen_flow_curve_tight(e1_start, e1_top, (e1_start+e1_top)/2 + np.array([0,0.5,0]), int(n*0.02), jitter=0.2))
    ear_pts.append(gen_flow_curve_tight(e1_top, e1_end, (e1_top+e1_end)/2 + np.array([0,0.5,0]), int(n*0.02), jitter=0.2))
    # 右耳
    e2_start = head_center + np.array([0, -1.5, 2.5])
    e2_top = head_center + np.array([-1, -3.5, 5.5]) # 耳尖
    e2_end = head_center + np.array([1.5, -2.5, 2.5])
    ear_pts.append(gen_flow_curve_tight(e2_start, e2_top, (e2_start+e2_top)/2 + np.array([0,-0.5,0]), int(n*0.02), jitter=0.2))
    ear_pts.append(gen_flow_curve_tight(e2_top, e2_end, (e2_top+e2_end)/2 + np.array([0,-0.5,0]), int(n*0.02), jitter=0.2))
    ear_pts_np = np.vstack(ear_pts)

    # 4. 灵动双尾 (更紧致清晰的线条)
    tail_start = np.array([-10, 0, 1])
    # 尾巴1
    t1_end = np.array([-24, 9, 8])
    t1_ctrl = np.array([-16, 16, 5])
    # jitter 显著降低，线条更清晰
    tail1_pts = gen_flow_curve_tight(tail_start, t1_end, t1_ctrl, n_points=int(n*0.12), jitter=0.7)
    # 尾巴2
    t2_end = np.array([-24, -9, 4])
    t2_ctrl = np.array([-16, -16, 2])
    tail2_pts = gen_flow_curve_tight(tail_start, t2_end, t2_ctrl, n_points=int(n*0.12), jitter=0.7)
    
    # 5. 基础微光环绕 (数量减少，避免喧宾夺主)
    aura_pts = []
    for _ in range(int(n*0.08)):
        # 在一个较大的扁平区域内随机生成
        theta = random.uniform(0, 2*math.pi)
        r = random.uniform(15, 32)
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        z = random.uniform(-5, 10)
        aura_pts.append(np.array([x,y,z]))
        
    return np.vstack([body_pts, head_pts, ear_pts_np, tail1_pts, tail2_pts, np.array(aura_pts)])

# (其他形态暂时沿用旧的云雾函数，后续可逐步替换为清晰结构版)
def gen_dragon_form(n): return gen_ethereal_cloud((0,0,0), n, 22, 6, 6)
def gen_mountain_forest_form(n): return gen_ethereal_cloud((0,0,-5), n, 18, 18, 22)
def gen_whale_form(n): return gen_ethereal_cloud((0,0,0), n, 28, 9, 12)
def gen_book_form(n): return gen_ethereal_cloud((0,0,0), n, 12, 3, 10)
def gen_gateway_form(n): return gen_ethereal_cloud((0,0,0), n, 6, 18, 24)
def gen_tree_form(n): return gen_ethereal_cloud((0,0,-5), n, 10, 10, 28)

# ==========================================
# 🌪️ 2. 氛围特效应用器 (Aspect Applicators)
# ==========================================
def jitter_vec(vec, intensity=1.0):
    return vec + np.random.normal(0, intensity, 3)

def apply_thunder_aspect(points): return jitter_vec(points, intensity=1.2)
def apply_foundation_aspect(points): return points 
def apply_warmth_aspect(points): return points
def apply_stardust_aspect(points): 
    stardust = []
    n_star = int(len(points) * 0.25) # 稍微减少星尘数量
    for _ in range(n_star):
        theta = random.uniform(0, 2*math.pi)
        phi = random.uniform(0, math.pi)
        r = random.uniform(30, 45) # 轨道范围
        x = r * math.sin(phi) * math.cos(theta)
        y = r * math.sin(phi) * math.sin(theta)
        z = r * math.cos(phi)
        stardust.append([x, y, z])
    return np.vstack([points, jitter_vec(np.array(stardust), intensity=0.8)])
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

    # 粒子总数
    base_count = max(600, len(user_nodes) * 4)

    generator_map = {
        "Agency": gen_dragon_form,
        "Coherence": gen_mountain_forest_form,
        "Care": gen_whale_form,
        "Curiosity": gen_spirit_cat, # 使用新的具象化灵猫
        "Reflection": gen_book_form,
        "Transcendence": gen_gateway_form,
        "Aesthetic": gen_tree_form
    }
    # 强制使用灵猫进行演示
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

    # 5. 颜色与透明度处理
    echarts_series_data = []
    c_map = {
        "Care": "#FF4081", "Agency": "#FFD700", "Reflection": "#536DFE",
        "Coherence": "#00CCFF", "Aesthetic": "#AB47BC", "Curiosity": "#00E676",
        "Transcendence": "#FFFFFF"
    }
    spirit_color = c_map.get(primary_attr, "#FFFFFF")
    is_prismatic = (secondary_attr == "Aesthetic")

    for i, pt in enumerate(final_points):
        # 简单的透明度逻辑：核心不透明，外围透明
        dist_to_center = np.linalg.norm(pt - np.array([5,0,0])) # 大致以身体中心为参考
        base_opacity = max(0.2, 1.0 - (dist_to_center / 25.0))

        if is_prismatic:
            hue = (pt[0]*2 + pt[1]*3 + pt[2]*4) % 360
            prism_colors = ["#FF0000", "#FF7F00", "#FFFF00", "#00FF00", "#0000FF", "#4B0082"]
            point_color = prism_colors[int(hue) % len(prism_colors)]
            opacity = base_opacity * 0.9
        else:
            point_color = spirit_color
            opacity = base_opacity * 0.7

        symbol_size = random.uniform(2.0, 4.5)

        if i < len(user_nodes):
            node = user_nodes[i]
            echarts_series_data.append({
                "name": node.get('care_point', 'Thought'), "value": pt,
                "itemStyle": {"color": point_color, "opacity": 1.0, "borderColor": "#FFF", "borderWidth": 1.0, "shadowBlur": 10, "shadowColor": point_color},
                "symbolSize": symbol_size * 2.5, "raw_content": node.get('content', '')
            })
        else:
            echarts_series_data.append({
                "name": "Spirit Particle", "value": pt,
                "itemStyle": {"color": point_color, "opacity": opacity},
                "symbolSize": symbol_size, "raw_content": ""
            })
            
    return echarts_series_data, primary_attr, secondary_attr

# ==========================================
# 🌲 4. 渲染主程序 (Renderer)
# ==========================================
def render_forest_scene(radar_dict, user_nodes=None):
    if user_nodes is None: user_nodes = []
    echarts_data, p_attr, s_attr = synthesize_creature_data(radar_dict, user_nodes)
    lang = st.session_state.get('language', 'en')
    
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
    
    # ==========================================
    # 🎯 核心修改：高对比度学术坐标系 & 构图调整
    # ==========================================
    
    # 定义更亮的颜色，在深色背景下清晰可见
    axis_line_color = "#E0E0E0" # 亮灰白色
    split_line_color = "#555555" # 中灰色网格
    background_color = "#0E1117" # 深蓝灰背景

    # 通用的轴配置 (开启标签显示)
    axis_config = {
        "show": True, 
        "min": -35, "max": 35, 
        "axisLine": {"lineStyle": {"color": axis_line_color, "width": 2}}, 
        # 🎯 核心修复：开启轴标签显示，并设置颜色和字体
        "axisLabel": {"show": True, "textStyle": {"color": axis_line_color, "fontSize": 10, "fontFamily": "JetBrains Mono"}},
        "splitLine": {"show": True, "lineStyle": {"color": split_line_color, "width": 0.8, "type": "solid"}},
        # 🎯 新增：轴标题样式
        "nameTextStyle": {"color": "#FFFFFF", "fontSize": 14, "fontWeight": "bold"}
    }

    option = {
        "backgroundColor": "transparent",
        "tooltip": { "show": True, "formatter": "{b}" },
        
        # 应用新的轴配置
        "xAxis3D": { **axis_config, "name": "X" },
        "yAxis3D": { **axis_config, "name": "Y" },
        "zAxis3D": { **axis_config, "name": "Z" },

        "grid3D": { 
            "boxWidth": 70, "boxDepth": 70, "boxHeight": 70, 
            "viewControl": { 
                "projection": 'perspective',
                "autoRotate": True, "autoRotateSpeed": 5,
                # 调整视角，更好地展示猫的侧面轮廓
                "distance": 130, 
                "alpha": 20, "beta": 50,
                "minDistance": 100, "maxDistance": 250,
                "panMouseButton": 'left', "rotateMouseButton": 'right'
            }, 
            "light": { 
                "main": {"intensity": 1.2, "alpha": 30, "beta": 30}, 
                "ambient": {"intensity": 0.6} 
            }, 
            "environment": background_color,
            # 确保盒子壁上的网格线显示
            "splitLine": {"show": True, "lineStyle": {"color": split_line_color, "width": 0.8}}
        },
        "series": [{ 
            "type": 'scatter3D', "data": echarts_data, 
            "shading": 'lambert',
            # 增强粒子发光感
            "itemStyle": {
                "borderColor": "rgba(255,255,255,0.3)",
                "borderWidth": 0.5,
                "shadowBlur": 8
            },
            "emphasis": { 
                "itemStyle": {"color": "#fff", "opacity": 1, "borderColor": "#fff", "borderWidth": 2, "shadowBlur": 20},
                "label": {"show": True, "formatter": "{b}", "position": "top", "textStyle": {"color": "#000", "backgroundColor": "#fff", "padding": [2,4], "borderRadius": 2}}
            } 
        }]
    }
    st_echarts(options=option, height="500px")
    viz.render_spectrum_legend()
