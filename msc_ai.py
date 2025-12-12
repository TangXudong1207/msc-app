import streamlit as st
import msc_config as config
import msc_ai as ai # 引用 AI 模块的算法
import json
import numpy as np
import hashlib
from datetime import datetime, timezone
from supabase import create_client

# ==========================================
# 🛑 初始化连接
# ==========================================
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"数据库连接失败: {e}")
    st.stop()

# ==========================================
# 🧮 核心算法 (v70.0 意义物理学)
# ==========================================

def cosine_similarity(v1, v2):
    vec1, vec2 = np.array(v1), np.array(v2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0: return 0
    return np.dot(vec1, vec2) / (norm1 * norm2)

# 🌟 v70 新增：计算意义链接分数 (MLS)
def calculate_MLS_v70(vec_a, vec_b, keywords_a, keywords_b, radar_a, radar_b):
    w = config.W_MLS
    
    # 1. 语义向量相似度
    s_vector = cosine_similarity(vec_a, vec_b)
    
    # 2. 标签重叠度 (Jaccard)
    set_a, set_b = set(keywords_a), set(keywords_b)
    s_meaning = len(set_a.intersection(set_b)) / len(set_a.union(set_b)) if (set_a and set_b) else 0
    
    # 3. 价值观(雷达)对齐度
    def radar_to_list(r): return [r.get(k,3) for k in ["Care","Curiosity","Reflection","Coherence","Empathy","Agency","Aesthetic"]]
    r_vec_a = radar_to_list(radar_a)
    r_vec_b = radar_to_list(radar_b)
    s_value = cosine_similarity(r_vec_a, r_vec_b)
    
    # 4. 最终公式
    # 假设 Existential 和 Temporal 暂时为默认值
    MLS = (w['TagOverlap'] * s_meaning) + \
          (w['SemanticSim'] * s_vector) + \
          (w['ValueAlign'] * s_value) + 0.1 # 基础分
          
    return MLS

# 🌟 v70 升级：雷达生长 (含时间衰减)
def update_radar_score(username, input_scores):
    try:
        user_data = get_user_profile(username)
        current = user_data.get('radar_profile')
        if not current: 
            current = {k: 3.0 for k in input_scores.keys()}
        elif isinstance(current, str): 
            current = json.loads(current)
        
        updated = {}
        alpha = config.RADAR_ALPHA # 学习率
        decay = config.RADAR_DECAY # 衰减率
        
        for k, v in input_scores.items():
            old_val = float(current.get(k, 3.0))
            new_val = float(v)
            # 公式：旧值衰减 + 新值学习
            final_val = (old_val * decay * (1 - alpha)) + (new_val * alpha)
            updated[k] = round(min(10.0, max(0.0, final_val)), 2)
            
        supabase.table('users').update({"radar_profile": json.dumps(updated)}).eq("username", username).execute()
    except: pass

# 🌟 v70 升级：寻找共鸣 (使用 MLS)
def find_resonance_v70(current_vec, current_user, current_data):
    if not current_vec: return None
    try:
        # 获取最近活跃的节点
        res = supabase.table('nodes').select("*").neq('username', current_user).eq('is_deleted', False).order('id', desc=True).limit(50).execute()
        others = res.data
        
        curr_profile = get_user_profile(current_user)
        curr_radar = json.loads(curr_profile.get('radar_profile', '{}')) if curr_profile else {}
        
        best_match = None
        highest_score = 0
        
        for row in others:
            if row['vector']:
                try:
                    o_vec = json.loads(row['vector'])
                    o_keywords = json.loads(row['keywords']) if row['keywords'] else []
                    
                    # 获取对方雷达 (简化：不查数据库，用默认值代替以提速，或者需额外查询)
                    o_radar = {} # 实际应查询
                    
                    MLS = calculate_MLS_v70(
                        current_vec, o_vec, 
                        current_data.get('keywords', []), o_keywords,
                        curr_radar, o_radar
                    )
                    
                    if MLS >= config.LINK_THRESHOLD['Strong'] and MLS > highest_score:
                        highest_score = MLS
                        best_match = {
                            "user": row['username'], 
                            "content": row['content'], 
                            "score": round(MLS * 100, 1),
                            "type": "Strong"
                        }
                except: continue
        return best_match
    except: return None

# ==========================================
# 💾 数据库操作 (保留所有功能)
# ==========================================

def make_hashes(password): return hashlib.sha256(str.encode(password)).hexdigest()

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
        
        coords = [116.4, 39.9] # Default
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
    return {"nickname": username, "radar_profile": None, "uid": "---"}

def update_heartbeat(username):
    try: supabase.table('users').update({"last_seen": datetime.now(timezone.utc).isoformat()}).eq("username", username).execute()
    except: pass

def check_is_online(last_seen_str):
    if not last_seen_str: return False
    try:
        if last_seen_str.endswith('Z'): last_seen = datetime.fromisoformat(last_seen_str.replace('Z', '+00:00'))
        else: last_seen = datetime.fromisoformat(last_seen_str)
        if last_seen.tzinfo is None: last_seen = last_seen.replace(tzinfo=timezone.utc)
        diff = datetime.now(timezone.utc) - last_seen
        return diff.total_seconds() < config.HEARTBEAT_TIMEOUT
    except: return False

# --- 社交 ---
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

# --- 节点 ---
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
        logic = data.get('m_score', 0.5) 
        keywords = data.get('keywords', [])
        insert_data = {
            "username": username, "content": content,
            "care_point": data.get('care_point', '未命名'),
            "meaning_layer": data.get('meaning_layer', '暂无结构'),
            "insight": data.get('insight', '生成中断'),
            "mode": mode, "vector": json.dumps(vector),
            "logic_score": logic, "keywords": json.dumps(keywords), "is_deleted": False,
            "c_score": data.get('c_score', 0), "m_score": data.get('m_score', 0)
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

# --- 群组 ---
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

def check_group_formation(new_node_data, vector, username): pass # 简化处理
