### msc_soul_gen.py ###
import random
import math
import numpy as np
import msc_config as config
import json

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

# 🟢 [物理引擎重构]：增强重力，减小斥力，防止飞出，形成凝聚态
def get_physics_config(primary_attr, secondary_attr):
    # 基础配置：所有模式都显著增加了 gravity (从 0.x 增加到 1.0+)
    base_configs = {
        # 爆发结构：稍微松散一点，但依然有强重力
        "Agency":        {"repulsion": 800,  "gravity": 1.5, "edgeLength": [30, 80]},
        # 凝聚结构：极高的重力，紧密的一团
        "Care":          {"repulsion": 60,   "gravity": 4.0, "edgeLength": [5, 20]},
        # 发散网络：虽然发散，但为了不飞出去，重力也要够
        "Curiosity":     {"repulsion": 400,  "gravity": 1.2, "edgeLength": [50, 150]},
        # 晶格结构
        "Coherence":     {"repulsion": 500,  "gravity": 2.0, "edgeLength": [20, 50]},
        # 深旋结构
        "Reflection":    {"repulsion": 300,  "gravity": 2.5, "edgeLength": [20, 60]},
        # 升腾云结构
        "Transcendence": {"repulsion": 600,  "gravity": 1.0, "edgeLength": [40, 100]},
        # 和谐球体
        "Aesthetic":     {"repulsion": 200,  "gravity": 3.0, "edgeLength": [30, 80]}
    }
    
    aspect_configs = {
        "Agency":        {"friction": 0.1},
        "Care":          {"friction": 0.8},
        "Curiosity":     {"friction": 0.3},
        "Coherence":     {"friction": 0.9},
        "Reflection":    {"friction": 0.5},
        "Transcendence": {"friction": 0.05},
        "Aesthetic":     {"friction": 0.4}
    }
    p_conf = base_configs.get(primary_attr, base_configs["Aesthetic"])
    s_conf = aspect_configs.get(secondary_attr, aspect_configs["Aesthetic"])
    return {**p_conf, **s_conf}

config.DIMENSION_MAP_REV = {v: k for k, v in config.DIMENSION_MAP.items()}

def get_dimension_color(dim):
    return config.SPECTRUM.get(config.DIMENSION_MAP_REV.get(dim, "Structure"), "#FFFFFF")

def generate_soul_network(radar_dict, user_nodes):
    if not radar_dict: radar_dict = {"Care": 3.0, "Reflection": 3.0}
    
    valid_keys = ["Care", "Curiosity", "Reflection", "Coherence", "Agency", "Aesthetic", "Transcendence"]
    clean_radar = {}
    for k, v in radar_dict.items():
        if k in valid_keys:
            try: val = float(v); 
            except: val = 0
            if val > 0: clean_radar[k] = val
            
    if not clean_radar: clean_radar = {"Care": 3.0, "Reflection": 3.0}
    
    sorted_dims = sorted(clean_radar.items(), key=lambda x: x[1], reverse=True)
    primary_attr = sorted_dims[0][0]
    secondary_attr = sorted_dims[1][0] if len(sorted_dims) > 1 else primary_attr
    
    total_score = sum([s for d, s in sorted_dims])
    if total_score == 0: total_score = 1
    
    dim_weights = {d: s/total_score for d, s in sorted_dims}
    dims_list = list(dim_weights.keys())
    weights_list = list(dim_weights.values())

    nodes = []
    edges = []
    node_indices = {}

    default_old_data_color = "#00E676" 

    # 2. 生成【思想节点】(主粒子)
    for i, user_node in enumerate(user_nodes):
        node_id = f"thought_{i}"
        kw = user_node.get('keywords', [])
        
        if isinstance(kw, str):
            try: kw = json.loads(kw)
            except: kw = []
        if kw is None: kw = []
            
        color = default_old_data_color 
        found_match = False
        
        if isinstance(kw, list) and len(kw) > 0:
            for k in kw:
                if k in config.SPECTRUM:
                    color = config.SPECTRUM[k]
                    found_match = True
                    break 
        
        nodes.append({
            "id": node_id,
            "name": str(user_node.get('care_point', 'Thought')),
            # 🟢 [修改点]：缩小为主粒子的 2/3 (原25 -> 16)
            "symbolSize": 16,
            "itemStyle": {
                "color": color,
                "borderColor": "#FFFFFF" if found_match else "#CCFFCC",
                "borderWidth": 1.5,
                # 🟢 [修改点]：增加 ShadowBlur，配合 Bloom 产生更强光晕
                "shadowBlur": 80, 
                "shadowColor": color,
                "opacity": 1.0
            },
            "value": str(user_node.get('insight', '')),
            "color_category": color
        })
        node_indices[node_id] = len(nodes) - 1

    # 3. 生成【氛围粒子】(背景点，形成彗星尾巴)
    # 🟢 [修改点]：增加数量，形成“雾/彗星”感
    # 系数从 5 -> 15，上限从 100 -> 250
    base_count = len(user_nodes) * 15
    num_atmosphere = int(min(250, max(80, base_count)))
    
    for i in range(num_atmosphere):
        node_id = f"atmos_{i}"
        target_dim = random.choices(dims_list, weights=weights_list, k=1)[0]
        color = get_dimension_color(target_dim)
        
        # 尺寸稍微随机大一点点，形成光斑感
        size = float(random.uniform(2, 6))
        opacity = float(random.uniform(0.3, 0.6)) 

        nodes.append({
            "id": node_id,
            "name": "",
            "symbolSize": size,
            "itemStyle": {
                "color": color,
                "borderColor": color,
                "borderWidth": 0,
                "opacity": opacity
            },
            "color_category": color
        })
        node_indices[node_id] = len(nodes) - 1

    # 4. 建立连接 (保持稀疏连接)
    thought_node_ids = [n["id"] for n in nodes if n["id"].startswith("thought")]
    atmos_node_ids = [n["id"] for n in nodes if n["id"].startswith("atmos")]
    
    for atmos_id in atmos_node_ids:
        source_idx = node_indices[atmos_id]
        source_color = nodes[source_idx]["color_category"]
        
        target_pool = thought_node_ids if (thought_node_ids and random.random() < 0.3) else atmos_node_ids
        if len(target_pool) > 20: sample_pool = random.sample(target_pool, 10)
        else: sample_pool = target_pool

        target_id = None
        same = [t for t in sample_pool if t!=atmos_id and nodes[node_indices[t]]["color_category"]==source_color]
        
        if same: target_id = random.choice(same)
        elif sample_pool: target_id = random.choice(sample_pool)

        if target_id:
            target_idx = node_indices[target_id]
            edges.append({
                "source": int(source_idx),
                "target": int(target_idx),
                "lineStyle": {
                    "color": source_color,
                    "opacity": 0.15, # 稍微增加一点连接线的可见度
                    "width": 0.5
                }
            })

    raw_physics = get_physics_config(primary_attr, secondary_attr)

    return (
        clean_for_json(nodes), 
        clean_for_json(edges), 
        clean_for_json(raw_physics), 
        str(primary_attr), 
        str(secondary_attr)
    )
