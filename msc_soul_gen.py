import random
import math
import numpy as np
import msc_config as config

# ==========================================
# 🌌 1. 物理引擎参数映射 (Physics Parameter Mapping)
# ==========================================
# 这些参数将直接控制 GraphGL 的力引导布局引擎

def get_physics_config(primary_attr, secondary_attr):
    """根据基底和氛围维度，返回物理引擎配置字典"""
    
    # --- 基底维度 (Primary) -> 定义结构骨架 (影响引力、斥力) ---
    base_configs = {
        "Agency":        {"repulsion": 2500, "gravity": 0.01, "edgeLength": [50, 150]},  # 爆发结构
        "Care":          {"repulsion": 100,  "gravity": 0.8,  "edgeLength": [10, 30]},   # 凝聚结构
        "Curiosity":     {"repulsion": 800,  "gravity": 0.05, "edgeLength": [100, 300]}, # 发散网络
        "Coherence":     {"repulsion": 1000, "gravity": 0.2,  "edgeLength": [30, 60]},   # 晶格结构
        "Reflection":    {"repulsion": 600,  "gravity": 0.3,  "edgeLength": [40, 80]},   # 深旋结构
        "Transcendence": {"repulsion": 1500, "gravity": 0.0,  "edgeLength": [80, 200]},  # 升腾云
        "Aesthetic":     {"repulsion": 500,  "gravity": 0.1,  "edgeLength": [50, 100]}   # 和谐球体
    }
    
    # --- 氛围维度 (Secondary) -> 定义动态气质 (影响摩擦力) ---
    aspect_configs = {
        "Agency":        {"friction": 0.1}, # 躁动
        "Care":          {"friction": 0.8}, # 柔缓
        "Curiosity":     {"friction": 0.3}, # 流转
        "Coherence":     {"friction": 0.9}, # 稳定
        "Reflection":    {"friction": 0.5}, # 呼吸
        "Transcendence": {"friction": 0.05},# 漂浮
        "Aesthetic":     {"friction": 0.4}  # 优雅
    }

    # 获取配置，如果未知则使用默认值
    p_conf = base_configs.get(primary_attr, base_configs["Aesthetic"])
    s_conf = aspect_configs.get(secondary_attr, aspect_configs["Aesthetic"])
    
    # 合并配置
    physics_config = {**p_conf, **s_conf}

    return physics_config

# ==========================================
# 🕸️ 2. 网络构建器 (Network Builder)
# ==========================================

def get_dimension_color(dim):
    """获取维度的颜色"""
    return config.SPECTRUM.get(config.DIMENSION_MAP_REV.get(dim, "Structure"), "#FFFFFF")

# 建立反向映射以便查色
config.DIMENSION_MAP_REV = {v: k for k, v in config.DIMENSION_MAP.items()}

def generate_soul_network(radar_dict, user_nodes):
    """生成符合物理规则的灵魂网络数据 (节点和边)"""
    
    # 1. 确定主次维度
    if not radar_dict: radar_dict = {"Care": 3.0, "Reflection": 3.0}
    valid_keys = ["Care", "Curiosity", "Reflection", "Coherence", "Agency", "Aesthetic", "Transcendence"]
    clean_radar = {k: v for k, v in radar_dict.items() if k in valid_keys and v > 0}
    if not clean_radar: clean_radar = {"Care": 3.0, "Reflection": 3.0}
    
    # 按分数排序
    sorted_dims = sorted(clean_radar.items(), key=lambda x: x[1], reverse=True)
    
    # 🔴 修复点：使用正确的变量名 sorted_dims
    primary_attr = sorted_dims[0][0]
    secondary_attr = sorted_dims[1][0] if len(sorted_dims) > 1 else primary_attr
    
    # 计算每个维度的权重比例
    total_score = sum([s for d, s in sorted_dims])
    dim_weights = {d: s/total_score for d, s in sorted_dims}
    dims_list = list(dim_weights.keys())
    weights_list = list(dim_weights.values())

    nodes = []
    edges = []
    node_indices = {} # 用于记录节点ID到索引的映射

    # 2. 生成【思想节点】(Thought Nodes) - 巨大、发光的核心
    for i, user_node in enumerate(user_nodes):
        node_id = f"thought_{i}"
        kw = user_node.get('keywords', [])
        if kw:
            color = "#FFFFFF"
            for k in kw:
                for dim_name, dim_color in config.SPECTRUM.items():
                    if k == dim_name:
                        color = dim_color
                        break
        else:
            color = get_dimension_color(primary_attr)

        nodes.append({
            "id": node_id,
            "name": user_node.get('care_point', 'Thought'),
            "symbolSize": 60, # 巨大尺寸
            "itemStyle": {
                "color": color,
                "borderColor": "#FFFFFF",
                "borderWidth": 3,
                "shadowBlur": 50,
                "shadowColor": color,
                "opacity": 1.0
            },
            "value": user_node.get('insight', ''), 
            "color_category": color
        })
        node_indices[node_id] = len(nodes) - 1

    # 3. 生成【氛围粒子】(Atmosphere Particles) - 微小、跟随
    num_atmosphere = max(500, len(user_nodes) * 100)
    
    for i in range(num_atmosphere):
        node_id = f"atmos_{i}"
        target_dim = random.choices(dims_list, weights=weights_list, k=1)[0]
        color = get_dimension_color(target_dim)
        size = random.uniform(3, 8)
        opacity = random.uniform(0.3, 0.7)

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

    # 4. 建立连接 (Edges) - 核心逻辑：颜色优先连接
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
            for tid in target_pool:
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
                    "source": source_idx,
                    "target": target_idx,
                    "lineStyle": {
                        "color": source_color,
                        "opacity": 0.1,
                        "width": 0.5
                    }
                })

    # 获取物理配置
    physics_config = get_physics_config(primary_attr, secondary_attr)

    return nodes, edges, physics_config, primary_attr, secondary_attr
