### msc_soul_gen.py ###
import random
import math
import numpy as np
import msc_config as config
import json

def clean_for_json(obj):
    if isinstance(obj, (np.integer, np.int64, np.int32)): return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)): return float(obj)
    elif isinstance(obj, np.ndarray): return clean_for_json(obj.tolist())
    elif isinstance(obj, dict): return {k: clean_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list): return [clean_for_json(v) for v in obj]
    else: return obj

def generate_nebula_data(radar_dict, user_nodes):
    """
    生成带有物理属性(相位、速度)的粒子数据
    """
    if not radar_dict: radar_dict = {"Care": 3.0, "Reflection": 3.0}

    # 1. 确定主属性
    valid_keys = config.RADAR_AXES
    clean_radar = {k: float(v) for k, v in radar_dict.items() if k in valid_keys and float(v) > 0}
    if not clean_radar: clean_radar = {"Reflection": 5.0}
    
    sorted_dims = sorted(clean_radar.items(), key=lambda x: x[1], reverse=True)
    primary_attr = sorted_dims[0][0]
    
    dims_list = list(clean_radar.keys())
    total_w = sum(clean_radar.values())
    weights_list = [v/total_w for v in clean_radar.values()]

    # 2. 初始分布函数
    def get_base_pos(shape):
        u = random.random(); v = random.random()
        theta = 2 * math.pi * u; phi = math.acos(2 * v - 1)
        if shape == "Agency": # 爆发
            r = random.uniform(0.1, 2.5)
            return r*math.sin(phi)*math.cos(theta), r*math.sin(phi)*math.sin(theta), r*math.cos(phi)
        elif shape == "Reflection": # 漩涡
            r = random.uniform(0.3, 2.2); angle = random.uniform(0, 2*math.pi)
            return r*math.cos(angle), r*math.sin(angle), random.gauss(0, 0.3)*(2.5-r)
        elif shape == "Transcendence": # 升腾
            h = random.uniform(-2, 2); w = random.gauss(0, 0.6)
            return w*math.cos(theta), w*math.sin(theta), h
        elif shape == "Care": # 核心
            r = random.uniform(0, 1.2)**2
            return r*math.sin(phi)*math.cos(theta), r*math.sin(phi)*math.sin(theta), r*math.cos(phi)
        else: # 默认云团
            r = random.gauss(0, 1.4)
            return r*math.sin(phi)*math.cos(theta), r*math.sin(phi)*math.sin(theta), r*math.cos(phi)

    # 3. 生成数据
    atmos_data = []
    thoughts_data = []

    # 🟢 优化：减少粒子数量，提升单个粒子质量，防止卡顿
    num_atmos = int(min(400, max(200, len(user_nodes) * 20))) 
    
    AXIS_COLOR = {
        "Care": config.SPECTRUM["Empathy"], "Agency": config.SPECTRUM["Vitality"],
        "Structure": config.SPECTRUM["Structure"], "Coherence": config.SPECTRUM["Rationality"],
        "Curiosity": config.SPECTRUM["Curiosity"], "Reflection": config.SPECTRUM["Melancholy"],
        "Aesthetic": config.SPECTRUM["Aesthetic"], "Transcendence": config.SPECTRUM["Consciousness"]
    }

    # 生成氛围粒子
    for _ in range(num_atmos):
        x, y, z = get_base_pos(primary_attr)
        dim = random.choices(dims_list, weights=weights_list, k=1)[0]
        color = AXIS_COLOR.get(dim, "#888888")
        
        atmos_data.append({
            "x": x, "y": y, "z": z, "c": color,
            "s": random.uniform(2.0, 5.0), # 粒子变大，增强视觉
            "phase": random.uniform(0, 2*math.pi), # 随机相位
            "speed": random.uniform(0.5, 1.5)      # 随机速度
        })

    # 生成思想粒子
    for node in user_nodes:
        x, y, z = get_base_pos(primary_attr)
        x *= 0.7; y *= 0.7; z *= 0.7 # 收缩在内部
        
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
        
        thoughts_data.append({
            "x": x, "y": y, "z": z, "c": color,
            "s": 8, # 恒星更大
            "t": f"<b>{node.get('care_point','?')}</b><br><span style='font-size:0.8em;color:#CCC'>{insight}</span>",
            "phase": random.uniform(0, 2*math.pi),
            "speed": random.uniform(0.8, 1.2)
        })

    return {"atmos": atmos_data, "thoughts": thoughts_data}, primary_attr
