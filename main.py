import streamlit as st
from openai import OpenAI
import json
import re
import sqlite3
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
except:
    st.error("🚨 配置缺失！请在 Secrets 中配置 API_KEY, BASE_URL 和 MODEL_NAME。")
    st.stop()

# ==========================================

# --- 🛠️ 基础设施：数据库管理 ---
def init_db():
    conn = sqlite3.connect('msc.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT, nickname TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS nodes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT, 
                  content TEXT, 
                  care_point TEXT, 
                  meaning_layer TEXT, 
                  insight TEXT,
                  mode TEXT,
                  created_at TIMESTAMP,
                  vector TEXT)''') 
    conn.commit()
    return conn

conn = init_db()

# --- 🔐 用户系统 ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text: return True
    return False

def add_user(username, password, nickname):
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users VALUES (?,?,?)', (username, make_hashes(password), nickname))
        conn.commit()
        return True
    except: return False

def login_user(username, password):
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username =? AND password = ?', (username, make_hashes(password)))
    return c.fetchall()

def get_nickname(username):
    c = conn.cursor()
    c.execute('SELECT nickname FROM users WHERE username=?', (username,))
    res = c.fetchone()
    return res[0] if res else username

# --- 🧠 AI 核心 ---
def call_ai_api(prompt):
    try:
        response = client.chat.completions.create(
            model=TARGET_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Output valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            stream=False,
            response_format={"type": "json_object"} 
        )
        content = response.choices[0].message.content
        try:
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match: return json.loads(match.group(0))
            else: return json.loads(content)
        except: return {"error": True, "msg": "JSON 解析失败"}
    except Exception as e:
        return {"error": True, "msg": f"API 调用失败: {str(e)}"}

def get_embedding(text):
    return np.random.rand(1536).tolist()

# --- 业务逻辑 ---
def generate_node_data(mode, text):
    prompt = f"""
    你是 MSC 意义构建者。场景：【{mode}】。用户输入："{text}"。
    请提取结构，必须直接返回合法的 JSON 格式:
    {{
        "care_point": "用户潜意识里的情绪/论点/张力...",
        "meaning_layer": "背后的深层逻辑/意象/范式...",
        "insight": "一句意想不到的升维洞察..."
    }}
    """
    return call_ai_api(prompt)

def generate_fusion(node_a_content, node_b_content):
    prompt = f"""
    请融合这两段看似不同但内核相似的观点。
    A: "{node_a_content}"
    B: "{node_b_content}"
    生成一个 C 节点 (必须是 JSON):
    {{
        "care_point": "两人共同的潜意识呼唤",
        "meaning_layer": "全景结构",
        "insight": "集体智慧金句"
    }}
    """
    return call_ai_api(prompt)

# --- 🧮 算法 ---
def cosine_similarity(v1, v2):
    if not v1 or not v2: return 0
    vec1 = np.array(v1)
    vec2 = np.array(v2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0: return 0
    return np.dot(vec1, vec2) / (norm1 * norm2)

def find_resonance(current_vector, current_user):
    if not current_vector: return None
    c = conn.cursor()
    c.execute('SELECT username, content, vector FROM nodes WHERE username != ?', (current_user,))
    others = c.fetchall()
    
    best_match = None
    highest_score = 0
    
    for row in others:
        other_user = row[0]
        other_content = row[1]
        other_vector_str = row[2]
        
        if other_vector_str:
            try:
                other_vector = json.loads(other_vector_str)
                score = cosine_similarity(current_vector, other_vector)
                if score > 0.7 and score > highest_score:
                    highest_score = score
                    best_match = {
                        "user": other_user,
                        "content": other_content,
                        "score": round(score * 100, 1)
                    }
            except: continue
    
    return best_match

# --- 💾 存取 ---
def save_node(username, content, data, mode, vector):
    c = conn.cursor()
    vector_str = json.dumps(vector)
    care = data.get('care_point', '未命名')
    meaning = data.get('meaning_layer', '暂无结构')
    insight = data.get('insight', '生成中断')
    c.execute('''INSERT INTO nodes (username, content, care_point, meaning_layer, insight, mode, created_at, vector)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (username, content, care, meaning, insight, mode, datetime.now(), vector_str))
    conn.commit()

def get_user_nodes(username):
    c = conn.cursor()
    c.execute('SELECT * FROM nodes WHERE username=? ORDER BY id DESC', (username,))
    return c.fetchall()

# ==========================================
# 🖥️ 界面主逻辑
# ==========================================

st.set_page_config(page_title="MSC v10.1 UI Fix", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌌 MSC 意义协作系统")
    st.caption("DeepSeek 商业引擎驱动")
    tab1, tab2 = st.tabs(["登录", "注册"])
    with tab1:
        u = st.text_input("用户名")
        p = st.text_input("密码", type='password')
        if st.button("登录"):
            res = login_user(u, p)
            if res:
                st.session_state.logged_in = True
                st.session_state.username = u
                st.session_state.nickname = res[0][2]
                st.session_state.messages = [] 
                st.rerun()
            else: st.error("错误")
    with tab2:
        nu = st.text_input("新用户名")
        np_pass = st.text_input("新密码", type='password')
        nn = st.text_input("昵称")
        if st.button("注册"):
            if add_user(nu, np_pass, nn): st.success("成功！请登录")
            else: st.error("已存在")

else:
    with st.sidebar:
        st.write(f"👋 **{st.session_state.nickname}**")
        if st.button("退出"):
            st.session_state.logged_in = False
            st.session_state.messages = [] 
            st.rerun()
        st.divider()
        st.header("🗂️ 我的意义档案")
        history = get_user_nodes(st.session_state.username)
        if history:
            for row in history:
                with st.expander(f"#{row[0]} {row[3][:10]}..."):
                    st.caption(f"{row[7]}")
                    st.write(f"**原话:** {row[2]}")
                    st.info(f"{row[5]}")
    
    st.title("MSC 意义构建 & 共鸣雷达")
    st.caption("基于 DeepSeek V3 强力驱动")
    
    mode = st.selectbox("场景", ["🌱 日常社交", "🎓 学术研讨", "🎨 艺术共创"])
    user_input = st.chat_input("输入思考...")
    
    if "messages" not in st.session_state: st.session_state.messages = []
    
    # 🌟 修复部分：渲染历史消息时，开启 HTML 支持
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            # 这里加了 unsafe_allow_html=True，乱码就会变回漂亮的卡片
            st.markdown(msg["content"], unsafe_allow_html=True)
            
            if "fusion_data" in msg:
                match = msg["fusion_data"]
                btn_key = f"btn_merge_{msg['id']}"
                if st.button(f"⚡ 发现共鸣 ({match['score']}%)：与 {get_nickname(match['user'])} 合并？", key=btn_key):
                    with st.spinner("正在融合..."):
                        c_node = generate_fusion(msg["my_content"], match["content"])
                        if "error" not in c_node:
                            # 生成漂亮的 HTML 卡片
                            fusion_html = f"""
                            <div style="background-color:#E8F5E9;padding:20px;border-radius:10px;border-left:5px solid #2E7D32;margin-top:10px;">
                                <h4 style="color:#2E7D32;margin:0;">🧬 融合成功：集体智慧节点</h4>
                                <hr style="border-top: 1px solid #A5D6A7;">
                                <p><strong>👤 A ({st.session_state.nickname}):</strong> {msg['my_content']}</p>
                                <p><strong>👤 B ({get_nickname(match['user'])}):</strong> {match['content']}</p>
                                <div style="background-color:#fff;padding:10px;border-radius:5px;margin-top:10px;">
                                    <p style="color:#1B5E20;font-weight:bold;font-size:1.1em;">💡 升维洞察: {c_node.get('insight')}</p>
                                    <p style="font-size:0.9em;color:#555;">🧩 结构: {c_node.get('meaning_layer')}</p>
                                </div>
                            </div>
                            """
                            # 这里也加了 unsafe_allow_html=True
                            st.markdown(fusion_html, unsafe_allow_html=True)
                            # 存入历史记录
                            st.session_state.messages.append({"role": "assistant", "content": fusion_html})
                        else:
                            st.error(f"融合失败: {c_node.get('msg', '未知错误')}")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
            
        with st.chat_message("assistant"):
            with st.spinner("DeepSeek 正在思考..."):
                res = generate_node_data(mode, user_input)
                
                if "error" in res:
                    st.error(f"⚠️ 生成失败: {res.get('msg')}")
                else:
                    vec = get_embedding(user_input)
                    save_node(st.session_state.username, user_input, res, mode, vec)
                    
                    card = f"""
                    **✨ 节点生成**
                    * **Care:** {res['care_point']}
                    > {res['insight']}
                    """
                    st.markdown(card)
                    
                    match = find_resonance(vec, st.session_state.username)
                    
                    msg_payload = {"role": "assistant", "content": card}
                    
                    if match:
                        msg_id = int(time.time())
                        msg_payload["fusion_data"] = match
                        msg_payload["my_content"] = user_input
                        msg_payload["id"] = msg_id
                        
                        st.success(f"🔔 滴！监测到与用户 **{get_nickname(match['user'])}** 的思想重叠度高达 **{match['score']}%**！")
                        st.button(f"⚡ 发现共鸣 ({match['score']}%)：与 {get_nickname(match['user'])} 合并？", key=f"btn_merge_{msg_id}")
                    
                    st.session_state.messages.append(msg_payload)
                    time.sleep(1)
                    st.rerun()
