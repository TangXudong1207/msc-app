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

# 内部辅助：通过雷达轴找到对应的颜色
def get_color_from_axis(axis_name):
    # 在 config.DIMENSION_MAP 中寻找属于该轴的第一个光谱关键词
    for keyword, target_axis in config.DIMENSION_MAP.items():
        if target_axis == axis_name:
            return config.SPECTRUM.get(keyword, "#FFFFFF")
    return "#FFFFFF"

def generate_soul_network(radar_dict, user_nodes):
    # 确保 radar_dict 有效
    if not radar_dict: 
        radar_dict = {k: 3.0 for k in config.RADAR_AXES}
    
    # 1. 整理雷达数据
    valid_keys = config.RADAR_AXES
    clean_radar = {}
    for k in valid_keys:
        try: clean_radar[k] = float(radar_dict.get(k, 3.0))
        except: clean_radar[k] = 3.0
        
    # 排序找到主维度
    sorted_dims = sorted(clean_radar.items(), key=lambda x: x[1], reverse=True)
    primary_attr = sorted_dims[0][0]
    secondary_attr = sorted_dims[1][0] if len(sorted_dims) > 1 else primary_attr
    
    # 2. 构建 NetworkX 图
    G = nx.Graph()
    
    # 计算每个维度的权重
    total_val = sum(clean_radar.values())
    dim_weights = {d: s/total_val for d, s in sorted_dims}
    dims_list = list(dim_weights.keys())
    weights_list = list(dim_weights.values())

    # --- 添加核心粒子 (思想节点) ---
    for i, user_node in enumerate(user_nodes):
        node_id = f"thought_{i}"
        kw = user_node.get('keywords', [])
        if isinstance(kw, str):
            try: kw = json.loads(kw)
            except: kw = []
        
        # 获取颜色
        color = "#00E676" 
        if isinstance(kw, list) and len(kw) > 0:
            color = config.SPECTRUM.get(kw[0], "#00E676")
        
        G.add_node(node_id, color=color, size=14, type='thought', 
                   name=str(user_node.get('care_point', 'Thought')),
                   insight=str(user_node.get('insight', '')))

    # --- 添加背景氛围粒子 ---
    num_atmosphere = 150 
    for i in range(num_atmosphere):
        node_id = f"atmos_{i}"
        # 根据用户性格权重随机分配粒子类别
        target_dim = random.choices(dims_list, weights=weights_list, k=1)[0]
        color = get_color_from_axis(target_dim)
        
        G.add_node(node_id, color=color, size=random.uniform(3, 6), type='atmos')

    # 3. 计算 3D 布局 (Spring Layout)
    # k 是点之间的排斥力，iterations 是计算次数
    pos_3d = nx.spring_layout(G, dim=3, k=0.6, iterations=30, seed=42)

    # 🟢 坐标归一化：将所有点强制约束在 [-1, 1] 的空间内
    all_coords = np.array(list(pos_3d.values()))
    min_vals = all_coords.min(axis=0)
    max_vals = all_coords.max(axis=0)
    range_vals = max_vals - min_vals
    # 防止除以 0
    range_vals[range_vals == 0] = 1.0
    
    for node_id in pos_3d:
        # 强制归一化到 [-1, 1]
        pos_3d[node_id] = (pos_3d[node_id] - min_vals) / range_vals * 2 - 1

    # 4. 转换数据为 Plotly 格式
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
        if node_attrs.get('type') == 'thought':
            plot_data["text"].append(f"<b>{node_attrs.get('name')}</b><br>{node_attrs.get('insight')}")
        else:
            plot_data["text"].append("")
        plot_data["type"].append(node_attrs.get('type'))
        
    return plot_data, primary_attr, secondary_attr
