### msc_soul_gen.py ###
import random
import numpy as np
import msc_config as config
import json
import networkx as nx
import math

def apply_aspect_distortion(coords, aspect_name, intensity=0.3):
    """
    根据次维度(Aspect)对粒子群施加数学形变，模拟特定的运动形态。
    由于Streamlit是静态刷新，我们通过随机相位模拟动态瞬间。
    """
    x, y, z = coords[0], coords[1], coords[2]
    
    # 随机因子，模拟时间流逝
    t = random.uniform(0, math.pi * 2) 
    
    # 1. Volatile (躁动): 随机的高频抖动
    if aspect_name == "Agency": 
        noise = np.random.normal(0, 0.1, 3)
        return coords + noise * intensity
        
    # 2. Gentle (柔缓): 正弦波浪起伏
    elif aspect_name == "Care": 
        dy = math.sin(x * 3 + t) * 0.2
        return np.array([x, y + dy, z])
        
    # 3. Flowing (流转): 沿对角线拉伸流动
    elif aspect_name == "Curiosity": 
        drift = math.sin(t) * 0.2
        return np.array([x + drift, y + drift, z])
        
    # 4. Stable (稳定): 强力结晶，向网格对齐
    elif aspect_name == "Coherence": 
        # 模拟吸附到网格点
        return np.round(coords * 3) / 3.0 + np.random.normal(0, 0.02, 3)
        
    # 5. Breathing (呼吸): 整体膨胀收缩
    elif aspect_name == "Reflection": 
        scale = 1.0 + math.sin(t) * 0.15
        return coords * scale
        
    # 6. Drifting (漂浮): Z轴上升，甚至由于重力反转
    elif aspect_name == "Transcendence": 
        dz = math.sin(x * 2 + t) * 0.2 + 0.1
        return np.array([x, y, z + dz])
        
    # 7. Elegant (优雅/熵): 螺旋扭曲
    elif aspect_name == "Aesthetic": 
        # 绕Z轴旋转
        theta = 0.5 * intensity
        x_new = x * math.cos(theta) - y * math.sin(theta)
        y_new = x * math.sin(theta) + y * math.cos(theta)
        return np.array([x_new, y_new, z])
        
    return coords

def generate_soul_network(radar_dict, user_nodes):
    # 1. 数据解析
    if not radar_dict: radar_dict = {k: 3.0 for k in config.RADAR_AXES}
    valid_keys = config.RADAR_AXES
    clean_radar = {k: float(radar_dict.get(k, 3.0)) for k in valid_keys}
    
    sorted_dims = sorted(clean_radar.items(), key=lambda x: x[1], reverse=True)
    primary_attr = sorted_dims[0][0]
    secondary_attr = sorted_dims[1][0] if len(sorted_dims) > 1 else primary_attr
    
    # 2. 构建图
    G = nx.Graph()
    total_val = sum(clean_radar.values())
    dim_weights = {d: s/total_val for d, s in sorted_dims}
    dims_list, weights_list = list(dim_weights.keys()), list(dim_weights.values())

    # --- A. 添加核心思想粒子 (Thought Nodes) ---
    for i, user_node in enumerate(user_nodes):
        node_id = f"thought_{i}"
        kw = user_node.get('keywords', [])
        if isinstance(kw, str):
            try: kw = json.loads(kw)
            except: kw = []
        color = config.SPECTRUM.get(kw[0], "#00E676") if kw else "#00E676"
        
        # 核心粒子：大尺寸，作为锚点
        G.add_node(node_id, color=color, size=12.0, type='thought', 
                   name=str(user_node.get('care_point', 'Thought')),
                   insight=str(user_node.get('insight', '')))

    # --- B. 添加氛围数据尘埃 (Data Dust) ---
    # 增加数量以形成“雾”的感觉
    num_atmosphere = 250 
    for i in range(num_atmosphere):
        node_id = f"atmos_{i}"
        target_dim = random.choices(dims_list, weights=weights_list, k=1)[0]
        color = config.SPECTRUM.get(target_dim, "#FFFFFF")
        
        # 氛围粒子：极小尺寸 (1/10 比例将在 viz 中通过绘图参数控制，这里只给相对值)
        # 这里 size 给 1.0，思想粒子是 12.0，大概就是 1:12
        G.add_node(node_id, color=color, size=1.0, type='atmos')

    # 3. 计算基础物理布局
    # k 值决定了聚类的紧密程度
    pos_3d = nx.spring_layout(G, dim=3, k=0.6, iterations=40, seed=None)

    # 4. 坐标归一化 & 动态形变
    coords_array = np.array(list(pos_3d.values()))
    c_min, c_max = coords_array.min(axis=0), coords_array.max(axis=0)
    
    plot_data = {"x":[], "y":[], "z":[], "color":[], "size":[], "text":[], "type":[]}
    
    for node_id, raw_p in pos_3d.items():
        # 1. 归一化到 [-1, 1]
        norm_p = (raw_p - c_min) / (c_max - c_min + 1e-6) * 2 - 1
        
        # 2. 🟢 关键：应用“文案映射逻辑”的运动形变
        # 思想粒子受影响较小(重质量)，氛围粒子受影响较大(轻质量)
        node_attrs = G.nodes[node_id]
        is_thought = node_attrs.get('type') == 'thought'
        intensity = 0.1 if is_thought else 0.4
        
        final_p = apply_aspect_distortion(norm_p, secondary_attr, intensity)
        
        # 3. 极微小的随机扰动 (Jitter) 模拟“雾”的布朗运动
        final_p += np.random.uniform(-0.03, 0.03, size=3)
        
        plot_data["x"].append(final_p[0])
        plot_data["y"].append(final_p[1])
        plot_data["z"].append(final_p[2])
        plot_data["color"].append(node_attrs['color'])
        plot_data["size"].append(node_attrs['size'])
        plot_data["type"].append(node_attrs['type'])
        
        if is_thought:
            plot_data["text"].append(f"<b>{node_attrs.get('name')}</b><br>{node_attrs.get('insight')}")
        else:
            plot_data["text"].append("")
        
    return plot_data, primary_attr, secondary_attr
