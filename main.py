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

# 🌟 强制锁定：只用这个额度最大(1500次/天)的模型
TARGET_MODEL = "gemini-1.5-flash"

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

# --- 🧠 AI 核心：HTTP 直连 + 强制锁定 ---

def call_gemini_http(prompt):
    """
    直接连接指定模型，不进行自动寻路
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{TARGET_MODEL}:generateContent?key={MY_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        # 30秒超时
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result_json = response.json()
            try:
                # 提取文本
                raw_text = result_json['candidates'][0]['content']['parts'][0]['text']
                # 清洗 JSON
                match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                if match:
                    res = json.loads(match.group(0))
                    res['model_used'] = TARGET_MODEL
                    return res
                else:
                    return {"error": True, "msg": "数据格式清洗失败"}
            except:
                return {"error": True, "msg": "API 返回结构异常"}
        elif response.status_code == 429:
             return {"error": True, "msg": "今日额度已达上限 (429)，请明天再试。"}
        else:
            return {"error": True, "msg": f"HTTP {response.status_code}: {response.text}"}
            
    except Exception as e:
        return {"error": True, "msg": f"网络层错误: {str(e)}"}

# --- 🧠 向量化 (HTTP 版) ---
def get_embedding_http(text):
    # 向量模型通常比较稳定，但也锁定一个
    url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={MY_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "model": "models/text-embedding-004",
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
    return call_gemini_http(prompt)

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
    return call_gemini_http(prompt)

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

st.set_page_config(page_title="MSC v8.1 Final", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- 1. 登录/注册 ---
if not st.session_state.logged_in:
    st.title("🌌 MSC 意义协作系统")
    st.caption("v8.1 稳定版")
    
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
    st.caption("当你的思想与他人重叠度 > 80% 时，系统将自动连接你们。")
    
    mode = st.selectbox("场景", ["🌱 日常社交", "🎓 学术研讨", "🎨 艺术共创"])
    user_input =
