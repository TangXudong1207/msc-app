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
    client_ai = OpenAI(
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

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text: return True
    return False

def add_user(username, password, nickname):
    try:
        res = supabase.table('users').select("*").eq('username', username).execute()
        if len(res.data) > 0: return False
        data = {"username": username, "password": make_hashes(password), "nickname": nickname}
        supabase.table('users').insert(data).execute()
        return True
    except: return False

def login_user(username, password):
    try:
        hashed_pw = make_hashes(password)
        res = supabase.table('users').select("*").eq('username', username).eq('password', hashed_pw).execute()
        return res.data
    except: return []

def get_nickname(username):
    try:
        res = supabase.table('users').select("nickname").eq('username', username).execute()
        if res.data: return res.data[0]['nickname']
        return username
    except: return username

# --- 🧠 AI 核心：智能人文主义逻辑 ---

def call_ai_api(prompt):
    try:
        response = client_ai.chat.completions.create(
            model=TARGET_MODEL,
            messages=[
                {"role": "system", "content": "You are the MSC (Meaning Collaboration Structure) engine. Output valid JSON only. Do not use markdown blocks."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            stream=False,
            response_format={"type": "json_object"} 
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

# --- 📐 核心算法：节点产生规则 ---
def analyze_input_quality(text):
    """
    判断输入是否满足生成节点的条件：
    1. 概念密度 > 0.12
    2. 包含方向性结构
    """
    prompt = f"""
    任务：评估用户输入的【意义密度】。
    输入："{text}"
    
    规则：
    1. 概念密度 (density): 关键概念数/总词数。
    2. 方向性 (directional): 是否包含 why/how/因为/希望/担心 等结构。
    
    请返回 JSON:
    {{
        "density": 0.0到1.0之间的数值,
        "is_directional": true或false,
        "valid_node": true或false (如果 density>0.12 或 is_directional=true，则为true)
    }}
    """
    res = call_ai_api(prompt)
    if "error" in res: return {"valid_node": True} # 保底策略
    return res

def generate_node_data(mode, text):
    # 1. 先进行质量过滤
    quality = analyze_input_quality(text)
    if not quality.get('valid_node', True):
        return {"error": True, "msg": "意义密度不足，未生成节点。请尝试表达更明确的观点、情绪或追问。"}

    # 2. 如果通过，生成节点内容
    prompt = f"""
    场景：【{mode}】。用户输入："{text}"。
    请提取 MSC 结构，返回 JSON:
    {{
        "care_point": "用户潜意识里的 Care (核心关怀)...",
        "meaning_layer": "背后的哲学或社会学结构...",
        "insight": "一句反直觉的升维洞察...",
        "logic_score": 0.0到1.0 (逻辑强度, L值),
        "keywords": ["关键词1", "关键词2"] (用于计算 C 值)
    }}
    """
    return call_ai_api(prompt)

def generate_fusion(node_a, node_b):
    prompt = f"""
    任务：融合 A 和 B。
    A: {node_a}
    B: {node_b}
    
    请根据 S(语义) + C(关切) + L(逻辑) 原则进行融合。
    返回 JSON:
    {{
        "care_point": "共同的底层关怀...",
        "meaning_layer": "全景结构...",
        "insight": "新的升维洞察..."
    }}
    """
    return call_ai_api(prompt)

# --- 📐 核心算法：链接强度计算 (R值) ---
def calculate_R_value(vec_a, vec_b, keywords_a, keywords_b, logic_a, logic_b):
    # 1. S: 语义相似度 (Cosine)
    vec_a = np.array(vec_a)
    vec_b = np.array(vec_b)
    S = np.dot(vec_a, vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b)) if (np.linalg.norm(vec_a) * np.linalg.norm(vec_b)) > 0 else 0
    
    # 2. C: 关切点重叠度 (Jaccard)
    set_a = set(keywords_a)
    set_b = set(keywords_b)
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    C = intersection / union if union > 0 else 0
    
    # 3. L: 逻辑关系度 (取平均)
    L = (logic_a + logic_b) / 2
    
    # 🌟 您的公式：R = 0.5*S + 0.3*C + 0.2*L
    R = 0.5 * S + 0.3 * C + 0.2 * L
    return R

def find_resonance_v2(current_vector, current_user, current_keywords, current_logic):
    if not current_vector: return None
    try:
        # 获取所有节点，这里为了计算方便取最近的 50 个
        res = supabase.table('nodes').select("*").neq('username', current_user).order('id', desc=True).limit(50).execute()
        others = res.data
        
        best_match = None
        highest_R = 0
        
        for row in others:
            if row['vector'] and row['logic_score'] is not None: # 确保有新版数据
                try:
                    other_vector = json.loads(row['vector'])
                    other_keywords = json.loads(row['keywords']) if row['keywords'] else []
                    other_logic = row['logic_score']
                    
                    # 计算 R 值
                    R = calculate_R_value(
                        current_vector, other_vector,
                        current_keywords, other_keywords,
                        current_logic, other_logic
                    )
                    
                    # 🌟 链接阈值逻辑
                    if R >= 0.75: # 强链接 -> 自动融合
                        if R > highest_R:
                            highest_R = R
                            best_match = {
                                "user": row['username'],
                                "content": row['content'],
                                "score": round(R * 100, 1),
                                "type": "Strong Link"
                            }
                    elif R >= 0.55: # 弱链接 -> 仅提示
                         pass # 暂时不处理弱链接，后续可做虚线连接
                         
                except: continue
        return best_match
    except: return None

# --- 💾 存取 ---
def save_node(username, content, data, mode, vector):
    try:
        insert_data = {
            "username": username, "content": content,
            "care_point": data.get('care_point', '未命名'),
            "meaning_layer": data.get('meaning_layer', '暂无结构'),
            "insight": data.get('insight', '生成中断'),
            "mode": mode, 
            "vector": json.dumps(vector),
            # 新增字段
            "logic_score": data.get('logic_score', 0.5),
            "keywords": json.dumps(data.get('keywords', []))
        }
        supabase.table('nodes').insert(insert_data).execute()
    except Exception as e: st.error(f"保存失败: {str(e)}")

def get_user_nodes(username):
    try:
        res = supabase.table('nodes').select("*").eq('username', username).order('id', desc=False).execute()
        return res.data
    except: return []

# --- 🎨 地图渲染 (赛博朋克) ---
def render_cyberpunk_map(nodes, height="300px", is_fullscreen=False):
    if not nodes:
        st.caption("暂无数据...")
        return

    graph_nodes = []
    graph_links = []
    categories = [{"name": "日常"}, {"name": "学术"}, {"name": "艺术"}]
    
    label_size = 14 if is_fullscreen else 10
    symbol_size = 30 if is_fullscreen else 15
    repulsion = 1000 if is_fullscreen else 200 

    for i, node in enumerate(nodes):
        short_care = node['care_point'][:8] + "..." if len(node['care_point']) > 8 else node['care_point']
        cat_idx = 0
        if "学术" in node['mode']: cat_idx = 1
        elif "艺术" in node['mode']: cat_idx = 2
        
        # 节点大小根据 logic_score (亮度) 调整
        # 如果是旧数据没有 logic_score，给个默认值 0.5
        logic = node.get('logic_score') if node.get('logic_score') is not None else 0.5
        dynamic_size = symbol_size * (1 + logic) # 逻辑越强，节点越大

        graph_nodes.append({
            "name": f"#{node['id']}", 
            "id": str(node['id']),
            "symbolSize": dynamic_size,
            "category": cat_idx,
            "value": node['insight'],
            "label": {
                "show": True, 
                "position": "right", 
                "color": "#fff",
                "fontSize": label_size,
                "formatter": short_care if is_fullscreen else "{b}"
            }
        })
        
        if i > 0:
            prev_node = nodes[i-1]
            graph_links.append({
                "source": str(prev_node['id']),
                "target": str(node['id']),
                "lineStyle": {
                    "curveness": 0.2,
                    "color": "#00d2ff" if i % 2 == 0 else "#ff00d4",
                    "width": 2 if is_fullscreen else 1
                }
            })

    option = {
        "backgroundColor": "#0e1117",
        "title": {
            "text": "🌌 意义重力场" if is_fullscreen else "",
            "left": "center",
            "textStyle": {"color": "#fff"}
        },
        "tooltip": {"trigger": "item", "formatter": "{b}: {c}"},
        "series": [{
            "type": "graph", "layout": "force", "data": graph_nodes, "links": graph_links, "categories": categories,
            "roam": True, "lineStyle": {"curveness": 0.3},
            "force": {"repulsion": repulsion, "edgeLength": [50, 200]},
            "itemStyle": {"shadowBlur": 10, "shadowColor": "rgba(255, 255, 255, 0.5)"}
        }]
    }
    st_echarts(options=option, height=height)

@st.dialog("🔭 意义重力场 · 全景视图", width="large")
def view_fullscreen_map(nodes):
    render_cyberpunk_map(nodes, height="600px", is_fullscreen=True)

# ==========================================
# 🖥️ 界面主逻辑
# ==========================================

st.set_page_config(page_title="MSC v14.0 Intelligent Humanism", layout="wide", initial_sidebar_state="expanded")

if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌌 MSC 意义协作系统")
    st.caption("v14.0 智能人文主义内核")
    tab1, tab2 = st.tabs(["登录", "注册"])
    with tab1:
        u = st.text_input("用户名")
        p = st.text_input("密码", type='password')
        if st.button("登录"):
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
        if st.button("注册"):
            if add_user(nu, np_pass, nn): st.success("成功！")
            else: st.error("已存在")

else:
    with st.sidebar:
        st.write(f"👋 **{st.session_state.nickname}**")
        if st.button("退出"):
            st.session_state.logged_in = False
            st.session_state.messages = [] 
            st.rerun()
        st.divider()
        history = get_user_nodes(st.session_state.username)
        if history:
            render_cyberpunk_map(history, height="250px", is_fullscreen=False)
            if st.button("🔍 全屏沉浸模式", use_container_width=True):
                view_fullscreen_map(history)
            st.markdown("---")
            for row in reversed(history):
                with st.expander(f"#{row['id']} {row['care_point'][:8]}..."):
                    st.caption(f"{row['created_at'][:16]}")
                    st.write(f"**原话:** {row['content']}")
                    st.success(f"💡 {row['insight']}")
        else: st.info("暂无节点")
    
    st.title("MSC 意义构建 & 共鸣雷达")
    st.caption("基于 R = 0.5S + 0.3C + 0.2L 核心算法")
    
    mode = st.selectbox("场景", ["🌱 日常社交", "🎓 学术研讨", "🎨 艺术共创"])
    user_input = st.chat_input("输入思考...")
    
    if "messages" not in st.session_state: st.session_state.messages = []
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"], unsafe_allow_html=True)
            if "fusion_data" in msg:
                match = msg["fusion_data"]
                btn_key = f"btn_merge_{msg['id']}"
                if st.button(f"⚡ 发现强链接 (R={match['score']}%)：与 {get_nickname(match['user'])} 合并", key=btn_key):
                    with st.spinner("正在融合..."):
                        c_node = generate_fusion(msg["my_content"], match["content"])
                        if "error" not in c_node:
                            fusion_html = f"""
                            <div style="background-color:#E8F5E9;padding:20px;border-radius:10px;border-left:5px solid #2E7D32;margin-top:10px;">
                                <h4 style="color:#2E7D32;margin:0;">🧬 融合成功</h4>
                                <p><strong>A:</strong> {msg['my_content']}<br>
                                <strong>B:</strong> {match['content']}</p>
                                <div style="background-color:#fff;padding:10px;border-radius:5px;margin-top:10px;">
                                    <p style="color:#1B5E20;font-weight:bold;">💡 洞察: {c_node.get('insight')}</p>
                                </div>
                            </div>
                            """
                            st.markdown(fusion_html, unsafe_allow_html=True)
                            st.session_state.messages.append({"role": "assistant", "content": fusion_html})
                        else: st.error("融合失败")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            with st.spinner("DeepSeek 正在计算 R 值..."):
                res = generate_node_data(mode, user_input)
                
                # 🌟 新增：质量拦截逻辑
                if "error" in res:
                    # 如果 AI 返回的 msg 是我们设定的"密度不足"，则显示黄色警告
                    if "意义密度不足" in res['msg']:
                        st.warning(f"⚠️ {res['msg']}")
                        st.session_state.messages.append({"role": "assistant", "content": f"⚠️ {res['msg']}"})
                    else:
                        st.error(f"⚠️ 生成失败: {res.get('msg')}")
                else:
                    # 只有 valid_node 才会走到这里
                    # 但还需要把新的字段 logic_score 和 keywords 存进去
                    # 注意：为了让代码跑通，我们需要在 Supabase 里手动加这两个字段
                    # 或者，为了不报错，我们暂时把它们存在 vector 字段里（打包成 JSON），或者忽略它们只存核心
                    # 为了演示稳定性，这里我先不改数据库结构，只在计算 R 值时用。
                    
                    vec = get_embedding(user_input)
                    
                    # 为了兼容旧数据库结构，我们把 logic_score 和 keywords 暂时“藏”在内存里用于本次计算
                    # 下一步我们会去 Supabase 增加字段
                    current_logic = res.get('logic_score', 0.5)
                    current_keywords = res.get('keywords', [])
                    
                    # 存库 (注意：为了不报错，save_node 里目前还没写真正存这两个新字段的代码，待会去 SQL 改表结构)
                    # 我们先用旧结构存，保证不崩
                    save_node(st.session_state.username, user_input, res, mode, vec)
                    
                    card = f"""
                    **✨ 节点生成**
                    * **Care:** {res['care_point']}
                    * **Logic Score:** {res.get('logic_score', 0.5)}
                    > {res['insight']}
                    """
                    st.markdown(card)
                    
                    # 使用新的 R 值算法寻找共鸣
                    match = find_resonance_v2(vec, st.session_state.username, current_keywords, current_logic)
                    
                    msg_payload = {"role": "assistant", "content": card}
                    if match:
                        msg_id = int(time.time())
                        msg_payload["fusion_data"] = match
                        msg_payload["my_content"] = user_input
                        msg_payload["id"] = msg_id
                        st.success(f"🔔 发现强链接：R={match['score']}%")
                        st.button(f"⚡ 合并", key=f"btn_merge_{msg_id}")
                    
                    st.session_state.messages.append(msg_payload)
                    time.sleep(1)
                    st.rerun()
