### msc_db.py ###
import streamlit as st
from supabase import create_client, Client
import hashlib
import json
from datetime import datetime, timezone

# ==========================================
# 🛡️ 安全配置 & 初始化
# ==========================================
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    SALT = st.secrets.get("PASSWORD_SALT", "msc_default_salt") 
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"Database Connection Failed: {e}")
    st.stop()

def make_hashes(password):
    raw = f"{SALT}{password}{SALT}"
    return hashlib.sha256(str.encode(raw)).hexdigest()

# ==========================================
# 📊 可观测性：系统日志
# ==========================================
def log_system_event(level, component, message, user="system"):
    try:
        payload = {
            "level": level, "component": component,
            "message": str(message)[:500],
            "created_at": datetime.now(timezone.utc).isoformat(), "user_id": user
        }
        supabase.table('system_logs').insert(payload).execute()
    except: pass 

# 🟢 新增：检查用户是否发生过某类事件 (用于一次性动画判断)
def check_user_event_exists(username, component_tag):
    try:
        res = supabase.table('system_logs').select("id").eq('user_id', username).eq('component', component_tag).limit(1).execute()
        return len(res.data) > 0
    except: return False

# ==========================================
# 👤 用户管理
# ==========================================
def login_user(username, password):
    try:
        hashed_new = make_hashes(password)
        res = supabase.table('users').select("*").eq('username', username).eq('password', hashed_new).execute()
        if res.data:
            log_system_event("INFO", "Auth", f"User {username} logged in (Secure)", username)
            return res.data
        
        hashed_old = hashlib.sha256(str.encode(password)).hexdigest()
        res_old = supabase.table('users').select("*").eq('username', username).eq('password', hashed_old).execute()
        
        if res_old.data:
            supabase.table('users').update({"password": hashed_new}).eq("username", username).execute()
            log_system_event("WARN", "Auth", f"User {username} migrated to secure password", username)
            return res_old.data
        return []
    except Exception as e:
        log_system_event("ERROR", "Login", str(e)) 
        return []

def add_user(username, password, nickname, country="Other"):
    try:
        res = supabase.table('users').select("*").eq('username', username).execute()
        if len(res.data) > 0: return False 
        
        radar = {"Care":3.0,"Curiosity":3.0,"Reflection":3.0,"Coherence":3.0,"Empathy":3.0,"Agency":3.0,"Aesthetic":3.0}
        data = {
            "username": username, "password": make_hashes(password),
            "nickname": nickname, "radar_profile": json.dumps(radar),
            "country": country, "last_seen": datetime.now(timezone.utc).isoformat()
        }
        supabase.table('users').insert(data).execute()
        return True
    except: return False

# ==========================================
# 📖 读取操作
# ==========================================

@st.cache_data(ttl=300)
def get_nickname(username):
    try:
        res = supabase.table('users').select("nickname").eq('username', username).execute()
        if res.data: return res.data[0]['nickname']
        return username
    except: return username

@st.cache_data(ttl=60)
def get_user_profile(username):
    try:
        res = supabase.table('users').select("*").eq('username', username).execute()
        if res.data: return res.data[0]
    except: pass
    return {"nickname": username, "radar_profile": None}

def update_radar_score(username, input_scores):
    try:
        supabase.table('users').update({"radar_profile": input_scores}).eq("username", username).execute()
        get_user_profile.clear()
    except: pass

def update_heartbeat(username):
    try: supabase.table('users').update({"last_seen": datetime.now(timezone.utc).isoformat()}).eq("username", username).execute()
    except: pass

# ==========================================
# 💾 数据写入
# ==========================================
def save_chat(username, role, content):
    try: 
        supabase.table('chats').insert({"username": username, "role": role, "content": content, "is_deleted": False}).execute()
        get_active_chats.clear()
        get_active_chats.clear()
    except: pass

@st.cache_data(ttl=10)
def get_active_chats(username):
    try:
        res = supabase.table('chats').select("*").eq('username', username).eq('is_deleted', False).order('id', desc=True).limit(50).execute()
        return list(reversed(res.data))
    except: return []

def save_node(username, content, data, mode, vector):
    try:
        logic = data.get('m_score', 0.5)
        kw = json.dumps(data.get('keywords', []))
        vec = str(vector) 
        loc_data = data.get('location', {}) if data.get('location') else {}

        payload = {
            "username": username, "content": content, "care_point": data.get('care_point','?'), 
            "meaning_layer": data.get('meaning_layer',''), "insight": data.get('insight', ''), 
            "mode": mode, "vector": vec, "logic_score": logic, 
            "keywords": kw, "is_deleted": False, "location": loc_data
        }
        
        supabase.table('nodes').insert(payload).execute()
        
        get_active_nodes_map.clear()
        get_global_nodes.clear()
        get_all_nodes_for_map.clear()
        
        log_system_event("INFO", "Node", f"Node created by {username} ({logic:.2f})", username)
        return True, "Success"
    except Exception as e:
        return False, str(e)

@st.cache_data(ttl=60)
def get_active_nodes_map(username):
    try:
        res = supabase.table('nodes').select("*").eq('username', username).eq('is_deleted', False).execute()
        return {n['content']: n for n in res.data}
    except: return {}

@st.cache_data(ttl=60)
def get_all_nodes_for_map(username):
    try:
        res = supabase.table('nodes').select("*").eq('username', username).eq('is_deleted', False).execute()
        return res.data
    except: return []

@st.cache_data(ttl=120)
def get_global_nodes():
    try: 
        return supabase.table('nodes').select("*").eq('is_deleted', False).order('id', desc=True).limit(500).execute().data
    except: return []

# ==========================================
# 📡 社交 & 消息 & 好友请求
# ==========================================
@st.cache_data(ttl=60)
def get_all_users(curr):
    try: 
        return supabase.table('users').select("username,nickname,last_seen,uid,radar_profile").neq('username',curr).execute().data
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

def send_friend_request(sender, receiver, match_type, metaphor):
    try:
        # 检查是否已存在
        existing = supabase.table('friend_requests').select("*").or_(f"and(sender.eq.{sender},receiver.eq.{receiver}),and(sender.eq.{receiver},receiver.eq.{sender})").execute()
        if existing.data: return False, "Link already exists or pending."
        
        payload = {
            "sender": sender, "receiver": receiver, 
            "status": "pending", "match_type": match_type, 
            "metaphor": metaphor,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        supabase.table('friend_requests').insert(payload).execute()
        return True, "Signal Sent"
    except Exception as e: return False, str(e)

def get_pending_requests(receiver):
    try:
        res = supabase.table('friend_requests').select("*").eq('receiver', receiver).eq('status', 'pending').execute()
        return res.data
    except: return []

def handle_friend_request(req_id, action): # action: 'accepted' or 'rejected'
    try:
        supabase.table('friend_requests').update({"status": action}).eq('id', req_id).execute()
        return True
    except: return False

def get_my_friends(username):
    try:
        r1 = supabase.table('friend_requests').select("receiver, metaphor").eq('sender', username).eq('status', 'accepted').execute()
        r2 = supabase.table('friend_requests').select("sender, metaphor").eq('receiver', username).eq('status', 'accepted').execute()
        friends = []
        for r in r1.data: friends.append({'username': r['receiver'], 'metaphor': r['metaphor']})
        for r in r2.data: friends.append({'username': r['sender'], 'metaphor': r['metaphor']})
        return friends
    except: return []

# ==========================================
# 🛠️ 系统维护
# ==========================================
def process_time_decay():
    try:
        res = supabase.table('nodes').select("*").neq('mode', 'Sediment').execute()
        active_nodes = res.data
        sediment_count = 0
        now = datetime.now(timezone.utc)
        for node in active_nodes:
            try:
                created_at = datetime.fromisoformat(node['created_at'].replace('Z', '+00:00'))
                if (now - created_at).total_seconds() / 3600 > 24:
                    supabase.table('nodes').update({"mode": "Sediment"}).eq("id", node['id']).execute()
                    sediment_count += 1
            except: continue
        return sediment_count
    except: return 0

def get_system_logs(limit=50):
    try:
        return supabase.table('system_logs').select("*").order('created_at', desc=True).limit(limit).execute().data
    except: return []

def nuke_user(target_username):
    try:
        try: supabase.table('system_logs').delete().eq('user_id', target_username).execute()
        except: pass 
        supabase.table('direct_messages').delete().eq('sender', target_username).execute()
        supabase.table('direct_messages').delete().eq('receiver', target_username).execute()
        supabase.table('nodes').delete().eq('username', target_username).execute()
        supabase.table('chats').delete().eq('username', target_username).execute()
        supabase.table('friend_requests').delete().eq('sender', target_username).execute() 
        supabase.table('friend_requests').delete().eq('receiver', target_username).execute() 
        supabase.table('users').delete().eq('username', target_username).execute()
        
        get_active_nodes_map.clear()
        get_global_nodes.clear()
        get_all_users.clear()
        get_user_profile.clear()
        get_active_chats.clear()
        
        return True, "Target eliminated."
    except Exception as e:
        return False, str(e)
