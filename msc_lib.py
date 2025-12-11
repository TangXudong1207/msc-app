import streamlit as st
from openai import OpenAI
from supabase import create_client, Client
from streamlit_echarts import st_echarts
import plotly.graph_objects as go
import pandas as pd
import json
import re
import hashlib
import time
import random
import numpy as np
from sklearn.decomposition import PCA 
from sklearn.cluster import KMeans

# 🛑 配置
def init_system():
    try:
        client = OpenAI(api_key=st.secrets["API_KEY"], base_url=st.secrets["BASE_URL"])
        model = st.secrets["MODEL_NAME"]
        supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
        return client, model, supabase
    except Exception as e: st.error(f"System Error: {e}"); st.stop()

client_ai, TARGET_MODEL, supabase = init_system()

# 🌍 国家坐标映射 (简化版)
COUNTRY_COORDS = {
    "China": [104.195, 35.861], "USA": [-95.712, 37.090], "UK": [-3.435, 55.378],
    "Japan": [138.252, 36.204], "Germany": [10.451, 51.165], "France": [2.213, 46.227],
    "Canada": [-106.346, 56.130], "Australia": [133.775, -25.274], "Russia": [105.318, 61.524],
    "India": [78.962, 20.593], "Brazil": [-51.925, -14.235], "Other": [0, 0]
}

# 🧮 算法
def get_embedding(text): return np.random.rand(1536).tolist()
def cosine_similarity(v1, v2):
    vec1, vec2 = np.array(v1), np.array(v2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)) if np.linalg.norm(vec1) > 0 else 0
def make_hashes(password): return hashlib.sha256(str.encode(password)).hexdigest()

def calculate_rank(radar_data):
    if not radar_data: return "MSC 公民", "🥉"
    if isinstance(radar_data, str): radar_data = json.loads(radar_data)
    total = sum(radar_data.values())
    if total < 25: return "观察者", "🥉"
    elif total < 38: return "探索者", "🥈"
    elif total < 54: return "构建者", "💎"
    else: return "领航员", "👑"

# 🔐 用户操作
def generate_uid():
    """生成8位随机数字ID"""
    return str(random.randint(10000000, 99999999))

def add_user(username, password, nickname, country):
    try:
        res = supabase.table('users').select("*").eq('username', username).execute()
        if len(res.data) > 0: return False 
        
        uid = generate_uid()
        coords = COUNTRY_COORDS.get(country, [0, 0])
        default_radar = {"Care": 3.0, "Curiosity": 3.0, "Reflection": 3.0, "Coherence": 3.0, "Empathy": 3.0, "Agency": 3.0, "Aesthetic": 3.0}
        
        data = {
            "username": username, "password": make_hashes(password), 
            "nickname": nickname, "radar_profile": json.dumps(default_radar),
            "uid": uid, "country": country, "location": json.dumps(coords)
        }
        supabase.table('users').insert(data).execute()
        return True
    except Exception as e: print(e); return False

def login_user(username, password):
    try:
        hashed_pw = make_hashes(password)
        res = supabase.table('users').select("*").eq('username', username).eq('password', hashed_pw).execute()
        return res.data
    except: return []

def get_user_profile(username):
    try:
        res = supabase.table('users').select("*").eq('username', username).execute()
        if res.data: return res.data[0]
    except: pass
    return {"nickname": username, "radar_profile": None, "uid": "Unknown", "country": "Unknown"}

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

# --- 消息与通知 ---
def get_all_users(current_user):
    try:
        # 获取所有用户的基本信息，用于好友列表
        res = supabase.table('users').select("username, nickname, uid, country, last_seen").neq('username', current_user).execute()
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
            sender = row['sender']
            counts[sender] = counts.get(sender, 0) + 1; total += 1
        return total, counts
    except: return 0, {}

def mark_messages_read(sender, receiver):
    try:
        supabase.table('direct_messages').update({"is_read": True}).eq('sender', sender).eq('receiver', receiver).eq('is_read', False).execute()
    except: pass

# --- 节点存取 ---
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
            "username": username, "content": content, "care_point": data.get('care_point', '未命名'), "meaning_layer": data.get('meaning_layer', '暂无结构'),
            "insight": data.get('insight', '生成中断'), "mode": mode, "vector": json.dumps(vector), "logic_score": logic, "keywords": json.dumps(keywords), "is_deleted": False
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
def soft_delete_chat_and_node(chat_id, content, username):
    try:
        supabase.table('chats').update({"is_deleted": True}).eq("id", chat_id).execute()
        supabase.table('nodes').update({"is_deleted": True}).eq("username", username).eq("content", content).execute()
        return True
    except: return False

# --- 在线状态 ---
def update_heartbeat(username):
    try: supabase.table('users').update({"last_seen": datetime.now(timezone.utc).isoformat()}).eq("username", username).execute()
    except: pass
def check_is_online(last_seen_str):
    if not last_seen_str: return False
    try:
        last_seen = datetime.fromisoformat(last_seen_str.replace('Z', '+00:00'))
        return (datetime.now(timezone.utc) - last_seen).total_seconds() < 300
    except: return False

# --- AI ---
def call_ai_api(prompt):
    try:
        response = client_ai.chat.completions.create(model=TARGET_MODEL, messages=[{"role": "system", "content": "Output valid JSON only."}, {"role": "user", "content": prompt}], temperature=0.7, stream=False, response_format={"type": "json_object"})
        content = response.choices[0].message.content
        try: match = re.search(r'\{.*\}', content, re.DOTALL); return json.loads(match.group(0)) if match else json.loads(content)
        except: return {"error": True}
    except Exception as e: return {"error": True}
def get_normal_response(history_messages):
    try:
        api_messages = [{"role": "system", "content": "你是温暖的对话伙伴。"}]
        for msg in history_messages: api_messages.append({"role": msg["role"], "content": msg["content"]})
        return client_ai.chat.completions.create(model=TARGET_MODEL, messages=api_messages, temperature=0.8, stream=True)
    except Exception as e: return f"Error: {e}"
def analyze_meaning_background(text):
    if len(text) < 4: return {"valid": False}
    prompt = f"""
    分析输入："{text}"。若无深层意义返回 {{ "valid": false }}。
    若有，返回 JSON: {{ "valid": true, "care_point": "...", "meaning_layer": "...", "insight": "...", "logic_score": 0.8, "keywords": [], "radar_scores": {{ "Care": 5, ... }} }}
    """
    res = call_ai_api(prompt)
    if res.get("valid") and res.get("logic_score", 0) < 0.4: res["valid"] = False
    return res
def generate_daily_question(username, radar_data):
    recent = get_user_nodes(username); ctx = f"关注点：{[n['care_point'] for n in recent[-3:]]}" if recent else ""
    res = call_ai_api(f"生成每日追问。用户：{json.dumps(radar_data)}。{ctx}。输出 JSON: {{ 'question': '...' }}")
    return res.get("question", "今天感觉如何？")
def analyze_persona_report(radar_data):
    return call_ai_api(f"任务：人物画像分析。雷达数据：{json.dumps(radar_data)}。输出 JSON: {{ 'static_portrait': '...', 'dynamic_growth': '...' }}")
def find_resonance(vec, user, data): return None # 简化

# --- 视觉渲染 (升级版) ---
def render_2d_world_map():
    """
    升级版地球：显示所有用户的位置（蓝色）和意义节点（黄色）
    """
    try:
        # 1. 获取所有用户
        users_res = supabase.table('users').select("username, location, country").execute()
        user_data = []
        for u in users_res.data:
            if u['location']:
                try:
                    loc = json.loads(u['location'])
                    user_data.append({"lat": loc[1], "lon": loc[0], "name": u['username'], "type": "Citizen"})
                except: pass
        
        # 2. 获取所有节点 (为了性能只取最新的100个)
        nodes_res = supabase.table('nodes').select("vector").eq('is_deleted', False).order('id', desc=True).limit(100).execute()
        # 这里为了演示，随机撒点，实际应该关联用户坐标
        # 为了美观，我们假设节点就在用户附近漂浮
        
        df = pd.DataFrame(user_data)
        if df.empty: return

        fig = go.Figure()

        # 层1：用户 (蓝色光点)
        fig.add_trace(go.Scattergeo(
            lon = df["lon"], lat = df["lat"],
            text = df["name"],
            mode = 'markers',
            marker = dict(size=8, color='#00d2ff', opacity=1.0, line=dict(width=1, color='white')),
            name = "Citizens"
        ))

        fig.update_layout(
            geo = dict(
                scope='world', projection_type='natural earth',
                showland=True, landcolor="#0e1117", 
                showocean=True, oceancolor="#050510",
                showcountries=True, countrycolor="#333",
                bgcolor="#000"
            ),
            margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="black", height=500,
            showlegend=True, legend=dict(font=dict(color="white"))
        )
        st.plotly_chart(fig, use_container_width=True)
    except: st.info("地图数据加载中...")

def render_radar_chart(radar_dict, height="200px"):
    keys = ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]
    scores = [radar_dict.get(k, 3.0) for k in keys]
    option = {"backgroundColor": "transparent", "radar": {"indicator": [{"name": k, "max": 10} for k in keys], "splitArea": {"show": False}}, "series": [{"type": "radar", "data": [{"value": scores, "areaStyle": {"color": "rgba(0,255,242,0.4)"}, "lineStyle": {"color": "#00fff2"}}]}]}
    st_echarts(options=option, height=height)

def render_cyberpunk_map(nodes, height="250px", is_fullscreen=False):
    # (保持原样，省略)
    if not nodes: return
    graph_nodes = [{"name": str(n['id']), "symbolSize": 20, "value": n['care_point']} for n in nodes]
    option = {"backgroundColor": "#0e1117", "series": [{"type": "graph", "layout": "force", "data": graph_nodes, "force": {"repulsion": 500}}]}
    st_echarts(options=option, height=height)
