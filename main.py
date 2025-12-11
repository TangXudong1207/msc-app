import streamlit as st
from openai import OpenAI
from supabase import create_client, Client
from streamlit_echarts import st_echarts
import plotly.express as px
import plotly.graph_objects as go
import json
import re
import hashlib
import time
import numpy as np
import pandas as pd
import networkx as nx # 🌟 新增：图论计算库
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
def make_hashes(password): return hashlib.sha256(str.encode(password)).hexdigest()
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
        if not current_radar: current_radar = {k: 3.0 for k in new_scores.keys()}
        elif isinstance(current_radar, str): current_radar = json.loads(current_radar)
        alpha = 0.05
        updated_radar = {}
        for key in new_scores:
            old_val = float(current_radar.get(key, 3.0))
            input_val = float(new_scores.get(key, 0))
            if input_val > 1.0:
                updated_val = old_val * (1 - alpha) + input_val * alpha
                updated_radar[key] = round(min(10.0, updated_val), 2)
            else: updated_radar[key] = old_val
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
def get_meta_nodes(username):
    try:
        res = supabase.table('meta_nodes').select("*").eq('username', username).execute()
        return res.data
    except: return []

# --- 🧠 AI 核心 ---
def call_ai_api(prompt):
    try:
        response = client.chat.completions.create(
            model=TARGET_MODEL,
            messages=[{"role": "system", "content": "Output valid JSON only."}, {"role": "user", "content": prompt}],
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

# --- 🧠 MSC 核心引擎 (Meaning = C * S * N) ---

def calculate_structure_score(new_vector, existing_nodes):
    """
    计算 S 值 (Structure Score)
    简单模拟：如果新节点能链接到多个旧节点，S值高
    """
    if not existing_nodes: return 0.5
    links = 0
    for node in existing_nodes:
        if node['vector']:
            try:
                sim = cosine_similarity(new_vector, json.loads(node['vector']))
                if sim > 0.7: links += 1
            except: pass
    # 归一化：假设连接超过5个就是强结构
    return min(1.0, links / 5.0)

def analyze_meaning_engine(text, user_profile, existing_nodes):
    """
    完整实现 Meaning = Care * Structure * Novelty
    """
    radar_str = json.dumps(user_profile.get('radar_profile', {}), ensure_ascii=False)
    
    prompt = f"""
    任务：基于 MSC (Meaning-Structure-Care) 模型评估输入。
    输入："{text}"
    用户画像：{radar_str}
    
    请评估以下三个维度 (0.0 - 1.0)：
    1. Care Score (C): 情绪强度、价值关联度。是否触及了用户的核心在乎？
    2. Novelty Score (N): 语义新度。这是否是一个新的认知突破？
    
    同时提取结构：
    - care_point (核心关切)
    - meaning_layer (深层结构/哲学隐喻)
    - insight (升维洞察)
    
    返回 JSON:
    {{
        "valid": true/false (Meaning Score > 0.4 则为 true),
        "c_score": 0.8,
        "n_score": 0.8,
        "care_point": "...",
        "meaning_layer": "...",
        "insight": "...",
        "radar_scores": {{ "Care": 8, ... }}
    }}
    """
    res = call_ai_api(prompt)
    
    if "error" in res: return res
    
    # 后处理计算 S 值
    # 在 Python 中计算 Structure，因为 AI 不知道数据库里有啥
    # 暂时用模拟向量计算，实际应用需用真实向量
    current_vec = get_embedding(text)
    s_score = calculate_structure_score(current_vec, existing_nodes)
    
    # 最终计算 M 值
    c = res.get('c_score', 0.5)
    n = res.get('n_score', 0.5)
    m_score = c * s_score * n * 2 # 乘个系数放大
    
    res['s_score'] = s_score
    res['m_score'] = m_score
    res['valid'] = m_score > 0.15 # 设定阈值
    res['vector'] = current_vec # 顺便传出去
    
    return res

def generate_fusion(node_a_content, node_b_content):
    prompt = f"""
    任务：基于意义链接 (Meaning-Link) 进行融合。
    A: "{node_a_content}"
    B: "{node_b_content}"
    寻找两者的共同底层关怀 (Care) 和价值方向。
    返回 JSON: {{ "care_point": "...", "meaning_layer": "...", "insight": "..." }}
    """
    return call_ai_api(prompt)

# --- 🌌 元节点归集引擎 (Convergence) ---

def run_convergence(username):
    """
    执行意义归集：寻找星云中心，生成 Meta-Node
    """
    nodes = get_all_nodes_for_map(username)
    if len(nodes) < 5: return None # 数量太少不聚类
    
    vectors = []
    ids = []
    for n in nodes:
        if n['vector']:
            try:
                vectors.append(json.loads(n['vector']))
                ids.append(n['id'])
            except: pass
    
    if not vectors: return None
    
    # 1. 使用 K-Means 聚类
    n_clusters = max(2, int(len(nodes) / 5)) # 每5个点聚一类
    kmeans = KMeans(n_clusters=n_clusters)
    labels = kmeans.fit_predict(vectors)
    
    # 2. 找到最大的簇
    counts = np.bincount(labels)
    major_cluster_idx = np.argmax(counts)
    
    # 3. 提取该簇的所有文本
    cluster_texts = [nodes[i]['care_point'] for i in range(len(labels)) if labels[i] == major_cluster_idx]
    cluster_ids = [ids[i] for i in range(len(labels)) if labels[i] == major_cluster_idx]
    
    # 4. 让 AI 命名这个元节点
    prompt = f"""
    任务：意义归集 (Convergence)。
    以下是一组相关的意义节点：
    {json.dumps(cluster_texts, ensure_ascii=False)}
    
    请提取它们共同指向的“元主题 (Meta-Theme)”。
    例如：存在主义焦虑、亲密关系的边界、自我实现的渴望。
    
    返回 JSON:
    {{
        "name": "元主题名称 (如：时间的焦虑)",
        "description": "对该主题的深度哲学描述",
        "gravity": {len(cluster_texts)} (重力值)
    }}
    """
    res = call_ai_api(prompt)
    if "name" in res:
        # 存入 meta_nodes 表
        try:
            supabase.table('meta_nodes').insert({
                "username": username,
                "name": res['name'],
                "description": res['description'],
                "gravity_score": len(cluster_texts)
            }).execute()
            
            # 暂时不更新 nodes 表的 meta_node_id，为了演示简单
            return res
        except: pass
        
    return None

# --- 🧮 算法 ---
def cosine_similarity(v1, v2):
    vec1, vec2 = np.array(v1), np.array(v2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)) if np.linalg.norm(vec1) > 0 else 0

def find_resonance(current_vector, current_user):
    if not current_vector: return None
    try:
        res = supabase.table('nodes').select("*").neq('username', current_user).eq('is_deleted', False).execute()
        others = res.data
        best_match, highest = None, 0
        for row in others:
            if row['vector']:
                try:
                    score = cosine_similarity(current_vector, json.loads(row['vector']))
                    if score > 0.75 and score > highest:
                        highest = score
                        best_match = {"user": row['username'], "content": row['content'], "score": round(score * 100, 1)}
                except: continue
        return best_match
    except: return None

# --- 💾 存取 (升级版：存 MSC 分数) ---
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
            # 🌟 新增字段
            "c_score": data.get('c_score', 0),
            "s_score": data.get('s_score', 0),
            "n_score": data.get('n_score', 0),
            "m_score": data.get('m_score', 0)
        }
        supabase.table('nodes').insert(insert_data).execute()
        return True
    except: return False

# --- 🌍 可视化 ---
def render_radar_chart(radar_dict, height="200px"):
    keys = ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]
    scores = [radar_dict.get(k, 3.0) for k in keys]
    option = {
        "backgroundColor": "transparent",
        "radar": {"indicator": [{"name": k, "max": 10} for k in keys], "splitArea": {"show": False}},
        "series": [{"type": "radar", "data": [{"value": scores, "areaStyle": {"color": "rgba(0,255,242,0.4)"}, "lineStyle": {"color": "#00fff2"}}]}]
    }
    st_echarts(options=option, height=height)

def render_2d_world_map(nodes):
    map_data = [{"name": "User", "value": [116.4, 39.9, 100]}]
    for _ in range(len(nodes) + 10): 
        map_data.append({"name": "Node", "value": [float(np.random.uniform(-150, 150)), float(np.random.uniform(-40, 60)), 50]})
    option = {
        "backgroundColor": "#080b10", "geo": {"map": "world", "itemStyle": {"areaColor": "#1a2639", "borderColor": "#2c3e50"}, "roam": True},
        "series": [{"type": "scatter", "coordinateSystem": "geo", "data": map_data, "symbolSize": 5, "itemStyle": {"color": "#ffd60a"}}]
    }
    st_echarts(options=option, height="500px", map="world")

def render_3d_galaxy(nodes, meta_nodes=[]):
    """
    3D 星河：包含普通节点(散点) 和 元节点(大球)
    """
    if not nodes: return
    vectors, labels, sizes, colors = [], [], [], []
    
    # 1. 普通节点
    for i, node in enumerate(nodes):
        if node['vector']:
            try:
                v = json.loads(node['vector'])
                vectors.append(v)
                labels.append(node['care_point'])
                sizes.append(5)
                colors.append(0) # 蓝色
            except: pass
    
    if not vectors: return
    pca = PCA(n_components=3)
    coords = pca.fit_transform(vectors)
    
    # 2. 渲染
    df = pd.DataFrame(coords, columns=['x', 'y', 'z'])
    df['label'] = labels
    df['size'] = sizes
    df['color'] = "#00d2ff" # 默认节点颜色

    # 3. 如果有元节点，把它作为巨大的红色核心加进去
    # (这里为了演示，随机取一个位置，实际应为聚类中心)
    if meta_nodes:
        meta_df = pd.DataFrame([{
            'x': 0, 'y': 0, 'z': 0, 
            'label': f"【元节点】{meta_nodes[0]['name']}", 
            'size': 50, # 巨大
            'color': "#ff0055" # 红色
        }])
        # 合并
        # 注意：Plotly处理多个trace比较好
        
    fig = go.Figure()
    
    # 普通星云
    fig.add_trace(go.Scatter3d(
        x=df['x'], y=df['y'], z=df['z'],
        mode='markers',
        marker=dict(size=5, color=df['color'], opacity=0.6),
        text=df['label'],
        hoverinfo='text'
    ))
    
    # 元节点 (如果有)
    if meta_nodes:
        fig.add_trace(go.Scatter3d(
            x=[0], y=[0], z=[0], # 暂时放在中心
            mode='markers+text',
            marker=dict(size=30, color='#ff0055', opacity=0.9, symbol='diamond'),
            text=[meta_nodes[0]['name']],
            textposition="top center",
            hoverinfo='text'
        ))

    fig.update_layout(
        scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False), bgcolor='black'),
        paper_bgcolor="black", margin={"r":0,"t":0,"l":0,"b":0}, height=600, showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

@st.dialog("🌍 MSC World · 上帝视角", width="large")
def view_msc_world(username):
    global_nodes = get_global_nodes()
    my_meta_nodes = get_meta_nodes(username)
    
    tab1, tab2 = st.tabs(["🌍 地球夜景", "🌌 意义重力场"])
    with tab1: render_2d_world_map(global_nodes)
    with tab2: 
        if my_meta_nodes:
            st.success(f"🌟 监测到元节点诞生：{my_meta_nodes[0]['name']}")
            st.caption(my_meta_nodes[0]['description'])
        else:
            st.info("💡 提示：当你的思想足够丰富时，点击侧边栏的‘归集’按钮，星云将会坍缩成恒星。")
        render_3d_galaxy(global_nodes, my_meta_nodes)

# ==========================================
# 🖥️ 主程序
# ==========================================

st.set_page_config(page_title="MSC v25.0 Gravity", layout="wide", initial_sidebar_state="expanded")

if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌌 MSC")
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
    
    # 解析雷达
    raw_radar = user_profile.get('radar_profile')
    if isinstance(raw_radar, str): radar_dict = json.loads(raw_radar)
    else: radar_dict = raw_radar if raw_radar else {k:3.0 for k in ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]}

    with st.sidebar:
        rank_name, rank_icon = calculate_rank(radar_dict)
        st.markdown(f"## {rank_icon} {st.session_state.nickname}")
        render_radar_chart(radar_dict)
        
        c_world, c_conv = st.columns(2)
        if c_world.button("🌍 世界", use_container_width=True):
            view_msc_world(st.session_state.username)
        
        # 🌟 新功能：手动触发归集
        if c_conv.button("🔮 归集", use_container_width=True, help="当节点足够多时，点击此按钮生成元节点"):
            with st.spinner("正在计算意义重力场..."):
                meta = run_convergence(st.session_state.username)
                if meta: st.balloons(); st.success(f"元节点诞生：{meta['name']}")
                else: st.warning("节点数量不足或过于分散，无法形成引力中心。")

        st.divider()
        c1, c2 = st.columns(2)
        if c1.button("🗑️ 回收站"): pass
        if c2.button("退出"): st.session_state.logged_in = False; st.rerun()

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
                    # 显示 MSC 分数
                    st.caption(f"M-Score: {node.get('m_score', 0):.2f} (C{node.get('c_score')} S{node.get('s_score')} N{node.get('n_score')})")
                    st.markdown(f"**Insight:** {node['insight']}")
                    st.markdown(f"**Structure:**\n{node['meaning_layer']}")

    if prompt := st.chat_input("输入..."):
        save_chat(st.session_state.username, "user", prompt)
        full_history = chat_history + [{'role':'user', 'content':prompt}]
        stream = get_normal_response(full_history)
        reply_text = st.write_stream(stream)
        save_chat(st.session_state.username, "assistant", reply_text)
        
        with st.spinner("⚡ 意义计算 (M=C×S×N)..."):
            # 传入已有节点列表用于计算 Structure Score
            analysis = analyze_meaning_engine(prompt, user_profile, all_nodes_list)
            
            if analysis.get("valid", False):
                # 存库时包含 MSC 分数
                save_node(st.session_state.username, prompt, analysis, "日常", analysis.get('vector'))
                
                # 更新雷达
                if "radar_scores" in analysis: update_radar_score(st.session_state.username, analysis["radar_scores"])
                
                # 共鸣
                match = find_resonance(analysis.get('vector'), st.session_state.username)
                if match: st.toast(f"🔔 发现共鸣！", icon="⚡")
            
            st.rerun()
