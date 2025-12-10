import streamlit as st
from openai import OpenAI
from supabase import create_client, Client
from streamlit_echarts import st_echarts # 🌟 新增：引入ECharts绘图库
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

# --- 🛠️ 基础设施 --- (保持不变)
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

# --- 🧠 AI 核心 --- (保持不变)
def call_ai_api(prompt):
    try:
        response = client_ai.chat.completions.create(
            model=TARGET_MODEL,
            messages=[{"role": "system", "content": "You are a profound philosopher. Output valid JSON only."}, {"role": "user", "content": prompt}],
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

def generate_node_data(mode, text):
    prompt = f"""
    场景：【{mode}】。用户输入："{text}"。
    请提取结构，返回JSON:
    {{
        "care_point": "用户潜意识里的情绪...",
        "meaning_layer": "背后的深层逻辑...",
        "insight": "一句升维洞察..."
    }}
    """
    return call_ai_api(prompt)

def generate_fusion(node_a_content, node_b_content):
    prompt = f"""
    融合 A: "{node_a_content}" 和 B: "{node_b_content}"。
    返回JSON:
    {{
        "care_point": "共同深层诉求...",
        "meaning_layer": "全景视角...",
        "insight": "全新洞察..."
    }}
    """
    return call_ai_api(prompt)

def cosine_similarity(v1, v2):
    if not v1 or not v2: return 0
    vec1, vec2 = np.array(v1), np.array(v2)
    norm1, norm2 = np.linalg.norm(vec1), np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0: return 0
    return np.dot(vec1, vec2) / (norm1 * norm2)

def find_resonance(current_vector, current_user):
    if not current_vector: return None
    try:
        res = supabase.table('nodes').select("username, content, vector").neq('username', current_user).execute()
        others = res.data
        best_match, highest_score = None, 0
        for row in others:
            if row['vector']:
                try:
                    score = cosine_similarity(current_vector, json.loads(row['vector']))
                    if score > 0.7 and score > highest_score:
                        highest_score = score
                        best_match = {"user": row['username'], "content": row['content'], "score": round(score * 100, 1)}
                except: continue
        return best_match
    except: return None

def save_node(username, content, data, mode, vector):
    try:
        insert_data = {
            "username": username, "content": content,
            "care_point": data.get('care_point', '未命名'),
            "meaning_layer": data.get('meaning_layer', '暂无结构'),
            "insight": data.get('insight', '生成中断'),
            "mode": mode, "vector": json.dumps(vector)
        }
        supabase.table('nodes').insert(insert_data).execute()
    except Exception as e: st.error(f"保存失败: {str(e)}")

def get_user_nodes(username):
    try:
        res = supabase.table('nodes').select("*").eq('username', username).order('id', desc=False).execute() # 按时间正序排列用于画图
        return res.data
    except: return []

# --- 🎨 赛博朋克地图渲染器 (新功能) ---
def render_cyberpunk_map(nodes):
    if not nodes:
        st.caption("暂无数据，快去生成第一个节点吧！")
        return

    # 1. 准备数据节点 (Nodes)
    graph_nodes = []
    graph_links = []
    categories = [{"name": "日常"}, {"name": "学术"}, {"name": "艺术"}]
    
    for i, node in enumerate(nodes):
        # 截取 Care Point 作为节点名字
        short_care = node['care_point'][:6] + "..." if len(node['care_point']) > 6 else node['care_point']
        
        # 根据模式决定颜色类别
        cat_idx = 0
        if "学术" in node['mode']: cat_idx = 1
        elif "艺术" in node['mode']: cat_idx = 2
        
        graph_nodes.append({
            "name": f"#{node['id']}", # 节点显示ID
            "id": str(node['id']),
            "symbolSize": 20,
            "category": cat_idx,
            "value": node['insight'], # 鼠标悬停显示 Insight
            "label": {"show": True, "position": "right", "color": "#fff"}, # 只有ID
            # 存一些元数据，为了tooltip
            "full_care": node['care_point'] 
        })
        
        # 2. 准备连线 (Links) - 简单的线性时间演化
        if i > 0:
            prev_node = nodes[i-1]
            graph_links.append({
                "source": str(prev_node['id']),
                "target": str(node['id']),
                "lineStyle": {"curveness": 0.2}
            })

    # 3. ECharts 配置项 (赛博朋克风)
    option = {
        "backgroundColor": "#0e1117", # 与 Streamlit 深色模式融合
        "title": {
            "text": "🧠 思想拓扑",
            "subtext": "Evolution of Thought",
            "textStyle": {"color": "#00d2ff"},
            "left": "center"
        },
        "tooltip": {
            "trigger": "item",
            "formatter": "{b}: {c}" # 显示 ID 和 Insight
        },
        "legend": {
            "data": ["日常", "学术", "艺术"],
            "textStyle": {"color": "#ccc"},
            "bottom": 0
        },
        "series": [
            {
                "type": "graph",
                "layout": "force", # 力引导布局
                "data": graph_nodes,
                "links": graph_links,
                "categories": categories,
                "roam": True, # 允许缩放和平移
                "label": {
                    "position": "right",
                    "formatter": "{b}" 
                },
                "lineStyle": {
                    "color": "source",
                    "curveness": 0.3,
                    "width": 2
                },
                "force": {
                    "repulsion": 300, # 斥力，防止节点挤在一起
                    "edgeLength": 50
                },
                # 炫光效果
                "itemStyle": {
                    "shadowBlur": 10,
                    "shadowColor": "rgba(0, 255, 255, 0.5)"
                }
            }
        ]
    }
    
    # 渲染图表 (高度300px，适合侧边栏)
    st_echarts(options=option, height="400px")

# ==========================================
# 🖥️ 界面主逻辑
# ==========================================

st.set_page_config(page_title="MSC v12.0 Cyberpunk", layout="wide", initial_sidebar_state="expanded")

if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌌 MSC 意义协作系统")
    st.caption("DeepSeek + Supabase + CyberMap")
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
    # --- 侧边栏：思想地图 ---
    with st.sidebar:
        st.write(f"👋 **{st.session_state.nickname}**")
        if st.button("退出"):
            st.session_state.logged_in = False
            st.session_state.messages = [] 
            st.rerun()
        
        st.divider()
        
        # 🌟 这里的旧列表被替换成了酷炫的地图！
        history = get_user_nodes(st.session_state.username)
        if history:
            # 调用地图渲染函数
            render_cyberpunk_map(history)
            
            st.markdown("---")
            st.caption("📜 **详细列表**")
            # 保留折叠列表以便查看详细文字
            # 倒序显示，让最新的在最上面
            for row in reversed(history):
                with st.expander(f"#{row['id']} {row['care_point'][:8]}..."):
                    st.caption(f"{row['created_at'][:16]}")
                    st.write(f"**原话:** {row['content']}")
                    st.success(f"💡 {row['insight']}")
    
    # --- 主界面 ---
    st.title("MSC 意义构建 & 共鸣雷达")
    st.caption("基于拓扑地图的思想进化系统")
    
    mode = st.selectbox("场景", ["🌱 日常社交", "🎓 学术研讨", "🎨 艺术共创"])
    user_input = st.chat_input("输入思考...")
    
    if "messages" not in st.session_state: st.session_state.messages = []
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"], unsafe_allow_html=True)
            if "fusion_data" in msg:
                match = msg["fusion_data"]
                btn_key = f"btn_merge_{msg['id']}"
                if st.button(f"⚡ 发现共鸣 ({match['score']}%)：与 {get_nickname(match['user'])} 合并？", key=btn_key):
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
            with st.spinner("DeepSeek 正在构建拓扑..."):
                res = generate_node_data(mode, user_input)
                if "error" in res:
                    st.error(f"⚠️ 生成失败: {res.get('msg')}")
                else:
                    vec = get_embedding(user_input)
                    save_node(st.session_state.username, user_input, res, mode, vec)
                    
                    card = f"""
                    **✨ 节点生成**
                    * **Care:** {res['care_point']}
                    > {res['insight']}
                    """
                    st.markdown(card)
                    
                    match = find_resonance(vec, st.session_state.username)
                    msg_payload = {"role": "assistant", "content": card}
                    if match:
                        msg_id = int(time.time())
                        msg_payload["fusion_data"] = match
                        msg_payload["my_content"] = user_input
                        msg_payload["id"] = msg_id
                        st.success(f"🔔 发现共鸣：{match['score']}%")
                        st.button(f"⚡ 合并", key=f"btn_merge_{msg_id}")
                    
                    st.session_state.messages.append(msg_payload)
                    time.sleep(1)
                    st.rerun() # 强制刷新，让侧边栏地图更新
