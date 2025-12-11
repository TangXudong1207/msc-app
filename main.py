import streamlit as st
import streamlit_antd_components as sac
import msc_lib as msc
import time
import json
import random

# ==========================================
# 🎨 MSC 视觉系统：光 × 线 × 空
# ==========================================
def inject_visual_system():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@300&display=swap');

        /* --- I. 基础环境 (极简白) --- */
        .stApp {
            background-color: #FFFFFF;
            font-family: 'Inter', sans-serif;
            color: #0D0D0D;
        }

        /* --- II. 侧边栏 (控制台) --- */
        [data-testid="stSidebar"] {
            background-color: #FAFAFA; /* 极淡灰，区分层级 */
            border-right: 1px solid rgba(0,0,0,0.05); /* 5% 透明度边框 */
        }
        
        /* --- III. 字体系统 --- */
        h1, h2, h3 {
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            letter-spacing: -0.02em;
            color: #0D0D0D;
        }
        
        /* --- IV. 组件：光与线 --- */
        
        /* 按钮：极轻边框 + 微光交互 */
        .stButton button {
            background: #FFFFFF;
            border: 1px solid #EAEAEA;
            border-radius: 8px;
            color: #0D0D0D;
            font-weight: 500;
            font-size: 14px;
            transition: all 0.3s ease;
        }
        .stButton button:hover {
            border-color: #4D79FF; /* 智能蓝 */
            box-shadow: 0 4px 12px rgba(77, 121, 255, 0.15); /* 蓝色微光 */
            color: #4D79FF;
            transform: translateY(-1px);
        }
        
        /* 输入框：呼吸感 */
        .stTextInput input {
            border: 1px solid #EAEAEA;
            border-radius: 8px;
            padding: 10px 15px;
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
        }
        .stTextInput input:focus {
            border-color: #9D7BFF; /* 深度紫 */
            box-shadow: 0 0 0 3px rgba(157, 123, 255, 0.1);
        }

        /* --- V. 核心组件：意义节点卡 (Node Card) --- */
        .meaning-card {
            background: #FFFFFF;
            border: 1px solid #EDEDED;
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 16px;
            transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
            position: relative;
            overflow: hidden;
        }
        
        .meaning-card:hover {
            border-color: #4D79FF; /* 激活时变蓝 */
            box-shadow: 0 8px 30px rgba(77, 121, 255, 0.12); /* 蓝色光晕 */
            transform: translateY(-2px);
        }
        
        /* 能量条 (Energy Bar) */
        .card-energy {
            height: 2px;
            width: 40px;
            background: linear-gradient(90deg, #4D79FF, #9D7BFF);
            margin-bottom: 12px;
            border-radius: 2px;
            opacity: 0.8;
        }
        
        .card-header {
            font-family: 'JetBrains Mono', monospace; /* 结构感字体 */
            font-size: 11px;
            color: #999;
            text-transform: uppercase;
            letter-spacing: 1px;
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
        }
        
        .card-care {
            font-size: 15px;
            font-weight: 600;
            color: #0D0D0D;
            margin-bottom: 10px;
            line-height: 1.4;
        }
        
        .card-insight {
            font-family: 'Inter', sans-serif;
            font-weight: 400;
            font-style: italic;
            color: #444; /* 深灰 */
            font-size: 13px;
            line-height: 1.6;
            padding-left: 10px;
            border-left: 2px solid rgba(157, 123, 255, 0.3); /* 紫色细线 */
        }
        
        /* --- VI. 聊天气泡：极简 --- */
        [data-testid="stChatMessageContent"] {
            background-color: transparent !important;
            padding: 0px 10px !important;
        }
        /* 用户消息：右侧，深色 */
        div[data-testid="stChatMessage"]:nth-child(odd) {
            flex-direction: row-reverse;
            background-color: transparent;
        }
        div[data-testid="stChatMessage"]:nth-child(odd) [data-testid="stChatMessageContent"] {
            text-align: right;
            border-right: 2px solid #0D0D0D; /* 用户是坚实的黑线 */
            padding-right: 15px !important;
        }
        
        /* AI 消息：左侧，光 */
        div[data-testid="stChatMessage"]:nth-child(even) [data-testid="stChatMessageContent"] {
            border-left: 2px solid #4D79FF; /* AI 是智能的蓝线 */
            padding-left: 15px !important;
            color: #444;
        }
        
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 🖥️ 主程序逻辑
# ==========================================

st.set_page_config(page_title="MSC v36.0 Light", layout="wide", initial_sidebar_state="expanded")
inject_visual_system()

if "logged_in" not in st.session_state: st.session_state.logged_in = False

# --- 场景 1: 极简登录 ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; font-weight: 300;'>MSC</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #999; font-size: 0.9em; letter-spacing: 2px;'>MEANING · STRUCTURE · CARE</p>", unsafe_allow_html=True)
        st.divider()
        
        tab = sac.tabs([sac.TabsItem('登录'), sac.TabsItem('注册')], align='center', size='sm', variant='outline')
        
        if tab == '登录':
            u = st.text_input("ID")
            p = st.text_input("Password", type='password')
            if st.button("Enter System", use_container_width=True):
                res = msc.login_user(u, p)
                if res:
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.session_state.nickname = res[0]['nickname']
                    st.session_state.messages = [] 
                    st.rerun()
                else: sac.alert("Access Denied", color='red', banner=True)
        else:
            nu = st.text_input("New ID")
            np = st.text_input("Set Password", type='password')
            nn = st.text_input("Nickname")
            if st.button("Initialize", use_container_width=True):
                if msc.add_user(nu, np, nn): sac.alert("Identity Created", color='success', banner=True)
                else: sac.alert("ID Exists", color='error', banner=True)

# --- 场景 2: 主界面 ---
else:
    chat_history = msc.get_active_chats(st.session_state.username)
    nodes_map = msc.get_active_nodes_map(st.session_state.username)
    all_nodes_list = msc.get_all_nodes_for_map(st.session_state.username)
    user_profile = msc.get_user_profile(st.session_state.username)
    
    raw_radar = user_profile.get('radar_profile')
    if isinstance(raw_radar, str): radar_dict = json.loads(raw_radar)
    else: radar_dict = raw_radar if raw_radar else {k:3.0 for k in ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]}

    # --- 侧边栏：仪表盘 ---
    with st.sidebar:
        # 用户状态：极简
        rank_name, rank_icon = msc.calculate_rank(radar_dict)
        st.markdown(f"**{st.session_state.nickname}** <span style='color:#999; font-size:0.8em; margin-left:10px;'>{rank_name}</span>", unsafe_allow_html=True)
        
        # 雷达图 (极简线条)
        msc.render_radar_chart(radar_dict, height="180px")
        
        # 菜单
        menu = sac.menu([
            sac.MenuItem('控制台', icon='grid'),
            sac.MenuItem('世界观', icon='globe'),
            sac.MenuItem('实验室', icon='box'),
            sac.MenuItem('系统', type='group', children=[
                sac.MenuItem('退出', icon='power'),
            ]),
        ], index=0, format_func='title', size='sm', variant='light', open_all=True)

        if menu == '退出': st.session_state.logged_in = False; st.rerun()
        
        elif menu == '世界观':
            @st.dialog("🌍 MSC World", width="large")
            def show_world():
                global_nodes = msc.get_global_nodes()
                t1, t2 = st.tabs(["2D Earth", "3D Galaxy"])
                with t1: 
                    # 🌟 修复：直接传 list，不再在 main.py 里处理 DataFrame，全交给 lib
                    msc.render_2d_world_map(global_nodes)
                with t2: 
                    msc.render_3d_galaxy(global_nodes)
            show_world()
            
        elif menu == '实验室':
            @st.dialog("🧪 仿真")
            def show_sim():
                t = st.text_input("Topic")
                if st.button("Inject Agents"):
                    cnt, msg = msc.simulate_civilization(t, 3)
                    st.success(msg)
            show_sim()

        st.divider()
        st.caption("Neural Topography")
        msc.render_cyberpunk_map(all_nodes_list, height="150px")
        
        if st.button("🔭 Full View", use_container_width=True): 
            msc.view_fullscreen_map(all_nodes_list, st.session_state.nickname)

    # --- 主对话区 ---
    st.subheader("Flow of Meaning")
    st.caption("在此刻，每一次输入都是生长的开始。")
    st.write("") # Spacer

    for msg in chat_history:
        col_chat, col_node = st.columns([0.6, 0.4], gap="large")
        
        # 聊天流
        with col_chat:
            c_msg, c_del = st.columns([0.9, 0.1])
            with c_msg:
                # 极简气泡：只靠线条和排版区分
                with st.chat_message(msg['role'], avatar=None):
                    st.markdown(msg['content'], unsafe_allow_html=True)
            with c_del:
                if msg['role'] == 'user':
                    if st.button("✕", key=f"del_{msg['id']}", help="Delete"):
                        if msc.soft_delete_chat_and_node(msg['id'], msg['content'], st.session_state.username): st.rerun()

        # 意义流 (Node Cards)
        with col_node:
            if msg['role'] == 'user' and msg['content'] in nodes_map:
                node = nodes_map[msg['content']]
                logic_score = node.get('logic_score', 0.5)
                
                # HTML 渲染：悬浮水晶卡片
                card_html = f"""
                <div class="meaning-card">
                    <div class="card-energy" style="width: {int(logic_score*50)}px;"></div>
                    <div class="card-header">
                        <span>#{node['id']}</span>
                        <span>C:{node.get('c_score',0)} S:{node.get('s_score',0)} N:{node.get('n_score',0)}</span>
                    </div>
                    <div class="card-care">{node['care_point']}</div>
                    <div class="card-insight">{node['insight']}</div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)

    # 输入区
    if prompt := st.chat_input("..."):
        msc.save_chat(st.session_state.username, "user", prompt)
        
        full_history = chat_history + [{'role':'user', 'content':prompt}]
        stream = msc.get_normal_response(full_history)
        reply_text = st.write_stream(stream)
        msc.save_chat(st.session_state.username, "assistant", reply_text)
        
        with st.spinner("Processing..."):
            analysis = msc.analyze_meaning_background(prompt)
            if analysis.get("valid", False):
                vec = msc.get_embedding(prompt)
                msc.save_node(st.session_state.username, prompt, analysis, "日常", vec)
                if "radar_scores" in analysis: msc.update_radar_score(st.session_state.username, analysis["radar_scores"])
                match = msc.find_resonance(vec, st.session_state.username, analysis)
                if match: st.toast(f"Resonance found", icon="⚡")
                msc.check_group_formation(analysis, vec, st.session_state.username)
        st.rerun()
