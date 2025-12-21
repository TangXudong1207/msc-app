### msc_soul_gen.py ###
import random
import math
import numpy as np
import msc_config as config
import json

# ==========================================
# 🧹 强力清洗工具：解决 MarshallComponentException
# ==========================================
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

# ==========================================
# 🌌 1. 物理引擎参数映射
# ==========================================
def get_physics_config(primary_attr, secondary_attr):
    base_configs = {
        "Agency":        {"repulsion": 2500, "gravity": 0.01, "edgeLength": [50, 150]},
        "Care":          {"repulsion": 100,  "gravity": 0.8,  "edgeLength": [10, 30]},
        "Curiosity":     {"repulsion": 800,  "gravity": 0.05, "edgeLength": [100, 300]},
        "Coherence":     {"repulsion": 1000, "gravity": 0.2,  "edgeLength": [30, 60]},
        "Reflection":    {"repulsion": 600,  "gravity": 0.3,  "edgeLength": [40, 80]},
        "Transcendence": {"repulsion": 1500, "gravity": 0.0,  "edgeLength": [80, 200]},
        "Aesthetic":     {"repulsion": 500,  "gravity": 0.1,  "edgeLength": [50, 100]}
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

# ==========================================
# 🕸️ 2. 网络构建器
# ==========================================

config.DIMENSION_MAP_REV = {v: k for k, v in config.DIMENSION_MAP.items()}

def get_dimension_color(dim):
    return config.SPECTRUM.get(config.DIMENSION_MAP_REV.get(dim, "Structure"), "#FFFFFF")

def generate_soul_network(radar_dict, user_nodes):
    # 1. 数据准备
    if not radar_dict: radar_dict = {"Care": 3.0, "Reflection": 3.0}
    
    valid_keys = ["Care", "Curiosity", "Reflection", "Coherence", "Agency", "Aesthetic", "Transcendence"]
    clean_radar = {}
    for k, v in radar_dict.items():
        if k in valid_keys:
            try:
                val = float(v)
                if val > 0: clean_radar[k] = val
            except: pass
            
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

    # 🟢 获取“好奇 (Curiosity)”的颜色作为老数据默认色
    # 根据之前的配置，Curiosity 应该是绿色 (#00E676)
    default_old_data_color = config.SPECTRUM.get("Curiosity", "#00E676")

    # 2. 生成【思想节点】(主粒子)
    for i, user_node in enumerate(user_nodes):
        node_id = f"thought_{i}"
        kw = user_node.get('keywords', [])
        if isinstance(kw, str):
            try: kw = json.loads(kw)
            except: kw = []
            
        # 🟢 [逻辑]：默认设为好奇色。如果有关键词匹配，则覆盖为特定颜色。
        color = default_old_data_color 
        found_match = False
        
        if kw and isinstance(kw, list):
            for k in kw:
                if k in config.SPECTRUM:
                    color = config.SPECTRUM[k]
                    found_match = True
                    break 
        
        nodes.append({
            "id": node_id,
            "name": str(user_node.get('care_point', 'Thought')),
            # 🟢 [保持设计]：尺寸 25，精致感
            "symbolSize": 25,
            "itemStyle": {
                "color": color,
                # 如果是匹配到的特定色，用白边；如果是老数据(好奇色)，用浅绿边区分一下
                "borderColor": "#FFFFFF" if found_match else "#CCFFCC",
                "borderWidth": 2,
                "shadowBlur": 50, # 保持发光
                "shadowColor": color,
                "opacity": 1.0
            },
            "value": str(user_node.get('insight', '')),
            "color_category": color
        })
        node_indices[node_id] = len(nodes) - 1

    # 3. 生成【氛围粒子】(背景点)
    # 🟢 [性能优化]：砍掉 70% 的数量
    # 原逻辑是 len * 100，现在改为 len * 30，并设置硬上限 300
    base_count = len(user_nodes) * 30
    num_atmosphere = int(min(300, max(100, base_count)))
    
    for i in range(num_atmosphere):
        node_id = f"atmos_{i}"
        target_dim = random.choices(dims_list, weights=weights_list, k=1)[0]
        color = get_dimension_color(target_dim)
        
        size = float(random.uniform(3, 8))
        opacity = float(random.uniform(0.3, 0.7))

        nodes.append({
            "id": node_id,
            "name": "",
            "symbolSize": size,
            "itemStyle": {
                "color": color,
                "borderColor": color,
                "borderWidth": 0.5,
                "opacity": opacity
            },
            "color_category": color
        })
        node_indices[node_id] = len(nodes) - 1

    # 4. 建立连接
    thought_node_ids = [n["id"] for n in nodes if n["id"].startswith("thought")]
    atmos_node_ids = [n["id"] for n in nodes if n["id"].startswith("atmos")]
    
    for atmos_id in atmos_node_ids:
        source_idx = node_indices[atmos_id]
        source_color = nodes[source_idx]["color_category"]
        
        # 🟢 [性能优化]：每个氛围粒子最多只连 1 条线，且优先连接同色
        target_pool = thought_node_ids if (thought_node_ids and random.random() < 0.4) else atmos_node_ids

        # 采样，避免遍历太多
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
