import streamlit as st
from openai import OpenAI
from supabase import create_client, Client
from streamlit_echarts import st_echarts
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import re
import hashlib
import time
import numpy as np
# 🌟 核心修复：确保数学库在最顶层被加载
from sklearn.decomposition import PCA 
from sklearn.cluster import KMeans
from datetime import datetime, timezone

# ==========================================
# 🛑 1. 配置与初始化
# ==========================================
def init_system():
    try:
        client = OpenAI(api_key=st.secrets["API_KEY"], base_url=st.secrets["BASE_URL"])
        model = st.secrets["MODEL_NAME"]
        supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
        return client, model, supabase
    except Exception as e: st.error(f"System Error: {e}"); st.stop()

client_ai, TARGET_MODEL, supabase = init_system()

# ==========================================
# 🧮 2. 核心算法 (意义拓扑学)
# ==========================================
def get_embedding(text):
    return np.random.rand(1536).tolist()

def cosine_similarity(v1, v2):
    if not v1 or not v2: return 0
    vec1 = np.array(v1); vec2 = np.array(v2)
    norm1 = np.linalg.norm(vec1); norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0: return 0
    return np.dot(vec1, vec2) / (norm1 * norm2)

# 🌟 升级：基于哲学结构的链接分计算
def calculate_MLS(vec_a, vec_b, node_a_data, node_b_data):
    # 1. 基础向量相似度 (Semantic Base)
    sim_vec = cosine_similarity(vec_a, vec_b)
    
    # 2. 哲学结构匹配 (Structural Match)
    # 提取维度标签
    dims_a = set(node_a_data.get('dimensions', []))
    dims_b = set(node_b_data.get('dimensions', []))
    
    # 规则 A: 结构深化 (如: 责任 -> 担当)
    # 如果两者处于同一通道但层级不同 (这里简化为共享标签)
    struct_overlap = len(dims_a.intersection(dims_b))
    
    # 规则 B: 张力解决 (如: 束缚 -> 自由)
    # 检测互补词 (这是简单的模拟，理想情况需向量空间计算)
    tension_bonus = 0.0
    keywords_a = str(node_a_data).lower()
    keywords_b = str(node_b_data).lower()
    
    # 定义一些经典的张力对 (Tension Pairs)
    pairs = [("责任", "自由"), ("爱", "独立"), ("恐惧", "勇气"), ("迷茫", "行动"), ("束缚", "释放")]
    for p1, p2 in pairs:
        if (p1 in keywords_a and p2 in keywords_b) or (p2 in keywords_a and p1 in keywords_b):
            tension_bonus = 0.4 # 巨大的张力加分
            break
            
    # 🌟 MLS 最终公式
    # 相似度权重降低，结构和张力权重提高
    MLS = 0.4 * sim_vec + 0.2 * (struct_overlap * 0.1) + tension_bonus
    
    # 归一化到 0-1 (虽然可能有加分溢出，但用于比较足够)
    return min(1.0, MLS)

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# ==========================================
# 🔐 3. 用户与数据库
# ==========================================
def login_user(username, password):
    try:
        hashed_pw = make_hashes(password)
        res = supabase.table('users').select("*").eq('username', username).eq('password', hashed_pw).execute()
        return res.data
    except: return []

def add_user(username, password, nickname, country="Other"):
    try:
        res = supabase.table('users').select("*").eq('username', username).execute()
        if len(res.data) > 0: return False 
        
        coords = [116.4, 39.9]
        if country == "USA": coords = [-95.7, 37.0]
        
        default_radar = {"Care": 3.0, "Curiosity": 3.0, "Reflection": 3.0, "Coherence": 3.0, "Empathy": 3.0, "Agency": 3.0, "Aesthetic": 3.0}
        data = {
            "username": username, "password": make_hashes(password), "nickname": nickname, 
            "radar_profile": json.dumps(default_radar), "country": country, "location": json.dumps(coords),
            "last_seen": datetime.now(timezone.utc).isoformat()
        }
        supabase.table('users').insert(data).execute()
        return True
    except: return False

def get_user_profile(username):
    try:
        res = supabase.table('users').select("*").eq('username', username).execute()
        if res.data: return res.data[0]
    except: pass
    return {"nickname": username, "radar_profile": None}

def update_radar_score(username, new_scores):
    try:
        user_data = get_user_profile(username)
        current_radar = user_data.get('radar_profile')
        if not current_radar: current_radar = {k: 3.0 for k in new_scores.keys()}
        elif isinstance(current_radar, str): current_radar = json.loads(current_radar)
        alpha = 0.2
        updated_radar = {}
        for key in new_scores:
            old_val = float(current_radar.get(key, 3.0)); input_val = float(new_scores.get(key, 0))
            if input_val > 1.0: updated_radar[key] = round(min(10.0, old_val*(1-alpha)+input_val*alpha), 2)
            else: updated_radar[key] = old_val
        supabase.table('users').update({"radar_profile": json.dumps(updated_radar)}).eq("username", username).execute()
    except: pass

def update_heartbeat(username):
    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        supabase.table('users').update({"last_seen": now_iso}).eq("username", username).execute()
    except: pass

def check_is_online(last_seen_str):
    if not last_seen_str: return False
    try:
        if last_seen_str.endswith('Z'): last_seen = datetime.fromisoformat(last_seen_str.replace('Z', '+00:00'))
        else: last_seen = datetime.fromisoformat(last_seen_str)
        if last_seen.tzinfo is None: last_seen = last_seen.replace(tzinfo=timezone.utc)
        diff = datetime.now(timezone.utc) - last_seen
        return diff.total_seconds() < 300
    except: return False

def get_all_users(current_user):
    try:
        res = supabase.table('users').select("username, nickname, last_seen, uid").neq('username', current_user).execute()
        return res.data
    except: return []

def get_direct_messages(user1, user2):
    try:
        res1 = supabase.table('direct_messages').select("*").eq('sender', user1).eq('receiver', user2).execute()
        res2 = supabase.table('direct_messages').select("*").eq('sender', user2).eq('receiver', user1).execute()
        all_msgs = res1.data + res2.data
        all_msgs.sort(key=lambda x: x['id'])
        return all_msgs
    except: return []

def send_direct_message(sender, receiver, content):
    try:
        supabase.table('direct_messages').insert({"sender": sender, "receiver": receiver, "content": content, "is_read": False}).execute()
        return True
    except: return False

def get_unread_counts(current_user):
    try:
        res = supabase.table('direct_messages').select("sender").eq('receiver', current_user).eq('is_read', False).execute()
        counts = {}; total = 0
        for row in res.data:
            sender = row['sender']; counts[sender] = counts.get(sender, 0) + 1; total += 1
        return total, counts
    except: return 0, {}

def mark_messages_read(sender, receiver):
    try:
        supabase.table('direct_messages').update({"is_read": True}).eq('sender', sender).eq('receiver', receiver).eq('is_read', False).execute()
    except: pass

def save_chat(username, role, content):
    try: supabase.table('chats').insert({"username": username, "role": role, "content": content, "is_deleted": False}).execute()
    except: pass

def get_active_chats(username, limit=50):
    try:
        res = supabase.table('chats').select("*").eq('username', username).eq('is_deleted', False).order('id', desc=True).limit(limit).execute()
        return list(reversed(res.data))
    except: return []

def save_node(username, content, data, mode, vector):
    try:
        logic = data.get('logic_score', 0.5)
        keywords = data.get('keywords', [])
        # 将新字段存入 jsonb 类型的 keywords 字段，或者如果数据库有 dimensions 列更好
        # 这里为了兼容，混入 keywords 存储
        dims = data.get('dimensions', [])
        all_tags = list(set(keywords + dims))
        
        insert_data = {
            "username": username, "content": content, "care_point": data.get('care_point', '未命名'), "meaning_layer": data.get('meaning_layer', '暂无结构'),
            "insight": data.get('insight', '生成中断'), "mode": mode, "vector": json.dumps(vector), "logic_score": logic, 
            "keywords": json.dumps(all_tags), # 存入所有标签
            "is_deleted": False, "c_score": data.get('c_score', 0), "m_score": data.get('m_score', 0)
        }
        supabase.table('nodes').insert(insert_data).execute()
        return True
    except: return False

def get_active_nodes_map(username):
    try:
        res = supabase.table('nodes').select("*").eq('username', username).eq('is_deleted', False).execute()
        return {node['content']: node for node in res.data}
    except: return {}

def get_all_nodes_for_map(username):
    try:
        res = supabase.table('nodes').select("*").eq('username', username).eq('is_deleted', False).order('id', desc=False).execute()
        return res.data
    except: return []

def get_user_nodes(username): return get_all_nodes_for_map(username)
def get_global_nodes():
    try: return supabase.table('nodes').select("*").eq('is_deleted', False).order('id', desc=True).limit(200).execute().data
    except: return []

def soft_delete_chat_and_node(chat_id, content, username):
    try:
        supabase.table('chats').update({"is_deleted": True}).eq("id", chat_id).execute()
        supabase.table('nodes').update({"is_deleted": True}).eq("username", username).eq("content", content).execute()
        return True
    except: return False

def check_group_formation(new_node_data, vector, username): pass # 简化
def get_available_rooms():
    try: return supabase.table('rooms').select("*").order('created_at', desc=True).execute().data
    except: return []
def join_room(rid, user):
    try:
        chk = supabase.table('room_members').select("*").eq('room_id', rid).eq('username', user).execute()
        if not chk.data: supabase.table('room_members').insert({"room_id": rid, "username": user}).execute()
    except: pass
def get_room_messages(rid):
    try: return supabase.table('room_chats').select("*").eq('room_id', rid).order('created_at', desc=False).execute().data
    except: return []
def send_room_message(rid, user, content):
    try: supabase.table('room_chats').insert({"room_id": rid, "username": user, "content": content}).execute()
    except: pass

def find_resonance(current_vector, current_user, current_data):
    if not current_vector: return None
    try:
        res = supabase.table('nodes').select("*").neq('username', current_user).eq('is_deleted', False).execute()
        others = res.data
        best_match, highest_score = None, 0
        for row in others:
            if row['vector']:
                try:
                    o_vec = json.loads(row['vector'])
                    o_data = {"keywords": json.loads(row['keywords'])} if row['keywords'] else {}
                    
                    # 🌟 使用新的 MLS 算法
                    MLS = calculate_MLS(current_vector, o_vec, current_data, o_data)
                    
                    if MLS > 0.65 and MLS > highest_score: # 降低一点阈值让张力更容易触发
                        highest_score = MLS
                        best_match = {"user": row['username'], "content": row['content'], "score": round(MLS * 100, 1)}
                except: continue
        return best_match
    except: return None

# ==========================================
# 🧠 4. AI 智能 (哲学灵魂注入)
# ==========================================
def call_ai_api(prompt):
    try:
        response = client_ai.chat.completions.create(
            model=TARGET_MODEL,
            messages=[{"role": "system", "content": "Output valid JSON only. No markdown."}, {"role": "user", "content": prompt}],
            temperature=0.7, stream=False, response_format={"type": "json_object"} 
        )
        content = response.choices[0].message.content
        try:
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match: return json.loads(match.group(0))
            else: return json.loads(content)
        except: return {"error": True}
    except Exception as e: return {"error": True, "msg": str(e)}

def get_normal_response(history_messages):
    try:
        api_messages = [{"role": "system", "content": "你是温暖的对话伙伴。"}]
        for msg in history_messages: api_messages.append({"role": msg["role"], "content": msg["content"]})
        return client_ai.chat.completions.create(model=TARGET_MODEL, messages=api_messages, temperature=0.8, stream=True)
    except Exception as e: return f"Error: {e}"

def analyze_meaning_background(text):
    # 🌟 注入《智能人文主义》哲学 Prompt
    prompt = f"""
    【任务】分析输入："{text}"
    请基于 MSC 意义模型进行深度解析。
    
    1. 意识功能位置 (Function): 这句话代表了什么意识状态？(如：规范意识、行动意志、情感交互)
    2. 结构运动 (Direction): 它是向内深化、向外扩展、还是寻求张力解决？
    3. 张力识别 (Tension): 是否包含"责任vs自由"、"自我vs他者"等张力？
    
    【判分】
    Care Score (0.0-1.0): 情感/价值强度。
    Novelty Score (0.0-1.0): 新颖度。
    
    返回 JSON: {{
        "valid": true,
        "care_point": "核心关切",
        "meaning_layer": "结构分析 (包含 Function/Direction/Tension 的描述)",
        "insight": "升维洞察",
        "c_score": 0.9, "n_score": 0.8, "m_score": 0.72,
        "dimensions": ["责任", "意志"], // 提取哲学维度标签
        "keywords": ["tag1"], 
        "radar_scores": {{ "Care": 5, ... }}
    }}
    """
    return call_ai_api(prompt)

def generate_fusion(node_a_content, node_b_content):
    prompt = f"""
    任务：基于 Meaning Linkage Model (意识-结构-张力) 进行融合。
    A: "{node_a_content}"
    B: "{node_b_content}"
    
    寻找二者之间的结构性跃迁（如从责任到自由的张力解决）。
    返回 JSON: {{ "care_point": "...", "meaning_layer": "...", "insight": "..." }}
    """
    return call_ai_api(prompt)

def analyze_persona_report(radar_data):
    radar_str = json.dumps(radar_data, ensure_ascii=False)
    prompt = f"任务：人物画像分析。雷达数据：{radar_str}。输出 JSON: {{ 'static_portrait': '...', 'dynamic_growth': '...' }}"
    return call_ai_api(prompt)

def generate_daily_question(username, radar_data):
    recent = get_user_nodes(username); ctx = f"关注点：{[n['care_point'] for n in recent[-3:]]}" if recent else ""
    res = call_ai_api(f"生成每日追问。用户：{json.dumps(radar_data)}。{ctx}。输出 JSON: {{ 'question': '...' }}")
    return res.get("question", "今天感觉如何？")

def get_ai_interjection(history_text):
    prompt = f"作为观察者评论这段对话：\n{history_text}\n简短幽默。直接返回文本。"
    try:
        response = client_ai.chat.completions.create(model=TARGET_MODEL, messages=[{"role": "user", "content": prompt}], temperature=0.9)
        return response.choices[0].message.content
    except: return None

# ==========================================
# 🎨 5. 视觉渲染
# ==========================================
def render_2d_world_map(nodes):
    map_data = [{"lat": 39.9, "lon": 116.4, "size": 10, "label": "HQ"}]
    for _ in range(len(nodes) + 15): 
        lon = np.random.uniform(-150, 150); lat = np.random.uniform(-40, 60)
        map_data.append({"lat": float(lat), "lon": float(lon), "size": 5, "label": "Node"})
    df = pd.DataFrame(map_data)
    fig = go.Figure(data=go.Scattergeo(lon=df["lon"], lat=df["lat"], mode='markers', marker=dict(size=5, color='#ffd60a', opacity=0.8)))
    fig.update_layout(geo=dict(scope='world', projection_type='natural earth', showland=True, landcolor="rgb(20, 20, 20)", bgcolor="black"), margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="black", height=500)
    st.plotly_chart(fig, use_container_width=True)

def render_3d_galaxy(nodes):
    if len(nodes) < 3: st.info("🌌 星河汇聚中..."); return
    vectors, labels, colors = [], [], []
    for i, node in enumerate(nodes):
        if node['vector']:
            try:
                v = json.loads(node['vector']); vectors.append(v); labels.append(node['care_point']); colors.append(i % 3)
            except: pass
    if not vectors: return
    pca = PCA(n_components=3); coords = pca.fit_transform(vectors)
    df = pd.DataFrame(coords, columns=['x','y','z']); df['label']=labels; df['cluster']=colors
    fig = px.scatter_3d(df, x='x', y='y', z='z', color='cluster', hover_name='label', template="plotly_dark", opacity=0.8)
    fig.update_layout(scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False), bgcolor='black'), paper_bgcolor="black", margin={"r":0,"t":0,"l":0,"b":0}, height=600, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

def render_radar_chart(radar_dict, height="200px"):
    keys = ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]
    scores = [radar_dict.get(k, 3.0) for k in keys]
    option = {"backgroundColor": "transparent", "radar": {"indicator": [{"name": k, "max": 10} for k in keys], "splitArea": {"show": False}}, "series": [{"type": "radar", "data": [{"value": scores, "areaStyle": {"color": "rgba(0,255,242,0.4)"}, "lineStyle": {"color": "#00fff2"}}]}]}
    st_echarts(options=option, height=height)

def render_cyberpunk_map(nodes, height="250px", is_fullscreen=False):
    if not nodes: return
    graph_nodes, graph_links = [], []
    symbol_base = 30 if is_fullscreen else 15
    for i, node in enumerate(nodes):
        # 兼容旧数据
        logic = node.get('m_score') if node.get('m_score') is not None else 0.5
        
        # 提取新哲学标签
        raw_kw = node.get('keywords', '[]')
        keywords = json.loads(raw_kw) if isinstance(raw_kw, str) else raw_kw
        
        vector = None
        if node.get('vector'):
            if isinstance(node['vector'], str): vector = json.loads(node['vector'])
            else: vector = node['vector']

        graph_nodes.append({
            "name": str(node['id']), "id": str(node['id']),
            "symbolSize": symbol_base * (0.8 + logic),
            "value": node['care_point'],
            "label": {"show": is_fullscreen, "formatter": node['care_point'][:5], "color": "#fff"},
            "vector": vector,
            "keywords": keywords
        })
    node_count = len(graph_nodes)
    for i in range(node_count):
        for j in range(i + 1, node_count):
            na, nb = graph_nodes[i], graph_nodes[j]
            if na['vector'] and nb['vector']:
                # 🌟 渲染时也使用 MLS 思想：如果标签有重叠(结构匹配)或者向量相似，就连线
                # 简化版：这里主要靠 keyword overlap 模拟哲学关联
                kw_a = set(na['keywords'])
                kw_b = set(nb['keywords'])
                kw_sim = len(kw_a.intersection(kw_b)) / (len(kw_a.union(kw_b)) or 1)
                
                vec_sim = cosine_similarity(na['vector'], nb['vector'])
                
                # 综合分
                score = 0.5 * vec_sim + 0.5 * kw_sim
                
                if score > 0.8: graph_links.append({"source": na['name'], "target": nb['name'], "lineStyle": {"width": 2, "color": "#00fff2"}})
                elif score > 0.6: graph_links.append({"source": na['name'], "target": nb['name'], "lineStyle": {"width": 0.5, "color": "#555", "type": "dashed"}})
    option = {"backgroundColor": "#0e1117", "series": [{"type": "graph", "layout": "force", "data": graph_nodes, "links": graph_links, "roam": True, "force": {"repulsion": 1000 if is_fullscreen else 300}, "itemStyle": {"shadowBlur": 10}}]}
    st_echarts(options=option, height=height)
