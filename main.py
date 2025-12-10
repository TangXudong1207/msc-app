import streamlit as st
import requests
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
    MY_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("🚨 未检测到密钥！请在 Streamlit 后台配置 GOOGLE_API_KEY。")
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

# --- 🧠 AI 核心：全能适配器 (解决 404 问题) ---

def call_gemini_universal(prompt):
    """
    穷举所有可能的 API 版本和模型名称，直到连通
    """
    # 备选组合：(API版本, 模型名称)
    # 优先试 v1beta 的 flash，不行试 v1 的 flash，再不行试 pro
    endpoints = [
        ("v1beta", "gemini-1.5-flash"),
        ("v1beta", "gemini-1.5-flash-latest"),
        ("v1beta", "gemini-1.5-flash-001"),
        ("v1", "gemini-1.5-flash"), # 尝试稳定版接口
        ("v1beta", "gemini-pro"),   # 保底老模型
    ]
    
    last_error = ""

    for version, model in endpoints:
        url = f"https://generativelanguage.googleapis.com/{version}/models/{model}:generateContent?key={MY_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        
        try:
            # 20秒超时
            response = requests.post(url, headers=headers, json=data, timeout=20)
            
            if response.status_code == 200:
                result_json = response.json()
                try:
                    # 提取文本
                    raw_text = result_json['candidates'][0]['content']['parts'][0]['text']
                    # 清洗 JSON
                    match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                    if match:
                        res = json.loads(match.group(0))
                        # 成功！记录下是哪条路通了
                        res['model_used'] = f"{model} ({version})"
                        return res
                except:
                    continue # 格式不对，试下一个
            elif response.status_code == 429:
                return {"error": True, "msg": "今日额度已达上限 (429)。"}
            else:
                last_error = f"{model} ({version}): {response.status_code}"
                continue # 报错，试下一个
                
        except Exception as e:
            last_error = str(e)
            continue
            
    # 如果所有路都堵死了
    return {"error": True, "msg": f"所有线路均不可用。最后错误: {last_error}"}

# --- 🧠 向量化 (通用版) ---
def get_embedding_universal(text):
    # 向量化也尝试两个版本
    endpoints = [
        ("v1beta", "text-embedding-004"),
        ("v1beta", "embedding-001")
    ]
    for version, model in endpoints:
        url = f"https://generativelanguage.googleapis.com/{version}/models/{model}:embedContent?key={MY_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        data = {
            "model": f"models/{model}",
            "content": {"parts": [{"text": text}]}
        }
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            if response.status_code == 200:
                return response.json()['embedding']['values']
        except: 
            pass
    return []

# --- 业务逻辑 ---
def generate_node_data(mode, text):
    prompt = f"""
    你是 MSC 意义构建者。场景：【{mode}】。用户输入："{text}"。
    请提取结构，直接返回 JSON:
    {{
        "care_point": "用户潜意识里的情绪/论点/张力...",
        "meaning_layer": "背后的深层逻辑/意象/范式...",
        "insight": "一句意想不到的升维洞察..."
    }}
    """
    return call_gemini_universal(prompt)

def generate_fusion(node_a_content, node_b_content):
    prompt = f"""
    请融合这两段看似不同但内核相似的观点。
    A: "{node_a_content}"
    B: "{node_b_content}"
    生成一个 C 节点 (JSON):
    {{
        "care_point": "两人共同的潜意识呼唤",
        "meaning_layer": "全景结构",
        "insight": "集体智慧金句"
    }}
    """
    return call_gemini_universal(prompt)

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
                if score > 0.8 and score > highest_score:
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

st.set_page_config(page_title="MSC v9.0 Universal", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- 1. 登录/注册 ---
if not st.session_state.logged_in:
    st.title("🌌 MSC 意义协作系统")
    st.caption("v9.0 全能适配器版")
    
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

# --- 2. 主系统 ---
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
    st.caption("全网路自适应：自动切换 v1/v1beta 和 Flash/Pro 模型。")
    
    mode = st.selectbox("场景", ["🌱 日常社交", "🎓 学术研讨", "🎨 艺术共创"])
    user_input = st.chat_input("输入思考...")
    
    if "messages" not in st.session_state: st.session_state.messages = []
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "fusion_data" in msg:
                match = msg["fusion_data"]
                btn_key = f"btn_merge_{msg['id']}"
                if st.button(f"⚡ 发现共鸣 ({match['score']}%)：与 {get_nickname(match['user'])} 合并？", key=btn_key):
                    with st.spinner("正在融合..."):
                        c_node = generate_fusion(msg["my_content"], match["content"])
                        if "error" not in c_node:
                            fusion_html = f"""
                            <div style="background-color:#E8F5E9;padding:15px;border-radius:10px;border-left:5px solid #2E7D32;">
                                <h4>🧬 融合成功：集体智慧节点</h4>
                                <p><strong>A ({st.session_state.nickname}):</strong> {msg['my_content']}</p>
                                <p><strong>B ({get_nickname(match['user'])}):</strong> {match['content']}</p>
                                <hr>
                                <p><strong>💡 升维洞察:</strong> {c_node.get('insight')}</p>
                                <p style="font-size:0.8em;color:grey;">(Via: {c_node.get('model_used')})</p>
                            </div>
                            """
                            st.markdown(fusion_html)
                            st.session_state.messages.append({"role": "assistant", "content": fusion_html})
                        else:
                            st.error(f"融合失败: {c_node.get('msg', '未知错误')}")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
            
        with st.chat_message("assistant"):
            with st.spinner("AI 正在尝试所有可用线路..."):
                res = generate_node_data(mode, user_input)
                
                if "error" in res:
                    error_msg = res.get('msg', '未知错误')
                    st.error(f"⚠️ 生成失败: {error_msg}")
                else:
                    vec = get_embedding_universal(user_input)
                    save_node(st.session_state.username, user_input, res, mode, vec)
                    
                    card = f"""
                    **✨ 节点生成**
                    * **Care:** {res['care_point']}
                    > {res['insight']}
                    
                    *(线路: {res.get('model_used', 'Auto')})*
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
