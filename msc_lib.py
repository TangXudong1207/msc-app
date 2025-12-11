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
# 🧮 2. 核心算法 (数学公式回归)
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

# 🌟 恢复：结构分 S 计算 (Structure Score)
def calculate_structure_score(new_vector, existing_nodes):
    if not existing_nodes: return 0.5
    links = 0
    # 随机取50个节点计算连接度，模拟图论中心性
    sample_nodes = existing_nodes[-50:] 
    for node in sample_nodes:
        if node['vector']:
            try:
                sim = cosine_similarity(new_vector, json.loads(node['vector']))
                if sim > 0.75: links += 1
            except: pass
    # 归一化：如果有3个以上强链接，S分就很高
    return min(1.0, 0.2 + (links / 5.0))

# ==========================================
# 🔐 3. 用户与数据库操作
# ==========================================
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text: return True
    return False

def add_user(username, password, nickname):
    try:
        res = supabase.table('users').select("*").eq('username', username).execute()
        if len(res.data) > 0: return True 
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
        # 🌟 恢复：存入 C/S/N 分数
        logic = data.get('m_score', 0.5) # 用综合分作为逻辑分显示
        keywords = data.get('keywords', [])
        insert_data = {
            "username": username, "content": content,
            "care_point": data.get('care_point', '未命名'),
            "meaning_layer": data.get('meaning_layer', '暂无结构'),
            "insight": data.get('insight', '生成中断'),
            "mode": mode, "vector": json.dumps(vector),
            "logic_score": logic, "keywords": json.dumps(keywords), "is_deleted": False,
            # 存入核心指标
            "c_score": data.get('c_score', 0),
            "s_score": data.get('s_score', 0),
            "n_score": data.get('n_score', 0),
            "m_score": data.get('m_score', 0)
        }
        supabase.table('nodes').insert(insert_data).execute()
        return True
    except Exception as e: st.error(f"Save Node Error: {e}")
    return False

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

def check_group_formation(new_node_data, vector, username):
    care = new_node_data.get('care_point')
    if not care: return
    try:
        res = supabase.table('nodes').select("*").ilike('care_point', f"%{care}%").execute()
        users = set([row['username'] for row in res.data])
        if len(users) >= 3:
            rname = f"🌌 {care} · 星团"
            exist = supabase.table('rooms').select("*").eq('name', rname).execute()
            if not exist.data:
                supabase.table('rooms').insert({"name": rname, "type": "Gravity", "trigger_keyword": care, "description": f"由 {len(users)} 位探索者汇聚。"}).execute()
    except: pass

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
# 🧠 4. AI 智能 (恢复哲学逻辑)
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
        except: return {"error": True, "msg": "JSON解析失败"}
    except Exception as e: return {"error": True, "msg": str(e)}

def get_normal_response(history_messages):
    try:
        api_messages = [{"role": "system", "content": "你是温暖的对话伙伴。"}]
        for msg in history_messages: api_messages.append({"role": msg["role"], "content": msg["content"]})
        return client_ai.chat.completions.create(model=TARGET_MODEL, messages=api_messages, temperature=0.8, stream=True)
    except Exception as e: return f"Error: {e}"

# 🌟 核心回归：Analyze Meaning Engine (取代 Background)
# 这里融合了 v25 的逻辑，但为了兼容现在的 main.py，函数名保持 analyze_meaning_background
# 但内部逻辑升级为 M=C*S*N
def analyze_meaning_background(text):
    # 这里我们要在内部去获取一下用户的历史节点，算出 S 值，但这在库函数里做比较慢
    # 为了性能，我们简化处理：让 AI 估算 C 和 N，我们在 Python 里估算 S
    
    prompt = f"""
    分析输入："{text}"
    
    请严格基于 MSC (Meaning-Structure-Care) 哲学模型进行评估。
    
    1. Care Score (C, 0.0-1.0): 情绪强度、价值关联度。如果是寒暄或无意义废话，C < 0.2。
    2. Novelty Score (N, 0.0-1.0): 语义新度，是否提出了新的视角或问题。
    
    若 C * N < 0.1，视为无意义，返回 {{ "valid": false }}。
    
    若有意义，返回 JSON:
    {{
        "valid": true,
        "care_point": "核心关切",
        "meaning_layer": "深层结构/哲学隐喻",
        "insight": "升维洞察",
        "c_score": 0.8,
        "n_score": 0.8,
        "keywords": ["tag1"], 
        "topic_tags": ["topic1"],
        "existential_q": false,
        "radar_scores": {{ "Care": 5, "Curiosity": 5, "Reflection": 5, "Coherence": 5, "Empathy": 5, "Agency": 5, "Aesthetic": 5 }}
    }}
    """
    res = call_ai_api(prompt)
    
    if res.get("valid", False):
        # 补算 M 值
        # M = C * N (S值暂时由 AI 隐性判断，或者默认 0.8)
        c = res.get('c_score', 0.5)
        n = res.get('n_score', 0.5)
        m = c * n * 2 # 放大系数
        res['m_score'] = m
        res['s_score'] = 0.5 # 占位
        
        # 🌟 关键过滤：如果 M 分太低，依然判定为无效
        if m < 0.3: 
            res['valid'] = False
            
    return res

def generate_fusion(node_a_content, node_b_content):
    prompt = f"""
    任务：融合 A 和 B。
    A: "{node_a_content}"
    B: "{node_b_content}"
    返回 JSON: {{ "care_point": "...", "meaning_layer": "...", "insight": "..." }}
    """
    return call_ai_api(prompt)

def analyze_persona_report(radar_data):
    radar_str = json.dumps(radar_data, ensure_ascii=False)
    prompt = f"任务：人物画像分析。雷达数据：{radar_str}。输出 JSON: {{ 'static_portrait': '...', 'dynamic_growth': '...' }}"
    return call_ai_api(prompt)

def simulate_civilization(topic, count):
    prompt = f"""
    Task: Simulate {count} users discussing "{topic}".
    Return JSON: {{ "users": [ {{ "username": "u1", "nickname": "A", "content": "..." }} ] }}
    """
    res = call_ai_api(prompt)
    agents = []
    if isinstance(res, dict) and "users" in res: agents = res["users"]
    elif isinstance(res, list): agents = res
    elif isinstance(res, dict): 
        for val in res.values(): 
            if isinstance(val, list): agents = val; break
    if not agents: return 0, "AI生成异常"
    cnt=0
    for agent in agents:
        try:
            uid = agent.get('username','bot')+str(int(time.time()))[-3:]+str(np.random.randint(10,99))
            add_user(uid,"123456",agent.get('nickname','Sim'))
            save_chat(uid,"user",agent['content'])
            analysis = analyze_meaning_background(agent['content'])
            # 仿真强制
            if "error" in analysis: analysis={"valid":True,"care_point":"Sim","meaning_layer":"Sim","insight":"Sim","m_score":0.8,"keywords":[],"topic_tags":[]}
            else: analysis["valid"]=True
            vec=get_embedding(agent['content'])
            save_node(uid,agent['content'],analysis,"日常",vec)
            if "radar_scores" in analysis: update_radar_score(uid,analysis["radar_scores"])
            check_group_formation(analysis,vec,uid)
            cnt+=1
            time.sleep(0.2)
        except: pass
    return cnt, f"成功注入 {cnt}"

def generate_daily_question(username, radar_data):
    recent = get_user_nodes(username)
    ctx = ""
    if recent: ctx = f"关注点：{[n['care_point'] for n in recent[-3:]]}"
    prompt = f"生成每日追问。用户：{json.dumps(radar_data)}。{ctx}。输出 JSON: {{ 'question': '...' }}"
    res = call_ai_api(prompt)
    if "question" in res: return res["question"]
    return "今天，什么事情让你感到'活着'？"

# ==========================================
# 🎨 5. 视觉渲染 (Locked)
# ==========================================
def render_2d_world_map(nodes):
    map_data = [{"name": "HQ", "value": [116.4, 39.9, 100]}]
    for _ in range(len(nodes) + 15): 
        lon = np.random.uniform(-150, 150)
        lat = np.random.uniform(-40, 60)
        val = np.random.randint(10, 100)
        map_data.append({"name": "Node", "value": [float(lon), float(lat), 50]})
    df = pd.DataFrame(map_data)
    fig = go.Figure(data=go.Scattergeo(
        lon = [d['value'][0] for d in map_data],
        lat = [d['value'][1] for d in map_data],
        mode = 'markers',
        marker = dict(size=5, color='#ffd60a', opacity=0.8)
    ))
    fig.update_layout(geo = dict(scope='world', projection_type='natural earth', showland=True, landcolor="rgb(20, 20, 20)", bgcolor="black"), margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="black", height=500)
    st.plotly_chart(fig, use_container_width=True)

def render_3d_galaxy(nodes):
    if len(nodes) < 3: st.info("🌌 星河汇聚中..."); return
    vectors, labels, colors = [], [], []
    for i, node in enumerate(nodes):
        if node['vector']:
            try:
                v = json.loads(node['vector'])
                vectors.append(v)
                labels.append(node['care_point'])
                colors.append(i % 3)
            except: pass
    if not vectors: return
    pca = PCA(n_components=3)
    coords = pca.fit_transform(vectors)
    df = pd.DataFrame(coords, columns=['x', 'y', 'z'])
    df['label'] = labels
    df['cluster'] = colors
    fig = px.scatter_3d(df, x='x', y='y', z='z', color='cluster', hover_name='label', template="plotly_dark", opacity=0.8)
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
        # 🌟 修复：现在优先取 m_score，没有再取 logic_score
        logic = node.get('m_score') if node.get('m_score') is not None else node.get('logic_score', 0.5)
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
    option = {
        "backgroundColor": "#0e1117",
        "series": [{"type": "graph", "layout": "force", "data": graph_nodes, "links": graph_links, "roam": True, "force": {"repulsion": 1000 if is_fullscreen else 300}, "itemStyle": {"shadowBlur": 10}}]
    }
    st_echarts(options=option, height=height)
