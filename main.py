import streamlit as st
# 尝试导入 SAC，如果失败也不崩溃
try:
    import streamlit_antd_components as sac
except ImportError:
    st.error("正在安装组件库，请稍后刷新...")
    st.stop()

import msc_lib as msc
import time
import json

# ==========================================
# 🎨 CSS：强制显示修复
# ==========================================
def inject_custom_css():
    st.markdown("""
    <style>
        /* 强制全局背景和文字颜色，防止白底白字 */
        .stApp {
            background-color: #FFFFFF !important;
            color: #1F1F1F !important;
        }
        
        /* 侧边栏样式 */
        [data-testid="stSidebar"] {
            background-color: #F8F9FA !important;
            border-right: 1px solid #E0E0E0;
        }
        [data-testid="stSidebar"] * {
            color: #1F1F1F !important;
        }
        
        /* 输入框修复 */
        .stTextInput input {
            color: #000000 !important;
            background-color: #FFFFFF !important;
            border: 1px solid #CCC !important;
        }
        
        /* 聊天气泡：我的 */
        .chat-bubble-me {
            background-color: #95EC69;
            color: #000000;
            padding: 10px 14px;
            border-radius: 8px;
            margin-bottom: 10px;
            display: inline-block;
            float: right;
            clear: both;
            max-width: 80%;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }
        /* 聊天气泡：对方 */
        .chat-bubble-other {
            background-color: #F1F1F1;
            color: #000000;
            padding: 10px 14px;
            border-radius: 8px;
            margin-bottom: 10px;
            display: inline-block;
            float: left;
            clear: both;
            border: 1px solid #ddd;
            max-width: 80%;
        }
        
        /* 意义卡片 */
        .meaning-card {
            background-color: #FFFFFF;
            border: 1px solid #DADCE0;
            border-left: 4px solid #1A73E8;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        .card-header { font-size: 12px; color: #1A73E8; font-weight: bold; margin-bottom: 5px; }
        .card-body { font-size: 15px; color: #202124; margin-bottom: 8px; font-weight: 500; }
        .card-insight { font-size: 13px; color: #555; font-style: italic; background: #f9f9f9; padding: 8px; border-radius: 4px; }
        
        /* 每日追问卡片 */
        .daily-card {
            background: linear-gradient(135deg, #e8f0fe 0%, #ffffff 100%);
            border: 1px solid #d2e3fc;
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 20px;
            text-align: center;
            color: #000;
        }
    </style>
    """, unsafe_allow_html=True)

st.set_page_config(page_title="MSC v44.0 Safe", layout="wide", initial_sidebar_state="expanded")
inject_custom_css()

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "current_chat_partner" not in st.session_state: st.session_state.current_chat_partner = None

# --- 场景 1: 登录注册 (回归原生组件，确保可见) ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("🌌 MSC 意义协作")
        
        action = st.radio("请选择", ["登录", "注册新账号"], horizontal=True)
        
        if action == "登录":
            u = st.text_input("用户名", key="login_u")
            p = st.text_input("密码", type='password', key="login_p")
            if st.button("进入系统", type="primary", use_container_width=True):
                res = msc.login_user(u, p)
                if res:
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.session_state.nickname = res[0]['nickname']
                    st.session_state.messages = [] 
                    st.rerun()
                else: st.error("账号或密码错误")
        else:
            nu = st.text_input("新账号", key="reg_u")
            np = st.text_input("设置密码", type='password', key="reg_p")
            nn = st.text_input("你的昵称", key="reg_n")
            if st.button("创建身份", type="primary", use_container_width=True):
                if msc.add_user(nu, np, nn): st.success("注册成功！请切换到登录页。")
                else: st.error("注册失败，用户名可能已存在。")

# --- 场景 2: 主应用 ---
else:
    # 数据预加载
    chat_history = msc.get_active_chats(st.session_state.username)
    nodes_map = msc.get_active_nodes_map(st.session_state.username)
    all_nodes_list = msc.get_all_nodes_for_map(st.session_state.username)
    user_profile = msc.get_user_profile(st.session_state.username)
    
    raw_radar = user_profile.get('radar_profile')
    if isinstance(raw_radar, str): radar_dict = json.loads(raw_radar)
    else: radar_dict = raw_radar if raw_radar else {k:3.0 for k in ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]}
    rank_name, rank_icon = msc.calculate_rank(radar_dict)
    
    total_unread, unread_counts = msc.get_unread_counts(st.session_state.username)

    # --- 侧边栏 ---
    with st.sidebar:
        st.markdown(f"### {rank_icon} {st.session_state.nickname}")
        
        # 每日追问
        if "daily_q" not in st.session_state: st.session_state.daily_q = None
        if st.session_state.daily_q is None:
            if st.button("📅 生成今日追问", use_container_width=True):
                with st.spinner("..."):
                    st.session_state.daily_q = msc.generate_daily_question(st.session_state.username, radar_dict)
                    st.rerun()
        else:
            st.markdown(f"<div class='daily-card'><b>今日追问</b><br>{st.session_state.daily_q}</div>", unsafe_allow_html=True)

        msc.render_radar_chart(radar_dict, height="180px")
        
        # 菜单 (带红点)
        menu = sac.menu([
            sac.MenuItem('AI 伴侣', icon='robot'),
            sac.MenuItem('好友', icon='chat-dots', tag=sac.Tag(str(total_unread), color='red') if total_unread > 0 else None),
            sac.MenuItem('星团', icon='people'),
            sac.MenuItem('世界', icon='globe'),
            sac.MenuItem('系统', type='group', children=[sac.MenuItem('退出登录', icon='box-arrow-right')]),
        ], index=0, format_func='title', open_all=True)

        st.divider()
        if st.button("🔭 全屏星云", use_container_width=True): 
            msc.view_fullscreen_map(all_nodes_list, st.session_state.nickname)

    if menu == '退出登录': st.session_state.logged_in = False; st.rerun()

    # --- A. AI 伴侣 ---
    elif menu == 'AI 伴侣':
        st.subheader("🤖 AI 意义构建")
        chat_history_ai = msc.get_active_chats(st.session_state.username)
        
        col_chat, col_node = st.columns([0.65, 0.35], gap="small")
        with col_chat:
            for msg in chat_history_ai:
                with st.chat_message(msg['role']): st.markdown(msg['content'])
        with col_node:
            for msg in chat_history_ai:
                if msg['role'] == 'user' and msg['content'] in nodes_map:
                    node = nodes_map[msg['content']]
                    logic_score = node.get('logic_score', 0.5)
                    card_class = "card-high-logic" if logic_score > 0.8 else "card-mid-logic"
                    with st.expander(f"✨ {node['care_point'][:8]}...", expanded=False):
                         st.markdown(f"**Insight:** {node['insight']}")
                         st.caption(f"Structure: {node['meaning_layer']}")

        if prompt := st.chat_input("与 AI 对话..."):
            msc.save_chat(st.session_state.username, "user", prompt)
            full_history = chat_history_ai + [{'role':'user', 'content':prompt}]
            stream = msc.get_normal_response(full_history)
            try:
                reply = stream.choices[0].message.content
                msc.save_chat(st.session_state.username, "assistant", reply)
            except: pass
            
            with st.spinner("⚡"):
                analysis = msc.analyze_meaning_background(prompt)
                if analysis.get("valid", False):
                    vec = msc.get_embedding(prompt)
                    msc.save_node(st.session_state.username, prompt, analysis, "日常", vec)
                    if "radar_scores" in analysis: msc.update_radar_score(st.session_state.username, analysis["radar_scores"])
            st.rerun()

    # --- B. 好友私聊 ---
    elif menu == '好友':
        col_list, col_chat = st.columns([0.3, 0.7])
        with col_list:
            st.caption("通讯录")
            users = msc.get_all_users(st.session_state.username)
            if users:
                for u in users:
                    unread = unread_counts.get(u['username'], 0)
                    btn_label = f"{u['nickname']}"
                    if unread > 0: btn_label += f" 🔴 {unread}"
                    if st.button(btn_label, key=f"friend_{u['username']}", use_container_width=True):
                        st.session_state.current_chat_partner = u['username']
                        msc.mark_messages_read(u['username'], st.session_state.username)
                        st.rerun()
            else: st.info("暂无其他用户")

        with col_chat:
            partner = st.session_state.current_chat_partner
            if partner:
                st.caption(f"与 {partner} 对话中")
                history = msc.get_direct_messages(st.session_state.username, partner)
                my_nodes = msc.get_active_nodes_map(st.session_state.username) 
                
                sub_chat, sub_node = st.columns([0.65, 0.35])
                with sub_chat:
                    with st.container(height=500):
                        for msg in history:
                            if msg['sender'] == st.session_state.username:
                                st.markdown(f"<div class='chat-bubble-me'>{msg['content']}</div>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<div class='chat-bubble-other'>{msg['content']}</div>", unsafe_allow_html=True)
                
                with sub_node:
                    for msg in reversed(history):
                        if msg['sender'] == st.session_state.username and msg['content'] in my_nodes:
                            node = my_nodes[msg['content']]
                            with st.expander(f"✨ {node['care_point'][:6]}...", expanded=False):
                                st.info(node['insight'])

                if prompt := st.chat_input(f"发给 {partner}..."):
                    msc.send_direct_message(st.session_state.username, partner, prompt)
                    with st.spinner("⚡"):
                        analysis = msc.analyze_meaning_background(prompt)
                        if analysis.get("valid", False):
                            vec = msc.get_embedding(prompt)
                            msc.save_node(st.session_state.username, prompt, analysis, "私聊", vec)
                            match = msc.find_resonance(vec, st.session_state.username, analysis)
                            if match: st.toast(f"私聊中产生共鸣！", icon="⚡")
                    st.rerun()
            else: st.info("👈 请选择好友")

    # --- C. 星团 ---
    elif menu == '星团':
        st.subheader("🌌 意义自组织星团")
        rooms = msc.get_available_rooms()
        if rooms:
            for room in rooms:
                with st.expander(f"{room['name']}", expanded=True):
                    st.caption(room['description'])
                    if st.button("进入星团", key=f"join_{room['id']}"):
                        msc.join_room(room['id'], st.session_state.username)
                        msc.view_group_chat(room, st.session_state.username)
        else: st.info("暂无星团")

    # --- D. 世界 ---
    elif menu == '世界':
        st.title("🌍 MSC World")
        global_nodes = msc.get_global_nodes()
        t1, t2 = st.tabs(["2D Earth", "3D Galaxy"])
        with t1: msc.render_2d_world_map(global_nodes)
        with t2: msc.render_3d_galaxy(global_nodes)
