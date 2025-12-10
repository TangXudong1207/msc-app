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

# --- 🧠 AI 核心 ---
def call_ai_api(prompt):
    try:
        response = client_ai.chat.completions.create(
            model=TARGET_MODEL,
            messages=[{"role": "system", "content": "You are a profound philosopher. Output valid JSON only."}, {"role": "user", "content": prompt}],
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

def generate_node_data(mode, text):
    prompt = f"""
    场景：【{mode}】。用户输入："{text}"。
    请提取结构，返回JSON:
    {{
        "care_point": "用户潜意识里的情绪...",
        "meaning_layer": "背后的深层逻辑...",
        "insight": "一句升维洞察...",
        "logic_score": 0.8
    }}
    """
    return call_ai_api(prompt)

def generate_fusion(node_a_content, node_b_content):
    prompt = f"""
    融合 A: "{node_a_content}" 和 B: "{node_b_content}"。
    返回JSON:
    {{
        "care_point": "共同深层诉求...",
        "meaning_layer": "全景视角...",
        "insight": "全新洞察..."
    }}
    """
    return call_ai_api(prompt)

def cosine_similarity(v1, v2):
    if not v1 or not v2: return 0
    vec1, vec2 = np.array(v1), np.array(v2)
    norm1, norm2 = np.linalg.norm(vec1), np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0: return 0
    return np.dot(vec1, vec2) / (norm1 * norm2)

def find_resonance(current_vector, current_user):
    if not current_vector: return None
    try:
        res = supabase.table('nodes').select("username, content, vector").neq('username', current_user).execute()
        others = res.data
        best_match, highest_score = None, 0
        for row in others:
            if row['vector']:
                try:
                    score = cosine_similarity(current_vector, json.loads(row['vector']))
                    if score > 0.75 and score > highest_score: # 提高阈值
                        highest_score = score
                        best_match = {"user": row['username'], "content": row['content'], "score": round(score * 100, 1)}
                except: continue
        return best_match
    except: return None

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
            "logic_score": logic
        }
        supabase.table('nodes').insert(insert_data).execute()
        return True
    except: return False

def get_user_nodes(username):
    try:
        # 获取所有节点用于构建全量地图
        res = supabase.table('nodes').select("*").eq('username', username).order('id', desc=False).execute()
        return res.data
    except: return []

# --- 🎨 自由星云地图 (Non-linear Topology) ---
def render_constellation_map(nodes, height="350px", is_fullscreen=False):
    if not nodes:
        st.caption("宇宙一片寂静...")
        return

    graph_nodes = []
    graph_links = []
    categories = [{"name": "日常"}, {"name": "学术"}, {"name": "艺术"}]
    
    # 1. 准备节点
    for node in nodes:
        logic = node.get('logic_score')
        if logic is None: logic = 0.5
        
        # 节点大小随逻辑分变化
        size = 10 + (logic * 20)
        if is_fullscreen: size *= 1.5
        
        cat_idx = 0
        if "学术" in node['mode']: cat_idx = 1
        elif "艺术" in node['mode']: cat_idx = 2
        
        graph_nodes.append({
            "name": str(node['id']),
            "id": str(node['id']),
            "symbolSize": size,
            "category": cat_idx,
            "value": node['care_point'], # 鼠标悬停显示
            "label": {
                "show": is_fullscreen, # 全屏才显示文字，侧边栏只显示点
                "formatter": "{b}", # 显示ID
                "color": "#eee"
            },
            "vector": json.loads(node['vector']) if node.get('vector') else None
        })

    # 2. 构建星系连接 (全量两两比对，O(N^2)对于个人数据量是可接受的)
    # 只有相似度够高才连接，不再按时间顺序连
    node_count = len(graph_nodes)
    for i in range(node_count):
        for j in range(i + 1, node_count): # 只比较后面的，避免重复
            node_a = graph_nodes[i]
            node_b = graph_nodes[j]
            
            if node_a['vector'] and node_b['vector']:
                sim = cosine_similarity(node_a['vector'], node_b['vector'])
                
                # 🌟 核心逻辑：只有共鸣才连接
                if sim > 0.85:
                    # 强链接：显眼的亮线 (星座连线)
                    graph_links.append({
                        "source": node_a['id'],
                        "target": node_b['id'],
                        "lineStyle": {"width": 2, "color": "#00fff2", "curveness": 0.1}
                    })
                elif sim > 0.65:
                    # 弱链接：暗淡的细线
                    graph_links.append({
                        "source": node_a['id'],
                        "target": node_b['id'],
                        "lineStyle": {"width": 0.5, "color": "#555", "curveness": 0.3}
                    })
                # < 0.65 的就是孤星，不产生连接

    option = {
        "backgroundColor": "#0e1117",
        "title": {
            "text": "🌌 思想星云" if is_fullscreen else "",
            "left": "center",
            "textStyle": {"color": "#fff"}
        },
        "tooltip": {"trigger": "item", "formatter": "ID: {b}<br/>{c}"},
        "series": [{
            "type": "graph",
            "layout": "force", # 力引导布局会自动把孤星推开，把星座聚在一起
            "data": graph_nodes,
            "links": graph_links,
            "categories": categories,
            "roam": True,
            "force": {
                "repulsion": 500 if is_fullscreen else 100,
                "gravity": 0.05,
                "edgeLength": [20, 100]
            },
            "itemStyle": {"shadowBlur": 10, "shadowColor": "rgba(255, 255, 255, 0.5)"}
        }]
    }
    st_echarts(options=option, height=height)

@st.dialog("🔭 浩荡宇宙 · 自由星云", width="large")
def view_fullscreen_map(nodes):
    render_constellation_map(nodes, height="600px", is_fullscreen=True)

# ==========================================
# 🖥️ 界面主逻辑
# ==========================================

st.set_page_config(page_title="MSC v16.0 Alignment", layout="wide", initial_sidebar_state="expanded")

if "logged_in" not in st.session_state: st.session_state.logged_in = False

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
                if add_user(nu, np_pass, nn): st.success("注册成功")
                else: st.error("失败")

else:
    # --- 全局数据准备 ---
    # 一次性拉取所有节点，构建 {content: node_data} 映射表，用于对齐显示
    history_nodes = get_user_nodes(st.session_state.username)
    node_map = {node['content']: node for node in history_nodes} if history_nodes else {}

    # --- 侧边栏 ---
    with st.sidebar:
        st.caption(f"当前用户: {st.session_state.nickname}")
        if st.button("退出"):
            st.session_state.logged_in = False
            st.rerun()
        st.divider()
        st.caption("🌐 全局拓扑")
        render_constellation_map(history_nodes, height="300px")
        if st.button("🔭 全屏星云", use_container_width=True):
            view_fullscreen_map(history_nodes)

    # --- 主界面：左右对齐流 ---
    st.subheader("💬 意义流")
    
    # 🌟 核心修改：逐行渲染，实现对齐
    # 每一条消息占用一行，这一行分左右两列
    for msg in st.session_state.messages:
        # 定义布局：左边 70% 聊天，右边 30% 卡片
        c_chat, c_node = st.columns([0.7, 0.3])
        
        # 1. 左列：显示聊天气泡
        with c_chat:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"], unsafe_allow_html=True)
                
                # 如果有共鸣按钮，显示在气泡下面
                if "fusion_data" in msg:
                    match = msg["fusion_data"]
                    btn_key = f"btn_merge_{msg['id']}"
                    if st.button(f"⚡ 发现共鸣 ({match['score']}%)：与 {get_nickname(match['user'])} 合并", key=btn_key):
                        with st.spinner("融合中..."):
                            c_node = generate_fusion(msg["my_content"], match["content"])
                            if "error" not in c_node:
                                fusion_html = f"""
                                <div style="background-color:#E8F5E9;padding:15px;border-radius:10px;border-left:5px solid #2E7D32;">
                                    <b>🧬 融合成功</b><br>
                                    <small>{msg['my_content']} + {match['content']}</small>
                                    <hr>
                                    <p style="color:#1B5E20;">{c_node.get('insight')}</p>
                                </div>
                                """
                                st.session_state.messages.append({"role": "assistant", "content": fusion_html})
                                st.rerun()

        # 2. 右列：显示对应的意义卡片 (如果有的话)
        with c_node:
            # 只有当消息是用户发的，并且能在数据库里找到对应的节点时，才显示
            if msg["role"] == "user" and msg["content"] in node_map:
                node = node_map[msg["content"]]
                # 渲染折叠卡片
                with st.expander(f"✨ #{node['id']} {node['care_point'][:5]}...", expanded=False):
                    st.caption(f"Logic: {node.get('logic_score', 0.5)}")
                    st.write(f"**Structure:** {node['meaning_layer']}")
                    st.info(f"💡 {node['insight']}")
            
            # 或者是 AI 发的融合结果，也可以在这里显示（当前暂且留空保持整洁）

    # --- 底部输入区 ---
    if prompt := st.chat_input("输入思考..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        # 显式重跑一次以渲染新消息
        st.rerun()

    # 处理最新的一条用户消息 (放在循环外处理逻辑，避免阻塞渲染)
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        last_msg = st.session_state.messages[-1]
        # 检查是否已经处理过（防止重复调用 AI）
        # 这里用简单判断：如果数据库里已经有这句话了，就不再处理
        if last_msg["content"] not in node_map:
            with st.spinner("AI 正在思考..."):
                # 1. 正常回复
                stream = get_normal_response(st.session_state.messages[:-1]) # 不包含刚发的这句，防止递归？其实没关系
                # 这里为了简单，我们还是用之前的逻辑，先回复再分析
                # 但由于 Streamlit 的刷新机制，我们需要把回复追加到 messages
                
                # ... (此处为了代码简洁，保留 v15 的逻辑，但集成在上面的渲染循环里其实更好)
                # 修正策略：Streamlit 的 chat_input 触发 rerrun。
                # 我们在最上面的循环里已经渲染了 user message。
                # 现在这里只负责生成 assistant response 和 异步分析。
                
                # 1. 生成回复
                resp_content = get_normal_response(st.session_state.messages) # 这里其实是模拟，简单起见直接调
                # 注意：get_normal_response 需要适配
                
                # 简化处理：直接在这里生成回复并追加
                api_messages = [{"role": "system", "content": "你是温暖的对话伙伴。"}]
                for m in st.session_state.messages: api_messages.append({"role": m["role"], "content": m["content"]})
                
                try:
                    r = client.chat.completions.create(model=TARGET_MODEL, messages=api_messages, temperature=0.8)
                    bot_reply = r.choices[0].message.content
                    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                except: pass

                # 2. 分析意义
                analysis = analyze_meaning_background(last_msg["content"])
                if analysis.get("valid", False):
                    vec = get_embedding(last_msg["content"])
                    save_node(st.session_state.username, last_msg["content"], analysis, "日常", vec)
                    
                    # 3. 寻找共鸣
                    match = find_resonance(vec, st.session_state.username)
                    if match:
                        # 往刚才那条 assistant 消息里塞入共鸣数据 (这是个 trick)
                        # 或者追加一条系统提示
                        msg_id = int(time.time())
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": "🔔 发现思想共鸣！", 
                            "fusion_data": match,
                            "my_content": last_msg["content"],
                            "id": msg_id
                        })
                
                st.rerun()
