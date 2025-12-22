### msc_soul_gen.py ###
import random
import math
import numpy as np
import msc_config as config
import json

# 辅助：JSON 清洗
def clean_for_json(obj):
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return clean_for_json(obj.tolist())
    elif isinstance(obj, dict):
        return {k: clean_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_for_json(v) for v in obj]
    else:
        return obj

# 辅助：获取颜色
def get_dimension_color(dim):
    # 反向查找 config 中的颜色
    return config.SPECTRUM.get(dim, "#FFFFFF")

def generate_nebula_data(radar_dict, user_nodes):
    """
    生成 3D 星云数据 (Nebula/Soul Field)
    不使用 NetworkX，纯数学生成粒子云
    """
    if not radar_dict: radar_dict = {"Care": 3.0, "Reflection": 3.0}

    # 1. 权重分析 (决定星云的颜色构成)
    valid_keys = config.RADAR_AXES
    clean_radar = {}
    total_score = 0
    for k, v in radar_dict.items():
        if k in valid_keys:
            try: val = float(v)
            except: val = 0
            if val > 0: 
                clean_radar[k] = val
                total_score += val
    
    if total_score == 0: 
        clean_radar = {"Reflection": 5.0}
        total_score = 5.0

    # 排序用于确定主属性
    sorted_dims = sorted(clean_radar.items(), key=lambda x: x[1], reverse=True)
    primary_attr = sorted_dims[0][0]
    secondary_attr = sorted_dims[1][0] if len(sorted_dims) > 1 else primary_attr

    # 权重归一化 (用于随机抽样)
    dims_list = list(clean_radar.keys())
    weights_list = [v/total_score for v in clean_radar.values()]

    # ---------------------------------------------------------
    # 🌌 2. 粒子生成逻辑
    # ---------------------------------------------------------
    
    # 容器
    particles = {
        "thoughts": {"x":[], "y":[], "z":[], "c":[], "s":[], "t":[]}, # 恒星 (用户数据)
        "atmos":    {"x":[], "y":[], "z":[], "c":[], "s":[]}          # 氛围 (尘埃)
    }

    # A. 生成氛围粒子 (Atmosphere Dust)
    # 数量取决于用户的思维密度，最少 200，最多 500
    num_atmos = int(min(500, max(200, len(user_nodes) * 20)))
    
    for _ in range(num_atmos):
        # 颜色：基于 Radar 权重随机
        dim = random.choices(dims_list, weights=weights_list, k=1)[0]
        
        # 坐标：球形正态分布 (Spherical Gaussian)
        # r 控制云的大小，theta/phi 控制方向
        r = random.gauss(0, 1.0) # 核心密集，边缘稀疏
        theta = random.uniform(0, 2 * math.pi)
        phi = random.uniform(0, math.pi)
        
        # 转换为直角坐标
        # 这里加一点扁平化处理 (multiply z by 0.7) 让它像个星系盘
        mx = r * math.sin(phi) * math.cos(theta)
        my = r * math.sin(phi) * math.sin(theta)
        mz = r * math.cos(phi) * 0.7 

        # 映射颜色
        # 我们用 DIMENSION_MAP 把 Radar 轴映射回 Spectrum 颜色
        # 但这里为了视觉丰富，我们可以直接用 Radar 轴对应的“代表色”
        # 简化处理：从 config.SPECTRUM 中找一个关联词
        color = "#888888"
        # 简单的映射表，把 7 轴映射到具体颜色
        AXIS_COLOR = {
            "Care": config.SPECTRUM["Empathy"],       # 粉红
            "Agency": config.SPECTRUM["Vitality"],    # 橙红
            "Structure": config.SPECTRUM["Structure"],# 灰白
            "Coherence": config.SPECTRUM["Rationality"],# 蓝
            "Curiosity": config.SPECTRUM["Curiosity"],# 绿
            "Reflection": config.SPECTRUM["Melancholy"],# 蓝紫
            "Aesthetic": config.SPECTRUM["Aesthetic"], # 紫
            "Transcendence": config.SPECTRUM["Consciousness"] # 青绿
        }
        color = AXIS_COLOR.get(dim, "#FFFFFF")

        particles["atmos"]["x"].append(mx)
        particles["atmos"]["y"].append(my)
        particles["atmos"]["z"].append(mz)
        particles["atmos"]["c"].append(color)
        particles["atmos"]["s"].append(random.uniform(1.5, 3.5)) # 粒子大小

    # B. 生成思维恒星 (User Thoughts)
    # 这些点应该更靠近核心，或者是结构中的“锚点”
    for node in user_nodes:
        # 颜色：尝试从 keywords 获取
        kw = node.get('keywords', [])
        if isinstance(kw, str):
            try: kw = json.loads(kw)
            except: kw = []
        
        color = "#FFFFFF" # 默认亮白
        if kw and len(kw) > 0:
            for k in kw:
                if k in config.SPECTRUM:
                    color = config.SPECTRUM[k]
                    break
        
        # 坐标：稍微均匀一点分布，避免重叠
        # 使用 Fibonacci Sphere 分布或者随机分布但 r 较小
        r = random.uniform(0.2, 0.8) # 核心区
        theta = random.uniform(0, 2 * math.pi)
        phi = random.uniform(0, math.pi)

        mx = r * math.sin(phi) * math.cos(theta)
        my = r * math.sin(phi) * math.sin(theta)
        mz = r * math.cos(phi) * 0.7

        particles["thoughts"]["x"].append(mx)
        particles["thoughts"]["y"].append(my)
        particles["thoughts"]["z"].append(mz)
        particles["thoughts"]["c"].append(color)
        particles["thoughts"]["s"].append(8) # 恒星大小
        
        # Tooltip 内容
        insight = node.get('insight', '')
        if len(insight) > 50: insight = insight[:50] + "..."
        particles["thoughts"]["t"].append(f"<b>{node.get('care_point','?')}</b><br>{insight}")

    return particles, primary_attr, secondary_attr
msc_soul_viz.py
