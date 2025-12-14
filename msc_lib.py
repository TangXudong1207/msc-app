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
# 🛑 1. 初始化
# ==========================================
def init_system():
    # A. 思考 (DeepSeek)
    try:
        client = OpenAI(api_key=st.secrets["API_KEY"], base_url=st.secrets["BASE_URL"])
        model = st.secrets["MODEL_NAME"]
    except: client = None; model = "gpt-3.5-turbo"

    # B. 记忆 (Vertex AI)
    vertex_model = None
    try:
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds = service_account.Credentials.from_service_account_info(creds_dict)
            vertexai.init(project=creds_dict['project_id'], location='us-central1', credentials=creds)
            vertex_model = TextEmbeddingModel.from_pretrained("text-embedding-004")
    except: pass
    return client, model, vertex_model

client_ai, TARGET_MODEL, vertex_embed_model = init_system()

# ==========================================
# 🌉 2. 数据库桥梁
# ==========================================
def login_user(u, p): return db.login_user(u, p)
def add_user(u, p, n, c="Other"): return db.add_user(u, p, n, c)
def get_nickname(u): return db.get_nickname(u)
def get_user_profile(u): return db.get_user_profile(u)
def get_all_users(u): return db.get_all_users(u)
def update_heartbeat(u): db.update_heartbeat(u)
def check_is_online(last):
    if not last: return False
    try:
        if last.endswith('Z'): last = datetime.fromisoformat(last.replace('Z', '+00:00'))
        else: last = datetime.fromisoformat(last)
        if last.tzinfo is None: last = last.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - last).total_seconds() < config.HEARTBEAT_TIMEOUT
    except: return False

def calculate_rank(radar):
    if not radar: return "MSC 公民", "🥉"
    if isinstance(radar, str): radar = json.loads(radar)
    total = sum(float(v) for v in radar.values())
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
def get_global_nodes(): return db.get_global_nodes()

# ==========================================
# 🧮 3. 向量
# ==========================================
def get_embedding(text):
    if vertex_embed_model:
        try:
            return vertex_embed_model.get_embeddings([text])[0].values
        except: pass
    return np.random.rand(768).tolist()

def cosine_similarity(v1, v2):
    if not v1 or not v2: return 0
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

# ==========================================
# 🧠 4. AI 核心
# ==========================================
def call_ai_api(prompt):
    if not client_ai: return {"error": "AI未连接"}
    try:
        response = client_ai.chat.completions.create(
            model=TARGET_MODEL,
            messages=[{"role": "system", "content": "Output JSON only."}, {"role": "user", "content": prompt}],
            temperature=0.7, stream=False, response_format={"type": "json_object"} 
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e: return {"error": True}

def get_normal_response(history):
    if not client_ai: return "AI Error"
    try:
        api_messages = [{"role": "system", "content": config.PROMPT_CHATBOT}]
        for msg in history:
            if msg['role'] in ['user', 'assistant']:
                api_messages.append({"role": msg['role'], "content": msg['content']})
        return client_ai.chat.completions.create(model=TARGET_MODEL, messages=api_messages, temperature=0.8, stream=False).choices[0].message.content
    except Exception as e: return f"Error: {e}"

def analyze_meaning_background(text):
    res = call_ai_api(f"{config.PROMPT_ANALYST}\nInput: \"{text}\"")
    if res.get("valid", False) or res.get("c_score", 0) > 0:
        res['m_score'] = (res.get('c_score', 0) * 0.6 + res.get('n_score', 0) * 0.4) * 2
        res["valid"] = res['m_score'] >= config.LEVELS["Weak"]
    return res

# === 新增：张力分析 ===
def analyze_tension(text):
    prompt = f"{config.PROMPT_TENSION}\nContent: \"{text}\""
    return call_ai_api(prompt)

def generate_daily_question(u, r):
    return call_ai_api(f"{config.PROMPT_DAILY}\nRadar: {json.dumps(r)}").get("question", "Why?")

def update_radar_score(u, scores):
    try:
        curr = json.loads(db.get_user_profile(u).get('radar_profile', '{}')) or {k:3.0 for k in scores}
        updated = {k: round(curr.get(k,3)*0.85 + scores.get(k,3)*0.15, 2) for k in scores}
        db.update_radar_score(u, json.dumps(updated))
    except: pass

def find_resonance(vec, u, d):
    # (同前)
    return None

def analyze_persona_report(r):
    return call_ai_api(f"Persona Report for {json.dumps(r)} JSON: {{'status_quo':'...', 'growth_path':'...'}}")
