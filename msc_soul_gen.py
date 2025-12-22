### msc_soul_gen.py ###
import random
import math
import numpy as np
import msc_config as config
import json
import networkx as nx

def clean_for_json(obj):
    if isinstance(obj, (np.integer, np.int64, np.int32)): return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)): return float(obj)
    elif isinstance(obj, np.ndarray): return clean_for_json(obj.tolist())
    elif isinstance(obj, dict): return {k: clean_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list): return [clean_for_json(v) for v in obj]
    else: return obj

def get_dimension_color(dim):
    # 查找颜色
    for axis, target_dim in config.DIMENSION_MAP.items():
        if target_dim == dim:
            return config.SPECTRUM.get(axis, "#FFFFFF")
    return "#FFFFFF"

def generate_soul_network(radar_dict, user_nodes):
    if not radar_dict: radar_dict = {k: 3.0 for k in config.RADAR_AXES}
    
    # 1. 提取核心维度
    valid_keys = config.RADAR_AXES
    clean_radar = {k: float(v) for k, v in radar_dict.items() if k in valid_keys}
    sorted_dims = sorted(clean_radar.items(), key=lambda x: x[1], reverse=True)
    primary_attr = sorted_dims[0][0]
    secondary_attr = sorted_dims[1][0] if len(sorted_dims) > 1 else primary_attr
    
    # 2. 构建图
    G = nx.Graph()
    dim_weights = {d: s/sum(clean_radar.values()) for d, s in sorted_dims}
    dims_list = list(dim_weights.keys())
    weights_list = list(dim_weights.values())

    # 添加思想节点 (核心粒子)
    for i, user_node in enumerate(user_nodes):
        node_id = f"thought_{i}"
        kw = user_node.get('keywords', [])
        if isinstance(kw, str):
            try: kw = json.loads(kw)
            except: kw = []
        
        color = "#00E676" # 默认绿色
        if isinstance(kw, list) and len(kw) > 0:
            color = config.SPECTRUM.get(kw[0], "#00E676")
        
        G.add_node(node_id, color=color, size=14, type='thought', 
                   name=str(user_node.get('care_point', 'Thought')),
                   insight=str(user_node.get('insight', '')))

    # 添加氛围粒子
    num_atmosphere = 150 # 减小数量提升性能
    for i in range(num_atmosphere):
        node_id = f"atmos_{i}"
        target_dim = random.choices(dims_list, weights=weights_list, k=1)[0]
        # 简单映射颜色
        color = "#FFFFFF"
        for k, v in config.DIMENSION_MAP.items():
            if v == target_dim:
                color = config.SPECTRUM.get(k, "#FFFFFF")
                break
        
        G.add_node(node_id, color=color, size=random.uniform(3, 6), type='atmos')

    # 3. 计算 3D 布局
    pos_3d = nx.spring_layout(G, dim=3, k=0.6, iterations=30, seed=42)

    # 🟢 核心修复：坐标归一化 (防止粒子飞出视野)
    # 将所有坐标压缩到 [-1, 1] 之间
    all_coords = np.array(list(pos_3d.values()))
    min_vals = all_coords.min(axis=0)
    max_vals = all_coords.max(axis=0)
    
    for node_id in pos_3d:
        # 归一化公式： (x - min) / (max - min) * 2 - 1
        pos_3d[node_id] = (pos_3d[node_id] - min_vals) / (max_vals - min_vals + 1e-6) * 2 - 1

    # 4. 导出数据
    plot_data = {
        "x": [], "y": [], "z": [],
        "color": [], "size": [], "text": [], "type": []
    }
    
    for node_id, coords in pos_3d.items():
        node_attrs = G.nodes[node_id]
        plot_data["x"].append(coords[0])
        plot_data["y"].append(coords[1])
        plot_data["z"].append(coords[2])
        plot_data["color"].append(node_attrs['color'])
        plot_data["size"].append(node_attrs['size'])
        if node_attrs['type'] == 'thought':
            plot_data["text"].append(f"<b>{node_attrs['name']}</b><br>{node_attrs['insight']}")
        else:
            plot_data["text"].append("")
        plot_data["type"].append(node_attrs['type'])
        
    return plot_data, primary_attr, secondary_attr
