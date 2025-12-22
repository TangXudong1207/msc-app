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
    物理引擎数据生成器
    返回：初始位置(pos)，颜色(color)，大小(size)，以及物理属性(velocity/phase)
    """
    if not radar_dict: radar_dict = {"Care": 3.0, "Reflection": 3.0}

    # 1. 确定主属性
    valid_keys = config.RADAR_AXES
    clean_radar = {k: float(v) for k, v in radar_dict.items() if k in valid_keys and float(v) > 0}
    if not clean_radar: clean_radar = {"Reflection": 5.0}
    
    sorted_dims = sorted(clean_radar.items(), key=lambda x: x[1], reverse=True)
    primary_attr = sorted_dims[0][0]
    
    # 颜色权重
    total_score = sum(clean_radar.values())
    dims_list = list(clean_radar.keys())
    weights_list = [v/total_score for v in clean_radar.values()]

    # ---------------------------------------------------------
    # 🌌 初始分布函数 (静态形态)
    # ---------------------------------------------------------
    def get_initial_pos(shape_type):
        u = random.random(); v = random.random()
        theta = 2 * math.pi * u; phi = math.acos(2 * v - 1)
        
        # 针对不同类型的初始分布优化
        if shape_type == "Agency": # 爆发
            r = random.uniform(0.1, 2.0)
            return r * math.sin(phi) * math.cos(theta), r * math.sin(phi) * math.sin(theta), r * math.cos(phi)
        elif shape_type == "Coherence": # 晶格
            step = 0.6
            x = round(random.gauss(0, 1.5)/step)*step
            y = round(random.gauss(0, 1.5)/step)*step
            z = round(random.gauss(0, 1.5)/step)*step
            return x, y, z
        elif shape_type == "Reflection": # 漩涡
            r_flat = random.uniform(0.2, 2.0)
            angle = random.uniform(0, 2*math.pi)
            return r_flat * math.cos(angle), r_flat * math.sin(angle), random.gauss(0, 0.2) * (2.0 - r_flat)
        elif shape_type == "Transcendence": # 升腾柱
            h = random.uniform(-2, 2)
            w = random.gauss(0, 0.5)
            return w * math.cos(theta), w * math.sin(theta), h
        elif shape_type == "Aesthetic": # 球壳
            r = random.gauss(1.8, 0.1)
            return r * math.sin(phi) * math.cos(theta), r * math.sin(phi) * math.sin(theta), r * math.cos(phi)
        else: # 默认云团
            r = random.gauss(0, 1.2)
            return r * math.sin(phi) * math.cos(theta), r * math.sin(phi) * math.sin(theta), r * math.cos(phi)

    # ---------------------------------------------------------
    # 🧪 数据容器
    # ---------------------------------------------------------
    # 使用 List 收集，最后转 NumPy
    atmos_data = [] 
    thoughts_data = []

    # 1. 生成氛围 (Atmosphere) - 增加数量以增强体积感
    num_atmos = int(min(800, max(400, len(user_nodes) * 40)))
    
    AXIS_COLOR = {
        "Care": config.SPECTRUM["Empathy"], "Agency": config.SPECTRUM["Vitality"],
        "Structure": config.SPECTRUM["Structure"], "Coherence": config.SPECTRUM["Rationality"],
        "Curiosity": config.SPECTRUM["Curiosity"], "Reflection": config.SPECTRUM["Melancholy"],
        "Aesthetic": config.SPECTRUM["Aesthetic"], "Transcendence": config.SPECTRUM["Consciousness"]
    }

    for _ in range(num_atmos):
        x, y, z = get_initial_pos(primary_attr)
        dim = random.choices(dims_list, weights=weights_list, k=1)[0]
        color = AXIS_COLOR.get(dim, "#888888")
        
        # 随机相位和速度，用于物理计算
        phase = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0.5, 1.5)
        
        atmos_data.append({
            "x": x, "y": y, "z": z, "c": color, 
            "s": random.uniform(1.0, 3.5), 
            "phase": phase, "speed": speed
        })

    # 2. 生成思想恒星 (Thoughts)
    for node in user_nodes:
        x, y, z = get_initial_pos(primary_attr)
        # 向中心收缩一点
        x *= 0.8; y *= 0.8; z *= 0.8
        
        kw = node.get('keywords', [])
        if isinstance(kw, str):
            try: kw = json.loads(kw)
            except: kw = []
        color = "#FFFFFF"
        if kw:
            for k in kw: 
                if k in config.SPECTRUM: color = config.SPECTRUM[k]; break
        
        insight = node.get('insight', '')
        if len(insight) > 60: insight = insight[:60] + "..."
        tooltip = f"<b>{node.get('care_point','?')}</b><br><span style='font-size:0.8em;color:#CCC'>{insight}</span>"
        
        thoughts_data.append({
            "x": x, "y": y, "z": z, "c": color, 
            "s": 7, "t": tooltip,
            "phase": random.uniform(0, 2 * math.pi), "speed": random.uniform(0.8, 1.2)
        })

    return {"atmos": atmos_data, "thoughts": thoughts_data}, primary_attr
