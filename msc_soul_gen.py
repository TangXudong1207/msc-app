### msc_soul_gen.py ###
import random
import math
import numpy as np
import msc_config as config

# ==========================================
# 🧹 强力清洗工具：彻底清除 Numpy 类型
# ==========================================
def clean_for_json(obj):
    """
    递归地将所有 numpy 类型转换为原生 Python 类型 (int, float, list, dict)。
    这是解决 MarshallComponentException 的关键。
    """
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
    """根据基底和氛围维度，返回物理引擎配置字典"""
    
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
    
    # 合并配置
    physics_config = {**p_conf, **s_conf}
    return physics_config

# ==========================================
# 🕸️ 2. 网络构建器
# ==========================================

config.DIMENSION_MAP_REV = {v: k for k, v in config.DIMENSION_MAP.items()}

def get_dimension_color(dim):
    """获取维度的颜色"""
    return config.SPECTRUM.get(config.DIMENSION_MAP_REV.get(dim, "Structure"), "#FFFFFF")

def generate_soul_network(radar_dict, user_nodes):
    """生成符合物理规则的灵魂网络数据"""
    
    # 1. 数据准备
    if not radar_dict: radar_dict = {"Care": 3.0, "Reflection": 3.0}
    
    # 过滤无效键
    valid_keys = ["Care", "Curiosity", "Reflection", "Coherence", "Agency", "Aesthetic", "Transcendence"]
    clean_radar = {}
    for k, v in radar_dict.items():
        if k in valid_keys:
            try:
                val = float(v) # 强制转 float
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

    # 2. 生成【思想节点】
    for i, user_node in enumerate(user_nodes):
        node_id = f"thought_{i}"
        kw = user_node.get('keywords', [])
        # 确保 kw 是列表
        if isinstance(kw, str):
            try: kw = json.loads(kw)
            except: kw = []
            
        color = "#FFFFFF"
        if kw and isinstance(kw, list):
            for k in kw:
                for dim_name, dim_color in config.SPECTRUM.items():
                    if k == dim_name:
                        color = dim_color
                        break
        else:
            color = get_dimension_color(primary_attr)

        nodes.append({
            "id": node_id,
            "name": str(user_node.get('care_point', 'Thought')), # 强制转字符串
            # 🟢 [修改点]：尺寸从 60 减小到 25，使其更精致
            "symbolSize": 25, 
            "itemStyle": {
                "color": color,
                "borderColor": "#FFFFFF",
                "borderWidth": 2, # 边框稍微变细一点
                # 🟢 [关键]：ShadowBlur 配合 viz 中的 bloom 产生发光感
                "shadowBlur": 50, 
                "shadowColor": color,
                "opacity": 1.0
            },
            "value": str(user_node.get('insight', '')), # 强制转字符串
            "color_category": color
        })
        node_indices[node_id] = len(nodes) - 1

    # 3. 生成【氛围粒子】
    num_atmosphere = max(500, len(user_nodes) * 100)
    
    for i in range(num_atmosphere):
        node_id = f"atmos_{i}"
        
        # 随机选择维度
        target_dim = random.choices(dims_list, weights=weights_list, k=1)[0]
        color = get_dimension_color(target_dim)
        
        size = float(random.uniform(3, 8)) # 强制 float
        opacity = float(random.uniform(0.3, 0.7)) # 强制 float

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
        
        num_links = random.choices([1, 2], weights=[0.7, 0.3])[0]
        
        for _ in range(num_links):
            if thought_node_ids and random.random() < 0.3:
                 target_pool = thought_node_ids
            else:
                 target_pool = atmos_node_ids

            same_color_targets = []
            diff_color_targets = []
            
            # 简化选择逻辑以提高性能
            if len(target_pool) > 50:
                sample_pool = random.sample(target_pool, 20)
            else:
                sample_pool = target_pool

            for tid in sample_pool:
                if tid == atmos_id: continue
                t_idx = node_indices[tid]
                if nodes[t_idx]["color_category"] == source_color:
                    same_color_targets.append(tid)
                else:
                    diff_color_targets.append(tid)
            
            target_id = None
            if random.random() < 0.8 and same_color_targets:
                target_id = random.choice(same_color_targets)
            elif diff_color_targets:
                 target_id = random.choice(diff_color_targets)
            elif same_color_targets:
                target_id = random.choice(same_color_targets)

            if target_id:
                target_idx = node_indices[target_id]
                edges.append({
                    "source": int(source_idx), # 强制 int
                    "target": int(target_idx), # 强制 int
                    "lineStyle": {
                        "color": source_color,
                        "opacity": 0.1,
                        "width": 0.5
                    }
                })

    raw_physics = get_physics_config(primary_attr, secondary_attr)

    # 🔴 核心修复：在返回前，调用清洗函数，将所有数据转换为原生类型
    return (
        clean_for_json(nodes), 
        clean_for_json(edges), 
        clean_for_json(raw_physics), 
        str(primary_attr), 
        str(secondary_attr)
    )
