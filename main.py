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
# 🛑 核心配置区
# ==========================================

try:
    client_ai = OpenAI(
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

# --- 💾 数据库操作 (增删改查) ---

def save_chat(username, role, content):
    try:
        data = {"username": username, "role": role, "content": content, "is_deleted": False}
        supabase.table('chats').insert(data).execute()
    except Exception as e: print(f"Chat save error: {e}")

def get_active_chats(username, limit=50):
    """获取未删除的聊天记录"""
    try:
        # 只取 is_deleted = false
        res = supabase.table('chats').select("*").eq('username', username).eq('is_deleted', False).order('id', desc=True).limit(limit).execute()
        return list(reversed(res.data))
    except: return []

def get_deleted_items(username):
    """获取回收站内容"""
    try:
        chats = supabase.table('chats').select("*").eq('username', username).eq('is_deleted', True).order('id', desc=True).execute()
        nodes = supabase.table('nodes').select("*").eq('username', username).eq('is_deleted', True).order('id', desc=True).execute()
        return chats.data, nodes.data
    except: return [], []

def soft_delete_chat_and_node(chat_id, content, username):
    """软删除：同时删除对话和对应的节点"""
    try:
        # 1. 标记对话为删除
        supabase.table('chats').update({"is_deleted": True}).eq("id", chat_id).execute()
        # 2. 尝试标记对应的节点为删除 (通过内容匹配)
        supabase.table('nodes').update({"is_deleted": True}).eq("username", username).eq("content", content).execute()
        return True
    except: return False

def restore_item(table, item_id):
    """恢复数据"""
    try:
        supabase.table(table).update({"is_deleted": False}).eq("id", item_id).execute()
        return True
    except: return False

def permanently_delete(table, item_id):
    """永久删除"""
    try:
        supabase.table(table).delete().eq("id", item_id).execute()
        return True
    except: return False

def save_node(username, content, data, mode, vector):
    try:
        logic = data.get('logic_score')
        if logic is None: logic = 0.5
        insert_data = {
            "username": username, "content": content,
            "care_point": data.get('care_point', '未命名'),
            "meaning_layer": data.get('meaning_layer', '暂无结构'),
            "insight": data.get('insight', '生成中断'),
            "mode": mode, "vector": json.dumps(vector),
            "logic_score": logic, "is_deleted": False
        }
        supabase.table('nodes').insert(insert_data).execute()
        return True
    except: return False

def get_active_nodes_map(username):
    """获取所有未删除节点，并转为字典 {content: node_data} 以便对齐"""
    try:
        res = supabase.table('nodes').select("*").eq('username', username).eq('is_deleted', False).execute()
        return {node['content']: node for node in res.data}
    except: return {}

def get_all_nodes_for_map(username):
    """获取未删除节点用于画图"""
    try:
        res = supabase.table('nodes').select("*").eq('username', username).eq('is_deleted', False).order('id', desc=False).execute()
        return res.data
    except: return []

# --- 🧠 AI 核心 ---
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
        except: return {"error": True, "msg": "JSON解析失败"}
    except Exception as e: return {"error": True, "msg": str(e)}

def get_embedding(text):
    return np.random.rand(1536).tolist()

def get_normal_response(history_messages):
    try:
        api_messages = [{"role": "system", "content": "你是温暖的对话伙伴。"}]
        for msg in history_messages:
            api_messages.append({"role": msg["role"], "content": msg["content"]})
        response = client_ai.chat.completions.create(
            model=TARGET_MODEL, messages=api_messages, temperature=0.8, stream=True 
        )
        return response
    except Exception as e: return f"Error: {e}"

def analyze_meaning_background(text):
    prompt = f"""
    判断输入："{text}" 是否有深层意义。
    若只是寒暄返回 {{ "valid": false }}。
    若有意义返回 JSON:
    {{ "valid": true, "care_point": "核心关切", "meaning_layer": "结构", "insight": "洞察", "logic_score": 0.8 }}
    """
    return call_ai_api(prompt)

def generate_fusion(node_a, node_b):
    prompt = f"""
    融合 A: "{node_a}" B: "{node_b}"。
    返回 JSON: {{ "care_point": "...", "meaning_layer": "...", "insight": "..." }}
    """
    return call_ai_api(prompt)

def cosine_similarity(v1, v2):
    vec1, vec2 = np.array(v1), np.array(v2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)) if np.linalg.norm(vec1) > 0 else 0

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

# --- 🎨 渲染 ---
def render_cyberpunk_map(nodes, height="250px", is_fullscreen=False):
    if not nodes: return
    graph_nodes = []
    graph_links = []
    label_size = 14 if is_fullscreen else 10
    symbol_base = 30 if is_fullscreen else 15
    repulsion = 1000 if is_fullscreen else 300

    for i, node in enumerate(nodes):
        logic = node.get('logic_score', 0.5)
        graph_nodes.append({
            "name": str(node['id']),
            "symbolSize": symbol_base * (0.8 + logic),
            "value": node['care_point'],
            "label": {"show": is_fullscreen, "formatter": node['care_point'][:5], "color": "#fff"},
            "vector": json.loads(node['vector']) if node.get('vector') else None
        })

    for i in range(len(graph_nodes)):
        for j in range(i + 1, len(graph_nodes)):
            na, nb = graph_nodes[i], graph_nodes[j]
            if na['vector'] and nb['vector']:
                sim = cosine_similarity(na['vector'], nb['vector'])
                if sim > 0.85:
                    graph_links.append({"source": na['name'], "target": nb['name'], "lineStyle": {"width": 2, "color": "#00fff2"}})
                elif sim > 0.65:
                    graph_links.append({"source": na['name'], "target": nb['name'], "lineStyle": {"width": 0.5, "color": "#555"}})

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
    
    st.caption("这里存放着被遗忘的思想碎片...")
    
    tab_c, tab_n = st.tabs([f"对话 ({len(deleted_chats)})", f"节点 ({len(deleted_nodes)})"])
    
    with tab_c:
        for chat in deleted_chats:
            c1, c2 = st.columns([8, 2])
            with c1: st.text(f"{chat['content'][:20]}...")
            with c2:
                if st.button("♻️", key=f"res_c_{chat['id']}"):
                    restore_item('chats', chat['id'])
                    st.rerun()
    
    with tab_n:
        for node in deleted_nodes:
            c1, c2 = st.columns([8, 2])
            with c1: st.info(f"{node['care_point']}")
            with c2:
                if st.button("♻️", key=f"res_n_{node['id']}"):
                    restore_item('nodes', node['id'])
                    st.rerun()

# ==========================================
# 🖥️ 主程序
# ==========================================

st.set_page_config(page_title="MSC v18.0 Aligned", layout="wide", initial_sidebar_state="expanded")

if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌌 MSC")
    # ... (登录注册代码省略，与之前相同，节省篇幅) ...
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
    # 准备数据
    chat_history = get_active_chats(st.session_state.username)
    nodes_map = get_active_nodes_map(st.session_state.username) # 获取所有节点用于匹配
    all_nodes_list = get_all_nodes_for_map(st.session_state.username)

    with st.sidebar:
        st.write(f"👋 **{st.session_state.nickname}**")
        c1, c2 = st.columns(2)
        if c1.button("🗑️ 回收站"):
            view_recycle_bin(st.session_state.username)
        if c2.button("退出"):
            st.session_state.logged_in = False
            st.rerun()
        
        st.divider()
        render_cyberpunk_map(all_nodes_list, height="250px")
        if st.button("🔭 全屏星云", use_container_width=True):
            view_fullscreen_map(all_nodes_list)

    # --- 核心：逐行对齐渲染 ---
    st.subheader("💬 意义流")
    
    # 遍历每一条聊天记录 (从旧到新显示)
    for msg in chat_history:
        # 定义一行两列：左边聊天，右边批注
        col_chat, col_node = st.columns([0.65, 0.35], gap="small")
        
        # --- 左列：聊天气泡 + 删除按钮 ---
        with col_chat:
            c_msg, c_del = st.columns([0.9, 0.1])
            with c_msg:
                # 区分用户和AI的样式
                with st.chat_message(
