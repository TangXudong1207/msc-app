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

def generate_nebula_data(radar_dict, user_nodes):
    """
    基于灵魂形态（Archetype）的粒子生成器
    """
    if not radar_dict: radar_dict = {"Care": 3.0, "Reflection": 3.0}

    # 1. 确定主属性 (Archetype)
    valid_keys = config.RADAR_AXES
    clean_radar = {k: float(v) for k, v in radar_dict.items() if k in valid_keys and float(v) > 0}
    if not clean_radar: clean_radar = {"Reflection": 5.0}
    
    sorted_dims = sorted(clean_radar.items(), key=lambda x: x[1], reverse=True)
    primary_attr = sorted_dims[0][0] # 主属性决定形状
    secondary_attr = sorted_dims[1][0] if len(sorted_dims) > 1 else primary_attr # 副属性影响颜色/密度
    
    # 颜色权重
    total_score = sum(clean_radar.values())
    dims_list = list(clean_radar.keys())
    weights_list = [v/total_score for v in clean_radar.values()]

    # ---------------------------------------------------------
    # 🌌 形状数学引擎
    # ---------------------------------------------------------
    def get_pos_by_shape(shape_type):
        """返回单个粒子的 (x, y, z)"""
        # 基础随机变量
        u = random.random()
        v = random.random()
        theta = 2 * math.pi * u
        phi = math.acos(2 * v - 1)
        r_base = random.gauss(0, 1)

        # 🟥 Agency -> Starburst (大爆炸，射线状)
        if shape_type == "Agency":
            r = random.uniform(0.1, 2.5) # 扩散得很远
            # 挤压成扁平爆发或球形爆发
            return r * math.sin(phi) * math.cos(theta), r * math.sin(phi) * math.sin(theta), r * math.cos(phi)

        # 🟦 Coherence -> Grid/Crystal (晶格，有序)
        elif shape_type == "Coherence":
            # 离散化坐标，制造“人造物”的感觉
            step = 0.5
            x = round(random.gauss(0, 1.5) / step) * step
            y = round(random.gauss(0, 1.5) / step) * step
            z = round(random.gauss(0, 1.5) / step) * step
            return x, y, z

        # 🟪 Reflection -> Swirl (螺旋，黑洞吸积盘)
        elif shape_type == "Reflection":
            a = 0.5
            b = 0.3 # 螺旋紧密度
            angle = random.uniform(0, 4 * math.pi) # 绕两圈
            dist = a * math.exp(b * angle) * random.uniform(0.8, 1.2) # 对数螺旋
            # 转换为笛卡尔坐标
            x = dist * math.cos(angle)
            y = dist * math.sin(angle)
            z = random.gauss(0, 0.2) * (dist * 0.5) # 中心薄，边缘厚
            return x, y, z

        # 🟩 Transcendence -> Ascending (升腾，垂直光柱)
        elif shape_type == "Transcendence":
            h = random.uniform(-1, 3) # 偏向上方
            w = random.gauss(0, 0.4 * (1 + h*0.2)) # 随高度略微扩散
            return w * math.cos(theta), w * math.sin(theta), h

        # 🟨 Curiosity -> Web (发散，多核心)
        elif shape_type == "Curiosity":
            # 随机选择 3 个中心点
            centers = [(1,0,0), (-0.5, 0.8, 0), (-0.5, -0.8, 0)]
            cx, cy, cz = random.choice(centers)
            # 在中心点附近生成
            return cx + random.gauss(0, 0.6), cy + random.gauss(0, 0.6), cz + random.gauss(0, 0.6)

        # 🟧 Care -> Cluster (凝聚，致密核心)
        elif shape_type == "Care":
            r = random.uniform(0, 1) ** 3 # 极度向中心聚集
            return r * math.sin(phi) * math.cos(theta) * 2, r * math.sin(phi) * math.sin(theta) * 2, r * math.cos(phi) * 2

        # 🟪 Aesthetic -> Sphere (完美球壳)
        elif shape_type == "Aesthetic":
            r = random.gauss(1.5, 0.1) # 这是一个空心球壳
            return r * math.sin(phi) * math.cos(theta), r * math.sin(phi) * math.sin(theta), r * math.cos(phi)

        # 默认：球形云
        else:
            r = random.gauss(0, 1)
            return r * math.sin(phi) * math.cos(theta), r * math.sin(phi) * math.sin(theta), r * math.cos(phi)

    # ---------------------------------------------------------
    # 🌌 生成数据
    # ---------------------------------------------------------
    particles = {
        "thoughts": {"x":[], "y":[], "z":[], "c":[], "s":[], "t":[]}, 
        "atmos":    {"x":[], "y":[], "z":[], "c":[], "s":[]}
    }

    # 1. 生成氛围 (Atmosphere)
    # 数量：稍微多一点，制造“雾”的感觉
    num_atmos = int(min(600, max(300, len(user_nodes) * 30)))
    
    # 颜色映射表
    AXIS_COLOR = {
        "Care": config.SPECTRUM["Empathy"], "Agency": config.SPECTRUM["Vitality"],
        "Structure": config.SPECTRUM["Structure"], "Coherence": config.SPECTRUM["Rationality"],
        "Curiosity": config.SPECTRUM["Curiosity"], "Reflection": config.SPECTRUM["Melancholy"],
        "Aesthetic": config.SPECTRUM["Aesthetic"], "Transcendence": config.SPECTRUM["Consciousness"]
    }

    for _ in range(num_atmos):
        x, y, z = get_pos_by_shape(primary_attr)
        
        # 氛围颜色：随机取样
        dim = random.choices(dims_list, weights=weights_list, k=1)[0]
        color = AXIS_COLOR.get(dim, "#888888")
        
        particles["atmos"]["x"].append(x)
        particles["atmos"]["y"].append(y)
        particles["atmos"]["z"].append(z)
        particles["atmos"]["c"].append(color)
        particles["atmos"]["s"].append(random.uniform(1, 3)) # 细小的尘埃

    # 2. 生成思想恒星 (Thoughts)
    for node in user_nodes:
        # 思想的位置也在同样的形状力场中，但更向中心靠拢，作为骨架
        tx, ty, tz = get_pos_by_shape(primary_attr)
        
        # 稍微收缩一点，保证核心有内容
        scale_factor = 0.8
        
        # 获取颜色
        kw = node.get('keywords', [])
        if isinstance(kw, str):
            try: kw = json.loads(kw)
            except: kw = []
        color = "#FFFFFF"
        if kw:
            for k in kw:
                if k in config.SPECTRUM: color = config.SPECTRUM[k]; break
        
        particles["thoughts"]["x"].append(tx * scale_factor)
        particles["thoughts"]["y"].append(ty * scale_factor)
        particles["thoughts"]["z"].append(tz * scale_factor)
        particles["thoughts"]["c"].append(color)
        particles["thoughts"]["s"].append(6) # 较大的亮点
        
        insight = node.get('insight', '')
        if len(insight) > 60: insight = insight[:60] + "..."
        particles["thoughts"]["t"].append(f"<b>{node.get('care_point','?')}</b><br><span style='font-size:0.8em;color:#CCC'>{insight}</span>")

    return particles, primary_attr, secondary_attr
