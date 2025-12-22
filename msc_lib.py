### msc_lib.py ###
import streamlit as st
import numpy as np
import json
import re
import time
import math
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

    vertex_embed = None
    try:
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds = service_account.Credentials.from_service_account_info(creds_dict)
            vertexai.init(project=creds_dict['project_id'], location='us-central1', credentials=creds)
            vertex_embed = TextEmbeddingModel.from_pretrained("text-embedding-004")
    except Exception as e:
         db.log_system_event("WARN", "Init_Vertex", f"Vertex AI failed: {str(e)}")
    
    return client_openai, model_openai, vertex_embed

client_ai, TARGET_MODEL, vertex_embed_model = init_system()

# ==========================================
# 🌉 2. 数据库桥梁
# ==========================================
def login_user(u, p): return db.login_user(u, p)
def add_user(u, p, n, c): return db.add_user(u, p, n, c)
def get_nickname(u): return db.get_nickname(u)
def get_user_profile(u): return db.get_user_profile(u)
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

# 消息与好友
def save_chat(u, r, c): db.save_chat(u, r, c)
def get_active_chats(u): return db.get_active_chats(u)
def get_direct_messages(u1, u2): return db.get_direct_messages(u1, u2)
def send_direct_message(s, r, c): return db.send_direct_message(s, r, c)
def get_unread_counts(c): return db.get_unread_counts(c)
def mark_messages_read(s, r): db.mark_read(s, r)
def send_friend_request(s, r, m, meta): return db.send_friend_request(s, r, m, meta) # 🟢
def get_pending_requests(u): return db.get_pending_requests(u) # 🟢
def handle_friend_request(rid, act): return db.handle_friend_request(rid, act) # 🟢
def get_my_friends(u): return db.get_my_friends(u) # 🟢

# 节点
def save_node(u, c, d, m, v): return db.save_node(u, c, d, m, v)
def get_active_nodes_map(u): return db.get_active_nodes_map(u)
def get_all_nodes_for_map(u): return db.get_all_nodes_for_map(u)
def get_global_nodes(): return db.get_global_nodes()
def get_system_logs(): return db.get_system_logs() 

def check_world_access(username):
    nodes = db.get_all_nodes_for_map(username)
    return len(nodes) >= config.WORLD_UNLOCK_THRESHOLD, len(nodes)

# ==========================================
# 🟢 3. 社交匹配算法 (Top Near & Far)
# ==========================================
def get_match_candidates(current_username):
    """
    返回: { 'near': [Top5 Users], 'far': [Top5 Users] }
    """
    candidates = db.get_all_users(current_username)
    if not candidates: return {'near':[], 'far':[]}

    my_profile = db.get_user_profile(current_username)
    my_radar_str = my_profile.get('radar_profile')
    my_radar = json.loads(my_radar_str) if isinstance(my_radar_str, str) else (my_radar_str or {})
    
    # 距离计算
    scored_users = []
    axes = config.RADAR_AXES
    
    for user in candidates:
        u_radar = json.loads(user['radar_profile']) if isinstance(user.get('radar_profile'), str) else (user.get('radar_profile') or {})
        dist_sq = 0
        valid_data = False
        
        # 简单欧氏距离
        for axis in axes:
            v1 = float(my_radar.get(axis, 3.0))
            v2 = float(u_radar.get(axis, 3.0))
            dist_sq += (v1 - v2) ** 2
            if u_radar: valid_data = True # 只要对方有数据
            
        distance = math.sqrt(dist_sq)
        if not valid_data: distance = 999 
        scored_users.append((user, distance))

    # 排序
    scored_users.sort(key=lambda x: x[1])
    
    # 筛选有效用户（排除距离999的幽灵数据，除非只有幽灵）
    valid_users = [x for x in scored_users if x[1] < 100]
    if not valid_users: valid_users = scored_users

    # Near: 距离最小
    near_list = [item[0] for item in valid_users[:5]]
    
    # Far: 距离最大 (且不是无效数据)
    far_list = [item[0] for item in reversed(valid_users[-5:])]

    return {'near': near_list, 'far': far_list}

# ==========================================
# 🧮 4. 向量与AI调用
# ==========================================
def get_embedding(text):
    if vertex_embed_model:
        try: return vertex_embed_model.get_embeddings([text])[0].values
        except: pass
    return np.random.rand(768).tolist()

def call_ai_api(prompt, use_google=False):
    if not client_ai: return {"error": "AI未连接"}
    try:
        response = client_ai.chat.completions.create(
            model=TARGET_MODEL,
            messages=[{"role": "system", "content": "Output valid JSON only."}, {"role": "user", "content": prompt}],
            temperature=0.7, stream=False, response_format={"type": "json_object"} 
        )
        content = response.choices[0].message.content
        try: return json.loads(re.search(r'\{.*\}', content, re.DOTALL).group(0))
        except: return json.loads(content)
    except Exception as e: return {"error": True, "msg": str(e)}

def get_stream_response(history_messages):
    if not client_ai: 
        yield "⚠️ AI Client Init Failed."; return
    try:
        lang = st.session_state.get('language', 'en')
        lang_instruction = "Reply in Chinese." if lang == 'zh' else "Reply in English."
        system_prompt = config.PROMPT_CHATBOT + f"\n[CURRENT LANGUAGE INSTRUCTION]: {lang_instruction}"
        api_messages = [{"role": "system", "content": system_prompt}]
        for msg in history_messages: 
            if msg['role'] in ['user', 'assistant']: api_messages.append({"role": msg["role"], "content": msg["content"]})
        stream = client_ai.chat.completions.create(model=TARGET_MODEL, messages=api_messages, temperature=0.8, stream=True)
        for chunk in stream:
            if chunk.choices[0].delta.content is not None: yield chunk.choices[0].delta.content
    except Exception as e: yield f"❌ API Error: {str(e)}"

def analyze_meaning_background(text):
    lang = st.session_state.get('language', 'en')
    lang_instruction = "Output 'care_point' and 'insight' in Simplified Chinese." if lang == 'zh' else "Output 'care_point' and 'insight' in English."
    prompt = f"{config.PROMPT_ANALYST}\n[LANGUAGE_OVERRIDE]: {lang_instruction}\nUser Input: \"{text}\""
    res = call_ai_api(prompt)
    if not isinstance(res, dict): return {"valid": False, "m_score": 0, "insight": "Analysis Failed"}
    if res.get("valid", False) or res.get("c_score", 0) > 0:
        c = res.get('c_score', 0); n = res.get('n_score', 0)
        if n == 0: n = 0.6 
        res['m_score'] = c * n * 2.2
        keywords = res.get('keywords', [])
        clean_keywords = [k for k in keywords if k in config.SPECTRUM]
        if not clean_keywords and res['m_score'] > config.LEVELS["Signal"]:
            fallback = "Consciousness" if len(text) > 20 else "Aesthetic"
            clean_keywords.append(fallback)
            res['keywords'] = clean_keywords
            res['radar_scores'] = {config.DIMENSION_MAP.get(fallback, "Aesthetic"): 1.0}
        res['keywords'] = clean_keywords
        if res['m_score'] < config.LEVELS["Signal"]: res["valid"] = False
        else: res["valid"] = True
    else: res["valid"] = False; res["m_score"] = 0
    return res

def generate_daily_question(username, radar_data):
    lang = st.session_state.get('language', 'en')
    radar_str = json.dumps(radar_data, ensure_ascii=False)
    lang_instruction = "Output the question strictly in Simplified Chinese." if lang == 'zh' else "Output the question strictly in English."
    prompt = f"{config.PROMPT_DAILY}\nUser Data: {radar_str}\n[CRITICAL]: {lang_instruction}"
    res = call_ai_api(prompt)
    return res.get("question", "")

# 🟢 新增：生成隐喻
def generate_relationship_metaphor(u_self, u_target, match_type):
    lang = st.session_state.get('language', 'en')
    # 获取两人的 Radar
    p1 = db.get_user_profile(u_self); r1 = p1.get('radar_profile', {})
    p2 = db.get_user_profile(u_target); r2 = p2.get('radar_profile', {})
    
    data_str = f"User A: {r1}\nUser B: {r2}\nMatch Type: {match_type}"
    lang_instr = "ZH" if lang == 'zh' else "EN"
    
    prompt = f"{config.PROMPT_METAPHOR}\nDATA:\n{data_str}\nTARGET_LANG: {lang_instr}"
    res = call_ai_api(prompt)
    
    fallback = "The moon and the tide." if lang_instr == "EN" else "月亮与潮汐。"
    return res.get("metaphor", fallback)

def update_radar_score(username, input_scores):
    try:
        user_data = db.get_user_profile(username)
        current = user_data.get('radar_profile')
        default_radar = {k: 3.0 for k in config.RADAR_AXES}
        if not current: current = default_radar
        elif isinstance(current, str): 
            try:
                current_dict = json.loads(current)
                for k in config.RADAR_AXES:
                    if k not in current_dict: current_dict[k] = 3.0
                current = current_dict
            except: current = default_radar
        updated = {}
        alpha = config.RADAR_ALPHA
        for k in config.RADAR_AXES:
            old_val = float(current.get(k, 3.0))
            if k in input_scores: new_val = old_val * (1 - alpha) + float(input_scores[k]) * alpha + 0.5 
            else: new_val = old_val 
            updated[k] = round(min(10.0, new_val), 2)
        db.update_radar_score(username, json.dumps(updated))
    except Exception as e: print(f"Radar Update Error: {e}")

def analyze_persona_report(radar_data):
    lang = st.session_state.get('language', 'en')
    radar_str = json.dumps(radar_data, ensure_ascii=False)
    lang_instruction = "Output the analysis in Simplified Chinese." if lang == 'zh' else "Output the analysis in English."
    prompt = f"{config.PROMPT_PROFILE}\nDATA: {radar_str}\n[INSTRUCTION]: {lang_instruction}"
    return call_ai_api(prompt)

def process_time_decay(): return db.process_time_decay()
