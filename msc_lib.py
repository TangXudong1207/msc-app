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
# 🌟 核心修复：补全了这行缺失的引用
from sklearn.decomposition import PCA 
from sklearn.cluster import KMeans
from datetime import datetime, timezone
import msc_config as config

# ==========================================
# 🛑 1. 配置与初始化
# ==========================================
def init_system():
    try:
        client = OpenAI(
            api_key=st.secrets["API_KEY"],
            base_url=st.secrets["BASE_URL"]
        )
        model = st.secrets["MODEL_NAME"]
        
        supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
        return client, model, supabase
    except Exception as e:
        st.error(f"系统启动失败: {e}")
        st.stop()

client_ai, TARGET_MODEL, supabase = init_system()

# ==========================================
# 🧮 2. 核心算法
# ==========================================
def get_embedding(text):
    return np.random.rand(1536).tolist()

def cosine_similarity(v1, v2):
    if not v1 or not v2: return 0
    vec1 = np.array(v1); vec2 = np.array(v2)
    norm1 = np.linalg.norm(vec1); norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0: return 0
    return np.dot(vec1, vec2) / (norm1 * norm2)

def calculate_MLS(vec_a, vec_b, topic_a, topic_b, meaning_a, meaning_b, ex_a, ex_b):
    sim_vec = cosine_similarity(vec_a, vec_b)
    t_inter = len(set(topic_a).intersection(set(topic_b)))
    t_union = len(set(topic_a).union(set(topic_b)))
    topic_sim = t_inter / t_union if t_union > 0 else 0
    m_inter = len(set(meaning_a).intersection(set(meaning_b)))
    m_union = len(set(meaning_a).union(set(meaning_b)))
    meaning_sim = m_inter / m_union if m_union > 0 else 0
    
    if topic_sim > 0.7 and meaning_sim < 0.3: return 0.2
    
    ex_match = 1.0 if (ex_a and ex_b) else 0.0
    return 0.5 * meaning_sim + 0.3 * sim_vec + 0.2 * ex_match

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# ==========================================
# 🔐 3. 用户与数据库操作
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

def get_nickname(username):
    try:
        res = supabase.table('users').select("nickname").eq('username', username).execute()
        if res.data: return res.data[0]['nickname']
        return username
    except: return username

def get_user_profile(username):
    try:
        res = supabase.table('users').select("nickname, radar_profile").eq('username', username).execute()
        if res.data: return res.data[0]
    except: pass
    return {"nickname": username, "radar_profile": None, "uid": "---"}

def update_radar_score(username, new_scores):
    try:
        user_data = get_user_profile(username)
        current_radar = user_data.get('radar_profile')
        if not current_radar: current_radar = {k: 3.0 for k in new_scores.keys()}
        elif isinstance(current_radar, str): current_radar = json.loads(current_radar)
        
        alpha = config.RADAR_ALPHA
        updated = {}
        for k, v in new_scores.items():
            old = float(current_radar.get(k, 3.0))
            new_val = float(v)
            updated[k] = round(old * 0.9 + new_val * 0.1, 2) # 简化版更新公式
            
        supabase.table('users').update({"radar_profile": json.dumps(updated)}).eq("username", username).execute()
    except: pass

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

def calculate_rank(radar_data):
    if not radar_data: return "青铜", "🥉"
    if isinstance(radar_data, str): radar_data = json.loads(radar_data)
    total = sum(radar_data.values())
    if total < 25: return "青铜", "🥉"
    elif total < 38: return "黄金", "🥇"
    elif total < 54: return "钻石", "💠"
    else: return "王者", "👑"

def save_chat(username, role, content):
    try: supabase.table('chats').insert({"username": username, "role": role, "content": content, "is_deleted": False}).execute()
    except: pass

def get_active_chats(username, limit=50):
    try:
        res = supabase.table('chats').select("*").eq('username', username).eq('is_deleted', False).order('id', desc=True).limit(limit).execute()
        return list(reversed(res.data))
    except: return []

def soft_delete_chat_and_node(chat_id, content, username):
    try:
        supabase.table('chats').update({"is_deleted": True}).eq("id", chat_id).execute()
        supabase.table('nodes').update({"is_deleted": True}).eq("username", username).eq("content", content).execute()
        return True
    except: return False

def restore_item(table, item_id):
    try:
        supabase.table(table).update({"is_deleted": False}).eq("id", item_id).execute()
        return True
    except: return False

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
        c_topics = current_data.get('topic_tags', [])
        c_meanings = current_data.get('keywords', [])
        c_ex = current_data.get('existential_q', False)
        for row in others:
            if row['vector']:
                try:
                    o_vec = json.loads(row['vector'])
                    o_keywords = json.loads(row['keywords']) if row['keywords'] else []
                    o_topics = [] 
                    o_ex = False
                    MLS = calculate_MLS(current_vector, o_vec, c_topics, o_topics, c_meanings, o_keywords, c_ex, o_ex)
                    if MLS > 0.75 and MLS > highest_score:
                        highest_score = MLS
                        best_match = {"user": row['username'], "content": row['content'], "score": round(MLS * 100, 1)}
                except: continue
        return best_match
    except: return None

# ==========================================
# 🧠 4. AI 智能
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
        api_messages = [{"role": "system", "content": config.PROMPT_CHATBOT}]
        for msg in history_messages: api_messages.append({"role": msg["role"], "content": msg["content"]})
        return client_ai.chat.completions.create(model=TARGET_MODEL, messages=api_messages, temperature=0.8, stream=True)
    except Exception as e: return f"Error: {e}"

def analyze_meaning_background(text):
    prompt = f"{config.PROMPT_ANALYST}\n用户输入: \"{text}\""
    res = call_ai_api(prompt)
    if res.get("valid", False):
        c = res.get('c_score', 0)
        n = res.get('n_score', 0)
        m = c * n * 2
        res['m_score'] = m
        if m < config.MEANING_THRESHOLD: res["valid"] = False
    return res

def generate_daily_question(username, radar_data):
    recent = get_user_nodes(username); ctx = f"关注点：{[n['care_point'] for n in recent[-3:]]}" if recent else ""
    prompt = f"{config.PROMPT_DAILY}\n用户：{json.dumps(radar_data)}。{ctx}。输出 JSON: {{ 'question': '...' }}"
    res = call_ai_api(prompt)
    return res.get("question", "今天感觉如何？")

def analyze_persona_report(radar_data):
    prompt = f"{config.PROMPT_PERSONA}\n数据：{json.dumps(radar_data)}。输出 JSON: {{ 'static_portrait': '...', 'dynamic_growth': '...' }}"
    return call_ai_api(prompt)

def get_ai_interjection(history_text):
    prompt = f"{config.PROMPT_OBSERVER}\n{history_text}\n输出: 纯文本"
    try: return client_ai.chat.completions.create(model=TARGET_MODEL, messages=[{"role": "user", "content": prompt}], temperature=0.9).choices[0].message.content
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
        logic = node.get('m_score') if node.get('m_score') is not None else 0.5
        keywords = []
        if node.get('keywords'):
            if isinstance(node['keywords'], str): keywords = json.loads(node['keywords'])
            else: keywords = node['keywords']
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
                vec_sim = cosine_similarity(na['vector'], nb['vector'])
                if vec_sim > 0.8: graph_links.append({"source": na['name'], "target": nb['name'], "lineStyle": {"width": 2, "color": "#00fff2"}})
                elif vec_sim > 0.6: graph_links.append({"source": na['name'], "target": nb['name'], "lineStyle": {"width": 0.5, "color": "#555", "type": "dashed"}})
    option = {"backgroundColor": "#0e1117", "series": [{"type": "graph", "layout": "force", "data": graph_nodes, "links": graph_links, "roam": True, "force": {"repulsion": 1000 if is_fullscreen else 300}, "itemStyle": {"shadowBlur": 10}}]}
    st_echarts(options=option, height=height)

@st.dialog("🔭 浩荡宇宙", width="large")
def view_fullscreen_map(nodes, user_name):
    st.markdown(f"### 🌌 {user_name} 的浩荡宇宙")
    render_cyberpunk_map(nodes, height="600px", is_fullscreen=True)
