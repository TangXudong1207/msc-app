### msc_lib.py (绝对完整版) ###

import streamlit as st
import numpy as np
import json
import re
import time
from datetime import datetime, timezone
from openai import OpenAI
from google.oauth2 import service_account
import vertexai
from vertexai.language_models import TextEmbeddingModel
import msc_config as config
import msc_db as db

# ==========================================
# 🛑 1. 初始化系统
# ==========================================
def init_system():
    # A. 思考引擎 (DeepSeek/OpenAI)
    try:
        client = OpenAI(
            api_key=st.secrets["API_KEY"],
            base_url=st.secrets["BASE_URL"]
        )
        model = st.secrets["MODEL_NAME"]
    except:
        client = None; model = "gpt-3.5-turbo"

    # B. 记忆引擎 (Google Vertex AI)
    vertex_model = None
    try:
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds = service_account.Credentials.from_service_account_info(creds_dict)
            vertexai.init(project=creds_dict['project_id'], location='us-central1', credentials=creds)
            vertex_model = TextEmbeddingModel.from_pretrained("text-embedding-004")
    except Exception as e:
        print(f"Vertex Init Error: {e}")

    return client, model, vertex_model

client_ai, TARGET_MODEL, vertex_embed_model = init_system()

# ==========================================
# 🌉 2. 数据库桥梁
# ==========================================
def login_user(username, password): return db.login_user(username, password)
def add_user(username, password, nickname, country="Other"): return db.add_user(username, password, nickname, country)
def get_nickname(username): return db.get_nickname(username)
def get_user_profile(username): return db.get_user_profile(username)
def get_all_users(current_user): return db.get_all_users(current_user)
def update_heartbeat(username): db.update_heartbeat(username)
def process_time_decay(): return db.process_time_decay()
def check_is_online(last_seen_str):
    if not last_seen_str: return False
    try:
        if last_seen_str.endswith('Z'): last_seen = datetime.fromisoformat(last_seen_str.replace('Z', '+00:00'))
        else: last_seen = datetime.fromisoformat(last_seen_str)
        if last_seen.tzinfo is None: last_seen = last_seen.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - last_seen).total_seconds() < config.HEARTBEAT_TIMEOUT
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

def save_chat(username, role, content): db.save_chat(username, role, content)
def get_active_chats(username): return db.get_active_chats(username)
def get_direct_messages(u1, u2): return db.get_direct_messages(u1, u2)
def send_direct_message(sender, receiver, content): return db.send_direct_message(sender, receiver, content)
def get_unread_counts(curr): return db.get_unread_counts(curr)
def mark_messages_read(sender, receiver): db.mark_read(sender, receiver)
def save_node(username, content, data, mode, vector): db.save_node(username, content, data, mode, vector)
def get_active_nodes_map(username): return db.get_active_nodes_map(username)
def get_all_nodes_for_map(username): return db.get_all_nodes_for_map(username)
def get_global_nodes(): return db.get_global_nodes()

# ==========================================
# 🧮 3. 向量算法
# ==========================================
def get_embedding(text):
    """
    智能路由：
    1. 优先尝试 Google Vertex (云端高性能)
    2. 失败则回退 Mock (本地/无网兜底)
    """
    if vertex_embed_model:
        try:
            embeddings = vertex_embed_model.get_embeddings([text])
            return embeddings[0].values
        except Exception as e:
            print(f"Vertex Embedding Failed: {e}")
    
    # Mock (随机向量)
    return np.random.rand(768).tolist()

def cosine_similarity(v1, v2):
    if not v1 or not v2: return 0
    vec1 = np.array(v1); vec2 = np.array(v2)
    norm1 = np.linalg.norm(vec1); norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0: return 0
    return np.dot(vec1, vec2) / (norm1 * norm2)

# ==========================================
# 🧠 4. AI 智能核心
# ==========================================
def call_ai_api(prompt):
    if not client_ai: return {"error": "AI未连接"}
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
        except: return {"error": True}
    except Exception as e: return {"error": True, "msg": str(e)}

# === 非流式响应 ===
def get_normal_response(history_messages):
    if not client_ai: return "⚠️ AI Client Init Failed."
    try:
        api_messages = [{"role": "system", "content": config.PROMPT_CHATBOT}]
        for msg in history_messages: 
            if msg['role'] in ['user', 'assistant']:
                api_messages.append({"role": msg["role"], "content": msg["content"]})
        
        response = client_ai.chat.completions.create(
            model=TARGET_MODEL, 
            messages=api_messages, 
            temperature=0.8, 
            stream=False # 关闭流式
        )
        return response.choices[0].message.content
    except Exception as e: 
        return f"❌ API Error: {str(e)}"

def analyze_meaning_background(text):
    prompt = f"{config.PROMPT_ANALYST}\n用户输入: \"{text}\""
    res = call_ai_api(prompt)
    
    if res.get("valid", False) or res.get("c_score", 0) > 0:
        c = res.get('c_score', 0)
        n = res.get('n_score', 0)
        if n == 0: n = 0.5 
        m = c * n * 2
        res['m_score'] = m
        if m < config.LEVELS["Weak"]: res["valid"] = False
        else: res["valid"] = True
    
    return res

# === 关键：张力分析 (之前可能缺失的部分) ===
def analyze_tension(text):
    """
    提取文本背后的哲学张力 (用于新闻地图)
    """
    prompt = f"{config.PROMPT_TENSION}\nContent: \"{text}\""
    return call_ai_api(prompt)

def generate_daily_question(username, radar_data):
    radar_str = json.dumps(radar_data, ensure_ascii=False)
    prompt = f"{config.PROMPT_DAILY}\n用户数据：{radar_str}。输出 JSON: {{ 'question': '...' }}"
    res = call_ai_api(prompt)
    return res.get("question", "今天，什么事情让你感到'活着'？")

def update_radar_score(username, input_scores):
    try:
        user_data = db.get_user_profile(username)
        current = user_data.get('radar_profile')
        if not current: 
            current = {k: 3.0 for k in input_scores.keys()}
        elif isinstance(current, str): 
            current = json.loads(current)
        
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
                    best_match = {
                        "user": row['username'], 
                        "content": row['content'], 
                        "score": round(score * 100, 1)
                    }
            except: continue
    return best_match
    
def analyze_persona_report(radar_data):
    radar_str = json.dumps(radar_data, ensure_ascii=False)
    prompt = f"""
    基于MSC系统的7维雷达数据：{radar_str}
    请生成一份简短深刻的用户画像报告，必须包含以下两个字段的JSON：
    1. "status_quo" (现状): 用心理学/哲学视角描述用户当前的精神底色。
    2. "growth_path" (成长): 基于当前维度的短板或优势，预测用户可能的思想进化方向。
    """
    return call_ai_api(prompt)
