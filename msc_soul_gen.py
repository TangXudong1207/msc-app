### msc_soul_gen.py ###
import random
import numpy as np
import msc_config as config
import json
import networkx as nx

def generate_soul_network(radar_dict, user_nodes):
    # 1. 数据清洗与维度提取
    if not radar_dict: 
        radar_dict = {k: 3.0 for k in config.RADAR_AXES}
    
    valid_keys = config.RADAR_AXES
    clean_radar = {k: float(radar_dict.get(k, 3.0)) for k in valid_keys}
    
    # 排序提取 主维度(Primary) 和 次维度(Secondary)
    sorted_dims = sorted(clean_radar.items(), key=lambda x: x[1], reverse=True)
    primary_attr = sorted_dims[0][0]
    secondary_attr = sorted_dims[1][0] if len(sorted_dims) > 1 else primary_attr
    
    # 2. 构建图网络
    G = nx.Graph()
    total_val = sum(clean_radar.values())
    dim_weights = {d: s/total_val for d, s in sorted_dims}
    dims_list, weights_list = list(dim_weights.keys()), list(dim_weights.values())

    # --- 添加核心思想粒子 ---
    for i, user_node in enumerate(user_nodes):
        node_id = f"thought_{i}"
        kw = user_node.get('keywords', [])
        if isinstance(kw, str):
            try: kw = json.loads(kw)
            except: kw = []
        
        # 颜色匹配
        color = "#00E676" 
        if isinstance(kw, list) and len(kw) > 0:
            color = config.SPECTRUM.get(kw[0], "#00E676")
        
        G.add_node(node_id, color=color, size=15, type='thought', 
                   name=str(user_node.get('care_point', 'Thought')),
                   insight=str(user_node.get('insight', '')))

    # --- 添加氛围背景粒子 ---
    num_atmosphere = 160 
    for i in range(num_atmosphere):
        node_id = f"atmos_{i}"
        target_dim = random.choices(dims_list, weights=weights_list, k=1)[0]
        
        # 查找颜色
        color = "#FFFFFF"
        for k, v in config.DIMENSION_MAP.items():
            if v == target_dim:
                color = config.SPECTRUM.get(k, "#FFFFFF")
                break
        
        G.add_node(node_id, color=color, size=random.uniform(3, 7), type='atmos')

    # 3. 计算 3D 布局 (Spring Layout)
    # seed=None 确保每次计算都有随机微动，增加“生命感”
    pos_3d = nx.spring_layout(G, dim=3, k=0.5, iterations=50, seed=None)

    # 🟢 核心修复：坐标归一化 (Normalization)
    # 无论计算结果如何，强制将所有点压缩到 [-1, 1] 的空间内
    coords_array = np.array(list(pos_3d.values()))
    c_min = coords_array.min(axis=0)
    c_max = coords_array.max(axis=0)
    
    plot_data = {"x":[], "y":[], "z":[], "color":[], "size":[], "text":[], "type":[]}
    
    for node_id, raw_p in pos_3d.items():
        # 归一化公式
        norm_p = (raw_p - c_min) / (c_max - c_min + 1e-6) * 2 - 1
        
        node_attrs = G.nodes[node_id]
        plot_data["x"].append(norm_p[0])
        plot_data["y"].append(norm_p[1])
        plot_data["z"].append(norm_p[2])
        plot_data["color"].append(node_attrs['color'])
        plot_data["size"].append(node_attrs['size'])
        plot_data["type"].append(node_attrs['type'])
        
        if node_attrs.get('type') == 'thought':
            plot_data["text"].append(f"<b>{node_attrs.get('name')}</b><br>{node_attrs.get('insight')}")
        else:
            plot_data["text"].append("")
        
    return plot_data, primary_attr, secondary_attr
