import streamlit as st
import streamlit_antd_components as sac
import msc_lib as msc
import time
import json

# ==========================================
# 🎨 CSS：极简科技风 (v48/v52 经典回归)
# ==========================================
def inject_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        
        /* 1. 全局去色，回归黑白灰 */
        .stApp { background-color: #FFFFFF; font-family: 'Roboto', sans-serif; color: #222; }
        
        /* 2. 侧边栏：纯净白 */
        [data-testid="stSidebar"] { background-color: #FAFAFA; border-right: 1px solid #EEE; }
        
        /* 3. 输入框：极细边框，无阴影 */
        .stTextInput input {
            border: 1px solid #E0E0E0; border-radius: 4px; padding: 10px;
            color: #333; background: #fff;
        }
        .stTextInput input:focus { border-color: #333; box-shadow: none; }
        
        /* 4. 按钮：黑白极简 */
        .stButton button {
            border: 1px solid #E0E0E0; background: #fff; color: #333;
            border-radius: 4px; font-weight: 400; font-size: 14px;
        }
        .stButton button:hover { border-color: #333; color: #000; background: #F9F9F9; }
        .stButton button[kind="primary"] { background-color: #333; color: white; border: none; }
        .stButton button[kind="primary"]:hover { background-color: #000; }
        
        /* 5. 聊天气泡：回归线条感与深色块 */
        .chat-bubble-me {
            background-color: #333; color: #fff; /* 我是深色块 */
            padding: 10px 15px; border-radius: 18px; border-bottom-right-radius: 2px;
            margin-bottom: 5px; display: inline-block; float: right; clear: both; max-width: 80%;
            font-size: 14px;
        }
        .chat-bubble-other {
            background-color: #F2F2F2; color: #333; /* 对方是浅灰块 */
            padding: 10px 15px; border-radius: 18px; border-bottom-left-radius: 2px;
            margin-bottom: 5px; display: inline-block; float: left; clear: both; max-width: 80%;
            font-size: 14px;
        }
        .chat-bubble-ai {
            background: transparent; color: #666; border: 1px solid #ddd;
            padding: 8px 12px; border-radius: 12px; margin: 15px auto;
            text-align: center; font-size: 0.85em; width: fit-content;
        }
        
        /* 6. 意义卡片 (AI 页面用) */
        .meaning-card {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-left: 3px solid #333;
            border-radius: 4px;
            padding: 12px;
            margin-bottom: 12px;
        }
        .card-header { font-size: 10px; color: #999; margin-bottom: 5px; letter-spacing: 1px; text-transform: uppercase; }
        .card-body { font-size: 14px; color: #222; font-weight: 500; margin-bottom: 5px; }
        .card-insight { font-size: 12px; color: #666; font-style: italic; }

        /* 7. 每日追问卡片 */
        .daily-card {
            border: 1px solid #eee; padding: 15px; border-radius: 8px;
            text-align: center; margin-bottom: 20px; background: #fff;
        }
        .daily-title { font-size: 10px; color: #999; letter-spacing: 1px; margin-bottom: 5px; }
        .daily-question { font-size: 14px; color: #333; font-weight: 500; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 🔐 页面：极简登录
# ==========================================
def render_login_page():
    inject_custom_css() # 确保在登录页也注入 CSS
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        # 极简标题
        st.markdown("""
        <h1 style='text-align: center; font-weight: 300; letter-spacing: 4px; color: #333;'>MSC</h1>
        <div style='text-align: center; color: #999; font-size: 0.8em; margin-bottom: 30px; letter-spacing: 1px;'>
        MEANING · STRUCTURE · CARE
        </div>
        """, unsafe_allow_html=True)
        
        tab = sac.tabs([
            sac.TabsItem('LOGIN', icon='box-arrow-in-right'),
            sac.TabsItem('SIGN UP', icon='person-plus'),
        ], align='center', size='sm', variant='outline')
        
        st.write("") 

        if tab == 'LOGIN':
            u = st.text_input("ID", placeholder="Username", label_visibility="collapsed")
            p = st.text_input("PASSWORD", type='password', placeholder="Password", label_visibility="collapsed")
            st.write("")
            if st.button("CONNECT SYSTEM", use_container_width=True, type="primary"):
                res = msc.login_user(u, p)
                if res:
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.session_state.nickname = res[0]['nickname']
                    st.session_state.messages = [] 
                    st.rerun()
                else: sac.alert("Access Denied", color='red', banner=True, icon='x-circle')

        else:
            nu = st.text_input("NEW ID", placeholder="New Username", label_visibility="collapsed")
            np = st.text_input("NEW PASSWORD", type='password', placeholder="New Password", label_visibility="collapsed")
            nn = st.text_input("NICKNAME", placeholder="Display Name", label_visibility="collapsed")
            nc = st.selectbox("REGION", ["China", "USA", "UK", "Japan", "Other"], label_visibility="collapsed")
            st.write("")
            if st.button("INITIALIZE IDENTITY", use_container_width=True):
                if msc.add_user(nu, np, nn, nc): 
                    sac.alert("Identity Created", color='success', banner=True, icon='check-circle')
                else: 
                    sac.alert("Creation Failed", color='error', banner=True, icon='x-circle')

# ==========================================
# 🤖 页面：AI 伴侣 (v53.2 对齐修复版)
# ==========================================
def render_ai_page(username):
    # 注入 CSS 确保风格一致
    inject_custom_css()
    st.caption("🤖 DEEPSEEK PARTNER")
    
    # 1. 获取数据
    chat_history = msc.get_active_chats(username)
    nodes_map = msc.get_active_nodes_map(username)
    
    # 2. 逐行渲染 (这就是您要求的修改)
    for msg in chat_history:
        # 定义一行：左边宽(气泡)，右边窄(圆点)
        c_msg, c_dot = st.columns([0.9, 0.1])
        
        # 左边画气泡
        with c_msg:
            with st.chat_message(msg['role']): 
                st.markdown(msg['content'])
        
        # 右边画圆点 (仅当有意义时)
        with c_dot:
            if msg['role'] == 'user' and msg['content'] in nodes_map:
                node = nodes_map[msg['content']]
                # 这里的 "●" 就是您要求的小灰点
                with st.popover("●", help="Deep Meaning"):
                    # 展开后的卡片内容
                    st.caption(f"MSC Score: {node.get('m_score', 0):.2f}")
                    st.markdown(f"**{node['care_point']}**")
                    st.info(node['insight'])
                    st.markdown(f"_{node['meaning_layer']}_")

    # 3. 输入区 (保持不变)
    if prompt := st.chat_input("Input..."):
        msc.save_chat(username, "user", prompt)
        
        # 乐观更新：先把用户的话画出来
        with st.chat_message("user"): st.markdown(prompt)

        # AI 回复
        full_history = chat_history + [{'role':'user', 'content':prompt}]
        stream = msc.get_normal_response(full_history)
        
        # 流式输出 AI 回复
        with st.chat_message("assistant"):
            try:
                response_text = st.write_stream(stream)
                msc.save_chat(username, "assistant", response_text)
            except: 
                st.error("Connection timeout")
        
        # 后台分析意义
        with st.spinner(""):
            analysis = msc.analyze_meaning_background(prompt)
            if analysis.get("valid", False):
                vec = msc.get_embedding(prompt)
                msc.save_node(username, prompt, analysis, "AI对话", vec)
                if "radar_scores" in analysis: msc.update_radar_score(username, analysis["radar_scores"])
                st.toast("Meaning Captured", icon="🌱")
        
        # 刷新页面以显示刚才生成的小圆点
        time.sleep(0.5)
        st.rerun()

# ==========================================
# 💬 页面：好友社交 (包含 AI 插话 & 私密圆点)
# ==========================================
def render_friends_page(username, unread_counts):
    inject_custom_css()
    col_list, col_chat = st.columns([0.3, 0.7])
    
    with col_list:
        st.text_input("🔍", placeholder="Search UID...", label_visibility="collapsed")
        users = msc.get_all_users(username)
        if users:
            st.markdown("---")
            for u in users:
                is_online = msc.check_is_online(u.get('last_seen'))
                status_color = "#4CAF50" if is_online else "#DDD"
                status_html = f"<span style='color:{status_color};'>•</span>"
                
                unread = unread_counts.get(u['username'], 0)
                label = f"{u['nickname']} {'🔴'+str(unread) if unread>0 else ''}"
                
                # 在按钮文字里没法直接加颜色代码，所以用 label
                if st.button(label, key=f"f_{u['username']}", use_container_width=True):
                    st.session_state.current_chat_partner = u['username']
                    msc.mark_messages_read(u['username'], username)
                    st.rerun()
        else:
            st.caption("No friends yet.")

    with col_chat:
        partner = st.session_state.current_chat_partner
        if partner:
            # 顶部栏
            c_name, c_switch = st.columns([0.8, 0.2])
            with c_name: st.markdown(f"**{partner}**")
            with c_switch: 
                auto_refresh = st.toggle("Live", value=False)
                if auto_refresh: time.sleep(3); st.rerun()

            history = msc.get_direct_messages(username, partner)
            my_nodes = msc.get_active_nodes_map(username)

            with st.container(height=500, border=False):
                chat_str_for_ai = ""
                for msg in history:
                    chat_str_for_ai += f"{msg['sender']}: {msg['content']}\n"
                    
                    c_msg, c_dot = st.columns([0.9, 0.1])
                    
                    with c_msg:
                        if msg['sender'] == 'AI':
                             st.markdown(f"<div class='chat-bubble-ai'>🤖 {msg['content']}</div>", unsafe_allow_html=True)
                        elif msg['sender'] == username:
                            st.markdown(f"<div class='chat-bubble-me'>{msg['content']}</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div class='chat-bubble-other'>{msg['content']}</div>", unsafe_allow_html=True)
                    
                    with c_dot:
                        # 🌟 隐私圆点：只显示我的，且只有在有意义时显示
                        if msg['sender'] == username and msg['content'] in my_nodes:
                            node = my_nodes[msg['content']]
                            with st.popover("●", help="My Meaning"):
                                st.caption(node['care_point'])
                                st.info(node['insight'])

            # 功能栏
            if st.button("🤖 AI Observer", use_container_width=True, help="Invoke DeepSeek"):
                 with st.spinner("..."):
                    comment = msc.get_ai_interjection(chat_str_for_ai)
                    if comment:
                        msc.send_direct_message('AI', username, comment)
                        msc.send_direct_message('AI', partner, comment)
                        st.rerun()

            if prompt := st.chat_input("Type a message..."):
                msc.send_direct_message(username, partner, prompt)
                
                with st.spinner(""):
                    analysis = msc.analyze_meaning_background(prompt)
                    if analysis.get("valid", False):
                        vec = msc.get_embedding(prompt)
                        msc.save_node(username, prompt, analysis, "私聊", vec)
                        # 共鸣检测
                        match = msc.find_resonance(vec, username, analysis)
                        if match: st.toast("Resonance detected!", icon="⚡")
                st.rerun()
        else:
            st.info("👈 Select a chat")

# ==========================================
# 🌍 页面：世界
# ==========================================
def render_world_page():
    inject_custom_css()
    st.caption("MSC GLOBAL VIEW")
    global_nodes = msc.get_global_nodes()
    t1, t2 = st.tabs(["2D MAP", "3D GALAXY"])
    with t1: msc.render_2d_world_map(global_nodes)
    with t2: msc.render_3d_galaxy(global_nodes)

# ==========================================
# 🪐 页面：星团
# ==========================================
def render_cluster_page(username):
    inject_custom_css()
    st.caption("SPONTANEOUS CLUSTERS")
    rooms = msc.get_available_rooms()
    if rooms:
        for room in rooms:
            with st.expander(f"{room['name']}", expanded=True):
                st.caption(room['description'])
                if st.button("Enter", key=f"join_{room['id']}"):
                    msc.join_room(room['id'], username)
                    msc.view_group_chat(room, username)
    else:
        st.info("No clusters formed yet.")
