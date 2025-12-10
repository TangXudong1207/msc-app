import streamlit as st
from openai import OpenAI
from supabase import create_client, Client
from streamlit_echarts import st_echarts
import json
import re
import hashlib
import time
import numpy as np
from datetime import datetime

# ==========================================
# 🛑 核心配置区
# ==========================================

try:
    client = OpenAI(
        api_key=st.secrets["API_KEY"],
        base_url=st.secrets["BASE_URL"]
    )
    TARGET_MODEL = st.secrets["MODEL_NAME"]

    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

except Exception as e:
    st.error(f"🚨 配置错误: {str(e)}")
    st.stop()

# ==========================================

# --- 🛠️ 基础设施 ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def add_user(username, password, nickname):
    try:
        res = supabase.table('users').select("*").eq('username', username).execute()
        if len(res.data) > 0: return False
        # 初始化雷达图：所有维度默认 3.0 分 (满分10分)
        default_radar = {
            "Care": 3.0, "Curiosity": 3.0, "Reflection": 3.0, "Coherence": 3.0,
            "Empathy": 3.0, "Agency": 3.0, "Aesthetic": 3.0
        }
        data = {
            "username": username, 
            "password": make_hashes(password), 
            "nickname": nickname,
            "radar_profile": json.dumps(default_radar)
        }
        supabase.table('users').insert(data).execute()
        return True
    except: return False

def login_user(username, password):
    try:
        hashed_pw = make_hashes(password)
        res = supabase.table('users').select("*").eq('username', username).eq('password', hashed_pw).execute()
        return res.data
    except: return []

def get_user_profile(username):
    """获取用户信息，包括雷达数据"""
    try:
        res = supabase.table('users').select("nickname, radar_profile").eq('username', username).execute()
        if res.data:
            return res.data[0]
    except: pass
    return {"nickname": username, "radar_profile": None}

def update_radar_score(username, new_scores):
    """
    元人性生长算法：
    新值 = 旧值 * 0.95 + 本次得分 * 0.05
    让雷达图呈现“缓慢生长”的生物特性，而不是剧烈跳动。
    """
    try:
        # 1. 获取旧数据
        user_data = get_user_profile(username)
        current_radar = user_data.get('radar_profile')
        
        if not current_radar:
            current_radar = {k: 3.0 for k in new_scores.keys()}
        elif isinstance(current_radar, str):
            current_radar = json.loads(current_radar)
            
        # 2. 计算进化
        alpha = 0.05 # 学习率，越小越稳定
        updated_radar = {}
        for key in new_scores:
            old_val = float(current_radar.get(key, 3.0))
            input_val = float(new_scores.get(key, 0))
            # 只有当本次输入在该维度有显著表现(>1)时才更新，避免被无效对话稀释
            if input_val > 1.0:
                updated_val = old_val * (1 - alpha) + input_val * alpha
                updated_radar[key] = round(min(10.0, updated_val), 2)
            else:
                updated_radar[key] = old_val # 保持不变

        # 3. 存回数据库
        supabase.table('users').update({"radar_profile": json.dumps(updated_radar)}).eq("username", username).execute()
        return updated_radar
    except Exception as e:
        print(f"Radar update error: {e}")
        return None

# --- 💾 数据库操作 ---
def save_chat(username, role, content):
    try:
        data = {"username": username, "role": role, "content": content, "is_deleted": False}
        supabase.table('chats').insert(data).execute()
    except: pass

def get_active_chats(username, limit=50):
    try:
        res = supabase.table('chats').select("*").eq('username', username).eq('is_deleted', False).order('id', desc=True).limit(limit).execute()
        return list(reversed(res.data))
    except: return []

def soft_delete_chat_and_node(chat_id, content, username):
    try:
        supabase.table('chats').update({"is_deleted": True}).eq("id", chat_id).execute()
        supabase.table('nodes').update({"is_deleted": True}).eq("username", username).eq("content", content).execute()
        return True
    except: return False

def save_node(username, content, data, mode, vector):
    try:
        logic = data.get('logic_score')
        if logic is None: logic = 0.5
        keywords = data.get('keywords', [])
        
        insert_data = {
            "username": username, "content": content,
            "care_point": data.get('care_point', '未命名'),
            "meaning_layer": data.get('meaning_layer', '暂无结构'),
            "insight": data.get('insight', '生成中断'),
            "mode": mode, "vector": json.dumps(vector),
            "logic_score": logic, "is_deleted": False,
            "keywords": json.dumps(keywords)
        }
        supabase.table('nodes').insert(insert_data).execute()
        return True
    except: return False

def get_active_nodes_map(username):
    try:
        res = supabase.table('nodes').select("*").eq('username', username).eq('is_deleted', False).execute()
        return {node['content']: node for node in res.data}
    except: return {}

def get_all_nodes_for_map(username):
    try:
        res = supabase.table('nodes').select("*").eq('username', username).eq('is_deleted', False).order('id', desc=False).execute()
        return res.data
    except: return []

# --- 🧠 AI 核心 (元人性升级版) ---
def call_ai_api(prompt):
    try:
        response = client.chat.completions.create(
            model=TARGET_MODEL,
            messages=[{"role": "system", "content": "You are a profound philosopher. Output valid JSON only. Do not use markdown blocks."}, {"role": "user", "content": prompt}],
            temperature=0.7, stream=False, response_format={"type": "json_object"} 
        )
        content = response.choices[0].message.content
        try:
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match: return json.loads(match.group(0))
            else: return json.loads(content)
        except: return {"error": True, "msg": "JSON解析失败"}
    except Exception as e: return {"error": True, "msg": str(e)}

def get_embedding(text):
    return np.random.rand(1536).tolist()

def get_normal_response(history_messages):
    try:
        api_messages = [{"role": "system", "content": "你是温暖的对话伙伴。"}]
        for msg in history_messages:
            api_messages.append({"role": msg["role"], "content": msg["content"]})
        response = client.chat.completions.create(
            model=TARGET_MODEL, messages=api_messages, temperature=0.8, stream=True 
        )
        return response
    except Exception as e: return f"Error: {e}"

def analyze_meaning_background(text):
    # 🌟 核心升级：增加元人性雷达评分
    prompt = f"""
    分析输入："{text}"
    
    1. 判断是否有深层意义 (valid: true/false)。
    2. 提取 MSC 结构 (care_point, meaning_layer, insight)。
    
    3. 【元人性评分 (Meta-Humanity Radar)】
    请对这段话背后的生成动机进行评分 (0-10分)：
    - Care (在乎力): 情感投入、责任感、对价值的执着。
    - Curiosity (探索欲): 对未知的追问、发现冲动。
    - Reflection (反思力): 质疑自身、向内审视。
    - Coherence (结构化): 逻辑清晰、体系化程度。
    - Empathy (共感力): 对他人或世界的共情。
    - Agency (行动力): 将意义转化为行动的倾向。
    - Aesthetic (审美力): 对和谐、美感、诗意的敏锐度。
    
    返回 JSON:
    {{
        "valid": true,
        "care_point": "...",
        "meaning_layer": "...",
        "insight": "...",
        "logic_score": 0.8,
        "keywords": ["tag1", "tag2"],
        "radar_scores": {{
            "Care": 8, "Curiosity": 5, "Reflection": 7, 
            "Coherence": 6, "Empathy": 4, "Agency": 2, "Aesthetic": 3
        }}
    }}
    """
    return call_ai_api(prompt)

def generate_fusion(node_a_content, node_b_content):
    prompt = f"""
    任务：基于 Deep Meaning 共鸣进行融合。
    A: "{node_a_content}"
    B: "{node_b_content}"
    返回 JSON: {{ "care_point": "...", "meaning_layer": "...", "insight": "..." }}
    """
    return call_ai_api(prompt)

def cosine_similarity(v1, v2):
    vec1, vec2 = np.array(v1), np.array(v2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)) if np.linalg.norm(vec1) > 0 else 0

def find_resonance(current_vector, current_user):
    if not current_vector: return None
    try:
        res = supabase.table('nodes').select("*").neq('username', current_user).eq('is_deleted', False).execute()
        others = res.data
        best_match, highest_score = None, 0
        for row in others:
            if row['vector']:
                try:
                    score = cosine_similarity(current_vector, json.loads(row['vector']))
                    if score > 0.75 and score > highest_score:
                        highest_score = score
                        best_match = {"user": row['username'], "content": row['content'], "score": round(score * 100, 1)}
                except: continue
        return best_match
    except: return None

# --- 🎨 渲染函数 ---

def render_radar_chart(profile_data):
    """渲染元人性雷达图"""
    if not profile_data or not profile_data.get('radar_profile'):
        scores = [3,3,3,3,3,3,3] # 默认值
    else:
        # 处理 JSON 字符串
        radar_json = profile_data['radar_profile']
        if isinstance(radar_json, str):
            radar_dict = json.loads(radar_json)
        else:
            radar_dict = radar_json
            
        # 提取7个维度的值
        keys = ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]
        scores = [radar_dict.get(k, 3.0) for k in keys]

    option = {
        "backgroundColor": "transparent",
        "radar": {
            "indicator": [
                {"name": "Care\n在乎", "max": 10},
                {"name": "Curiosity\n探索", "max": 10},
                {"name": "Reflection\n反思", "max": 10},
                {"name": "Coherence\n结构", "max": 10},
                {"name": "Empathy\n共感", "max": 10},
                {"name": "Agency\n行动", "max": 10},
                {"name": "Aesthetic\n审美", "max": 10}
            ],
            "splitNumber": 4,
            "axisName": {"color": "#bbb"},
            "splitLine": {"lineStyle": {"color": ["#333", "#444", "#555", "#666"]}},
            "splitArea": {"show": False}
        },
        "series": [{
            "type": "radar",
            "data": [{
                "value": scores,
                "name": "Meta-Humanity",
                "areaStyle": {"color": "rgba(0, 255, 242, 0.4)"}, # 赛博青
                "lineStyle": {"color": "#00fff2", "width": 2},
                "itemStyle": {"color": "#fff"}
            }]
        }]
    }
    st_echarts(options=option, height="300px")

def render_cyberpunk_map(nodes, height="250px", is_fullscreen=False):
    if not nodes: return
    graph_nodes, graph_links = [], []
    symbol_base = 30 if is_fullscreen else 15
    repulsion = 1000 if is_fullscreen else 300

    for i, node in enumerate(nodes):
        logic = node.get('logic_score', 0.5)
        graph_nodes.append({
            "name": str(node['id']),
            "id": str(node['id']),
            "symbolSize": symbol_base * (0.8 + logic),
            "value": node['care_point'],
            "label": {"show": is_fullscreen, "formatter": node['care_point'][:5], "color": "#fff"},
            "vector": json.loads(node['vector']) if node.get('vector') else None,
            "keywords": json.loads(node['keywords']) if node.get('keywords') else []
        })

    node_count = len(graph_nodes)
    for i in range(node_count):
        for j in range(i + 1, node_count):
            na, nb = graph_nodes[i], graph_nodes[j]
            if na['vector'] and nb['vector']:
                m_inter = len(set(na['keywords']).intersection(set(nb['keywords'])))
                m_union = len(set(na['keywords']).union(set(nb['keywords'])))
                m_sim = m_inter / m_union if m_union > 0 else 0
                vec_sim = cosine_similarity(na['vector'], nb['vector'])
                score = 0.6 * m_sim + 0.4 * vec_sim
                if score > 0.8:
                    graph_links.append({"source": na['name'], "target": nb['name'], "lineStyle": {"width": 2, "color": "#00fff2"}})
                elif score > 0.6:
                    graph_links.append({"source": na['name'], "target": nb['name'], "lineStyle": {"width": 0.5, "color": "#555", "type": "dashed"}})

    option = {
        "backgroundColor": "#0e1117",
        "series": [{
            "type": "graph", "layout": "force", "data": graph_nodes, "links": graph_links,
            "roam": True, "force": {"repulsion": repulsion, "gravity": 0.05},
            "itemStyle": {"shadowBlur": 10, "shadowColor": "rgba(255, 255, 255, 0.5)"}
        }]
    }
    st_echarts(options=option, height=height)

@st.dialog("🔭 浩荡宇宙", width="large")
def view_fullscreen_map(nodes):
    render_cyberpunk_map(nodes, height="600px", is_fullscreen=True)

# ==========================================
# 🖥️ 主程序
# ==========================================

st.set_page_config(page_title="MSC v20.0 Radar", layout="wide", initial_sidebar_state="expanded")

if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌌 MSC")
    # Login... (omitted for brevity, same as v19)
    tab1, tab2 = st.tabs(["登录", "注册"])
    with tab1:
        u = st.text_input("用户名")
        p = st.text_input("密码", type='password')
        if st.button("登录", use_container_width=True):
            res = login_user(u, p)
            if res and len(res) > 0:
                st.session_state.logged_in = True
                st.session_state.username = u
                st.session_state.nickname = res[0]['nickname']
                st.session_state.messages = [] 
                st.rerun()
            else: st.error("错误")
    with tab2:
        nu = st.text_input("新用户名")
        np_pass = st.text_input("新密码", type='password')
        nn = st.text_input("昵称")
        if st.button("注册", use_container_width=True):
            if add_user(nu, np_pass, nn): st.success("成功")
            else: st.error("失败")

else:
    chat_history = get_active_chats(st.session_state.username)
    nodes_map = get_active_nodes_map(st.session_state.username)
    all_nodes_list = get_all_nodes_for_map(st.session_state.username)
    # 获取用户画像（包含雷达数据）
    user_profile = get_user_profile(st.session_state.username)

    with st.sidebar:
        st.write(f"👋 **{st.session_state.nickname}**")
        
        # 🌟 核心新功能：元人性雷达图
        st.caption("🧬 元人性雷达 (Meta-Humanity Radar)")
        render_radar_chart(user_profile)
        
        c1, c2 = st.columns(2)
        if c1.button("🗑️ 回收站"): st.toast("功能维护中...")
        if c2.button("退出"): st.session_state.logged_in = False; st.rerun()
        
        st.divider()
        st.caption("🌐 思想星云")
        render_cyberpunk_map(all_nodes_list, height="200px")
        if st.button("🔭 全屏星云", use_container_width=True): view_fullscreen_map(all_nodes_list)

    st.subheader("💬 意义流")
    
    for msg in chat_history:
        col_chat, col_node = st.columns([0.65, 0.35], gap="small")
        with col_chat:
            c_msg, c_del = st.columns([0.9, 0.1])
            with c_msg:
                with st.chat_message(msg['role']): st.markdown(msg['content'])
            with c_del:
                if msg['role'] == 'user':
                    if st.button("✕", key=f"del_{msg['id']}"):
                        if soft_delete_chat_and_node(msg['id'], msg['content'], st.session_state.username): st.rerun()
            
            if msg.get('role') == 'assistant' and "🧬 融合成功" in msg['content']:
                 pass 

        with col_node:
            if msg['role'] == 'user' and msg['content'] in nodes_map:
                node = nodes_map[msg['content']]
                with st.expander(f"✨ {node['care_point']}", expanded=False):
                    st.caption(f"MLS Logic: {node.get('logic_score', 0.5)}")
                    st.markdown(f"**Insight:** {node['insight']}")
                    st.markdown(f"**Structure:**\n{node['meaning_layer']}")
                    st.caption(f"Time: {node['created_at'][:16]}")

    if prompt := st.chat_input("输入..."):
        save_chat(st.session_state.username, "user", prompt)
        
        full_history = chat_history + [{'role':'user', 'content':prompt}]
        stream = get_normal_response(full_history)
        reply_text = st.write_stream(stream)
        save_chat(st.session_state.username, "assistant", reply_text)
        
        with st.spinner("⚡ 意义判别 & 雷达扫描..."):
            analysis = analyze_meaning_background(prompt)
            if analysis.get("valid", False):
                vec = get_embedding(prompt)
                save_node(st.session_state.username, prompt, analysis, "日常", vec)
                
                # 🌟 更新用户的雷达数据
                if "radar_scores" in analysis:
                    update_radar_score(st.session_state.username, analysis["radar_scores"])
                
                match = find_resonance(vec, st.session_state.username)
                if match:
                    st.toast(f"🔔 发现深度共鸣！", icon="⚡")
        
        st.rerun()
