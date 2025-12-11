import streamlit as st
from openai import OpenAI
from supabase import create_client, Client
from streamlit_echarts import st_echarts
import pydeck as pdk
import pandas as pd
import json
import re
import hashlib
import time
import numpy as np
from datetime import datetime
from sklearn.decomposition import PCA 
from sklearn.cluster import KMeans    

# ==========================================
# 🛑 核心配置区
# ==========================================

try:
    client = OpenAI(
        api_key=st.secrets["API_KEY"],
        base_url=st.secrets["BASE_URL"]
    )
    TARGET_MODEL = st.secrets["MODEL_NAME"]

    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

except Exception as e:
    st.error(f"🚨 配置错误: {str(e)}")
    st.stop()

# ==========================================

# --- 🛠️ 基础设施 ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def add_user(username, password, nickname):
    try:
        res = supabase.table('users').select("*").eq('username', username).execute()
        if len(res.data) > 0: return False
        default_radar = {"Care": 3.0, "Curiosity": 3.0, "Reflection": 3.0, "Coherence": 3.0, "Empathy": 3.0, "Agency": 3.0, "Aesthetic": 3.0}
        data = {"username": username, "password": make_hashes(password), "nickname": nickname, "radar_profile": json.dumps(default_radar)}
        supabase.table('users').insert(data).execute()
        return True
    except: return False

def login_user(username, password):
    try:
        hashed_pw = make_hashes(password)
        res = supabase.table('users').select("*").eq('username', username).eq('password', hashed_pw).execute()
        return res.data
    except: return []

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
    return {"nickname": username, "radar_profile": None}

def update_radar_score(username, new_scores):
    try:
        user_data = get_user_profile(username)
        current_radar = user_data.get('radar_profile')
        if not current_radar:
            current_radar = {k: 3.0 for k in new_scores.keys()}
        elif isinstance(current_radar, str):
            current_radar = json.loads(current_radar)
        alpha = 0.08
        updated_radar = {}
        for key in new_scores:
            old_val = float(current_radar.get(key, 3.0))
            input_val = float(new_scores.get(key, 0))
            if input_val > 1.0:
                updated_val = old_val * (1 - alpha) + input_val * alpha
                updated_radar[key] = round(min(10.0, updated_val), 2)
            else:
                updated_radar[key] = old_val
        supabase.table('users').update({"radar_profile": json.dumps(updated_radar)}).eq("username", username).execute()
    except: pass

def calculate_rank(radar_data):
    if not radar_data: return "倔强青铜 III", "🥉"
    total_score = sum(radar_data.values())
    if total_score < 25: return "倔强青铜", "🥉"
    elif total_score < 30: return "秩序白银", "🥈"
    elif total_score < 38: return "荣耀黄金", "🥇"
    elif total_score < 46: return "尊贵铂金", "💎"
    elif total_score < 54: return "永恒钻石", "💠"
    elif total_score < 62: return "至尊星耀", "✨"
    else: return "最强王者", "👑"

# --- 💾 数据库操作 ---
def save_chat(username, role, content):
    try:
        data = {"username": username, "role": role, "content": content, "is_deleted": False}
        supabase.table('chats').insert(data).execute()
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

def save_node(username, content, data, mode, vector):
    try:
        logic = data.get('logic_score')
        if logic is None: logic = 0.5
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

def get_global_nodes():
    try:
        res = supabase.table('nodes').select("*").eq('is_deleted', False).order('id', desc=True).limit(200).execute()
        return res.data
    except: return []

# --- 🌌 群组反应堆 (Spontaneous Group Engine) ---

def check_group_formation(new_node_data, vector, username):
    """
    每次生成新节点时触发，检查是否满足建群条件
    """
    care_point = new_node_data.get('care_point')
    if not care_point: return
    
    # 路径 1: 意义星团引力 (Cluster Gravity)
    # 检查数据库中是否有足够多的人讨论过类似的 Care Point
    try:
        # 简单模糊匹配
        res = supabase.table('nodes').select("*").ilike('care_point', f"%{care_point}%").execute()
        count = len(res.data)
        
        # 阈值：假设超过 2 个不同用户提到，就建立星团 (测试用低阈值)
        unique_users = set([row['username'] for row in res.data])
        
        if len(unique_users) >= 2:
            room_name = f"🌌 {care_point} · 星团"
            # 检查房间是否已存在
            existing = supabase.table('rooms').select("*").eq('name', room_name).execute()
            if not existing.data:
                # 创建房间
                supabase.table('rooms').insert({
                    "name": room_name,
                    "type": "Gravity",
                    "trigger_keyword": care_point,
                    "description": f"由 {len(unique_users)} 位探索者的共同意义汇聚而成。"
                }).execute()
                st.toast(f"🌟 意义引力临界点已突破！自动生成星团：{room_name}", icon="🪐")
    except Exception as e: print(f"Group check error: {e}")

def get_available_rooms():
    try:
        res = supabase.table('rooms').select("*").order('created_at', desc=True).execute()
        return res.data
    except: return []

def join_room(room_id, username):
    try:
        # 检查是否已加入
        check = supabase.table('room_members').select("*").eq('room_id', room_id).eq('username', username).execute()
        if not check.data:
            supabase.table('room_members').insert({"room_id": room_id, "username": username}).execute()
    except: pass

def get_room_messages(room_id):
    try:
        res = supabase.table('room_chats').select("*").eq('room_id', room_id).order('created_at', desc=False).execute()
        return res.data
    except: return []

def send_room_message(room_id, username, content):
    try:
        supabase.table('room_chats').insert({"room_id": room_id, "username": username, "content": content}).execute()
    except: pass

# --- 🧠 AI 核心 ---
def call_ai_api(prompt):
    try:
        response = client.chat.completions.create(
            model=TARGET_MODEL,
            messages=[{"role": "system", "content": "Output valid JSON only. Do not use markdown blocks."}, {"role": "user", "content": prompt}],
            temperature=0.7, stream=False, response_format={"type": "json_object"} 
        )
        content = response.choices[0].message.content
        try:
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match: return json.loads(match.group(0))
            else: return json.loads(content)
        except: return {"error": True, "msg": "JSON解析失败"}
    except Exception as e: return {"error": True, "msg": str(e)}

def get_embedding(text):
    return np.random.rand(1536).tolist()

def get_normal_response(history_messages):
    try:
        api_messages = [{"role": "system", "content": "你是温暖的对话伙伴。"}]
        for msg in history_messages:
            api_messages.append({"role": msg["role"], "content": msg["content"]})
        response = client.chat.completions.create(
            model=TARGET_MODEL, messages=api_messages, temperature=0.8, stream=True 
        )
        return response
    except Exception as e: return f"Error: {e}"

def analyze_meaning_background(text):
    prompt = f"""
    分析输入："{text}"
    1. 判断是否生成节点 (valid: true/false)。只有具备深层观点或情绪才生成。
    2. 提取 Topic Tags (表层话题)。
    3. 提取 Meaning Tags (深层价值)。
    4. 提取 Care Point (简短关切)。
    5. 提取 Meaning Layer (结构分析)。
    6. 提取 Insight (升维洞察)。
    
    返回 JSON:
    {{
        "valid": true,
        "care_point": "...",
        "meaning_layer": "...",
        "insight": "...",
        "logic_score": 0.8,
        "keywords": ["tag1", "tag2"], 
        "topic_tags": ["topic1", "topic2"],
        "existential_q": false,
        "radar_scores": {{ "Care": 7 ... }}
    }}
    """
    return call_ai_api(prompt)

def generate_fusion(node_a_content, node_b_content):
    prompt = f"""
    任务：基于 Deep Meaning 共鸣进行融合。
    A: "{node_a_content}"
    B: "{node_b_content}"
    返回 JSON: {{ "care_point": "...", "meaning_layer": "...", "insight": "..." }}
    """
    return call_ai_api(prompt)

# --- 🧮 算法 ---
def cosine_similarity(v1, v2):
    vec1, vec2 = np.array(v1), np.array(v2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)) if np.linalg.norm(vec1) > 0 else 0

def find_resonance(current_vector, current_user):
    if not current_vector: return None
    try:
        res = supabase.table('nodes').select("*").neq('username', current_user).eq('is_deleted', False).execute()
        others = res.data
        best_match, highest_score = None, 0
        for row in others:
            if row['vector']:
                try:
                    score = cosine_similarity(current_vector, json.loads(row['vector']))
                    if score > 0.75 and score > highest_score:
                        highest_score = score
                        best_match = {"user": row['username'], "content": row['content'], "score": round(score * 100, 1)}
                except: continue
        return best_match
    except: return None

# --- 🌍 视觉渲染 ---
def render_2d_world_map(nodes):
    map_data = [{"name": "HQ", "value": [116.4, 39.9, 100]}]
    for _ in range(len(nodes) + 10): 
        lon, lat = np.random.uniform(-150, 150), np.random.uniform(-40, 60)
        map_data.append({"name": "Node", "value": [float(lon), float(lat), 50]})
    option = {
        "backgroundColor": "#080b10",
        "title": {"text": "🌍 全球意义分布", "left": "center", "textStyle": {"color": "#fff"}},
        "geo": {"map": "world", "roam": True, "itemStyle": {"normal": {"areaColor": "#1a2639", "borderColor": "#2c3e50"}, "emphasis": {"areaColor": "#2a9d8f"}}},
        "series": [{"type": "scatter", "coordinateSystem": "geo", "data": map_data, "symbolSize": 5, "itemStyle": {"color": "#ffd60a", "shadowBlur": 10, "shadowColor": "#ffd60a"}}]
    }
    st_echarts(options=option, height="500px", map="world")

def render_3d_galaxy(nodes):
    if len(nodes) < 3: st.info("🌌 星河汇聚中..."); return
    vectors, labels, sizes, colors = [], [], [], []
    for i, node in enumerate(nodes):
        if node['vector']:
            try:
                v = json.loads(node['vector'])
                vectors.append(v)
                labels.append(node['care_point'])
                sizes.append(np.random.randint(5, 15))
                colors.append(i % 3)
            except: pass
    if not vectors: return
    pca = PCA(n_components=3)
    coords = pca.fit_transform(vectors)
    df = pd.DataFrame(coords, columns=['x', 'y', 'z'])
    df['label'] = labels
    df['size'] = sizes
    df['cluster'] = colors
    fig = px.scatter_3d(df, x='x', y='y', z='z', color='cluster', size='size', hover_name='label', template="plotly_dark", opacity=0.8)
    fig.update_layout(scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False), bgcolor='black'), paper_bgcolor="black", margin={"r":0,"t":0,"l":0,"b":0}, height=600, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

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
        logic = node.get('logic_score', 0.5)
        graph_nodes.append({
            "name": str(node['id']), "id": str(node['id']),
            "symbolSize": symbol_base * (0.8 + logic),
            "value": node['care_point'],
            "label": {"show": is_fullscreen, "formatter": node['care_point'][:5], "color": "#fff"},
            "vector": json.loads(node['vector']) if node.get('vector') else None,
            "keywords": json.loads(node['keywords']) if node.get('keywords') else []
        })
    node_count = len(graph_nodes)
    # 🌟 连线逻辑：只显示强共鸣，模拟星系
    for i in range(node_count):
        for j in range(i + 1, node_count):
            na, nb = graph_nodes[i], graph_nodes[j]
            if na['vector'] and nb['vector']:
                vec_sim = cosine_similarity(na['vector'], nb['vector'])
                if vec_sim > 0.8: # 强链接
                    graph_links.append({"source": na['name'], "target": nb['name'], "lineStyle": {"width": 2, "color": "#00fff2"}})
                elif vec_sim > 0.65: # 弱链接
                    graph_links.append({"source": na['name'], "target": nb['name'], "lineStyle": {"width": 0.5, "color": "#555", "type": "dashed"}})
    
    option = {
        "backgroundColor": "#0e1117",
        "series": [{"type": "graph", "layout": "force", "data": graph_nodes, "links": graph_links, "roam": True, "force": {"repulsion": 1000 if is_fullscreen else 300}, "itemStyle": {"shadowBlur": 10}}]
    }
    st_echarts(options=option, height=height)

# --- 🖥️ 弹窗 ---
@st.dialog("🔭 浩荡宇宙", width="large")
def view_fullscreen_map(nodes, user_name):
    st.markdown(f"### 🌌 {user_name} 的浩荡宇宙")
    render_cyberpunk_map(nodes, height="600px", is_fullscreen=True)

@st.dialog("🌍 MSC World · 上帝视角", width="large")
def view_msc_world():
    global_nodes = get_global_nodes()
    tab1, tab2 = st.tabs(["🌍 地球夜景 (2D)", "🌌 意义星河 (3D)"])
    with tab1: render_2d_world_map(global_nodes)
    with tab2: render_3d_galaxy(global_nodes)

@st.dialog("🧬 元人性进化面板", width="large")
def view_radar_details(radar_dict):
    st.caption("您的意义生成动力学模型")
    render_radar_chart(radar_dict, height="300px")
    st.divider()
    # 这里可以放AI分析报告，为了代码精简暂略

@st.dialog("🪐 进入星团房间")
def view_group_chat(room, username):
    st.markdown(f"### {room['name']}")
    st.caption(room['description'])
    
    # 渲染群聊消息
    messages = get_room_messages(room['id'])
    for m in messages:
        with st.chat_message("user" if m['username'] == username else "assistant"):
            st.markdown(f"**{m['username']}**: {m['content']}")
            
    if prompt := st.chat_input("在星团中发言..."):
        send_room_message(room['id'], username, prompt)
        st.rerun()

# ==========================================
# 🖥️ 主程序
# ==========================================

st.set_page_config(page_title="MSC v26.0 Community", layout="wide", initial_sidebar_state="expanded")

if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌌 MSC")
    # Login UI (same)
    tab1, tab2 = st.tabs(["登录", "注册"])
    with tab1:
        u = st.text_input("用户名")
        p = st.text_input("密码", type='password')
        if st.button("登录", use_container_width=True):
            res = login_user(u, p)
            if res:
                st.session_state.logged_in = True
                st.session_state.username = u
                st.session_state.nickname = res[0]['nickname']
                st.session_state.messages = [] 
                st.rerun()
            else: st.error("错误")
    with tab2:
        nu = st.text_input("新用户名")
        np_pass = st.text_input("新密码", type='password')
        nn = st.text_input("昵称")
        if st.button("注册", use_container_width=True):
            if add_user(nu, np_pass, nn): st.success("成功")
            else: st.error("失败")

else:
    chat_history = get_active_chats(st.session_state.username)
    nodes_map = get_active_nodes_map(st.session_state.username)
    all_nodes_list = get_all_nodes_for_map(st.session_state.username)
    user_profile = get_user_profile(st.session_state.username)
    
    raw_radar = user_profile.get('radar_profile')
    if isinstance(raw_radar, str): radar_dict = json.loads(raw_radar)
    else: radar_dict = raw_radar if raw_radar else {k:3.0 for k in ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]}

    with st.sidebar:
        rank_name, rank_icon = calculate_rank(radar_dict)
        st.markdown(f"## {rank_icon} {st.session_state.nickname}")
        
        # 1. 雷达详情入口
        render_radar_chart(radar_dict)
        if st.button("🧬 查看详细画像", use_container_width=True):
            view_radar_details(radar_dict)
        
        # 2. 世界入口
        if st.button("🌍 MSC World", use_container_width=True, type="primary"):
            view_msc_world()
            
        # 3. 🌟 新增：发现星团
        st.divider()
        st.subheader("🌌 发现星团")
        rooms = get_available_rooms()
        if rooms:
            for room in rooms:
                if st.button(f"{room['name']}", key=f"room_{room['id']}", use_container_width=True):
                    join_room(room['id'], st.session_state.username)
                    view_group_chat(room, st.session_state.username)
        else:
            st.caption("暂无自发星团，等待意义汇聚...")

        st.divider()
        render_cyberpunk_map(all_nodes_list, height="200px")
        # 4. 个性化全屏入口
        if st.button(f"🔭 {st.session_state.nickname} 的浩荡宇宙", use_container_width=True): 
            view_fullscreen_map(all_nodes_list, st.session_state.nickname)
        
        if st.button("退出"): st.session_state.logged_in = False; st.rerun()

    st.subheader("💬 意义流")
    for msg in chat_history:
        col_chat, col_node = st.columns([0.65, 0.35], gap="small")
        with col_chat:
            c_msg, c_del = st.columns([0.9, 0.1])
            with c_msg:
                with st.chat_message(msg['role']): st.markdown(msg['content'], unsafe_allow_html=True)
            with c_del:
                if msg['role'] == 'user':
                    if st.button("✕", key=f"del_{msg['id']}"):
                        if soft_delete_chat_and_node(msg['id'], msg['content'], st.session_state.username): st.rerun()
            if msg.get('role') == 'assistant' and "🧬 融合成功" in msg['content']: pass 

        with col_node:
            if msg['role'] == 'user' and msg['content'] in nodes_map:
                node = nodes_map[msg['content']]
                with st.expander(f"✨ {node['care_point']}", expanded=False):
                    st.caption(f"MLS Logic: {node.get('logic_score', 0.5)}")
                    st.markdown(f"**Insight:** {node['insight']}")
                    st.markdown(f"**Structure:**\n{node['meaning_layer']}")
                    st.caption(f"Time: {node['created_at'][:16]}")

    if prompt := st.chat_input("输入..."):
        save_chat(st.session_state.username, "user", prompt)
        full_history = chat_history + [{'role':'user', 'content':prompt}]
        stream = get_normal_response(full_history)
        reply_text = st.write_stream(stream)
        save_chat(st.session_state.username, "assistant", reply_text)
        
        with st.spinner("⚡ 意义判别 & 星团扫描..."):
            analysis = analyze_meaning_background(prompt)
            if analysis.get("valid", False):
                vec = get_embedding(prompt)
                save_node(st.session_state.username, prompt, analysis, "日常", vec)
                if "radar_scores" in analysis: update_radar_score(st.session_state.username, analysis["radar_scores"])
                
                # 🌟 触发群组形成逻辑
                check_group_formation(analysis, vec, st.session_state.username)
                
                match = find_resonance(vec, st.session_state.username)
                if match: st.toast(f"🔔 发现共鸣！", icon="⚡")
        st.rerun()
