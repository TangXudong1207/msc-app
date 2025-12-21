### msc_soul_gen.py ###
import random
import math
import numpy as np
import msc_config as config
import json
import networkx as nx # 🟢 引入 NetworkX

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

def get_dimension_color(dim):
    return config.SPECTRUM.get(config.DIMENSION_MAP_REV.get(dim, "Structure"), "#FFFFFF")

# 🟢 我们不再需要前端物理配置了，因为位置由 Python 算好了
def generate_soul_network(radar_dict, user_nodes):
    if not radar_dict: radar_dict = {"Care": 3.0, "Reflection": 3.0}
    
    # ... (前段逻辑保持不变，为了获取颜色和分类) ...
    valid_keys = ["Care", "Curiosity", "Reflection", "Coherence", "Agency", "Aesthetic", "Transcendence"]
    clean_radar = {}
    for k, v in radar_dict.items():
        if k in valid_keys:
            try: val = float(v)
            except: val = 0
            if val > 0: clean_radar[k] = val
    if not clean_radar: clean_radar = {"Care": 3.0, "Reflection": 3.0}
    
    sorted_dims = sorted(clean_radar.items(), key=lambda x: x[1], reverse=True)
    primary_attr = sorted_dims[0][0]
    secondary_attr = sorted_dims[1][0] if len(sorted_dims) > 1 else primary_attr
    
    # ----------------------------------------------------
    # 🟢 1. 构建 NetworkX 图对象
    # ----------------------------------------------------
    G = nx.Graph()
    
    dim_weights = {d: s/sum(clean_radar.values()) for d, s in sorted_dims}
    dims_list = list(dim_weights.keys())
    weights_list = list(dim_weights.values())

    default_old_data_color = "#00E676" 

    # 添加主节点
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
        
        G.add_node(node_id, 
                   color=color, 
                   size=16, # 主粒子大小
                   type='thought', 
                   name=str(user_node.get('care_point', 'Thought')),
                   insight=str(user_node.get('insight', '')))

    # 添加氛围节点
    base_count = len(user_nodes) * 15
    num_atmosphere = int(min(300, max(100, base_count)))
    
    for i in range(num_atmosphere):
        node_id = f"atmos_{i}"
        target_dim = random.choices(dims_list, weights=weights_list, k=1)[0]
        color = get_dimension_color(target_dim)
        G.add_node(node_id, 
                   color=color, 
                   size=random.uniform(2, 5), # 氛围粒子大小
                   type='atmos', 
                   name="",
                   insight="")

    # 添加连线 (影响布局)
    nodes_list = list(G.nodes())
    thought_nodes = [n for n in nodes_list if n.startswith('thought')]
    atmos_nodes = [n for n in nodes_list if n.startswith('atmos')]
    
    for atmos in atmos_nodes:
        # 80% 连向某个主节点，20% 连向其他氛围节点
        if thought_nodes and random.random() < 0.8:
            target = random.choice(thought_nodes)
        else:
            target = random.choice(nodes_list)
        
        if target != atmos:
            G.add_edge(atmos, target)

    # ----------------------------------------------------
    # 🟢 2. 使用 NetworkX 计算 3D 布局 (Spring Layout)
    # ----------------------------------------------------
    # k 控制节点间距 (越大越开), iterations 控制迭代次数 (越大越稳定)
    # seed 保证每次刷新稍微固定，不会乱跳
    pos_3d = nx.spring_layout(G, dim=3, k=0.5, iterations=50, seed=42)

    # ----------------------------------------------------
    # 🟢 3. 导出数据给 Plotly
    # ----------------------------------------------------
    # Plotly 需要 x, y, z 数组
    plot_data = {
        "x": [], "y": [], "z": [],
        "color": [], "size": [], "text": [],
        "lines_x": [], "lines_y": [], "lines_z": [], "line_color": []
    }
    
    for node_id, coords in pos_3d.items():
        node_attrs = G.nodes[node_id]
        plot_data["x"].append(coords[0])
        plot_data["y"].append(coords[1])
        plot_data["z"].append(coords[2])
        plot_data["color"].append(node_attrs['color'])
        plot_data["size"].append(node_attrs['size'])
        # Tooltip 文本
        if node_attrs['type'] == 'thought':
            plot_data["text"].append(f"<b>{node_attrs['name']}</b><br>{node_attrs['insight']}")
        else:
            plot_data["text"].append("") # 氛围粒子不显示字

    # 生成连线坐标 (用于 Plotly Lines)
    for u, v in G.edges():
        x0, y0, z0 = pos_3d[u]
        x1, y1, z1 = pos_3d[v]
        plot_data["lines_x"].extend([x0, x1, None])
        plot_data["lines_y"].extend([y0, y1, None])
        plot_data["lines_z"].extend([z0, z1, None])
        
    return plot_data, primary_attr, secondary_attr
