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
from sklearn.decomposition import PCA 
from sklearn.cluster import KMeans

# 🛑 配置与初始化
def init_system():
    try:
        client = OpenAI(api_key=st.secrets["API_KEY"], base_url=st.secrets["BASE_URL"])
        model = st.secrets["MODEL_NAME"]
        supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
        return client, model, supabase
    except Exception as e: st.error(f"Error: {e}"); st.stop()

client_ai, TARGET_MODEL, supabase = init_system()

# 🧮 算法
def get_embedding(text): return np.random.rand(1536).tolist()
def cosine_similarity(v1, v2):
    if not v1 or not v2: return 0
    vec1, vec2 = np.array(v1), np.array(v2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)) if np.linalg.norm(vec1) > 0 else 0

def make_hashes(password): return hashlib.sha256(str.encode(password)).hexdigest()

# 🔐 用户操作
def login_user(username, password):
    try:
        hashed_pw = make_hashes(password)
        res = supabase.table('users').select("*").eq('username', username).eq('password', hashed_pw).execute()
        return res.data
    except: return []

def add_user(username, password, nickname):
    try:
        res = supabase.table('users').select("*").eq('username', username).execute()
        if len(res.data) > 0: return True 
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
            old_val = float(current_radar.get(key, 3.0))
            input_val = float(new_scores.get(key, 0))
            if input_val > 1.0: updated_radar[key] = round(min(10.0, old_val*(1-alpha)+input_val*alpha), 2)
            else: updated_radar[key] = old_val
        supabase.table('users').update({"radar_profile": json.dumps(updated_radar)}).eq("username", username).execute()
    except: pass

def calculate_rank(radar_data):
    if not radar_data: return "倔强青铜 III", "🥉"
    if isinstance(radar_data, str): radar_data = json.loads(radar_data)
    total = sum(radar_data.values())
    if total < 25: return "倔强青铜", "🥉"
    elif total < 30: return "秩序白银", "🥈"
    elif total < 38: return "荣耀黄金", "🥇"
    elif total < 46: return "尊贵铂金", "💎"
    elif total < 54: return "永恒钻石", "💠"
    elif total < 62: return "至尊星耀", "✨"
    else: return "最强王者", "👑"

# 🌟 社交功能：获取所有用户（模拟好友列表）
def get_all_users(current_user):
    try:
        res = supabase.table('users').select("username, nickname").neq('username', current_user).execute()
        return res.data
    except: return []

# 🌟 社交功能：获取私聊记录
def get_direct_messages(user1, user2):
    try:
        # 获取 sender=u1, receiver=u2 OR sender=u2, receiver=u1
        # Supabase 的 or 语法比较特殊，这里为了简单，分别查两次合并并排序（或者用 SQL view，这里用代码处理）
        res1 = supabase.table('direct_messages').select("*").eq('sender', user1).eq('receiver', user2).execute()
        res2 = supabase.table('direct_messages').select("*").eq('sender', user2).eq('receiver', user1).execute()
        
        all_msgs = res1.data + res2.data
        # 按时间排序
        all_msgs.sort(key=lambda x: x['id'])
        return all_msgs
    except: return []

# 🌟 社交功能：发送私信
def send_direct_message(sender, receiver, content):
    try:
        supabase.table('direct_messages').insert({
            "sender": sender, "receiver": receiver, "content": content
        }).execute()
        return True
    except: return False

# 💾 节点存取
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

# 🧠 AI 业务
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
        except: return {"error": True, "msg": "JSON解析失败"}
    except Exception as e: return {"error": True, "msg": str(e)}

def analyze_meaning_background(text):
    prompt = f"""
    分析输入："{text}"
    判断是否有深层意义（观点/情绪/洞察）。若只是寒暄（如你好/在吗/好的）返回 {{ "valid": false }}。
    若有意义返回 JSON:
    {{
        "valid": true,
        "care_point": "核心关切",
        "meaning_layer": "结构分析",
        "insight": "升维洞察",
        "logic_score": 0.8, 
        "keywords": ["tag1"], 
        "radar_scores": {{ "Care": 5, "Curiosity": 5, "Reflection": 5, "Coherence": 5, "Empathy": 5, "Agency": 5, "Aesthetic": 5 }}
    }}
    """
    return call_ai_api(prompt)

def find_resonance(current_vector, current_user):
    if not current_vector: return None
    try:
        res = supabase.table('nodes').select("*").neq('username', current_user).eq('is_deleted', False).execute()
        best_match, highest = None, 0
        for row in res.data:
            if row['vector']:
                try:
                    score = cosine_similarity(current_vector, json.loads(row['vector']))
                    if score > 0.75 and score > highest:
                        highest = score
                        best_match = {"user": row['username'], "content": row['content'], "score": round(score * 100, 1)}
                except: continue
        return best_match
    except: return None

# 🎨 渲染函数
def render_radar_chart(radar_dict, height="200px"):
    keys = ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]
    scores = [radar_dict.get(k, 3.0) for k in keys]
    option = {
        "backgroundColor": "transparent",
        "radar": {"indicator": [{"name": k, "max": 10} for k in keys], "splitArea": {"show": False}},
        "series": [{"type": "radar", "data": [{"value": scores, "areaStyle": {"color": "rgba(0,255,242,0.4)"}, "lineStyle": {"color": "#00fff2"}}]}]
    }
    st_echarts(options=option, height=height)

def render_cyberpunk_map(nodes, height="250px", is_fullscreen=False):
    if not nodes: return
    graph_nodes, graph_links = [], []
    symbol_base = 30 if is_fullscreen else 15
    for i, node in enumerate(nodes):
        logic = node.get('logic_score')
        if logic is None: logic = 0.5
        graph_nodes.append({
            "name": str(node['id']), "id": str(node['id']),
            "symbolSize": symbol_base * (0.8 + logic),
            "value": node['care_point'],
            "label": {"show": is_fullscreen, "formatter": node['care_point'][:5], "color": "#fff"},
            "vector": json.loads(node['vector']) if node.get('vector') else None
        })
    # 简单连线逻辑
    for i in range(len(graph_nodes)-1):
        graph_links.append({"source": graph_nodes[i]['id'], "target": graph_nodes[i+1]['id']})

    option = {
        "backgroundColor": "#0e1117",
        "series": [{"type": "graph", "layout": "force", "data": graph_nodes, "links": graph_links, "roam": True, "force": {"repulsion": 1000 if is_fullscreen else 300}, "itemStyle": {"shadowBlur": 10}}]
    }
    st_echarts(options=option, height=height)

# 🌟 修复：确保这个函数存在
@st.dialog("🔭 浩荡宇宙", width="large")
def view_fullscreen_map(nodes, user_name):
    st.markdown(f"### 🌌 {user_name} 的浩荡宇宙")
    render_cyberpunk_map(nodes, height="600px", is_fullscreen=True)

def render_2d_world_map(nodes):
    map_data = [{"lat": 39.9, "lon": 116.4, "size": 10, "label": "HQ"}]
    for _ in range(len(nodes) + 15): 
        map_data.append({"lat": float(np.random.uniform(-40, 60)), "lon": float(np.random.uniform(-130, 150)), "size": 5, "label": "Node"})
    df = pd.DataFrame(map_data)
    fig = go.Figure(data=go.Scattergeo(
        lon = df["lon"], lat = df["lat"], mode = 'markers',
        marker = dict(size=5, color='#ffd60a', opacity=0.8)
    ))
    fig.update_layout(
        geo = dict(scope='world', projection_type='natural earth', showland=True, landcolor="rgb(20, 20, 20)", bgcolor="black"),
        margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="black", height=500
    )
    st.plotly_chart(fig, use_container_width=True)

def render_3d_galaxy(nodes):
    st.info("星河数据加载中...")
