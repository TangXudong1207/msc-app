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
        api_messages = [{"role": "system", "content": "你是一个温暖、智慧的对话伙伴。请用自然、流畅的语言与用户交流。不要输出JSON。"}]
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
    判断标准：必须包含明确观点、强烈情绪或独特洞察。只是寒暄则返回 {{ "valid": false }}。
    若符合，请提取结构并返回 JSON：
    {{
        "valid": true,
        "care_point": "简短核心关切(10字内)",
        "meaning_layer": "完整结构分析...",
        "insight": "升维洞察金句...",
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
        logic = data.get('logic_score')
        if logic is None: logic = 0.5
        insert_data = {
            "username": username, "content": content,
            "care_point": data.get('care_point', '未命名'),
            "meaning_layer": data.get('meaning_layer', '暂无结构'),
            "insight": data.get('insight', '生成中断'),
            "mode": "日常", "vector": json.dumps(vector),
            "logic_score": logic, "keywords": json.dumps([]) 
        }
        supabase.table('nodes').insert(insert_data).execute()
        return True
    except: return False

def get_recent_nodes(username, limit=20):
    try:
        # 获取最近的N个节点用于绘图
        res = supabase.table('nodes').select("*").eq('username', username).order('id', desc=True).limit(limit).execute()
        # 翻转顺序，让旧的在前，方便画时间线
        return list(reversed(res.data))
    except: return []

# --- 🧮 算法：余弦相似度 ---
def cosine_similarity(v1, v2):
    if not v1 or not v2: return 0
    vec1, vec2 = np.array(v1), np.array(v2)
    norm1, norm2 = np.linalg.norm(vec1), np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0: return 0
    return np.dot(vec1, vec2) / (norm1 * norm2)

# --- 🎨 赛博朋克地图 (孤星版) ---
def render_cyberpunk_map(nodes, height="300px", is_fullscreen=False):
    if not nodes: return

    graph_nodes = []
    graph_links = []
    
    # 全屏时的参数调整
    label_size = 14 if is_fullscreen else 10
    symbol_base_size = 30 if is_fullscreen else 15
    repulsion = 1500 if is_fullscreen else 300

    # 1. 生成节点
    for i, node in enumerate(nodes):
        logic = node.get('logic_score')
        if logic is None: logic = 0.5
        
        # 节点大小随逻辑分变化
        size = symbol_base_size * (0.8 + logic)
        
        short_care = node['care_point'][:6] + "..."
        
        graph_nodes.append({
            "name": f"#{node['id']}",
            "id": str(node['id']),
            "symbolSize": size,
            "value": node['insight'], # tooltip显示
            "label": {
                "show": True,
                "formatter": short_care if is_fullscreen else "{b}",
                "color": "#fff",
                "fontSize": label_size
            },
            # 存向量数据用于前端计算不太方便，我们在后端算好 Link
            "vector": json.loads(node['vector']) if node.get('vector') else None
        })

        # 2. 生成连线 (基于相似度的“星座”逻辑)
        # 我们只尝试连接当前节点和它之前的节点
        if i > 0:
            curr_vec = json.loads(node['vector']) if node.get('vector') else None
            prev_vec = json.loads(nodes[i-1]['vector']) if nodes[i-1].get('vector') else None
            
            if curr_vec and prev_vec:
                # 计算相似度
                sim = cosine_similarity(curr_vec, prev_vec)
                
                # 🌟 核心逻辑：只有相似度够高才连接
                if sim > 0.8:
                    # 强链接：粗、亮、青色
                    graph_links.append({
                        "source": str(nodes[i-1]['id']),
                        "target": str(node['id']),
                        "lineStyle": {"width": 3, "color": "#00d2ff", "curveness": 0.2}
                    })
                elif sim > 0.6:
                    # 弱链接：细、暗、紫色
                    graph_links.append({
                        "source": str(nodes[i-1]['id']),
                        "target": str(node['id']),
                        "lineStyle": {"width": 1, "color": "#ff00d4", "type": "dashed", "curveness": 0.1}
                    })
                else:
                    # 无链接：孤独的漂浮
                    pass 

    option = {
        "backgroundColor": "#0e1117",
        "title": {
            "text": "🌌 思想星云" if is_fullscreen else "",
            "left": "center",
            "textStyle": {"color": "#fff"}
        },
        "tooltip": {"trigger": "item", "formatter": "{b}: {c}"},
        "series": [{
            "type": "graph",
            "layout": "force",
            "data": graph_nodes,
            "links": graph_links,
            "roam": True,
            "force": {
                "repulsion": repulsion,
                "gravity": 0.1, # 稍微有点引力，让孤星不至于飘太远
                "edgeLength": [50, 150]
            },
            "itemStyle": {
                "shadowBlur": 10,
                "shadowColor": "rgba(255, 255, 255, 0.5)",
                "color": "#7b68ee" # 默认星体颜色
            }
        }]
    }
    st_echarts(options=option, height=height)

# --- 🖥️ 全屏弹窗 ---
@st.dialog("🔭 浩荡宇宙 · 思想星云", width="large")
def view_fullscreen_map(nodes):
    st.caption("孤独是常态，连接是奇迹。")
    render_cyberpunk_map(nodes, height="600px", is_fullscreen=True)

# ==========================================
# 🖥️ 界面主逻辑
# ==========================================

st.set_page_config(page_title="MSC v16.0 Lonely Universe", layout="wide", initial_sidebar_state="expanded")

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
    # 获取历史数据
    history_nodes = get_recent_nodes(st.session_state.username, limit=30)

    with st.sidebar:
        st.caption(f"当前用户: {st.session_state.nickname}")
        if st.button("退出"):
            st.session_state.logged_in = False
            st.rerun()
        st.divider()
        st.caption("🌐 全局拓扑")
        
        # 1. 渲染侧边栏地图
        render_cyberpunk_map(history_nodes, height="250px")
        
        # 2. 全屏按钮回归
        if st.button("🔭 全屏星云模式", use_container_width=True):
            view_fullscreen_map(history_nodes)

    col_chat, col_insight = st.columns([0.7, 0.3], gap="large")

    with col_chat:
        st.subheader("💬 对话")
        
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"], unsafe_allow_html=True)

        if prompt := st.chat_input("说点什么..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                stream = get_normal_response(st.session_state.messages)
                response_text = st.write_stream(stream)
            
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            
            with st.spinner("⚡ 正在捕捉意义..."):
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
        
        if not history_nodes:
            st.info("这里是你的思想副驾驶。")
        
        # 显示最近5个节点的折叠卡片
        for node in reversed(history_nodes[-5:]):
            with st.expander(f"✨ {node['care_point']}", expanded=False):
                st.markdown(f"**Insight:** {node['insight']}")
                st.caption(f"Structure: {node['meaning_layer']}")
                st.caption(f"Time: {node['created_at'][:16]}")
                
        if st.session_state.get("new_node"):
            st.toast(f"捕获新意义：{st.session_state.new_node['care_point']}")
            st.session_state.new_node = None
