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

# --- 向量算法 ---
def get_embedding(text):
    # 模拟向量 (实际应调用 API)
    return np.random.rand(1536).tolist()

def cosine_similarity(v1, v2):
    vec1, vec2 = np.array(v1), np.array(v2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)) if np.linalg.norm(vec1) > 0 else 0

# --- 核心逻辑 v70.0 ---

def calculate_novelty_relative(current_vec, username):
    """
    计算相对新颖度：1 - 与过去最近10个节点的平均相似度
    """
    recent_nodes = db.get_user_nodes(username) # 假设返回按时间倒序
    if not recent_nodes: return 1.0 # 没历史，绝对新颖
    
    # 取最近 10 条
    check_list = recent_nodes[-10:] if len(recent_nodes) > 10 else recent_nodes
    sims = []
    for node in check_list:
        if node.get('vector'):
            try:
                # 简单模拟，实际应用真实向量计算
                # 这里为了演示逻辑，假设 get_embedding 返回的是真实可比的
                # 由于现在 get_embedding 是随机的，所以 sim 会很低，Novelty 会很高
                # 生产环境需接真实 Embedding API
                v_old = json.loads(node['vector'])
                sims.append(cosine_similarity(current_vec, v_old))
            except: pass
            
    if not sims: return 1.0
    avg_sim = sum(sims) / len(sims)
    return 1.0 - avg_sim # 越不相似，新颖度越高

def calculate_m_score(ai_data, n_relative):
    """
    M_score = 0.35*C_emotion + 0.25*C_self + 0.20*N_abstract + 0.20*N_relative
    """
    c_emo = ai_data.get('score_emotion', 0)
    c_self = ai_data.get('score_self', 0)
    n_abs = ai_data.get('score_abstract', 0)
    
    w = config.W_MEANING
    m_score = (w['C_emotion'] * c_emo) + \
              (w['C_self'] * c_self) + \
              (w['N_abstract'] * n_abs) + \
              (w['N_relative'] * n_relative)
    return m_score

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

def analyze_meaning_engine(text, username):
    # 1. 构造 Prompt
    prompt = f"""
    {config.PROMPT_ANALYST}
    用户输入："{text}"
    
    返回 JSON:
    {{
        "score_emotion": 0.0-1.0,
        "score_self": 0.0-1.0,
        "score_abstract": 0.0-1.0,
        "is_existential": true/false,
        "care_point": "...", "meaning_layer": "...", "insight": "...",
        "keywords": ["A", "B", "C"],
        "radar_scores": {{ "Care": 5, "Curiosity": 5, "Reflection": 5, "Coherence": 5, "Empathy": 5, "Agency": 5, "Aesthetic": 5 }}
    }}
    """
    
    # 2. AI 分析
    ai_res = call_ai_api(prompt)
    if "error" in ai_res: return ai_res

    # 3. 计算相对新颖度 (Python端计算)
    current_vec = get_embedding(text)
    n_relative = calculate_novelty_relative(current_vec, username)
    
    # 4. 综合计算 M_score
    m_score = calculate_m_score(ai_res, n_relative)
    
    # 5. 判定等级
    status = "NonMeaning"
    if m_score >= config.LEVELS['Core']: status = "Core"
    elif m_score >= config.LEVELS['Strong']: status = "Strong"
    elif m_score >= config.LEVELS['Weak']: status = "Weak"
    
    # 6. 只有 Weak 以上才 Valid
    ai_res['valid'] = (m_score >= config.LEVELS['NonMeaning'])
    ai_res['m_score'] = m_score
    ai_res['status'] = status
    ai_res['vector'] = current_vec
    
    return ai_res

# ... (其他函数保持原样: get_normal_response, generate_daily, etc.) ...
def get_normal_response(history_messages):
    try:
        api_messages = [{"role": "system", "content": config.PROMPT_CHATBOT}]
        for msg in history_messages: api_messages.append({"role": msg["role"], "content": msg["content"]})
        return client_ai.chat.completions.create(model=TARGET_MODEL, messages=api_messages, temperature=0.8, stream=True)
    except Exception as e: return str(e)

def generate_daily_question(username, radar_data):
    ctx = ""
    # Simplified context fetching
    prompt = f"{config.PROMPT_DAILY}\n用户：{json.dumps(radar_data)}。{ctx}。输出 JSON: {{ 'question': '...' }}"
    res = call_ai_api(prompt)
    return res.get("question", "今天感觉如何？")

def analyze_persona_report(radar_data):
    prompt = f"{config.PROMPT_PERSONA}\n数据：{json.dumps(radar_data)}。输出 JSON: {{ 'static_portrait': '...', 'dynamic_growth': '...' }}"
    return call_ai_api(prompt)

def get_ai_interjection(history_text):
    prompt = f"{config.PROMPT_OBSERVER}\n{history_text}\n输出: 纯文本"
    try: return client_ai.chat.completions.create(model=TARGET_MODEL, messages=[{"role": "user", "content": prompt}], temperature=0.9).choices[0].message.content
    except: return None

def generate_fusion(a, b): return call_ai_api(f"融合 {a} 和 {b}。JSON: {{'care_point':'...', 'meaning_layer':'...', 'insight':'...'}}")
def find_resonance(v, u, d): return None # 占位，逻辑移到 lib
def calculate_rank(d): return "MSC 公民", "🥉" # 占位
