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

def get_physics_config(primary_attr, secondary_attr):
    # 🟢 [关键修改]：让粒子飘起来！
    # 1. 摩擦力极低 (0.05)，保持运动惯性
    # 2. 重力极低 (0.1 - 0.3)，不再死死吸在中间，允许扩散
    # 3. 斥力适中，连线变长
    
    base_friction = 0.05 
    
    base_configs = {
        # 爆发结构：大范围扩散
        "Agency":        {"repulsion": 1000, "gravity": 0.1, "edgeLength": [100, 300]},
        # 凝聚结构：虽然凝聚，但也允许外围飘荡
        "Care":          {"repulsion": 300,  "gravity": 0.5, "edgeLength": [20, 100]},
        # 发散网络：极度发散
        "Curiosity":     {"repulsion": 1200, "gravity": 0.05, "edgeLength": [150, 400]},
        # 晶格结构
        "Coherence":     {"repulsion": 800,  "gravity": 0.2, "edgeLength": [50, 150]},
        # 深旋结构
        "Reflection":    {"repulsion": 600,  "gravity": 0.3, "edgeLength": [50, 200]},
        # 升腾云结构：反重力感
        "Transcendence": {"repulsion": 1500, "gravity": 0.02, "edgeLength": [100, 400]},
        # 和谐球体
        "Aesthetic":     {"repulsion": 500,  "gravity": 0.2, "edgeLength": [50, 200]}
    }
    
    aspect_configs = {k: {"friction": base_friction} for k in base_configs.keys()}

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
            "symbolSize": 16,
            "itemStyle": {
                "color": color,
                "borderColor": "#FFFFFF" if found_match else "#CCFFCC",
                "borderWidth": 1.5,
                "shadowBlur": 80, 
                "shadowColor": color,
                "opacity": 1.0
            },
            "value": str(user_node.get('insight', '')),
            "color_category": color
        })
        node_indices[node_id] = len(nodes) - 1

    # 3. 生成【氛围粒子】(填充空间)
    # 🟢 [修改点]：增加填充粒子，系数提升到 30
    base_count = len(user_nodes) * 30
    num_atmosphere = int(min(400, max(150, base_count)))
    
    for i in range(num_atmosphere):
        node_id = f"atmos_{i}"
        target_dim = random.choices(dims_list, weights=weights_list, k=1)[0]
        color = get_dimension_color(target_dim)
        
        # 尺寸差异化，有的很小像尘埃，有的大一点像卫星
        size = float(random.uniform(1, 5))
        opacity = float(random.uniform(0.2, 0.6)) 

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

    # 4. 建立连接 (松散连接)
    thought_node_ids = [n["id"] for n in nodes if n["id"].startswith("thought")]
    atmos_node_ids = [n["id"] for n in nodes if n["id"].startswith("atmos")]
    
    for atmos_id in atmos_node_ids:
        source_idx = node_indices[atmos_id]
        source_color = nodes[source_idx]["color_category"]
        
        # 🟢 [关键逻辑]：让部分氛围粒子“断线”，或者连向其他氛围粒子，而不是全连主粒子
        # 这样它们就会因为没有弹簧拉力，而在微弱重力下飘得更远
        rand_val = random.random()
        
        if rand_val < 0.2:
             target_pool = thought_node_ids # 20% 紧跟主粒子
        elif rand_val < 0.6:
             target_pool = atmos_node_ids # 40% 互连，形成云团
        else:
             target_pool = [] # 40% 不连线！变成自由漂浮的尘埃！
             
        if target_pool:
            if len(target_pool) > 20: sample_pool = random.sample(target_pool, 5)
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
                        "opacity": 0.1,
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
