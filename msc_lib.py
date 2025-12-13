### msc_lib.py (本地向量版 - 星河点亮) ###

import streamlit as st
import numpy as np
import json
import re
import time
from datetime import datetime, timezone
from openai import OpenAI
from sklearn.decomposition import PCA
import msc_config as config
import msc_db as db

# === 新增：引入本地向量库 ===
# 使用 @st.cache_resource 确保模型只加载一次，不会拖慢速度
from sentence_transformers import SentenceTransformer

@st.cache_resource
def load_embedding_model():
    # 使用一个超轻量级的中文模型 (约 20MB)，下载飞快
    return SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# ==========================================
# 🛑 1. 初始化系统
# ==========================================
def init_system():
    try:
        client = OpenAI(
            api_key=st.secrets["API_KEY"],
            base_url=st.secrets["BASE_URL"]
        )
        model = st.secrets["MODEL_NAME"]
        return client, model
    except Exception as e:
        print(f"系统初始化警告: {e}")
        return None, "gpt-3.5-turbo"

client_ai, TARGET_MODEL = init_system()

# ==========================================
# 🌉 2. 数据库桥梁
# ==========================================
def login_user(username, password): return db.login_user(username, password)
def add_user(username, password, nickname, country="Other"): return db.add_user(username, password, nickname, country)
def get_nickname(username): return db.get_nickname(username)
def get_user_profile(username): return db.get_user_profile(username)
def get_all_users(current_user): return db.get_all_users(current_user)
def update_heartbeat(username): db.update_heartbeat(username)

def check_is_online(last_seen_str):
    if not last_seen_str: return False
    try:
        if last_seen_str.endswith('Z'): last_seen = datetime.fromisoformat(last_seen_str.replace('Z', '+00:00'))
        else: last_seen = datetime.fromisoformat(last_seen_str)
        if last_seen.tzinfo is None: last_seen = last_seen.replace(tzinfo=timezone.utc)
        diff = datetime.now(timezone.utc) - last_seen
        return diff.total_seconds() < config.HEARTBEAT_TIMEOUT
    except: return False

def calculate_rank(radar_data):
    if not radar_data: return "MSC 公民", "🥉"
    if isinstance(radar_data, str): 
        try: radar_data = json.loads(radar_data)
        except: return "MSC 公民", "🥉"
    try: total = sum(float(v) for v in radar_data.values())
    except: total = 0
    if total < 25: return "观察者", "🥉"
    elif total < 38: return "探索者", "🥈"
    elif total < 54: return "构建者", "💎"
    else: return "领航员", "👑"

def save_chat(u, r, c): db.save_chat(u, r, c)
def get_active_chats(u): return db.get_active_chats(u)
def get_direct_messages(u1, u2): return db.get_direct_messages(u1, u2)
def send_direct_message(s, r, c): return db.send_direct_message(s, r, c)
def get_unread_counts(c): return db.get_unread_counts(c)
def mark_messages_read(s, r): db.mark_read(s, r)
def save_node(u, c, d, m, v): db.save_node(u, c, d, m, v)
def get_active_nodes_map(u): return db.get_active_nodes_map(u)
def get_all_nodes_for_map(u): return db.get_all_nodes_for_map(u)
def get_global_nodes(): return db.get_global_nodes()

# ==========================================
# 🧮 3. 数学与向量算法 (升级版)
# ==========================================
def get_embedding(text):
    """
    使用本地模型将文本转化为 384 维向量
    这会让相似的意义在空间中真正靠近
    """
    try:
        model = load_embedding_model()
        # 转化为 list 方便 JSON 存储
        vector = model.encode(text).tolist()
        return vector
    except Exception as e:
        print(f"Embedding Error: {e}")
        # 降级方案：如果模型加载失败，返回随机向量防止报错
        return np.random.rand(384).tolist()

def cosine_similarity(v1, v2):
    if not v1 or not v2: return 0
    vec1 = np.array(v1); vec2 = np.array(v2)
    norm1 = np.linalg.norm(vec1); norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0: return 0
    return np.dot(vec1, vec2) / (norm1 * norm2)

# ==========================================
# 🧠 4. AI 智能核心 (IHIL v1.0)
# ==========================================
def call_ai_api(prompt):
    if not client_ai: return {"error": "AI未连接"}
    try:
        response = client_ai.chat.completions.create(
            model=TARGET_MODEL,
            messages=[
                {"role": "system", "content": "Output valid JSON only. No markdown."}, 
                {"role": "user", "content": prompt}
            ],
            temperature=0.7, stream=False, response_format={"type": "json_object"} 
        )
        content = response.choices[0].message.content
        try:
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match: return json.loads(match.group(0))
            else: return json.loads(content)
        except: return {"error": True}
    except Exception as e: return {"error": True, "msg": str(e)}

def get_normal_response(history_messages):
    if not client_ai: yield "AI 未配置"; return
    try:
        api_messages = [{"role": "system", "content": config.PROMPT_CHATBOT}]
        for msg in history_messages: 
            if msg['role'] in ['user', 'assistant']:
                api_messages.append({"role": msg["role"], "content": msg["content"]})
        return client_ai.chat.completions.create(model=TARGET_MODEL, messages=api_messages, temperature=0.8, stream=True)
    except Exception as e: return f"Error: {e}"

def analyze_meaning_background(text):
    # 使用 IHIL v1.0 分析
    prompt = f"{config.PROMPT_ANALYST}\n用户输入: \"{text}\""
    res = call_ai_api(prompt)
    if res.get("valid", False) or res.get("c_score", 0) > 0:
        c = res.get('c_score', 0); n = res.get('n_score', 0)
        if n == 0: n = 0.5 
        m = c * n * 2
        res['m_score'] = m
        if m < config.LEVELS["Weak"]: res["valid"] = False
        else: res["valid"] = True
    return res

def generate_daily_question(username, radar_data):
    try:
        recent = db.get_all_nodes_for_map(username)
        ctx = ""
        if recent: ctx = f"关注点：{[n['care_point'] for n in recent[-3:]]}"
    except: ctx = ""
    radar_str = json.dumps(radar_data, ensure_ascii=False) if isinstance(radar_data, dict) else str(radar_data)
    prompt = f"{config.PROMPT_DAILY}\n用户数据：{radar_str}。{ctx}。输出 JSON: {{ 'question': '...' }}"
    res = call_ai_api(prompt)
    return res.get("question", "今天，什么事情让你感到'活着'？")

def analyze_persona_report(radar_data):
    radar_str = json.dumps(radar_data, ensure_ascii=False)
    prompt = f"基于MSC系统的7维雷达数据：{radar_str}。生成JSON报告：{{ 'status_quo': '心理学视角描述现状', 'growth_path': '预测思想进化方向' }}"
    return call_ai_api(prompt)

def update_radar_score(username, input_scores):
    try:
        user_data = db.get_user_profile(username)
        current = user_data.get('radar_profile')
        if not current: current = {k: 3.0 for k in input_scores.keys()}
        elif isinstance(current, str): current = json.loads(current)
        updated = {}
        alpha = config.RADAR_ALPHA
        for k, v in input_scores.items():
            old_val = float(current.get(k, 3.0))
            new_val = float(v)
            updated[k] = round(old_val * (1-alpha) + new_val * alpha, 2)
        db.update_radar_score(username, json.dumps(updated))
    except: pass
    
def find_resonance(current_vector, current_user, current_data):
    if not current_vector: return None
    others = db.get_global_nodes()
    if not others: return None
    best_match, highest_score = None, 0
    for row in others:
        if row['username'] == current_user: continue
        if row['vector']:
            try:
                o_vec = json.loads(row['vector'])
                score = cosine_similarity(current_vector, o_vec)
                if score > config.LINK_THRESHOLD["Strong"] and score > highest_score:
                    highest_score = score
                    best_match = {"user": row['username'], "content": row['content'], "score": round(score * 100, 1)}
            except: continue
    return best_match
