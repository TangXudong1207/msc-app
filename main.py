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
# 🛠️ 1. 基础设施函数 (先定义，防止报错)
# ==========================================

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

# --- 💾 数据库存取 (新增：聊天记录) ---

def save_chat(username, role, content):
    """保存日常对话到数据库"""
    try:
        data = {"username": username, "role": role, "content": content}
        supabase.table('chats').insert(data).execute()
    except Exception as e: print(f"Chat save error: {e}")

def get_chat_history(username, limit=50):
    """获取最近的聊天记录"""
    try:
        # 按时间正序排列
        res = supabase.table('chats').select("*").eq('username', username).order('id', desc=False).limit(limit).execute()
        # 修正：如果 limit 生效，取回来的是最新的N条，但顺序可能是反的，需要确认 desc=False 取的是最旧的还是最新的
        # 通常我们取 desc=True (最新的50条)，然后反转列表显示
        res = supabase.table('chats').select("*").eq('username', username).order('id', desc=True).limit(limit).execute()
        return list(reversed(res.data))
    except: return []

def save_node(username, content, data, mode, vector):
    """保存意义节点"""
    try:
        logic = data.get('logic_score')
        if logic is None: logic = 0.5
        insert_data = {
            "username": username, "content": content,
            "care_point": data.get('care_point', '未命名'),
            "meaning_layer": data.get('meaning_layer', '暂无结构'),
            "insight": data.get('insight', '生成中断'),
            "mode": mode, "vector": json.dumps(vector),
            "logic_score": logic, "keywords": json.dumps([])
        }
        supabase.table('nodes').insert(insert_data).execute()
        return True
    except: return False

def get_user_nodes(username):
    try:
        res = supabase.table('nodes').select("*").eq('username', username).order('id', desc=False).execute()
        return res.data
    except: return []

# ==========================================
# 🧠 2. AI 核心逻辑函数
# ==========================================

def get_embedding(text):
    return np.random.rand(1536).tolist()

def cosine_similarity(v1, v2):
    if not v1 or not v2: return 0
    vec1, vec2 = np.array(v1), np.array(v2)
    norm1, norm2 = np.linalg.norm(vec1), np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0: return 0
    return np.dot(vec1, vec2) / (norm1 * norm2)

# --- 聊天机器人 ---
def get_normal_response(history_messages):
    """
    普通聊天模式
    """
    try:
        api_messages = [{"role": "system", "content": "你是一个温暖、智慧的对话伙伴。请用自然、流畅的语言与用户交流。不要输出JSON。"}]
        # 转换数据库格式到 OpenAI 格式
        for msg in history_messages:
            # 过滤掉非 standard role
            role = msg['role'] if msg['role'] in ['user', 'assistant'] else 'user'
            api_messages.append({"role": role, "content": msg['content']})
        
        response = client_ai.chat.completions.create(
            model=TARGET_MODEL,
            messages=api_messages,
            temperature=0.8,
            stream=True 
        )
        return response
    except Exception as e:
        return f"（思考中断：{str(e)}）"

# --- 意义分析师 ---
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
        response = client_ai.chat.completions.create(
            model=TARGET_MODEL,
            messages=[{"role": "system", "content": "Output JSON only."}, {"role": "user", "content": prompt}],
            temperature=0.5, 
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except:
        return {"valid": False}

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
    try:
        response = client_ai.chat.completions.create(
            model=TARGET_MODEL,
            messages=[{"role": "system", "content": "Output JSON only."}, {"role": "user", "content": prompt}],
            temperature=0.7, response_format={"type": "json_object"} 
        )
        return json.loads(response.choices[0].message.content)
    except: return {"error": True}

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
                    if score > 0.75 and score > highest_score:
                        highest_score = score
                        best_match = {"user": row['username'], "content": row['content'], "score": round(score * 100, 1)}
                except: continue
        return best_match
    except: return None

# ==========================================
# 🎨 3. UI 渲染函数
# ==========================================

def render_constellation_map(nodes, height="350px", is_fullscreen=False):
    if not nodes:
        st.caption("宇宙一片寂静...")
        return

    graph_nodes = []
    graph_links = []
    categories = [{"name": "日常"}, {"name": "学术"}, {"name": "艺术"}]
    
    label_size = 14 if is_fullscreen else 10
    symbol_base = 30 if is_fullscreen else 15
    repulsion = 800 if is_fullscreen else 200

    for i, node in enumerate(nodes):
        logic = node.get('logic_score')
        if logic is None: logic = 0.5
        size = symbol_base * (0.8 + logic)
        cat_idx = 0
        if "学术" in node['mode']: cat_idx = 1
        elif "艺术" in node['mode']: cat_idx = 2
        
        graph_nodes.append({
            "name": str(node['id']),
            "id": str(node['id']),
            "symbolSize": size,
            "category": cat_idx,
            "value": node['care_point'],
            "label": {"show": is_fullscreen, "formatter": "{b}", "color": "#eee"},
            "vector": json.loads(node['vector']) if node.get('vector') else None
        })

    node_count = len(graph_nodes)
    for i in range(node_count):
        for j in range(i + 1, node_count):
            node_a, node_b = graph_nodes[i], graph_nodes[j]
            if node_a['vector'] and node_b['vector']:
                sim = cosine_similarity(node_a['vector'], node_b['vector'])
                if sim > 0.85:
                    graph_links.append({"source": node_a['id'], "target": node_b['id'], "lineStyle": {"width": 2, "color": "#00fff2"}})
                elif sim > 0.65:
                    graph_links.append({"source": node_a['id'], "target": node_b['id'], "lineStyle": {"width": 0.5, "color": "#555"}})

    option = {
        "backgroundColor": "#0e1117",
        "title": {"text": "🌌 思想星云" if is_fullscreen else "", "left": "center", "textStyle": {"color": "#fff"}},
        "tooltip": {"trigger": "item", "formatter": "ID: {b}<br/>{c}"},
        "series": [{
            "type": "graph", "layout": "force", "data": graph_nodes, "links": graph_links, "categories": categories,
            "roam": True, "force": {"repulsion": repulsion, "gravity": 0.05, "edgeLength": [20, 100]},
            "itemStyle": {"shadowBlur": 10, "shadowColor": "rgba(255, 255, 255, 0.5)"}
        }]
    }
    st_echarts(options=option, height=height)

@st.dialog("🔭 浩荡宇宙 · 自由星云", width="large")
def view_fullscreen_map(nodes):
    render_constellation_map(nodes, height="600px", is_fullscreen=True)

# ==========================================
# 🖥️ 4. 主程序入口
# ==========================================

st.set_page_config(page_title="MSC v17.0 Eternal Chat", layout="wide", initial_sidebar_state="expanded")

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
    # --- 数据加载 ---
    # 1. 加载节点历史（用于地图和右侧批注）
    history_nodes = get_user_nodes(st.session_state.username)
    node_map = {node['content']: node for node in history_nodes} if history_nodes else {}
    
    # 2. 加载聊天历史（用于中间对话框）
    # 注意：这里我们每次都从数据库拉取最新的 N 条，保证不丢失
    chat_history = get_chat_history(st.session_state.username, limit=50)

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

    # --- 主界面布局 ---
    col_chat, col_insight = st.columns([0.7, 0.3], gap="large")

    # --- 1. 左侧：聊天流 ---
    with col_chat:
        st.subheader("💬 意义流")
        
        # 渲染数据库里的历史记录
        for msg in chat_history:
            with st.chat_message(msg['role']):
                st.markdown(msg['content'], unsafe_allow_html=True)
                # 这里暂时不渲染历史共鸣按钮，避免界面太乱，只在实时交互时出现

        # 输入处理
        if prompt := st.chat_input("输入思考..."):
            # A. 立即显示并保存用户消息
            with st.chat_message("user"):
                st.markdown(prompt)
            save_chat(st.session_state.username, "user", prompt)

            # B. 生成并保存助手回复
            with st.chat_message("assistant"):
                # 传入当前历史上下文（包含刚存入的那条）
                # 为了流式效果，我们直接调用 AI，不重新拉数据库
                stream_response = get_normal_response(chat_history + [{'role':'user', 'content':prompt}])
                response_text = st.write_stream(stream_response)
            save_chat(st.session_state.username, "assistant", response_text)
            
            # C. 异步进行意义分析
            with st.spinner("⚡ 解析中..."):
                analysis = analyze_meaning_background(prompt)
                
                if analysis.get("valid", False):
                    vec = get_embedding(prompt)
                    save_node(st.session_state.username, prompt, analysis, "日常", vec)
                    
                    # 寻找共鸣
                    match = find_resonance(vec, st.session_state.username)
                    if match:
                        msg_id = int(time.time())
                        # 把共鸣提示也作为一条 assistant 消息存进去？
                        # 或者只存入 Session 供本次显示？
                        # 这里为了简单，我们只在界面显示，不存入 chat 表，因为它是一种“系统通知”
                        st.toast(f"🔔 发现与 {match['user']} 的共鸣！", icon="⚡")
                        # (由于 Streamlit 刷新机制，这里不好直接插按钮，
                        # 我们依赖 rerun 后，在右侧或者新的一行显示。
                        # 为了演示方便，我们暂时不存库共鸣事件，仅刷新显示节点)
                
                # 刷新页面，让右侧的节点卡片显示出来
                st.rerun()

    # --- 2. 右侧：批注流 ---
    with col_insight:
        # 只显示与当前屏幕上的对话匹配的节点
        # 倒序遍历聊天记录，找到有节点的
        
        # 为了美观，我们只显示最近生成的几个节点，或者匹配到的
        st.caption("🧩 深度批注")
        
        # 我们可以显示所有历史节点，或者只显示和当前对话有关的
        # 这里显示所有历史节点的折叠板，按时间倒序
        for node in reversed(history_nodes):
            with st.expander(f"✨ #{node['id']} {node['care_point'][:6]}...", expanded=False):
                st.caption(f"Logic: {node.get('logic_score', 0.5)}")
                st.write(f"**Structure:** {node['meaning_layer']}")
                st.info(f"💡 {node['insight']}")
