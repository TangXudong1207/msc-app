### msc_soul_gen.py ###
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
    # repulsion: 斥力大小，决定节点散开的程度
    # gravity: 中心引力，决定节点向中心聚集的程度
    # edgeLength: 理想边长，决定网络的紧密/松散
    base_configs = {
        "Agency":        {"repulsion": 2500, "gravity": 0.01, "edgeLength": [50, 150]},  # 爆发结构：强斥力，极弱引力
        "Care":          {"repulsion": 100,  "gravity": 0.8,  "edgeLength": [10, 30]},   # 凝聚结构：极弱斥力，强中心引力
        "Curiosity":     {"repulsion": 800,  "gravity": 0.05, "edgeLength": [100, 300]}, # 发散网络：长边长，弱引力
        "Coherence":     {"repulsion": 1000, "gravity": 0.2,  "edgeLength": [30, 60]},   # 晶格结构：中等平衡
        "Reflection":    {"repulsion": 600,  "gravity": 0.3,  "edgeLength": [40, 80]},   # 深旋结构：中等配置，旋转靠后期力场
        "Transcendence": {"repulsion": 1500, "gravity": 0.0,  "edgeLength": [80, 200]},  # 升腾云：无中心引力，松散
        "Aesthetic":     {"repulsion": 500,  "gravity": 0.1,  "edgeLength": [50, 100]}   # 和谐球体：完美平衡
    }
    
    # --- 氛围维度 (Secondary) -> 定义动态气质 (影响摩擦力、速度) ---
    # friction: 摩擦力 (0.0-1.0)，越小停下来的速度越慢，动态感越强
    aspect_configs = {
        "Agency":        {"friction": 0.1}, # 躁动：极低摩擦，停不下来
        "Care":          {"friction": 0.8}, # 柔缓：高摩擦，缓慢移动
        "Curiosity":     {"friction": 0.3}, # 流转：中低摩擦
        "Coherence":     {"friction": 0.9}, # 稳定：极高摩擦，很快静止
        "Reflection":    {"friction": 0.5}, # 呼吸：中等摩擦
        "Transcendence": {"friction": 0.05},# 漂浮：几乎无摩擦，永远漂浮
        "Aesthetic":     {"friction": 0.4}  # 优雅：中等偏低
    }

    # 获取配置，如果未知则使用默认值
    p_conf = base_configs.get(primary_attr, base_configs["Aesthetic"])
    s_conf = aspect_configs.get(secondary_attr, aspect_configs["Aesthetic"])
    
    # 合并配置
    physics_config = {**p_conf, **s_conf}

    # --- 特殊力场标志 (在可视化层处理) ---
    physics_config["force_field"] = "none"
    if primary_attr == "Reflection": physics_config["force_field"] = "rotate" # 深旋
    if primary_attr == "Transcendence": physics_config["force_field"] = "ascend" # 升腾

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
    
    # 按分数排序，分数作为权重
    sorted_dims = sorted(clean_radar.items(), key=lambda x: x[1], reverse=True)
    primary_attr = sorted_attr[0][0]
    secondary_attr = sorted_attr[1][0] if len(sorted_attr) > 1 else primary_attr
    
    # 计算每个维度的权重比例，用于生成氛围粒子
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
        # 尝试从节点的关键词获取颜色，如果没有则用主维度颜色
        kw = user_node.get('keywords', [])
        if kw:
            # 简化的颜色查找
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
                "borderColor": "#FFFFFF", # 白光描边
                "borderWidth": 3,
                "shadowBlur": 50, # 强烈的发光效果
                "shadowColor": color,
                "opacity": 1.0
            },
            # 用于标签显示的内容
            "value": user_node.get('insight', ''), 
            # 自定义属性：颜色类别，用于连接计算
            "color_category": color
        })
        node_indices[node_id] = len(nodes) - 1

    # 3. 生成【氛围粒子】(Atmosphere Particles) - 微小、跟随
    # 粒子数量根据用户节点数动态调整，保证足够的氛围感
    num_atmosphere = max(500, len(user_nodes) * 100)
    
    for i in range(num_atmosphere):
        node_id = f"atmos_{i}"
        # 根据雷达权重随机选择一个所属维度
        target_dim = random.choices(dims_list, weights=weights_list, k=1)[0]
        color = get_dimension_color(target_dim)
        
        # 随机大小，增加层次感
        size = random.uniform(3, 8)
        # 透明度随机，增加虚无感
        opacity = random.uniform(0.3, 0.7)

        nodes.append({
            "id": node_id,
            "name": "", # 氛围粒子不显示名字
            "symbolSize": size,
            "itemStyle": {
                "color": color,
                "borderColor": color, # 自身颜色描边，增加一点实体感
                "borderWidth": 0.5,
                "opacity": opacity
            },
             # 自定义属性：颜色类别
            "color_category": color
        })
        node_indices[node_id] = len(nodes) - 1

    # 4. 建立连接 (Edges) - 核心逻辑：颜色优先连接
    # 规则：每个氛围粒子连接 1-2 个其他节点
    # 80% 概率连接同色节点，20% 概率连接异色节点
    
    thought_node_ids = [n["id"] for n in nodes if n["id"].startswith("thought")]
    atmos_node_ids = [n["id"] for n in nodes if n["id"].startswith("atmos")]
    
    for atmos_id in atmos_node_ids:
        source_idx = node_indices[atmos_id]
        source_color = nodes[source_idx]["color_category"]
        
        # 决定连接次数 (1 或 2)
        num_links = random.choices([1, 2], weights=[0.7, 0.3])[0]
        
        for _ in range(num_links):
            # 决定连接目标类型：优先连接思想节点作为核心
            if thought_node_ids and random.random() < 0.3: # 30%概率连接思想节点
                 target_pool = thought_node_ids
            else:
                 target_pool = atmos_node_ids # 70%概率连接其他氛围粒子

            # 过滤目标池
            same_color_targets = []
            diff_color_targets = []
            for tid in target_pool:
                if tid == atmos_id: continue # 不连接自己
                t_idx = node_indices[tid]
                if nodes[t_idx]["color_category"] == source_color:
                    same_color_targets.append(tid)
                else:
                    diff_color_targets.append(tid)
            
            target_id = None
            # 80% 概率尝试连接同色
            if random.random() < 0.8 and same_color_targets:
                target_id = random.choice(same_color_targets)
            # 20% 概率，或没有同色目标时，连接异色
            elif diff_color_targets:
                 target_id = random.choice(diff_color_targets)
            # 如果实在没得连（比如只有一种颜色），就随机连同色
            elif same_color_targets:
                target_id = random.choice(same_color_targets)

            if target_id:
                target_idx = node_indices[target_id]
                edges.append({
                    "source": source_idx, # 使用索引而不是ID，性能更好
                    "target": target_idx,
                    "lineStyle": {
                        "color": source_color, # 线条颜色跟随源节点
                        "opacity": 0.1,        # 线条非常淡，若隐若现
                        "width": 0.5
                    }
                })

    # 获取物理配置
    physics_config = get_physics_config(primary_attr, secondary_attr)

    return nodes, edges, physics_config, primary_attr, secondary_attr
