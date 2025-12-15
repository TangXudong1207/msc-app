### msc_news_real.py (Oracle Engine: Tiered Grid Scan) ###

import msc_lib as msc
import msc_config as config
import json
import time
import random

# ==========================================
# 🗺️ 坐标字典 (Geo-Mapping)
# ==========================================
# 包含 G20、关键城市、极地中心
GEO_DB = {
    # Tier 1 G20
    "USA": {"lat": 38.90, "lon": -77.03}, "China": {"lat": 39.90, "lon": 116.40},
    "Russia": {"lat": 55.75, "lon": 37.61}, "UK": {"lat": 51.50, "lon": -0.12},
    "France": {"lat": 48.85, "lon": 2.35}, "Germany": {"lat": 52.52, "lon": 13.40},
    "Japan": {"lat": 35.67, "lon": 139.65}, "India": {"lat": 28.61, "lon": 77.20},
    "Brazil": {"lat": -15.82, "lon": -47.92}, "Canada": {"lat": 45.42, "lon": -75.69},
    "Australia": {"lat": -35.28, "lon": 149.13}, "South Korea": {"lat": 37.56, "lon": 126.97},
    "Italy": {"lat": 41.90, "lon": 12.49}, "Turkey": {"lat": 39.93, "lon": 32.85},
    "Saudi Arabia": {"lat": 24.71, "lon": 46.67}, "South Africa": {"lat": -25.74, "lon": 28.22},
    "Argentina": {"lat": -34.60, "lon": -58.38}, "Mexico": {"lat": 19.43, "lon": -99.13},
    "Indonesia": {"lat": -6.20, "lon": 106.84}, "Israel": {"lat": 31.76, "lon": 35.21},
    "Iran": {"lat": 35.68, "lon": 51.38},
    
    # Tier 2 Regions (Sample Capitals)
    "North Korea": {"lat": 39.03, "lon": 125.76}, "Taiwan Region": {"lat": 25.03, "lon": 121.56},
    "Ukraine": {"lat": 50.45, "lon": 30.52}, "Poland": {"lat": 52.22, "lon": 21.01},
    "Vietnam": {"lat": 21.02, "lon": 105.83}, "Thailand": {"lat": 13.75, "lon": 100.50},
    "Pakistan": {"lat": 33.68, "lon": 73.04}, "Egypt": {"lat": 30.04, "lon": 31.23},
    "Nigeria": {"lat": 9.08, "lon": 7.39}, "Kenya": {"lat": -1.29, "lon": 36.82},
    "Chile": {"lat": -33.44, "lon": -70.66}, "New Zealand": {"lat": -41.28, "lon": 174.77},
    
    # Tier 3 Polar
    "Arctic": {"lat": 80.00, "lon": 0.00}, "Antarctica": {"lat": -82.86, "lon": 135.00},
    
    # General
    "Global": {"lat": 0, "lon": 0}
}

def get_coords(name):
    # 1. 精确查找
    if name in GEO_DB: return GEO_DB[name]
    # 2. 模糊查找
    for k, v in GEO_DB.items():
        if k.lower() in name.lower() or name.lower() in k.lower(): return v
    # 3. 兜底 (南大西洋无人区，避免视觉干扰)
    return {"lat": -40.0, "lon": -20.0}

def scan_grid_tier(tier_name, tier_config):
    """
    执行单个层级的扫描 (Google 引擎优先)
    """
    all_logs = []
    limit = tier_config["limit"]
    weight = tier_config.get("weight_multiplier", 1.0)
    
    # 构造 Prompt 的 Scope 描述
    scope_desc = ""
    
    if tier_name == "Tier_1_G20":
        countries = ", ".join(tier_config["countries"])
        scope_desc = f"G20 Major Powers & Hotspots. Focus ONLY on: {countries}."
        
        # === 执行 G20 扫描 ===
        logs = _execute_scan(scope_desc, limit, weight, "Tier_1")
        all_logs.extend(logs)

    elif tier_name == "Tier_2_Regions":
        # 遍历 Tier 2 下的所有子区域
        for region_name, region_rules in tier_config["regions"].items():
            focus_list = ", ".join(region_rules["focus"])
            exclude_list = ", ".join(region_rules["exclude"])
            
            scope_desc = f"Region: {region_name}. Focus on: {focus_list}. EXCLUDE: {exclude_list}."
            
            # === 执行区域扫描 ===
            logs = _execute_scan(scope_desc, limit, weight, region_name)
            all_logs.extend(logs)
            time.sleep(1) # 区域间冷却

    elif tier_name == "Tier_3_Polar":
        focus_list = ", ".join(tier_config["focus"])
        scope_desc = f"Polar Regions (Arctic/Antarctica). Focus on: {focus_list} as targets of geopolitics or climate."
        
        # === 执行极地扫描 ===
        logs = _execute_scan(scope_desc, limit, weight, "Polar")
        all_logs.extend(logs)

    return all_logs

def _execute_scan(scope_desc, limit, weight, layer_tag):
    """
    底层扫描执行函数
    """
    logs = []
    
    # 1. 组装 Prompt
    prompt = config.PROMPT_ORACLE_TEMPLATE.format(
        scope_description=scope_desc,
        limit=limit
    )
    
    # 2. 调用 AI (Google First)
    response = msc.call_ai_api(prompt, use_google=True)
    
    # 3. 解析结果
    news_list = response if isinstance(response, list) else response.get('news', [])
    # 兼容处理
    if not news_list and isinstance(response, dict):
        for v in response.values():
            if isinstance(v, list): news_list = v; break
            
    if not news_list: return []

    # 4. 生成节点
    for item in news_list:
        try:
            title = item.get('title', 'Unknown')
            tension = item.get('tension', 'Tension')
            dim = item.get('dimension', 'Structure')
            origin = item.get('origin', 'Global')
            impact = item.get('impact', origin)
            
            # 颜色映射
            color = config.SPECTRUM.get(dim, "#E0E0E0")
            
            # 坐标映射
            origin_loc = get_coords(origin)
            target_loc = get_coords(impact)
            
            # 构造节点数据
            content = f"[{dim}] {title}"
            node_data = {
                "c_score": 0.9 * weight, # 权重影响分数
                "care_point": tension,
                "insight": f"{title} ({origin} -> {impact})",
                "meaning_layer": layer_tag,
                "keywords": [dim, color, "OracleNews", layer_tag],
                "location": origin_loc,
                "target_location": target_loc if impact != origin else None,
                "intensity": item.get('intensity', 0.5) * weight, # 权重影响大小
                "ttl_category": dim # 用于后续计算 TTL
            }
            
            # 向量化 (Google Vertex)
            vec = msc.get_embedding(content)
            
            # 存库
            msc.save_node("World_Observer", content, node_data, "News_Stream", vec)
            
            logs.append(f"📡 {origin}: {title[:20]}... ({dim})")
            
        except Exception as e:
            print(f"Item Error: {e}")
            continue
            
    return logs

def fetch_real_news_auto():
    """
    全自动扫描入口 (遍历整个 GRID)
    """
    total_logs = []
    
    # 遍历配置表中的所有 Tier
    for tier_key, tier_cfg in config.GLOBAL_GRID.items():
        logs = scan_grid_tier(tier_key, tier_cfg)
        total_logs.extend(logs)
        time.sleep(1) # Tier 间冷却
        
    return total_logs
