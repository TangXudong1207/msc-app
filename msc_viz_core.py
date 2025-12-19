### msc_viz_core.py ###
import pandas as pd
import json
import random
import msc_config as config
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# ==========================================
# 🎨 颜色与辅助工具
# ==========================================
def get_spectrum_color(keywords_str):
    if not keywords_str: return "#00CCFF"
    for dim, color in config.SPECTRUM.items():
        if dim in keywords_str: return color
    for color in config.SPECTRUM.values():
        if color in keywords_str: return color
    return "#00CCFF"

def get_cluster_color(cluster_id):
    CLUSTER_COLORS = list(config.SPECTRUM.values())
    return CLUSTER_COLORS[cluster_id % len(CLUSTER_COLORS)]

def get_random_coordinate():
    """完全随机的全球坐标（模拟卫星巡游）"""
    lat = random.uniform(-60, 70) # 避开极地
    lon = random.uniform(-180, 180)
    return lat, lon

# ==========================================
# 🧠 聚类算法 (Clustering)
# ==========================================
def compute_clusters(nodes, n_clusters=5):
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

    # 简单对齐向量长度
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
