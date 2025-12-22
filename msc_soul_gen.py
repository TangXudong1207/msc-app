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
    生成粒子数据：
    - 坐标基于 Primary Dimension (形态)
    - 动态物理将基于 Secondary Dimension (行为)
    """
    if not radar_dict: radar_dict = {"Care": 3.0, "Reflection": 3.0}

    # 1. 维度解析与排序
    valid_keys = config.RADAR_AXES
    clean_radar = {k: float(v) for k, v in radar_dict.items() if k in valid_keys and float(v) > 0}
    if not clean_radar: clean_radar = {"Reflection": 5.0}
    
    sorted_dims = sorted(clean_radar.items(), key=lambda x: x[1], reverse=True)
    
    # 🌟 核心逻辑：双维度提取
    primary_attr = sorted_dims[0][0] # 决定形状 (Shape)
    # 如果只有一个维度，次维度就是主维度本身
    secondary_attr = sorted_dims[1][0] if len(sorted_dims) > 1 else primary_attr # 决定动态 (Motion)

    dims_list = list(clean_radar.keys())
    total_w = sum(clean_radar.values())
    weights_list = [v/total_w for v in clean_radar.values()]

    # 2. 形态生成器 (Primary Dimension -> XYZ)
    # 基于您提供的物理参数隐喻：斥力(扩散度)、引力(向心度)
    def get_base_pos(shape_type):
        u = random.random(); v = random.random()
        theta = 2 * math.pi * u; phi = math.acos(2 * v - 1)
        
        # 🟥 Agency: 大爆炸 (高斥力, 低引力)
        if shape_type == "Agency":
            r = random.uniform(0.5, 3.0) # 扩散极远
            # 随机化方向，模拟无序爆炸
            return r*math.sin(phi)*math.cos(theta), r*math.sin(phi)*math.sin(theta), r*math.cos(phi)
            
        # 🟧 Care: 高密核心 (低斥力, 高引力)
        elif shape_type == "Care":
            r = random.uniform(0, 0.8) # 极度致密
            return r*math.sin(phi)*math.cos(theta), r*math.sin(phi)*math.sin(theta), r*math.cos(phi)
            
        # 🟨 Curiosity: 弥散星云 (中斥力, 不规则)
        elif shape_type == "Curiosity":
            # 多中心分布
            centers = [(1.0,0,0), (-0.5, 0.8, 0), (-0.5, -0.8, 0)]
            cx, cy, cz = random.choice(centers)
            return cx + random.gauss(0, 0.8), cy + random.gauss(0, 0.8), cz + random.gauss(0, 0.8)
            
        # 🟦 Coherence: 晶格矩阵 (高斥力, 有序)
        elif shape_type == "Coherence":
            step = 0.6
            x = round(random.gauss(0, 1.8)/step)*step
            y = round(random.gauss(0, 1.8)/step)*step
            z = round(random.gauss(0, 1.8)/step)*step
            return x, y, z
            
        # 🟪 Reflection: 漩涡盘 (平衡)
        elif shape_type == "Reflection":
            r = random.uniform(0.4, 2.2)
            angle = random.uniform(0, 2*math.pi)
            # 扁平化，Z轴压缩
            return r*math.cos(angle), r*math.sin(angle), random.gauss(0, 0.2)
            
        # 🟩 Transcendence: 升腾流 (高斥力, 零引力)
        elif shape_type == "Transcendence":
            h = random.uniform(-2.5, 2.5) # 垂直拉长
            w = random.gauss(0, 0.5) # 水平收窄
            return w*math.cos(theta), w*math.sin(theta), h
            
        # 🟪 Aesthetic: 和谐球壳 (平衡)
        elif shape_type == "Aesthetic":
            r = random.gauss(1.8, 0.15) # 空心球壳
            return r*math.sin(phi)*math.cos(theta), r*math.sin(phi)*math.sin(theta), r*math.cos(phi)
            
        else:
            r = random.gauss(0, 1.5)
            return r*math.sin(phi)*math.cos(theta), r*math.sin(phi)*math.sin(theta), r*math.cos(phi)

    # 3. 生成数据
    atmos_data = []
    thoughts_data = []

    # 粒子数量控制 (保证性能)
    num_atmos = int(min(450, max(250, len(user_nodes) * 25)))
    
    AXIS_COLOR = {
        "Care": config.SPECTRUM["Empathy"], "Agency": config.SPECTRUM["Vitality"],
        "Structure": config.SPECTRUM["Structure"], "Coherence": config.SPECTRUM["Rationality"],
        "Curiosity": config.SPECTRUM["Curiosity"], "Reflection": config.SPECTRUM["Melancholy"],
        "Aesthetic": config.SPECTRUM["Aesthetic"], "Transcendence": config.SPECTRUM["Consciousness"]
    }

    # 氛围粒子
    for _ in range(num_atmos):
        x, y, z = get_base_pos(primary_attr)
        dim = random.choices(dims_list, weights=weights_list, k=1)[0]
        color = AXIS_COLOR.get(dim, "#888888")
        
        atmos_data.append({
            "x": x, "y": y, "z": z, "c": color,
            "s": random.uniform(2.0, 4.5),
            "phase": random.uniform(0, 2*math.pi), # 动态相位
            "speed": random.uniform(0.8, 1.2)      # 个体速度差异
        })

    # 思想粒子
    for node in user_nodes:
        x, y, z = get_base_pos(primary_attr)
        # 思想粒子稍微向内收敛，作为骨架
        scale = 0.8
        x *= scale; y *= scale; z *= scale
        
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
            "s": 7.0, 
            "t": f"<b>{node.get('care_point','?')}</b><br><span style='font-size:0.8em;color:#CCC'>{insight}</span>",
            "phase": random.uniform(0, 2*math.pi),
            "speed": random.uniform(0.9, 1.1)
        })

    return {"atmos": atmos_data, "thoughts": thoughts_data}, primary_attr, secondary_attr
