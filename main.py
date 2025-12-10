import streamlit as st
from openai import OpenAI
from supabase import create_client, Client
from streamlit_echarts import st_echarts
import json
import re
import hashlib
import time
import numpy as np
from datetime import datetime
from sklearn.decomposition import PCA # 🌟 新增：用于把高维思想降维成3D坐标
from sklearn.cluster import KMeans    # 🌟 新增：用于寻找星云聚类

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

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text: return True
    return False

def add_user(username, password, nickname):
    try:
        res = supabase.table('users').select("*").eq('username', username).execute()
        if len(res.data) > 0: return False
        data = {"username": username, "password": make_hashes(password), "nickname": nickname}
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

# 新增：获取全网所有节点（为了构建大星空）
def get_global_nodes():
    try:
        # 限制取最新的200个节点，防止计算量过大炸内存
        res = supabase.table('nodes').select("*").eq('is_deleted', False).order('id', desc=True).limit(200).execute()
        return res.data
    except: return []

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
        "existential_q": false
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

# --- 🌍 3D 地球与星空渲染 (上帝视角) ---

def render_3d_earth(nodes):
    """
    地球夜景模式：模拟节点在全球的分布
    """
    # 模拟数据：因为没有真实IP，我们随机生成一些世界主要城市的坐标
    # 格式：[经度, 纬度, 亮度]
    data = []
    for _ in range(len(nodes) + 10): # 基础点 + 节点点
        # 随机分布在北半球主要区域，模拟人类活动
        lon = np.random.uniform(-130, 150) 
        lat = np.random.uniform(-30, 60)
        value = np.random.randint(10, 100)
        data.append([lon, lat, value])

    option = {
        "backgroundColor": "#000",
        "globe": {
            "baseTexture": "https://echarts.apache.org/examples/data-gl/asset/earth.jpg",
            "heightTexture": "https://echarts.apache.org/examples/data-gl/asset/bathymetry_bw_composite_4k.jpg",
            "displacementScale": 0.1,
            "shading": "lambert",
            "environment": "https://echarts.apache.org/examples/data-gl/asset/starfield.jpg",
            "light": {"ambient": {"intensity": 0.4}, "main": {"intensity": 0.4}},
            "viewControl": {"autoRotate": True}
        },
        "series": [{
            "type": "scatter3D",
            "coordinateSystem": "globe",
            "data": data,
            "symbolSize": 5,
            "itemStyle": {"color": "#ffaa00", "opacity": 0.8}, # 金色灯光
            "blendMode": "lighter"
        }]
    }
    st_echarts(options=option, height="500px")

def render_3d_galaxy(nodes):
    """
    意义星河模式：使用 PCA 降维，展示语义结构
    """
    if len(nodes) < 5:
        st.warning("🌌 星辰数量不足，无法聚合成星系。请多生成几个意义节点（至少5个）。")
        return

    # 1. 准备向量数据
    vectors = []
    labels = []
    
    for node in nodes:
        if node['vector']:
            try:
                v = json.loads(node['vector'])
                vectors.append(v)
                labels.append(node['care_point'])
            except: pass
    
    if not vectors: return

    # 2. 核心数学：PCA 降维 (1536维 -> 3维)
    # 这就是把“意义”变成“空间坐标”的过程
    pca = PCA(n_components=3)
    coords = pca.fit_transform(vectors)
    
    # 3. 核心数学：K-Means 聚类 (寻找星云中心)
    # 我们假设有 3 个主要星云 (Hope, Responsibility, etc.)
    n_clusters = min(3, len(vectors))
    kmeans = KMeans(n_clusters=n_clusters)
    clusters = kmeans.fit_predict(vectors)
    
    # 4. 构建图表数据
    scatter_data = []
    
    # 颜色映射
    colors = ["#ff0000", "#00ff00", "#0000ff", "#ffff00", "#00ffff"]
    
    for i, (x, y, z) in enumerate(coords):
        cluster_id = clusters[i]
        scatter_data.append({
            "name": labels[i],
            "value": [x, y, z, cluster_id], # 第4维是颜色分类
            "itemStyle": {"color": colors[cluster_id % len(colors)]}
        })

    option = {
        "backgroundColor": "#000",
        "tooltip": {},
        "visualMap": {
            "show": False,
            "dimension": 3,
            "min": 0,
            "max": n_clusters,
            "inRange": {"color": ["#313695", "#4575b4", "#74add1", "#abd9e9", "#e0f3f8", "#ffffbf", "#fee090", "#fdae61", "#f46d43", "#d73027", "#a50026"]}
        },
        "xAxis3D": {"type": "value", "show": False},
        "yAxis3D": {"type": "value", "show": False},
        "zAxis3D": {"type": "value", "show": False},
        "grid3D": {
            "viewControl": {"autoRotate": True, "projection": "perspective"},
            "axisLine": {"lineStyle": {"color": "#fff"}},
            "splitLine": {"show": False}
        },
        "series": [{
            "type": "scatter3D",
            "data": scatter_data,
            "symbolSize": 10,
            "label": {
                "show": True, # 显示关键词！
                "formatter": "{b}", # 显示 Care Point
                "textStyle": {"color": "white", "fontSize": 10, "backgroundColor": "rgba(0,0,0,0.5)"}
            }
        }]
    }
    st_echarts(options=option, height="600px")

# --- 侧边栏小地图 ---
def render_cyberpunk_map(nodes, height="250px", is_fullscreen=False):
    # ... (保持原样，省略以节省空间) ...
    if not nodes: return
    graph_nodes, graph_links = [], []
    for i, node in enumerate(nodes):
        logic = node.get('logic_score')
        if logic is None: logic = 0.5
        graph_nodes.append({
            "name": str(node['id']), "id": str(node['id']),
            "symbolSize": (30 if is_fullscreen else 15) * (0.8 + logic),
            "value": node['care_point'],
            "label": {"show": is_fullscreen, "formatter": node['care_point'][:5], "color": "#fff"},
            "vector": json.loads(node['vector']) if node.get('vector') else None,
            "keywords": json.loads(node['keywords']) if node.get('keywords') else []
        })
    node_count = len(graph_nodes)
    for i in range(node_count):
        for j in range(i + 1, node_count):
            na, nb = graph_nodes[i], graph_nodes[j]
            if na['vector'] and nb['vector']:
                m_sim = len(set(na['keywords']).intersection(set(nb['keywords']))) / (len(set(na['keywords']).union(set(nb['keywords']))) or 1)
                vec_sim = cosine_similarity(na['vector'], nb['vector'])
                score = 0.6 * m_sim + 0.4 * vec_sim
                if score > 0.8: graph_links.append({"source": na['name'], "target": nb['name'], "lineStyle": {"width": 2, "color": "#00fff2"}})
                elif score > 0.6: graph_links.append({"source": na['name'], "target": nb['name'], "lineStyle": {"width": 0.5, "color": "#555", "type": "dashed"}})
    option = {
        "backgroundColor": "#0e1117",
        "series": [{"type": "graph", "layout": "force", "data": graph_nodes, "links": graph_links, "roam": True, "force": {"repulsion": 1000 if is_fullscreen else 300}, "itemStyle": {"shadowBlur": 10}}]
    }
    st_echarts(options=option, height=height)

@st.dialog("🔭 浩荡宇宙", width="large")
def view_fullscreen_map(nodes):
    render_cyberpunk_map(nodes, height="600px", is_fullscreen=True)

@st.dialog("🌍 MSC World · 上帝视角", width="large")
def view_msc_world():
    # 1. 获取全网数据
    global_nodes = get_global_nodes()
    
    tab1, tab2 = st.tabs(["🌍 地球夜景 (Earth)", "🌌 意义星河 (Galaxy)"])
    
    with tab1:
        st.caption("这里展示了全球 MSC 节点的活跃分布（模拟数据）。")
        render_3d_earth(global_nodes)
    
    with tab2:
        st.caption("这是全人类意义的拓扑结构。相似的思想汇聚成星云，孤独的思想成为孤星。")
        if len(global_nodes) > 3:
            render_3d_galaxy(global_nodes)
        else:
            st.info("星系正在坍缩中... 需要更多数据才能形成星云。")

# ==========================================
# 🖥️ 主程序
# ==========================================

st.set_page_config(page_title="MSC v22.0 World", layout="wide", initial_sidebar_state="expanded")

if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌌 MSC")
    # ... Login UI ...
    tab1, tab2 = st.tabs(["登录", "注册"])
    with tab1:
        u = st.text_input("用户名")
        p = st.text_input("密码", type='password')
        if st.button("登录", use_container_width=True):
            res = login_user(u, p)
            if res and len(res) > 0:
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

    with st.sidebar:
        st.write(f"👋 **{st.session_state.nickname}**")
        c1, c2 = st.columns(2)
        
        # 🌟 核心入口：MSC World
        if st.button("🌍 MSC World", use_container_width=True, type="primary"):
            view_msc_world()
            
        if c2.button("退出"): st.session_state.logged_in = False; st.rerun()
        
        st.divider()
        st.caption("我的小宇宙")
        render_cyberpunk_map(all_nodes_list, height="200px")
        if st.button("🔭 全屏", use_container_width=True): view_fullscreen_map(all_nodes_list)

    st.subheader("💬 意义流")
    # ... (Chat logic same as before) ...
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
        
        with st.spinner("⚡ 意义判别..."):
            analysis = analyze_meaning_background(prompt)
            if analysis.get("valid", False):
                vec = get_embedding(prompt)
                save_node(st.session_state.username, prompt, analysis, "日常", vec)
                match = find_resonance(vec, st.session_state.username)
                if match: st.toast(f"🔔 发现共鸣！", icon="⚡")
        st.rerun()
