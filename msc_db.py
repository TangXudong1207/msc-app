import streamlit as st
from supabase import create_client, Client
import hashlib
import json
from datetime import datetime, timezone

# 🛑 数据库初始化
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"DB连接失败: {e}")
    st.stop()

# --- 基础工具 ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- 用户管理 ---
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
        # 简化处理其他国家坐标
        
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

def update_radar_score(username, new_scores):
    try:
        user_data = get_user_profile(username)
        current_radar = user_data.get('radar_profile')
        if not current_radar: current_radar = {k: 3.0 for k in new_scores.keys()}
        elif isinstance(current_radar, str): current_radar = json.loads(current_radar)
        alpha = 0.2
        updated_radar = {}
        for key in new_scores:
            old_val = float(current_radar.get(key, 3.0))
            input_val = float(new_scores.get(key, 0))
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

# --- 社交数据 ---
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

# --- 节点数据 ---
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

def get_global_nodes():
    try:
        res = supabase.table('nodes').select("*").eq('is_deleted', False).order('id', desc=True).limit(200).execute()
        return res.data
    except: return []

def soft_delete_chat_and_node(chat_id, content, username):
    try:
        supabase.table('chats').update({"is_deleted": True}).eq("id", chat_id).execute()
        supabase.table('nodes').update({"is_deleted": True}).eq("username", username).eq("content", content).execute()
        return True
    except: return False

# --- 查找共鸣数据 ---
def get_resonance_candidates(current_user):
    try:
        res = supabase.table('nodes').select("*").neq('username', current_user).eq('is_deleted', False).execute()
        return res.data
    except: return []
