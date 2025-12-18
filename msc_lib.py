### msc_lib.py ###

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
# 🛑 1. 初始化系统 (带容错日志)
# ==========================================
def init_system():
    # A. OpenAI/DeepSeek 客户端
    client_openai = None
    model_openai = "gpt-3.5-turbo"
    
    try:
        if "API_KEY" in st.secrets and "BASE_URL" in st.secrets:
            client_openai = OpenAI(
                api_key=st.secrets["API_KEY"],
                base_url=st.secrets["BASE_URL"]
            )
            model_openai = st.secrets["MODEL_NAME"]
        else:
            db.log_system_event("WARN", "Init", "OpenAI Credentials missing")
    except Exception as e:
        db.log_system_event("ERROR", "Init_OpenAI", str(e))

    # B. Google Vertex AI (Embedding)
    vertex_embed = None
    try:
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds = service_account.Credentials.from_service_account_info(creds_dict)
            vertexai.init(project=creds_dict['project_id'], location='us-central1', credentials=creds)
            vertex_embed = TextEmbeddingModel.from_pretrained("text-embedding-004")
    except Exception as e:
         # 这不是致命错误，降级处理即可，但需要记录
         db.log_system_event("WARN", "Init_Vertex", f"Vertex AI failed: {str(e)}")
    
    return client_openai, model_openai, vertex_embed

client_ai, TARGET_MODEL, vertex_embed_model = init_system()

# ==========================================
# 🌉 2. 数据库桥梁 (透传 DB 函数)
# ==========================================
def login_user(u, p): return db.login_user(u, p)
def add_user(u, p, n, c): return db.add_user(u, p, n, c)
def get_nickname(u): return db.get_nickname(u)
def get_user_profile(u): return db.get_user_profile(u)
def get_all_users(curr): return db.get_all_users(curr)
def update_heartbeat(u): db.update_heartbeat(u)
def check_is_online(last_seen_str):
    if not last_seen_str: return False
    try:
        if last_seen_str.endswith('Z'): last_seen = datetime.fromisoformat(last_seen_str.replace('Z', '+00:00'))
        else: last_seen = datetime.fromisoformat(last_seen_str)
        if last_seen.tzinfo is None: last_seen = last_seen.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - last_seen).total_seconds() < config.HEARTBEAT_TIMEOUT
    except: return False

def calculate_rank(radar_data):
    if not radar_data: return "Citizen", "🥉"
    if isinstance(radar_data, str): 
        try: radar_data = json.loads(radar_data)
        except: return "Citizen", "🥉"
    try: total = sum(float(v) for v in radar_data.values())
    except: total = 0
    if total < 25: return "Observer", "🥉"
    elif total < 38: return "Seeker", "🥈"
    elif total < 54: return "Architect", "💎"
    else: return "Navigator", "👑"

def save_chat(u, r, c): db.save_chat(u, r, c)
def get_active_chats(u): return db.get_active_chats(u)
def get_direct_messages(u1, u2): return db.get_direct_messages(u1, u2)
def send_direct_message(s, r, c): return db.send_direct_message(s, r, c)
def get_unread_counts(c): return db.get_unread_counts(c)
def mark_messages_read(s, r): db.mark_read(s, r)
def save_node(u, c, d, m, v): return db.save_node(u, c, d, m, v)
def get_active_nodes_map(u): return db.get_active_nodes_map(u)
def get_all_nodes_for_map(u): return db.get_all_nodes_for_map(u)
def get_global_nodes(): return db.get_global_nodes()
def get_system_logs(): return db.get_system_logs() # 导出日志函数

def check_world_access(username):
    nodes = db.get_all_nodes_for_map(username)
    return len(nodes) >= config.WORLD_UNLOCK_THRESHOLD, len(nodes)

# ==========================================
# 🧮 3. 向量算法
# ==========================================
def get_embedding(text):
    if vertex_embed_model:
        try:
            embeddings = vertex_embed_model.get_embeddings([text])
            return embeddings[0].values
        except Exception as e:
             db.log_system_event("ERROR", "Embedding", str(e))
    # Fallback: Random Vector (避免系统完全崩溃)
    return np.random.rand(768).tolist()

def cosine_similarity(v1, v2):
    if not v1 or not v2: return 0
    try:
        vec1 = np.array(v1); vec2 = np.array(v2)
        norm1 = np.linalg.norm(vec1); norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0: return 0
        return np.dot(vec1, vec2) / (norm1 * norm2)
    except: return 0

# ==========================================
# 🧠 4. AI 智能核心 (流式升级版)
# ==========================================
def call_ai_api(prompt, use_google=False):
    # 非流式调用（用于后台分析）
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
    except Exception as e: 
        db.log_system_event("ERROR", "AI_Call", str(e))
        return {"error": True, "msg": str(e)}

def get_stream_response(history_messages):
    """
    核心升级：返回一个生成器，支持流式输出
    """
    if not client_ai: 
        yield "⚠️ AI Client Init Failed."
        return

    try:
        api_messages = [{"role": "system", "content": config.PROMPT_CHATBOT}]
        for msg in history_messages: 
            if msg['role'] in ['user', 'assistant']:
                api_messages.append({"role": msg["role"], "content": msg["content"]})
        
        # 开启 stream=True
        stream = client_ai.chat.completions.create(
            model=TARGET_MODEL, 
            messages=api_messages, 
            temperature=0.8, 
            stream=True 
        )
        
        # 逐块 yield
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    except Exception as e:
        db.log_system_event("ERROR", "AI_Stream", str(e))
        yield f"❌ API Error: {str(e)}"

def analyze_meaning_background(text):
    prompt = f"{config.PROMPT_ANALYST}\nUser Input: \"{text}\""
    res = call_ai_api(prompt)
    if not isinstance(res, dict):
        return {"valid": False, "m_score": 0, "insight": "Analysis Failed"}

    if res.get("valid", False) or res.get("c_score", 0) > 0:
        c = res.get('c_score', 0)
        n = res.get('n_score', 0)
        if n == 0: n = 0.5 
        m = c * n * 2 # 计算逻辑
        res['m_score'] = m
        # 硬门槛过滤
        if m < config.LEVELS["Signal"]: res["valid"] = False
        else: res["valid"] = True
    else:
        res["valid"] = False
        res["m_score"] = 0
    return res

def generate_daily_question(username, radar_data):
    radar_str = json.dumps(radar_data, ensure_ascii=False)
    prompt = f"{config.PROMPT_DAILY}\nUser Data: {radar_str}"
    res = call_ai_api(prompt, use_google=False)
    return res.get("question", "What constitutes the boundary of your self?")

def update_radar_score(username, input_scores):
    try:
        user_data = db.get_user_profile(username)
        current = user_data.get('radar_profile')
        if not current: current = {k: 3.0 for k in input_scores.keys()}
        elif isinstance(current, str): current = json.loads(current)
        updated = {}
        alpha = config.RADAR_ALPHA
        for k, v in input_scores.items():
            old = float(current.get(k, 3.0)); val = float(v)
            updated[k] = round(old * (1-alpha) + val * alpha, 2)
        db.update_radar_score(username, json.dumps(updated))
    except: pass
    
def find_resonance(current_vector, current_user, current_data):
    if not current_vector: return None
    others = db.get_global_nodes()
    if not others: return None
    
    best_match, highest_score = None, 0
    
    # 获取当前内容的颜色 (作为一种情感滤镜)
    my_color = current_data.get('keywords', [''])[0] if current_data.get('keywords') else ''
    
    for row in others:
        if row['username'] == current_user: continue
        
        # 1. 向量相似度 (基础分)
        if row['vector']:
            try:
                o_vec = json.loads(row['vector'])
                sim_score = cosine_similarity(current_vector, o_vec)
                
                # 2. 颜色共鸣加成 (Bonus)
                bonus = 0
                if my_color and my_color in str(row.get('keywords','')):
                    bonus = 0.1
                
                final_score = sim_score + bonus
                
                if final_score > config.LINK_THRESHOLD["Strong"] and final_score > highest_score:
                    highest_score = final_score
                    best_match = {"user": row['username'], "content": row['content'], "score": round(final_score * 100, 1)}
            except: continue
            
    return best_match
    
def analyze_persona_report(radar_data):
    radar_str = json.dumps(radar_data, ensure_ascii=False)
    prompt = f"{config.PROMPT_PROFILE}\nDATA: {radar_str}"
    return call_ai_api(prompt, use_google=False)

def process_time_decay():
    return db.process_time_decay()
