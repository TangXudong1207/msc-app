import streamlit as st
import msc_lib as msc
import time
import json

# ==========================================
# 🎨 1. 注入 Google Studio 风格 CSS
# ==========================================
def inject_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

        /* --- 全局容器：极简白 --- */
        .stApp {
            background-color: #FFFFFF;
            font-family: 'Roboto', sans-serif;
            color: #1F1F1F;
        }
        
        /* --- 侧边栏：淡灰背景 --- */
        [data-testid="stSidebar"] {
            background-color: #F8F9FA;
            border-right: 1px solid #E0E0E0;
        }
        
        /* --- 标题：Google 风格 --- */
        h1, h2, h3 {
            font-family: 'Roboto', sans-serif;
            font-weight: 500;
            color: #202124;
            letter-spacing: -0.5px;
        }
        
        /* --- 按钮：圆角胶囊 --- */
        .stButton button {
            background-color: #FFFFFF;
            border: 1px solid #DADCE0;
            color: #1A73E8;
            border-radius: 24px; /* 胶囊形状 */
            padding: 0.5rem 1.5rem;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        .stButton button:hover {
            background-color: #F1F3F4;
            border-color: #DADCE0;
            color: #174EA6;
            box-shadow: 0 1px 2px rgba(60,64,67,0.3);
        }
        /* 主按钮 (Primary) */
        .stButton button[kind="primary"] {
            background-color: #1A73E8;
            color: white;
            border: none;
        }
        .stButton button[kind="primary"]:hover {
            background-color: #185ABC;
        }

        /* --- 核心：意义卡片 (Google Card) --- */
        .meaning-card {
            background-color: #FFFFFF;
            border: 1px solid #DADCE0;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            transition: box-shadow 0.3s ease;
            font-family: 'Roboto', sans-serif;
        }
        
        .meaning-card:hover {
            box-shadow: 0 4px 12px rgba(60,64,67,0.15);
            border-color: #1A73E8;
        }
        
        /* 不同的左侧边框颜色代表不同逻辑分 */
        .card-high-logic { border-left: 4px solid #1A73E8; } /* 蓝 */
        .card-mid-logic { border-left: 4px solid #A142F4; }  /* 紫 */
        
        .card-header {
            font-size: 12px;
            color: #5F6368;
            font-weight: 500;
            text-transform: uppercase;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
        }
        
        .card-care {
            font-size: 16px;
            color: #202124;
            font-weight: 500;
            margin-bottom: 12px;
            line-height: 1.5;
        }
        
        .card-insight {
            background-color: #F8F9FA;
            padding: 12px;
            border-radius: 8px;
            color: #3C4043;
            font-size: 14px;
            line-height: 1.6;
            font-style: italic;
            border-left: 2px solid #DADCE0;
        }
        
        .card-structure {
            font-size: 13px;
            color: #70757A;
            margin-top: 10px;
            line-height: 1.5;
        }

        /* --- 聊天气泡：极简风格 --- */
        [data-testid="stChatMessageContent"] {
            border-radius: 16px;
            padding: 16px;
            font-size: 15px;
            line-height: 1.6;
            box-shadow: none;
        }
        /* 用户气泡 */
        div[data-testid="stChatMessage"]:nth-child(odd) [data-testid="stChatMessageContent"] {
            background-color: #E8F0FE; /* 极淡蓝 */
            color: #174EA6;
            border: none;
        }
        /* AI 气泡 */
        div[data-testid="stChatMessage"]:nth-child(even) [data-testid="stChatMessageContent"] {
            background-color: #F1F3F4; /* 极淡灰 */
            color: #202124;
            border: none;
        }
        
        /* 输入框优化 */
        .stTextInput input {
            border-radius: 24px;
            border: 1px solid #DADCE0;
            padding-left: 20px;
        }
        .stTextInput input:focus {
            border-color: #1A73E8;
            box-shadow: 0 0 0 2px rgba(26,115,232,0.2);
        }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 🖥️ 主界面逻辑
# ==========================================

st.set_page_config(page_title="MSC v33.0 Clean", layout="wide", initial_sidebar_state="expanded")
inject_custom_css() # 注入皮肤

if "logged_in" not in st.session_state: st.session_state.logged_in = False

# --- 场景 1: 登录注册 ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: #1A73E8;'>🔷 MSC</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #5F6368;'>智能人文主义 · 意义协作系统</p>", unsafe_allow_html=True)
        st.divider()
        tab1, tab2 = st.tabs(["登录", "注册"])
        with tab1:
            u = st.text_input("用户名")
            p = st.text_input("密码", type='password')
            if st.button("登录", use_container_width=True, type="primary"):
                res = msc.login_user(u, p)
                if res:
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.session_state.nickname = res[0]['nickname']
                    st.session_state.messages = [] 
                    st.rerun()
                else: st.error("用户名或密码错误")
        with tab2:
            nu = st.text_input("新用户名")
            np_pass = st.text_input("新密码", type='password')
            nn = st.text_input("昵称")
            if st.button("注册账户", use_container_width=True):
                if msc.add_user(nu, np_pass, nn): st.success("注册成功")
                else: st.error("注册失败")

# --- 场景 2: 主应用 ---
else:
    chat_history = msc.get_active_chats(st.session_state.username)
    nodes_map = msc.get_active_nodes_map(st.session_state.username)
    all_nodes_list = msc.get_all_nodes_for_map(st.session_state.username)
    user_profile = msc.get_user_profile(st.session_state.username)
    
    raw_radar = user_profile.get('radar_profile')
    if isinstance(raw_radar, str): radar_dict = json.loads(raw_radar)
    else: radar_dict = raw_radar if raw_radar else {k:3.0 for k in ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]}

    # --- 侧边栏 (Clean Style) ---
    with st.sidebar:
        rank_name, rank_icon = msc.calculate_rank(radar_dict)
        st.markdown(f"### {st.session_state.nickname}")
        st.caption(f"{rank_icon} {rank_name}")
        
        msc.render_radar_chart(radar_dict)
        
        st.markdown("#### 探索")
        if st.button("🌍 MSC World", use_container_width=True):
            msc.view_msc_world()
            
        @st.dialog("🧬 画像分析")
        def show_persona():
            if st.button("生成报告", type="primary"):
                with st.spinner("分析中..."):
                    res = msc.analyze_persona_report(radar_dict)
                    st.markdown(f"### 🖼️ 静态画像")
                    st.write(res.get('static_portrait'))
                    st.markdown(f"### 🚀 动态成长")
                    st.write(res.get('dynamic_growth'))
        
        c1, c2 = st.columns(2)
        if c1.button("🧬 画像"): show_persona()
        
        @st.dialog("🧪 仿真实验室")
        def show_sim():
            topic = st.text_input("话题")
            if st.button("开始注入", type="primary"):
                cnt, msg = msc.simulate_civilization(topic, 3)
                st.success(msg)
        if c2.button("🧪 实验"): show_sim()

        st.divider()
        st.caption("我的星云")
        msc.render_cyberpunk_map(all_nodes_list, height="200px")
        
        @st.dialog("🔭 全屏", width="large")
        def show_full_map():
            msc.render_cyberpunk_map(all_nodes_list, height="600px", is_fullscreen=True)
        if st.button("🔭 全屏视图", use_container_width=True): show_full_map()
        
        st.markdown("")
        if st.button("退出登录", use_container_width=True): st.session_state.logged_in = False; st.rerun()

    # --- 主对话区 ---
    st.subheader("💬 意义流")
    
    for msg in chat_history:
        col_chat, col_node = st.columns([0.6, 0.4], gap="medium")
        
        with col_chat:
            c_msg, c_del = st.columns([0.9, 0.1])
            with c_msg:
                with st.chat_message(msg['role']): st.markdown(msg['content'], unsafe_allow_html=True)
            with c_del:
                if msg['role'] == 'user':
                    if st.button("✕", key=f"del_{msg['id']}", help="删除"):
                        if msc.soft_delete_chat_and_node(msg['id'], msg['content'], st.session_state.username): st.rerun()

        with col_node:
            if msg['role'] == 'user' and msg['content'] in nodes_map:
                node = nodes_map[msg['content']]
                
                logic_score = node.get('logic_score', 0.5)
                # 高逻辑分用蓝色，低逻辑分用紫色 (符合 Google Gemini 调性)
                card_class = "card-high-logic" if logic_score > 0.8 else "card-mid-logic"
                
                # HTML 卡片渲染
                card_html = f"""
                <div class="meaning-card {card_class}">
                    <div class="card-header">
                        <span style="color: #1A73E8;">● NODE #{node['id']}</span>
                        <span>SCORE: {logic_score}</span>
                    </div>
                    <div class="card-care">{node['care_point']}</div>
                    <div class="card-insight">{node['insight']}</div>
                    <div class="card-structure">{node['meaning_layer']}</div>
                    <div style="margin-top:10px; font-size:11px; color:#9AA0A6;">{node['created_at'][:16]}</div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)

    if prompt := st.chat_input("输入您的思考..."):
        msc.save_chat(st.session_state.username, "user", prompt)
        
        full_history = chat_history + [{'role':'user', 'content':prompt}]
        stream = msc.get_normal_response(full_history)
        reply_text = st.write_stream(stream)
        msc.save_chat(st.session_state.username, "assistant", reply_text)
        
        with st.spinner("✨ 正在构建意义结构..."):
            analysis = msc.analyze_meaning_background(prompt)
            if analysis.get("valid", False):
                vec = msc.get_embedding(prompt)
                msc.save_node(st.session_state.username, prompt, analysis, "日常", vec)
                if "radar_scores" in analysis: msc.update_radar_score(st.session_state.username, analysis["radar_scores"])
                
                match = msc.find_resonance(vec, st.session_state.username, analysis)
                if match: st.toast(f"🔔 发现共鸣！(MLS={match['score']})", icon="⚡")
                
                msc.check_group_formation(analysis, vec, st.session_state.username)
        st.rerun()
