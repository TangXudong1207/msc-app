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

def prepare_soul_data(radar_dict, user_nodes):
    """
    为 JS 引擎准备数据包
    """
    if not radar_dict: radar_dict = {"Care": 3.0, "Reflection": 3.0}

    # 1. 维度解析
    valid_keys = config.RADAR_AXES
    clean_radar = {k: float(v) for k, v in radar_dict.items() if k in valid_keys and float(v) > 0}
    if not clean_radar: clean_radar = {"Reflection": 5.0}
    
    sorted_dims = sorted(clean_radar.items(), key=lambda x: x[1], reverse=True)
    primary_attr = sorted_dims[0][0]
    secondary_attr = sorted_dims[1][0] if len(sorted_dims) > 1 else primary_attr

    # 2. 颜色映射表
    AXIS_COLOR = {
        "Care": config.SPECTRUM["Empathy"], "Agency": config.SPECTRUM["Vitality"],
        "Structure": config.SPECTRUM["Structure"], "Coherence": config.SPECTRUM["Rationality"],
        "Curiosity": config.SPECTRUM["Curiosity"], "Reflection": config.SPECTRUM["Melancholy"],
        "Aesthetic": config.SPECTRUM["Aesthetic"], "Transcendence": config.SPECTRUM["Consciousness"]
    }
    
    # 3. 思想节点数据 (Thoughts)
    thoughts_payload = []
    for node in user_nodes:
        kw = node.get('keywords', [])
        if isinstance(kw, str):
            try: kw = json.loads(kw)
            except: kw = []
        
        # 确定颜色
        color = "#FFFFFF"
        if kw:
            for k in kw: 
                if k in config.SPECTRUM: color = config.SPECTRUM[k]; break
        
        safe_content = node.get('care_point','?').replace('"', '&quot;')
        safe_insight = node.get('insight', '').replace('"', '&quot;')
        
        thoughts_payload.append({
            "color": color,
            "text": safe_content,
            "insight": safe_insight
        })

    # 4. 氛围数据 (Atmosphere)
    total_w = sum(clean_radar.values())
    weights = {k: v/total_w for k,v in clean_radar.items()}
    
    # 计算氛围颜色池
    atmos_colors = []
    for k, w in weights.items():
        count = int(w * 100)
        c = AXIS_COLOR.get(k, "#888888")
        atmos_colors.extend([c] * count)
    if not atmos_colors: atmos_colors = ["#888888"]

    payload = {
        "primary": primary_attr,
        "secondary": secondary_attr,
        "thoughts": thoughts_payload,
        "atmos_colors": atmos_colors,
        "node_count": len(user_nodes)
    }
    
    return payload, primary_attr, secondary_attr
