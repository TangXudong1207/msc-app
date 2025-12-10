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

# ==========================================
# 🛑 1. 核心配置区
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
# 🧮 2. 核心算法 & 工具函数 (提到最前，防止报错)
# ==========================================

def get_embedding(text):
    """生成模拟向量 (1536维)"""
    return np.random.rand(1536).tolist()

def cosine_similarity(v1, v2):
    """计算余弦相似度"""
    if not v1 or not v2: return 0
    vec1 = np.array(v1)
    vec2 = np.array(v2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0: return 0
    return np.dot(vec1, vec2) / (norm1 * norm2)

def calculate_MLS(vec_a, vec_b, topic_a, topic_b, meaning_a, meaning_b, ex_a, ex_b):
    """计算意义链接分数 (Meaning-Link Score)"""
    # 1. 向量相似度
    sim_vec = cosine_similarity(vec_a, vec_b)
    
    # 2. Topic Overlap
    t_inter = len(set(topic_a).intersection(set(topic_b)))
    t_union = len(set(topic_a).union(set(topic_b)))
    topic_sim = t_inter / t_union if t_union > 0 else 0
    
    # 3. Meaning Overlap
    m_inter = len(set(meaning_a).intersection(set(meaning_b)))
    m_union = len(set(meaning_a).union(set(meaning_b)))
    meaning_sim = m_inter / m_union if m_union > 0 else 0
    
    # 规则：Topic高 Meaning低 -> 惩罚
    if topic_sim > 0.7 and meaning_sim < 0.3:
        return 0.2
        
    # 4. 存在性匹配
    ex_match = 1.0 if (ex_a and ex_b) else 0.0
    
    # 5. 综合打分
    MLS = 0.5 * meaning_sim + 0.3 * sim_vec + 0.2 * ex_match
    return MLS

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text: return True
    return False

# ==========================================
# 💾 3. 数据库操作
# ==========================================

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

def save_chat(username, role, content):
    try:
        data = {"username": username, "role": role, "content": content, "is_deleted": False}
        supabase.table('chats').insert(data).execute()
    except Exception as e: print(f"Chat save error: {e}")

def get_active_chats(username, limit=50):
    try:
        res = supabase.table('chats').select("*").eq('username', username).eq('is_deleted', False).order('id', desc=True).limit(limit).execute()
        return list(reversed(res.data))
    except: return []

def get_deleted_items(username):
    try:
        chats = supabase.table('chats').select("*").eq('username', username).eq('is_deleted', True).order('id', desc=True).execute()
        nodes = supabase.table('nodes').select("*").eq('username', username).eq('is_deleted', True).order('id', desc=True).execute()
        return chats.data, nodes.data
    except: return [], []

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
        logic = data.get('logic_score')
        if logic is None: logic = 0.5
        keywords = data.get('keywords', [])
        
        insert_data = {
            "username": username, "content": content,
            "care_point": data.get('care_point', '未命名'),
            "meaning_layer": data.get('meaning_layer', '暂无结构'),
            "insight": data.get('insight', '生成中断'),
            "mode": mode, "vector": json.dumps(vector),
            "logic_score": logic, "is_deleted": False,
            "keywords": json.dumps(keywords)
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
                    
                    MLS = calculate_MLS(
                        current_vector, o_vec,
                        c_topics, o_topics,
                        c_meanings, o_keywords,
                        c_ex, o_ex
                    )
                    
                    if MLS > 0.75 and MLS > highest_score:
                        highest_score = MLS
                        best_match = {"user": row['username'], "content": row['content'], "score": round(MLS * 100, 1)}
                except: continue
        return best_match
    except: return None

# ==========================================
# 🧠 4. AI 业务逻辑
# ==========================================

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

# ==========================================
# 🎨 5. 渲染与主程序
# ==========================================

def render_cyberpunk_map(nodes, height="250px", is_fullscreen=False):
    if not nodes: return
    graph_nodes = []
    graph_links = []
    label_size = 14 if is_fullscreen else 10
    symbol_base = 30 if is_fullscreen else 15
    repulsion = 1000 if is_fullscreen else 300

    for i, node in enumerate(nodes):
        logic = node.get('logic_score')
        if logic is None: logic = 0.5
        
        # 解析关键字用于绘图连线计算
        node_keywords = json.loads(node['keywords']) if node.get('keywords') else []
        node_vector = json.loads(node['vector']) if node.get('vector') else None

        graph_nodes.append({
            "name": str(node['id']),
            "id": str(node['id']),
            "symbolSize": symbol_base * (0.8 + logic),
            "value": node['care_point'],
            "label": {"show": is_fullscreen, "formatter": node['care_point'][:5], "color": "#fff"},
            "vector": node_vector,
            "keywords": node_keywords
        })

    # 绘图时的简单链接逻辑 (模拟 MLS)
    node_count = len(graph_nodes)
    for i in range(node_count):
        for j in range(i + 1, node_count):
            na, nb = graph_nodes[i], graph_nodes[j]
            if na['vector'] and nb['vector']:
                # 这里简化计算，只看向量和标签重叠
                m_inter = len(set(na['keywords']).intersection(set(nb['keywords'])))
                m_union = len(set(na['keywords']).union(set(nb['keywords'])))
                m_sim = m_inter / m_union if m_union > 0 else 0
                
                vec_sim = cosine_similarity(na['vector'], nb['vector'])
                score = 0.6 * m_sim + 0.4 * vec_sim
                
                if score > 0.8:
                    graph_links.append({"source": na['name'], "target": nb['name'], "lineStyle": {"width": 2, "color": "#00fff2"}})
                elif score > 0.6:
                    graph_links.append({"source": na['name'], "target": nb['name'], "lineStyle": {"width": 0.5, "color": "#555", "type": "dashed"}})

    option = {
        "backgroundColor": "#0e1117",
        "series": [{
            "type": "graph", "layout": "force", "data": graph_nodes, "links": graph_links,
            "roam": True, "force": {"repulsion": repulsion, "gravity": 0.05}
        }]
    }
    st_echarts(options=option, height=height)

@st.dialog("🔭 浩荡宇宙", width="large")
def view_fullscreen_map(nodes):
    render_cyberpunk_map(nodes, height="600px", is_fullscreen=True)

@st.dialog("🗑️ 回收站")
def view_recycle_bin(username):
    deleted_chats, deleted_nodes = get_deleted_items(username)
    st.caption("碎片...")
    tab_c, tab_n = st.tabs([f"对话 ({len(deleted_chats)})", f"节点 ({len(deleted_nodes)})"])
    with tab_c:
        for chat in deleted_chats:
            c1, c2 = st.columns([8, 2])
            with c1: st.text(f"{chat['content'][:20]}...")
            with c2:
                if st.button("♻️", key=f"res_c_{chat['id']}"):
                    restore_item('chats', chat['id']); st.rerun()
    with tab_n:
        for node in deleted_nodes:
            c1, c2 = st.columns([8, 2])
            with c1: st.info(f"{node['care_point']}")
            with c2:
                if st.button("♻️", key=f"res_n_{node['id']}"):
                    restore_item('nodes', node['id']); st.rerun()

st.set_page_config(page_title="MSC v19.1 Stable", layout="wide", initial_sidebar_state="expanded")

if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌌 MSC")
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
        if c1.button("🗑️ 回收站"): view_recycle_bin(st.session_state.username)
        if c2.button("退出"): st.session_state.logged_in = False; st.rerun()
        st.divider()
        render_cyberpunk_map(all_nodes_list, height="250px")
        if st.button("🔭 全屏星云", use_container_width=True): view_fullscreen_map(all_nodes_list)

    st.subheader("💬 意义流")
    
    for msg in chat_history:
        col_chat, col_node = st.columns([0.65, 0.35], gap="small")
        with col_chat:
            c_msg, c_del = st.columns([0.9, 0.1])
            with c_msg:
                with st.chat_message(msg['role']): st.markdown(msg['content'])
            with c_del:
                if msg['role'] == 'user':
                    if st.button("✕", key=f"del_{msg['id']}"):
                        if soft_delete_chat_and_node(msg['id'], msg['content'], st.session_state.username): st.rerun()
            
            if msg.get('role') == 'assistant' and "🧬 融合成功" in msg['content']:
                 pass 

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
        
        with st.spinner("⚡ 意义判别中..."):
            analysis = analyze_meaning_background(prompt)
            if analysis.get("valid", False):
                vec = get_embedding(prompt)
                save_node(st.session_state.username, prompt, analysis, "日常", vec)
                
                match = find_resonance(vec, st.session_state.username, analysis)
                if match:
                    st.toast(f"🔔 发现深度共鸣！(MLS={match['score']})", icon="⚡")
        
        st.rerun()
