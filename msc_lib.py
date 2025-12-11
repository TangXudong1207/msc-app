import streamlit as st
from openai import OpenAI
from supabase import create_client, Client
from streamlit_echarts import st_echarts
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import re
import hashlib
import time
import numpy as np
from datetime import datetime, timezone
import msc_config as config # 🌟 引入配置文件

# 🛑 初始化
def init_system():
    try:
        client = OpenAI(api_key=st.secrets["API_KEY"], base_url=st.secrets["BASE_URL"])
        model = st.secrets["MODEL_NAME"]
        supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
        return client, model, supabase
    except Exception as e: st.error(f"System Error: {e}"); st.stop()

client_ai, TARGET_MODEL, supabase = init_system()

# 🧮 算法
def get_embedding(text): return np.random.rand(1536).tolist()
def cosine_similarity(v1, v2):
    vec1, vec2 = np.array(v1), np.array(v2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)) if np.linalg.norm(vec1) > 0 else 0
def make_hashes(password): return hashlib.sha256(str.encode(password)).hexdigest()

def calculate_rank(radar_data):
    if not radar_data: return "青铜", "🥉"
    if isinstance(radar_data, str): radar_data = json.loads(radar_data)
    total = sum(radar_data.values())
    if total < 25: return "青铜", "🥉"
    elif total < 38: return "黄金", "🥇"
    elif total < 54: return "钻石", "💠"
    else: return "王者", "👑"

# 🔐 用户
def login_user(username, password):
    try:
        hashed_pw = make_hashes(password)
        res = supabase.table('users').select("*").eq('username', username).eq('password', hashed_pw).execute()
        return res.data
    except: return []

def add_user(username, password, nickname):
    try:
        res = supabase.table('users').select("*").eq('username', username).execute()
        if len(res.data) > 0: return False 
        default_radar = {"Care": 3.0, "Curiosity": 3.0, "Reflection": 3.0, "Coherence": 3.0, "Empathy": 3.0, "Agency": 3.0, "Aesthetic": 3.0}
        data = {"username": username, "password": make_hashes(password), "nickname": nickname, "radar_profile": json.dumps(default_radar)}
        supabase.table('users').insert(data).execute()
        return True
    except: return False

def get_user_profile(username):
    try:
        res = supabase.table('users').select("nickname, radar_profile").eq('username', username).execute()
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

# --- 在线状态 ---
def update_heartbeat(username):
    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        supabase.table('users').update({"last_seen": now_iso}).eq("username", username).execute()
    except: pass

def check_is_online(last_seen_str):
    if not last_seen_str: return False
    try:
        last_seen = datetime.fromisoformat(last_seen_str.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        diff = now - last_seen
        return diff.total_seconds() < config.HEARTBEAT_TIMEOUT
    except: return False

# --- 社交 ---
def get_all_users(current_user):
    try:
        res = supabase.table('users').select("username, nickname, last_seen").neq('username', current_user).execute()
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

# --- 节点 ---
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
            "logic_score": logic, "keywords": json.dumps(keywords), "is_deleted": False
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

# --- 群组 (保留) ---
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

# --- AI ---
def call_ai_api(prompt):
    try:
        response = client_ai.chat.completions.create(
            model=TARGET_MODEL,
            messages=[{"role": "system", "content": "Output valid JSON only."}, {"role": "user", "content": prompt}],
            temperature=0.7, stream=False, response_format={"type": "json_object"} 
        )
        content = response.choices[0].message.content
        try:
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match: return json.loads(match.group(0))
            else: return json.loads(content)
        except: return {"error": True}
    except Exception as e: return {"error": True, "msg": str(e)}

def analyze_meaning_background(text):
    # 🌟 使用配置文件的 Prompt 和 阈值
    prompt = f"{config.PROMPT_ANALYST}\n用户输入: \"{text}\""
    res = call_ai_api(prompt)
    if res.get("valid", False):
        # 计算 M 值
        c = res.get('c_score', 0.5) if res.get('c_score') else 0.5 # 兼容
        # 🌟 这里的阈值现在是 config.MEANING_THRESHOLD (0.25)
        # 我们这里简单点，如果 AI 说 valid，我们就信它（因为 Prompt 里已经要求了）
        pass
    return res

# 🌟 新增：AI 观察者插话
def get_ai_interjection(history_text):
    prompt = f"{config.PROMPT_OBSERVER}\n对话记录:\n{history_text}"
    try:
        # 这里不需要 JSON，直接返回文本
        response = client_ai.chat.completions.create(
            model=TARGET_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9, # 更有创造力
        )
        return response.choices[0].message.content
    except: return None

def generate_daily_question(username, radar_data):
    recent = get_user_nodes(username)
    ctx = ""
    if recent: ctx = f"关注点：{[n['care_point'] for n in recent[-3:]]}"
    prompt = f"生成每日追问。用户：{json.dumps(radar_data)}。{ctx}。输出 JSON: {{ 'question': '...' }}"
    res = call_ai_api(prompt)
    if "question" in res: return res["question"]
    return "今天，什么事情让你感到'活着'？"

# --- 渲染 (保持不变) ---
def render_2d_world_map(nodes):
    map_data = [{"lat": 39.9, "lon": 116.4, "size": 10, "label": "HQ"}]
    for _ in range(len(nodes) + 15): 
        map_data.append({"lat": float(np.random.uniform(-40, 60)), "lon": float(np.random.uniform(-130, 150)), "size": 5, "label": "Node"})
    df = pd.DataFrame(map_data)
    fig = go.Figure(data=go.Scattergeo(lon=df["lon"], lat=df["lat"], mode='markers', marker=dict(size=5, color='#ffd60a', opacity=0.8)))
    fig.update_layout(geo=dict(scope='world', projection_type='natural earth', showland=True, landcolor="rgb(20, 20, 20)", bgcolor="black"), margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="black", height=500)
    st.plotly_chart(fig, use_container_width=True)

def render_3d_galaxy(nodes):
    if len(nodes)<3: st.info("🌌"); return
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
        logic = node.get('logic_score') or 0.5
        graph_nodes.append({"name": str(node['id']), "id": str(node['id']), "symbolSize": symbol_base * (0.8 + logic), "value": node['care_point'], "label": {"show": is_fullscreen, "formatter": node['care_point'][:5], "color": "#fff"}, "vector": json.loads(node['vector']) if node.get('vector') else None, "keywords": json.loads(node['keywords']) if node.get('keywords') else []})
    option = {"backgroundColor": "#0e1117", "series": [{"type": "graph", "layout": "force", "data": graph_nodes, "links": [], "roam": True, "force": {"repulsion": 1000 if is_fullscreen else 300}, "itemStyle": {"shadowBlur": 10}}]}
    st_echarts(options=option, height=height)
