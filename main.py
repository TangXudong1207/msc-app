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

# --- 🧠 引擎 A：正常聊天 (ChatBot) ---
def get_normal_response(history_messages):
    try:
        api_messages = [{"role": "system", "content": "你是一个温暖、智慧的对话伙伴。请用自然、流畅的语言与用户交流。不要输出JSON，就像朋友聊天一样。"}]
        for msg in history_messages:
            if msg["role"] != "system":
                api_messages.append({"role": msg["role"], "content": msg["content"]})
        
        response = client.chat.completions.create(
            model=TARGET_MODEL,
            messages=api_messages,
            temperature=0.8,
            stream=True 
        )
        return response
    except Exception as e:
        return f"（网络小差：{str(e)}）"

# --- 🧠 引擎 B：意义分析 (MSC Analyst) ---
def analyze_meaning_background(text):
    prompt = f"""
    任务：判断用户的这句话是否有深层意义。
    输入："{text}"
    
    判断标准：
    1. 必须包含明确的观点、强烈的情绪、独特的洞察或方向性的追问。
    2. 如果只是寒暄（如“你好”、“吃了没”、“哈哈”），请返回 {{ "valid": false }}。
    
    如果符合标准，请提取结构并返回 JSON：
    {{
        "valid": true,
        "care_point": "简短的核心关切（不超过10字）",
        "meaning_layer": "完整的结构分析...",
        "insight": "一句升维洞察金句...",
        "logic_score": 0.8
    }}
    """
    try:
        response = client.chat.completions.create(
            model=TARGET_MODEL,
            messages=[{"role": "system", "content": "Output JSON only."}, {"role": "user", "content": prompt}],
            temperature=0.5, 
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except:
        return {"valid": False}

def get_embedding(text):
    return np.random.rand(1536).tolist()

def save_node(username, content, data, vector):
    try:
        # 🛡️ 兼容性修正：确保 logic_score 有值
        logic = data.get('logic_score')
        if logic is None: logic = 0.5

        insert_data = {
            "username": username, "content": content,
            "care_point": data.get('care_point', '未命名'),
            "meaning_layer": data.get('meaning_layer', '暂无结构'),
            "insight": data.get('insight', '生成中断'),
            "mode": "日常", "vector": json.dumps(vector),
            "logic_score": logic,
            "keywords": json.dumps([]) 
        }
        supabase.table('nodes').insert(insert_data).execute()
        return True
    except: return False

def get_recent_nodes(username, limit=5):
    try:
        res = supabase.table('nodes').select("*").eq('username', username).order('id', desc=True).limit(limit).execute()
        return res.data
    except: return []

# --- 🎨 侧边栏小地图 (修正版) ---
def render_mini_map(nodes):
    if not nodes: return
    graph_nodes = []
    graph_links = []
    for i, node in enumerate(nodes):
        # 🌟 修复点：处理旧数据中 logic_score 为 None 的情况
        logic = node.get('logic_score')
        if logic is None: logic = 0.5 # 默认值

        graph_nodes.append({
            "name": str(node['id']),
            "symbolSize": 10 + (logic * 10),
            "value": node['care_point']
        })
        if i > 0:
            graph_links.append({"source": str(nodes[i-1]['id']), "target": str(node['id'])})
    option = {
        "backgroundColor": "transparent",
        "series": [{
            "type": "graph", "layout": "force", "data": graph_nodes, "links": graph_links,
            "label": {"show": False}, "itemStyle": {"color": "#00d2ff"}
        }]
    }
    st_echarts(options=option, height="200px")

# ==========================================
# 🖥️ 界面主逻辑
# ==========================================

st.set_page_config(page_title="MSC v15.1 Fix", layout="wide")

if "logged_in" not in st.session_state: st.session_state.logged_in = False

# --- 登录页 ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.title("🌌 MSC")
        st.caption("人机共生 · 意义构建系统")
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
                    st.session_state.new_node = None 
                    st.rerun()
                else: st.error("账号或密码错误")
        with tab2:
            nu = st.text_input("新用户名")
            np_pass = st.text_input("新密码", type='password')
            nn = st.text_input("昵称")
            if st.button("注册", use_container_width=True):
                if add_user(nu, np_pass, nn): st.success("注册成功，请登录")
                else: st.error("注册失败")

# --- 主界面 ---
else:
    with st.sidebar:
        st.caption(f"当前用户: {st.session_state.nickname}")
        if st.button("退出"):
            st.session_state.logged_in = False
            st.rerun()
        st.divider()
        st.caption("🌐 全局拓扑")
        history = get_recent_nodes(st.session_state.username, limit=20)
        render_mini_map(history)

    col_chat, col_insight = st.columns([0.7, 0.3], gap="large")

    with col_chat:
        st.subheader("💬 对话")
        
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("说点什么..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                stream = get_normal_response(st.session_state.messages)
                response_text = st.write_stream(stream)
            
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            
            with st.spinner("⚡ 正在后台解析结构..."):
                analysis = analyze_meaning_background(prompt)
                
                if analysis.get("valid", False):
                    vec = get_embedding(prompt)
                    save_node(st.session_state.username, prompt, analysis, vec)
                    st.session_state.new_node = analysis
                    st.rerun()
                else:
                    pass

    with col_insight:
        st.subheader("🧩 意义注释")
        
        recent_nodes = get_recent_nodes(st.session_state.username, limit=5)
        
        if not recent_nodes:
            st.info("这里是你的思想副驾驶。\n\n当你聊到有深度的内容时，我会在这里为你做笔记。")
        
        for node in recent_nodes:
            with st.expander(f"✨ {node['care_point']}", expanded=False):
                st.markdown(f"**Insight:** {node['insight']}")
                st.caption(f"Structure: {node['meaning_layer']}")
                st.caption(f"Time: {node['created_at'][:16]}")
                
        if st.session_state.get("new_node"):
            st.toast(f"捕获新意义：{st.session_state.new_node['care_point']}")
            st.session_state.new_node = None
