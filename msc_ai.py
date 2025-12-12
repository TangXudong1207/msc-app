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
except: st.stop()

# --- 核心算法 ---

def get_embedding(text):
    # 模拟向量 (实际应调用 API)
    return np.random.rand(1536).tolist()

def cosine_similarity(v1, v2):
    vec1, vec2 = np.array(v1), np.array(v2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)) if np.linalg.norm(vec1) > 0 else 0

# 🌟 核心修复：补全 calculate_rank 函数 (main.py 在找它)
def calculate_rank(radar_data):
    if not radar_data: return "MSC 公民", "🥉"
    
    # 兼容处理：如果是字符串就转字典
    if isinstance(radar_data, str): 
        try:
            radar_data = json.loads(radar_data)
        except:
            return "MSC 公民", "🥉"
            
    # 安全求和
    try:
        total = sum(float(v) for v in radar_data.values())
    except:
        total = 0
    
    # 段位逻辑
    if total < 25: return "观察者", "🥉"
    elif total < 38: return "探索者", "🥈"
    elif total < 54: return "构建者", "💎"
    else: return "领航员", "👑"

# 🌟 核心修复：补全 find_resonance
def find_resonance(current_vector, current_user, current_data):
    if not current_vector: return None
    # 从数据库获取候选人
    others = db.get_resonance_candidates(current_user)
    if not others: return None
    
    best_match, highest_score = None, 0
    
    for row in others:
        if row['vector']:
            try:
                o_vec = json.loads(row['vector'])
                # 简单计算相似度
                score = cosine_similarity(current_vector, o_vec)
                
                if score > config.RESONANCE_THRESHOLD and score > highest_score:
                    highest_score = score
                    best_match = {
                        "user": row['username'], 
                        "content": row['content'], 
                        "score": round(score * 100, 1)
                    }
            except: continue
    return best_match

# 🌟 核心修复：补全 update_user_radar
def update_user_radar(username, input_scores):
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
            updated[k] = round(old_val * 0.9 + new_val * 0.1, 2)
            
        db.update_radar_profile_db(username, json.dumps(updated))
    except: pass

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

# 兼容旧函数名
analyze_meaning_engine = analyze_meaning_background

def generate_daily_question(username, radar_data):
    try:
        recent = db.get_user_nodes(username)
        ctx = ""
        if recent: 
            last_3 = recent[-3:]
            ctx = f"关注点：{[n['care_point'] for n in last_3]}"
    except: ctx = ""

    radar_str = json.dumps(radar_data, ensure_ascii=False)
    prompt = f"{config.PROMPT_DAILY}\n用户：{radar_str}。{ctx}。输出 JSON: {{ 'question': '...' }}"
    res = call_ai_api(prompt)
    return res.get("question", "今天，什么事情让你感到'活着'？")

def analyze_persona_report(radar_data):
    prompt = f"{config.PROMPT_PERSONA}\n数据：{json.dumps(radar_data)}。输出 JSON: {{ 'static_portrait': '...', 'dynamic_growth': '...' }}"
    return call_ai_api(prompt)

def get_ai_interjection(history_text):
    prompt = f"{config.PROMPT_OBSERVER}\n{history_text}\n输出: 纯文本"
    try: return client_ai.chat.completions.create(model=TARGET_MODEL, messages=[{"role": "user", "content": prompt}], temperature=0.9).choices[0].message.content
    except: return None
