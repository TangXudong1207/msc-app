import streamlit as st
from openai import OpenAI
import json
import re
import numpy as np
import msc_config as config
import msc_db as db

# 🛑 AI 初始化
try:
    client_ai = OpenAI(api_key=st.secrets["API_KEY"], base_url=st.secrets["BASE_URL"])
    TARGET_MODEL = st.secrets["MODEL_NAME"]
except Exception as e: st.error(f"AI Config Error: {e}"); st.stop()

# --- 核心算法 ---
def get_embedding(text):
    return np.random.rand(1536).tolist()

def cosine_similarity(v1, v2):
    vec1, vec2 = np.array(v1), np.array(v2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)) if np.linalg.norm(vec1) > 0 else 0

def calculate_MLS(vec_a, vec_b, topic_a, topic_b, meaning_a, meaning_b):
    sim_vec = cosine_similarity(vec_a, vec_b)
    # 简化版 MLS，主要依赖向量相似度
    return sim_vec

def find_resonance(current_vector, current_user, current_data):
    if not current_vector: return None
    others = db.get_resonance_candidates(current_user)
    if not others: return None
    
    best_match, highest_score = None, 0
    for row in others:
        if row['vector']:
            try:
                score = cosine_similarity(current_vector, json.loads(row['vector']))
                if score > config.RESONANCE_THRESHOLD and score > highest_score:
                    highest_score = score
                    best_match = {"user": row['username'], "content": row['content'], "score": round(score * 100, 1)}
            except: continue
    return best_match

def calculate_rank(radar_data):
    if not radar_data: return "青铜", "🥉"
    if isinstance(radar_data, str): radar_data = json.loads(radar_data)
    total = sum(radar_data.values())
    if total < 25: return "青铜", "🥉"
    elif total < 38: return "黄金", "🥇"
    elif total < 54: return "钻石", "💠"
    else: return "王者", "👑"

# --- LLM 调用 ---
def call_ai_api(prompt):
    try:
        response = client_ai.chat.completions.create(
            model=TARGET_MODEL,
            messages=[{"role": "system", "content": "Output valid JSON only. No markdown."}, {"role": "user", "content": prompt}],
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
    try:
        api_messages = [{"role": "system", "content": config.PROMPT_CHATBOT}]
        for msg in history_messages: 
            if msg['role'] in ['user', 'assistant']:
                api_messages.append({"role": msg["role"], "content": msg["content"]})
        return client_ai.chat.completions.create(model=TARGET_MODEL, messages=api_messages, temperature=0.8, stream=True)
    except Exception as e: return str(e)

def analyze_meaning_background(text):
    prompt = f"{config.PROMPT_ANALYST}\n用户输入: \"{text}\""
    res = call_ai_api(prompt)
    if res.get("valid", False):
        c = res.get('c_score', 0)
        n = res.get('n_score', 0)
        m = c * n * 2
        res['m_score'] = m
        if m < config.MEANING_THRESHOLD: res["valid"] = False
    return res

def generate_daily_question(username, radar_data):
    recent = db.get_all_nodes_for_map(username)
    ctx = ""
    if recent: ctx = f"关注点：{[n['care_point'] for n in recent[-3:]]}"
    prompt = f"{config.PROMPT_DAILY}\n用户：{json.dumps(radar_data)}。{ctx}。输出 JSON: {{ 'question': '...' }}"
    res = call_ai_api(prompt)
    return res.get("question", "今天感觉如何？")

def analyze_persona_report(radar_data):
    prompt = f"{config.PROMPT_PERSONA}\n雷达数据：{json.dumps(radar_data)}。输出 JSON: {{ 'static_portrait': '...', 'dynamic_growth': '...' }}"
    return call_ai_api(prompt)

def get_ai_interjection(history_text):
    # 使用简单 Prompt
    prompt = f"作为观察者评论这段对话：\n{history_text}\n简短幽默。直接返回文本。"
    try:
        response = client_ai.chat.completions.create(model=TARGET_MODEL, messages=[{"role": "user", "content": prompt}], temperature=0.9)
        return response.choices[0].message.content
    except: return None
