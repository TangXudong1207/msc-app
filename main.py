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

# --- 🏆 游戏化：段位计算系统 ---
def calculate_rank(radar_data):
    """
    根据雷达图总分计算段位
    7个维度，每个维度最高10分，满分70分。
    """
    if not radar_data: return "倔强青铜 III", "🥉"
    
    total_score = sum(radar_data.values())
    
    # 段位阈值设计
    if total_score < 25: return "倔强青铜", "🥉"
    elif total_score < 30: return "秩序白银", "🥈"
    elif total_score < 38: return "荣耀黄金", "🥇"
    elif total_score < 46: return "尊贵铂金", "💎"
    elif total_score < 54: return "永恒钻石", "💠"
    elif total_score < 62: return "至尊星耀", "✨"
    else: return "最强王者", "👑"

# --- 🛠️ 基础设施 ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text: return True
    return False

def add_user(username, password, nickname):
    try:
        res = supabase.table('users').select("*").eq('username', username).execute()
        if len(res.data) > 0: return False
        # 初始化：全部 3.0 分
        default_radar = {
            "Care": 3.0, "Curiosity": 3.0, "Reflection": 3.0, "Coherence": 3.0,
            "Empathy": 3.0, "Agency": 3.0, "Aesthetic": 3.0
        }
        data = {"username": username, "password": make_hashes(password), "nickname": nickname, "radar_profile": json.dumps(default_radar)}
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
    try:
        res = supabase.table('users').select("nickname, radar_profile").eq('username', username).execute()
        if res.data: return res.data[0]
    except: pass
    return {"nickname": username, "radar_profile": None}

def update_radar_score(username, new_scores):
    try:
        user_data = get_user_profile(username)
        current_radar = user_data.get('radar_profile')
        if not current_radar:
            current_radar = {k: 3.0 for k in new_scores.keys()}
        elif isinstance(current_radar, str):
            current_radar = json.loads(current_radar)
            
        alpha = 0.08 # 稍微调高学习率，让升级快一点点
        updated_radar = {}
        for key in new_scores:
            old_val = float(current_radar.get(key, 3.0))
            input_val = float(new_scores.get(key, 0))
            if input_val > 1.0:
                updated_val = old_val * (1 - alpha) + input_val * alpha
                updated_radar[key] = round(min(10.0, updated_val), 2)
            else:
                updated_radar[key] = old_val

        supabase.table('users').update({"radar_profile": json.dumps(updated_radar)}).eq("username", username).execute()
        return updated_radar
    except Exception as e: return None

# --- 🧠 AI 核心 ---
def call_ai_api(prompt):
    try:
        response = client.chat.completions.create(
            model=TARGET_MODEL,
            messages=[{"role": "system", "content": "Output valid JSON only."}, {"role": "user", "content": prompt}],
            temperature=0.7, stream=False, response_format={"type": "json_object"} 
        )
        content = response.choices[0].message.content
        try:
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match: return json.loads(match.group(0))
            else: return json.loads(content)
        except: return {"error": True, "msg": "JSON解析失败"}
    except Exception as e: return {"error": True, "msg": str(e)}

def analyze_persona_report(radar_data):
    """
    生成人物画像分析报告
    """
    radar_str = json.dumps(radar_data, ensure_ascii=False)
    prompt = f"""
    任务：基于用户的元人性雷达数据，生成一份深度人物画像。
    雷达数据：{radar_str}
    
    请输出 JSON 格式：
    {{
        "static_portrait": "静态画像：用心理学和哲学语言描述该用户的核心人格底色、优势与盲点...",
        "dynamic_growth": "动态成长：分析该用户目前的进化趋势，并给出下一步提升段位的具体建议..."
    }}
    """
    return call_ai_api(prompt)

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
    prompt = f"""
    分析输入："{text}"
    1. 判断是否生成节点。
    2. 提取 MSC 结构。
    3. 【雷达评分】请对这段话体现的维度打分(0-10)：
       Care, Curiosity, Reflection, Coherence, Empathy, Agency, Aesthetic。
    
    返回 JSON:
    {{
        "valid": true,
        "care_point": "...", "meaning_layer": "...", "insight": "...",
        "logic_score": 0.8, "keywords": [],
        "radar_scores": {{ "Care": 7, "Curiosity": 5, ... }}
    }}
    """
    return call_ai_api(prompt)

def generate_fusion(node_a_content, node_b_content):
    prompt = f"""
    融合 A: "{node_a_content}" B: "{node_b_content}"。
    返回 JSON: {{ "care_point": "...", "meaning_layer": "...", "insight": "..." }}
    """
    return call_ai_api(prompt)

# --- 数据库与算法 (保持不变) ---
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
        logic = data.get('logic_score', 0.5)
        keywords = data.get('keywords', [])
        insert_data = {
            "username": username, "content": content,
            "care_point": data.get('care_point', '未命名'),
            "meaning_layer": data.get('meaning_layer', '暂无结构'),
            "insight": data.get('insight', '生成中断'),
            "mode": mode, "vector": json.dumps(vector),
            "logic_score": logic, "keywords": json.dumps(keywords), "is_deleted": False
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

def cosine_similarity(v1, v2):
    vec1, vec2 = np.array(v1), np.array(v2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)) if np.linalg.norm(vec1) > 0 else 0

def find_resonance(current_vector, current_user):
    if not current_vector: return None
    try:
        res = supabase.table('nodes').select("*").neq('username', current_user).eq('is_deleted', False).execute()
        best_match, highest = None, 0
        for row in res.data:
            if row['vector']:
                try:
                    score = cosine_similarity(current_vector, json.loads(row['vector']))
                    if score > 0.75 and score > highest:
                        highest = score
                        best_match = {"user": row['username'], "content": row['content'], "score": round(score * 100, 1)}
                except: continue
        return best_match
    except: return None

# --- 🎨 渲染函数 ---

def render_radar_chart(radar_dict, height="300px"):
    keys = ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]
    scores = [radar_dict.get(k, 3.0) for k in keys]
    
    option = {
        "backgroundColor": "transparent",
        "radar": {
            "indicator": [{"name": k, "max": 10} for k in keys],
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
                "areaStyle": {"color": "rgba(0, 255, 242, 0.4)"},
                "lineStyle": {"color": "#00fff2", "width": 2},
                "itemStyle": {"color": "#fff"}
            }]
        }]
    }
    st_echarts(options=option, height=height)

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

# --- 🖥️ 弹窗 Dialog ---
@st.dialog("🔭 浩荡宇宙", width="large")
def view_fullscreen_map(nodes):
    render_cyberpunk_map(nodes, height="600px", is_fullscreen=True)

@st.dialog("🧬 元人性进化面板", width="large")
def view_radar_details(radar_dict):
    rank, icon = calculate_rank(radar_dict)
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown(f"### {icon} {rank}")
        total = sum(radar_dict.values())
        st.metric("总灵力值", f"{total:.1f} / 70")
        st.caption("随你的思想深度动态生长")
    
    with c2:
        render_radar_chart(radar_dict, height="250px")

    st.divider()
    st.subheader("📊 维度解析")
    
    cols = st.columns(4)
    keys = list(radar_dict.keys())
    for i, k in enumerate(keys):
        with cols[i % 4]:
            val = radar_dict[k]
            st.metric(k, f"{val:.1f}", delta=None)
            st.progress(val / 10)

    st.markdown("---")
    
    # 🔥 AI 画像分析按钮
    if st.button("🤖 生成人物画像分析", type="primary", use_container_width=True):
        with st.spinner("DeepSeek 正在扫描您的灵魂结构..."):
            analysis = analyze_persona_report(radar_dict)
            if "error" not in analysis:
                st.success("分析完成")
                st.markdown(f"### 🖼️ 静态画像")
                st.write(analysis.get('static_portrait', '无数据'))
                st.markdown(f"### 🚀 动态成长")
                st.write(analysis.get('dynamic_growth', '无数据'))
            else:
                st.error("分析失败，请重试")

# ==========================================
# 🖥️ 主程序
# ==========================================

st.set_page_config(page_title="MSC v21.0 Rank", layout="wide", initial_sidebar_state="expanded")

if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌌 MSC")
    # Login UI (omitted)
    tab1, tab2 = st.tabs(["登录", "注册"])
    with tab1:
        u = st.text_input("用户名")
        p = st.text_input("密码", type='password')
        if st.button("登录"):
            res = login_user(u, p)
            if res:
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
        if st.button("注册"):
            if add_user(nu, np_pass, nn): st.success("成功")
            else: st.error("失败")

else:
    chat_history = get_active_chats(st.session_state.username)
    nodes_map = get_active_nodes_map(st.session_state.username)
    all_nodes_list = get_all_nodes_for_map(st.session_state.username)
    user_profile = get_user_profile(st.session_state.username)
    
    # 处理雷达数据
    raw_radar = user_profile.get('radar_profile')
    if isinstance(raw_radar, str): radar_dict = json.loads(raw_radar)
    elif isinstance(raw_radar, dict): radar_dict = raw_radar
    else: radar_dict = {k:3.0 for k in ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]}

    with st.sidebar:
        # 🌟 游戏化入口
        rank_name, rank_icon = calculate_rank(radar_dict)
        st.markdown(f"## {rank_icon} {st.session_state.nickname}")
        st.caption(f"当前段位: **{rank_name}**")
        
        # 雷达图 (点击放大)
        render_radar_chart(radar_dict, height="200px")
        if st.button("📈 查看进化面板", use_container_width=True):
            view_radar_details(radar_dict)
            
        st.divider()
        c1, c2 = st.columns(2)
        if c1.button("🗑️ 回收站"): st.toast("功能维护中...")
        if c2.button("退出"): st.session_state.logged_in = False; st.rerun()
        st.divider()
        render_cyberpunk_map(all_nodes_list, height="200px")
        if st.button("🔭 全屏星云", use_container_width=True): view_fullscreen_map(all_nodes_list)

    st.subheader("💬 意义流")
    
    for msg in chat_history:
        col_chat, col_node = st.columns([0.65, 0.35], gap="small")
        with col_chat:
            c_msg, c_del = st.columns([0.9, 0.1])
            with c_msg:
                with st.chat_message(msg['role']): st.markdown(msg['content'], unsafe_allow_html=True)
            with c_del:
                if msg['role'] == 'user':
                    if st.button("✕", key=f"del_{msg['id']}"):
                        if soft_delete_chat_and_node(msg['id'], msg['content'], st.session_state.username): st.rerun()
            if msg.get('role') == 'assistant' and "🧬 融合成功" in msg['content']: pass 

        with col_node:
            if msg['role'] == 'user' and msg['content'] in nodes_map:
                node = nodes_map[msg['content']]
                with st.expander(f"✨ {node['care_point']}", expanded=False):
                    st.caption(f"Logic: {node.get('logic_score', 0.5)}")
                    st.markdown(f"**Insight:** {node['insight']}")
                    st.markdown(f"**Structure:**\n{node['meaning_layer']}")
                    st.caption(f"Time: {node['created_at'][:16]}")

    if prompt := st.chat_input("输入..."):
        save_chat(st.session_state.username, "user", prompt)
        
        full_history = chat_history + [{'role':'user', 'content':prompt}]
        stream = get_normal_response(full_history)
        reply_text = st.write_stream(stream)
        save_chat(st.session_state.username, "assistant", reply_text)
        
        with st.spinner("⚡ 意义判别..."):
            analysis = analyze_meaning_background(prompt)
            if analysis.get("valid", False):
                vec = get_embedding(prompt)
                save_node(st.session_state.username, prompt, analysis, "日常", vec)
                
                # 更新雷达并计算新段位
                if "radar_scores" in analysis:
                    update_radar_score(st.session_state.username, analysis["radar_scores"])
                
                match = find_resonance(vec, st.session_state.username)
                if match: st.toast(f"🔔 发现共鸣！", icon="⚡")
        
        st.rerun()
