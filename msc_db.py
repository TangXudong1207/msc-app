### msc_db.py (含时间衰变逻辑) ###

import streamlit as st
from supabase import create_client, Client
import hashlib
import json
from datetime import datetime, timezone

try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except: st.stop()

def make_hashes(password): return hashlib.sha256(str.encode(password)).hexdigest()

# --- 用户 ---
def login_user(username, password):
    try:
        hashed = make_hashes(password)
        res = supabase.table('users').select("*").eq('username', username).eq('password', hashed).execute()
        return res.data
    except: return []

def add_user(username, password, nickname, country="Other"):
    try:
        res = supabase.table('users').select("*").eq('username', username).execute()
        if len(res.data) > 0: return False 
        coords = [116.4, 39.9]
        if country == "USA": coords = [-95.7, 37.0]
        radar = {"Care":3.0,"Curiosity":3.0,"Reflection":3.0,"Coherence":3.0,"Empathy":3.0,"Agency":3.0,"Aesthetic":3.0}
        data = {"username":username,"password":make_hashes(password),"nickname":nickname,"radar_profile":json.dumps(radar),"country":country,"location":json.dumps(coords),"last_seen":datetime.now(timezone.utc).isoformat()}
        supabase.table('users').insert(data).execute()
        return True
    except: return False

def get_nickname(username):
    try:
        res = supabase.table('users').select("nickname").eq('username', username).execute()
        if res.data: return res.data[0]['nickname']
        return username
    except: return username

def get_user_profile(username):
    try:
        res = supabase.table('users').select("*").eq('username', username).execute()
        if res.data: return res.data[0]
    except: pass
    return {"nickname": username, "radar_profile": None}

def update_radar_score(username, input_scores):
    # (保留原有逻辑，此处略)
    pass

def update_heartbeat(username):
    try: supabase.table('users').update({"last_seen": datetime.now(timezone.utc).isoformat()}).eq("username", username).execute()
    except: pass

# --- 数据 ---
def save_chat(username, role, content):
    try: supabase.table('chats').insert({"username": username, "role": role, "content": content, "is_deleted": False}).execute()
    except: pass

def get_active_chats(username):
    try:
        res = supabase.table('chats').select("*").eq('username', username).eq('is_deleted', False).order('id', desc=True).limit(50).execute()
        return list(reversed(res.data))
    except: return []

def save_node(username, content, data, mode, vector):
    try:
        logic = data.get('m_score', 0.5)
        kw = json.dumps(data.get('keywords', []))
        vec = json.dumps(vector)
        # 注意：这里我们默认 mode='News' 或 'AI对话'
        # 沉淀后，mode 会变成 'Sediment'
        data = {
            "username":username, "content":content, 
            "care_point":data.get('care_point','?'), 
            "meaning_layer":data.get('meaning_layer',''), 
            "insight":data['insight'], "mode":mode, "vector":vec, 
            "logic_score":logic, "keywords":kw, "is_deleted":False,
            "location": json.dumps(data.get('location', {})) # 存位置
        }
        supabase.table('nodes').insert(data).execute()
        return True
    except: return False

def get_active_nodes_map(username):
    try:
        res = supabase.table('nodes').select("*").eq('username', username).eq('is_deleted', False).execute()
        return {n['content']: n for n in res.data}
    except: return {}

def get_all_nodes_for_map(username):
    try:
        res = supabase.table('nodes').select("*").eq('username', username).eq('is_deleted', False).execute()
        return res.data
    except: return []

def get_global_nodes():
    try: return supabase.table('nodes').select("*").eq('is_deleted', False).limit(200).execute().data
    except: return []

# --- 社交 ---
def get_all_users(curr):
    try: return supabase.table('users').select("username,nickname,last_seen,uid").neq('username',curr).execute().data
    except: return []

def get_direct_messages(u1, u2):
    try:
        r1 = supabase.table('direct_messages').select("*").eq('sender',u1).eq('receiver',u2).execute()
        r2 = supabase.table('direct_messages').select("*").eq('sender',u2).eq('receiver',u1).execute()
        msgs = r1.data + r2.data
        msgs.sort(key=lambda x: x['id'])
        return msgs
    except: return []

def send_direct_message(s, r, c):
    try: supabase.table('direct_messages').insert({"sender":s,"receiver":r,"content":c}).execute(); return True
    except: return False

def get_unread_counts(curr):
    try:
        res = supabase.table('direct_messages').select("sender").eq('receiver', curr).eq('is_read', False).execute()
        counts = {}
        for r in res.data: counts[r['sender']] = counts.get(r['sender'], 0) + 1
        return len(res.data), counts
    except: return 0, {}

def mark_read(s, r):
    try: supabase.table('direct_messages').update({"is_read":True}).eq('sender',s).eq('receiver',r).execute()
    except: pass

# ==========================================
# ⏳ 核心：时间流逝与沉淀 (New!)
# ==========================================
def process_time_decay():
    """
    检查所有 'News_Stream' 模式的节点。
    如果太旧 (比如 > 0.05 小时)，则将 mode 改为 'Sediment'。
    """
    try:
        # 1. 找出活跃新闻
        res = supabase.table('nodes').select("*").eq('mode', 'News_Stream').execute()
        active_nodes = res.data
        
        sediment_count = 0
        now = datetime.now(timezone.utc)
        TTL_HOURS = 0.05 # 3分钟寿命 (测试用)
        
        for node in active_nodes:
            try:
                created_at_str = node['created_at']
                if created_at_str.endswith('Z'):
                    created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                else:
                    created_at = datetime.fromisoformat(created_at_str)
                
                # 补全时区信息以免报错
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)

                age = (now - created_at).total_seconds() / 3600
                
                if age > TTL_HOURS:
                    # 沉淀：修改 mode
                    supabase.table('nodes').update({"mode": "Sediment"}).eq("id", node['id']).execute()
                    sediment_count += 1
            except: continue
            
        return sediment_count
    except Exception as e:
        print(f"Decay Error: {e}")
        return 0
