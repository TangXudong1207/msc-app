### msc_transformer.py ###
import pandas as pd
import json
import random
import numpy as np
import msc_config as config
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# ==========================================
# 🎨 1. 颜色与辅助工具
# ==========================================
def get_spectrum_color(keywords_str):
    """根据关键词匹配光谱颜色"""
    if not keywords_str: return "#607D8B" # Default: Nihilism
    
    # 优先精确匹配
    for dim, color in config.SPECTRUM.items():
        if dim in keywords_str: return color
    
    # 模糊匹配
    for color in config.SPECTRUM.values():
        if color in keywords_str: return color
        
    return "#607D8B"

def get_cluster_color(cluster_id):
    """根据聚类ID获取颜色"""
    CLUSTER_COLORS = list(config.SPECTRUM.values())
    return CLUSTER_COLORS[cluster_id % len(CLUSTER_COLORS)]

def get_random_coordinate():
    """随机生成海洋坐标"""
    zones = [
        {"lat_min": -40, "lat_max": 40, "lon_min": 160, "lon_max": 180},
        {"lat_min": -40, "lat_max": 40, "lon_min": -180, "lon_max": -130},
        {"lat_min": -30, "lat_max": 40, "lon_min": -60, "lon_max": -20},
        {"lat_min": -30, "lat_max": 20, "lon_min": 60, "lon_max": 90}
    ]
    zone = random.choice(zones)
    lat = random.uniform(zone["lat_min"], zone["lat_max"])
    lon = random.uniform(zone["lon_min"], zone["lon_max"])
    return lat, lon

def clean_for_json(obj):
    """清理 NumPy 数据类型以便 JSON 序列化"""
    if isinstance(obj, (np.integer, np.int64, np.int32)): return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)): return float(obj)
    elif isinstance(obj, np.ndarray): return clean_for_json(obj.tolist())
    elif isinstance(obj, dict): return {k: clean_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list): return [clean_for_json(v) for v in obj]
    else: return obj

# ==========================================
# 🧠 2. 聚类算法 (Clustering)
# ==========================================
def compute_clusters(nodes, n_clusters=5):
    """计算节点的 3D 聚类坐标"""
    raw_vectors = []
    raw_meta = []
    
    for node in nodes:
        if node['vector']:
            try:
                v = json.loads(node['vector'])
                if isinstance(v, list) and len(v) > 0:
                    raw_vectors.append(v)
                    raw_meta.append({
                        "care_point": node['care_point'],
                        "insight": node.get('insight', ''),
                        "id": str(node['id'])
                    })
            except: pass
    
    if not raw_vectors or len(raw_vectors) < 2: return pd.DataFrame()

    target_len = len(raw_vectors[0])
    clean_vectors = [v for v in raw_vectors if len(v) == target_len]
    clean_meta = [m for i, m in enumerate(raw_meta) if len(raw_vectors[i]) == target_len]
    
    if len(clean_vectors) < 2: return pd.DataFrame()

    try:
        real_n_clusters = min(n_clusters, len(clean_vectors))
        kmeans = KMeans(n_clusters=real_n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(clean_vectors)
        
        pca = PCA(n_components=3)
        coords_3d = pca.fit_transform(clean_vectors)

        df = pd.DataFrame(clean_meta)
        df['cluster'] = labels
        df['color'] = [get_cluster_color(l) for l in labels]
        df['x'] = coords_3d[:, 0]
        df['y'] = coords_3d[:, 1]
        df['z'] = coords_3d[:, 2]
        return df
    except: return pd.DataFrame()

# ==========================================
# 👻 3. 灵魂数据准备 (Soul Data)
# ==========================================
def prepare_soul_data(radar_dict, user_nodes):
    """为 Soul Viz 准备渲染数据包"""
    if not radar_dict: radar_dict = {"Care": 3.0, "Reflection": 3.0}

    # A. 维度解析
    valid_keys = config.RADAR_AXES
    clean_radar = {k: float(v) for k, v in radar_dict.items() if k in valid_keys and float(v) > 0}
    if not clean_radar: clean_radar = {"Reflection": 5.0}
    
    sorted_dims = sorted(clean_radar.items(), key=lambda x: x[1], reverse=True)
    primary_attr = sorted_dims[0][0]
    secondary_attr = sorted_dims[1][0] if len(sorted_dims) > 1 else primary_attr

    # B. 颜色映射表 (氛围)
    AXIS_COLOR = {
        "Care": config.SPECTRUM["Empathy"], "Agency": config.SPECTRUM["Vitality"],
        "Structure": config.SPECTRUM["Structure"], "Coherence": config.SPECTRUM["Rationality"],
        "Curiosity": config.SPECTRUM["Curiosity"], "Reflection": config.SPECTRUM["Melancholy"],
        "Aesthetic": config.SPECTRUM["Aesthetic"], "Transcendence": config.SPECTRUM["Consciousness"]
    }
    
    # C. 思想节点数据 (Thoughts)
    thoughts_payload = []
    for node in user_nodes:
        kw = node.get('keywords', [])
        if isinstance(kw, str):
            try: kw = json.loads(kw)
            except: kw = []
        
        color = "#FFFFFF"
        if kw:
            for k in kw: 
                if k in config.SPECTRUM: color = config.SPECTRUM[k]; break
        
        safe_content = node.get('care_point','?').replace('"', '&quot;')
        safe_insight = node.get('insight', '').replace('"', '&quot;')
        
        thoughts_payload.append({
            "color": color,
            "text": safe_content,
            "insight": safe_insight
        })

    # D. 氛围数据 (Atmosphere)
    total_w = sum(clean_radar.values())
    weights = {k: v/total_w for k,v in clean_radar.items()}
    
    atmos_colors = []
    for k, w in weights.items():
        count = int(w * 100)
        c = AXIS_COLOR.get(k, "#888888")
        atmos_colors.extend([c] * count)
    if not atmos_colors: atmos_colors = ["#888888"]

    payload = {
        "primary": primary_attr,
        "secondary": secondary_attr,
        "thoughts": thoughts_payload,
        "atmos_colors": atmos_colors,
        "node_count": len(user_nodes)
    }
    
    return clean_for_json(payload), primary_attr, secondary_attr
