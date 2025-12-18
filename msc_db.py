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
    # 获取盐值，如果未配置则使用默认值（仅限开发环境，生产环境必须配置）
    SALT = st.secrets.get("PASSWORD_SALT", "msc_default_salt_2025") 
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"Database Connection Failed: {e}")
    st.stop()

def make_hashes(password):
    # 🛡️ Security Upgrade: 加盐哈希
    # 将盐值拼接到密码前后，防止彩虹表攻击
    raw = f"{SALT}{password}{SALT}"
    return hashlib.sha256(str.encode(raw)).hexdigest()

# ==========================================
# 📊 可观测性：系统日志
# ==========================================
def log_system_event(level, component, message, user="system"):
    """
    将系统事件写入数据库以便在 Admin 面板监控
    Level: INFO, WARN, ERROR
    """
    try:
        # 这一步不应阻塞主线程，尽力而为
        payload = {
            "level": level,
            "component": component,
            "message": str(message)[:500], # 截断防止过长
            "created_at": datetime.now(timezone.utc).isoformat(),
            "user_id": user
        }
        # 假设你已经在 Supabase 建了一个 'system_logs' 表
        # 如果没有建表，这行代码会静默失败（这是预期的，不应导致主程序崩溃）
        supabase.table('system_logs').insert(payload).execute()
    except:
        # 如果日志系统本身挂了，打印到控制台作为最后防线
        print(f"[{level}] {component}: {message}")

# ==========================================
# 👤 用户管理
# ==========================================
def login_user(username, password):
    try:
        hashed = make_hashes(password)
        res = supabase.table('users').select("*").eq('username', username).eq('password', hashed).execute()
        if res.data:
            log_system_event("INFO", "Auth", f"User {username} logged in", username)
            return res.data
        else:
            log_system_event("WARN", "Auth", f"Failed login attempt for {username}", username)
            return []
    except Exception as e: 
        log_system_event("ERROR", "Auth", str(e))
        return []

def add_user(username, password, nickname, country="Other"):
    try:
        res = supabase.table('users').select("*").eq('username', username).execute()
        if len(res.data) > 0: return False 
        
        radar = {"Care":3.0,"Curiosity":3.0,"Reflection":3.0,"Coherence":3.0,"Empathy":3.0,"Agency":3.0,"Aesthetic":3.0}
        
        data = {
            "username": username,
            "password": make_hashes(password),
            "nickname": nickname,
            "radar_profile": json.dumps(radar),
            "country": country,
            "last_seen": datetime.now(timezone.utc).isoformat()
        }
        supabase.table('users').insert(data).execute()
        log_system_event("INFO", "Auth", f"New user created: {username}", username)
        return True
    except Exception as e:
        log_system_event("ERROR", "Register", str(e))
        return False

# ==========================================
# 📖 读取操作 (缓存策略)
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
    except Exception as e:
        log_system_event("ERROR", "Radar", str(e), username)

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
    except Exception as e:
        log_system_event("ERROR", "ChatSave", str(e), username)

@st.cache_data(ttl=30)
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
        loc_data = data.get('location', {})
        if not loc_data: loc_data = {}

        payload = {
            "username": username, 
            "content": content, 
            "care_point": data.get('care_point','?'), 
            "meaning_layer": data.get('meaning_layer',''), 
            "insight": data.get('insight', ''), 
            "mode": mode, 
            "vector": vec, 
            "logic_score": logic, 
            "keywords": kw, 
            "is_deleted": False,
            "location": loc_data
        }
        
        supabase.table('nodes').insert(payload).execute()
        
        # 缓存失效
        get_active_nodes_map.clear()
        get_global_nodes.clear()
        get_all_nodes_for_map.clear() # 确保好友界面也能刷到
        
        log_system_event("INFO", "Node", f"Node created by {username} (Score: {logic:.2f})", username)
        return True, "Success"
    except Exception as e:
        log_system_event("ERROR", "NodeSave", str(e), username)
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
        return supabase.table('nodes').select("*").eq('is_deleted', False).order('id', desc=True).limit(200).execute().data
    except: return []

# ==========================================
# 📡 社交功能
# ==========================================
@st.cache_data(ttl=60)
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
    try: 
        supabase.table('direct_messages').insert({"sender":s,"receiver":r,"content":c}).execute()
        return True
    except Exception as e:
        log_system_event("ERROR", "DM", str(e), s)
        return False

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

def process_time_decay():
    try:
        res = supabase.table('nodes').select("*").neq('mode', 'Sediment').neq('mode', 'Genesis_Sim').execute()
        active_nodes = res.data
        sediment_count = 0
        now = datetime.now(timezone.utc)
        TTL_HOURS = 24 
        for node in active_nodes:
            try:
                created_at_str = node['created_at']
                if created_at_str.endswith('Z'): created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                else: created_at = datetime.fromisoformat(created_at_str)
                if created_at.tzinfo is None: created_at = created_at.replace(tzinfo=timezone.utc)
                age = (now - created_at).total_seconds() / 3600
                if age > TTL_HOURS:
                    supabase.table('nodes').update({"mode": "Sediment"}).eq("id", node['id']).execute()
                    sediment_count += 1
            except: continue
        if sediment_count > 0:
            log_system_event("INFO", "Decay", f"{sediment_count} nodes became sediment")
        return sediment_count
    except Exception as e: 
        log_system_event("ERROR", "Decay", str(e))
        return 0
    
# ==========================================
# 🆕 获取系统日志 (供 Admin 使用)
# ==========================================
def get_system_logs(limit=50):
    try:
        res = supabase.table('system_logs').select("*").order('created_at', desc=True).limit(limit).execute()
        return res.data
    except: return []
