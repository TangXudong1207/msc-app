import streamlit as st
import msc_lib as msc
import time
import json
import streamlit_antd_components as sac

# ==========================================
# 🔐 登录页
# ==========================================
def render_login_page():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("""
        <h1 style='text-align: center; font-weight: 300; letter-spacing: 4px; color: #333;'>MSC</h1>
        <div style='text-align: center; color: #999; font-size: 0.8em; margin-bottom: 30px; letter-spacing: 1px;'>
        MEANING · STRUCTURE · CARE
        </div>
        """, unsafe_allow_html=True)
        
        tab = sac.tabs([sac.TabsItem('LOGIN'), sac.TabsItem('SIGN UP')], align='center', size='sm', variant='outline')
        st.write("") 

        if tab == 'LOGIN':
            u = st.text_input("ID", placeholder="Username", label_visibility="collapsed")
            p = st.text_input("PASSWORD", type='password', placeholder="Password", label_visibility="collapsed")
            st.write("")
            if st.button("CONNECT", use_container_width=True, type="primary"):
                res = msc.login_user(u, p)
                if res:
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.session_state.nickname = res[0]['nickname']
                    st.session_state.messages = [] 
                    st.rerun()
                else: sac.alert("Access Denied", color='red')
        else:
            nu = st.text_input("NEW ID", placeholder="New Username", label_visibility="collapsed")
            np = st.text_input("NEW PASSWORD", type='password', placeholder="New Password", label_visibility="collapsed")
            nn = st.text_input("NICKNAME", placeholder="Display Name", label_visibility="collapsed")
            nc = st.selectbox("REGION", ["China", "USA", "UK", "Other"], label_visibility="collapsed")
            st.write("")
            if st.button("INITIALIZE", use_container_width=True):
                if msc.add_user(nu, np, nn, nc): sac.alert("Created", color='success')
                else: sac.alert("Failed", color='error')

# ==========================================
# 🤖 页面：AI 伴侣 (严格对齐版)
# ==========================================
def render_ai_page(username):
    # 顶部留白
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    chat_history = msc.get_active_chats(username)
    nodes_map = msc.get_active_nodes_map(username)
    
    # 🌟 核心：逐行渲染
    for msg in chat_history:
        # 定义一行：左92%(对话)，右8%(圆点)
        c_msg, c_dot = st.columns([0.92, 0.08])
        
        with c_msg:
            # 使用 avatar=None，配合 main.py 的 CSS 隐藏默认头像
            if msg['role'] == 'user':
                st.markdown(f"<div class='chat-bubble-me'>{msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-bubble-other'>{msg['content']}</div>", unsafe_allow_html=True)
        
        with c_dot:
            # 只有用户发送的、且有意义的消息，才在同一行显示圆点
            if msg['role'] == 'user' and msg['content'] in nodes_map:
                node = nodes_map[msg['content']]
                # 包裹在 div 里以便 CSS 控制垂直居中
                st.markdown('<div class="meaning-dot-btn">', unsafe_allow_html=True)
                with st.popover("●", help="Deep Meaning"):
                    st.caption(f"MSC Score: {node.get('m_score', 0):.2f}")
                    st.markdown(f"**{node['care_point']}**")
                    st.info(node['insight'])
                    st.caption(f"Structure: {node['meaning_layer']}")
                st.markdown('</div>', unsafe_allow_html=True)

    # 底部输入
    if prompt := st.chat_input("Input..."):
        msc.save_chat(username, "user", prompt)
        
        # 乐观更新
        with st.container():
             st.markdown(f"<div class='chat-bubble-me'>{prompt}</div>", unsafe_allow_html=True)
        
        # AI 回复
        full_history = chat_history + [{'role':'user', 'content':prompt}]
        try:
            resp = msc.get_normal_response(full_history)
            reply = resp.choices[0].message.content
            msc.save_chat(username, "assistant", reply)
        except: pass
        
        # 意义分析
        with st.spinner(""):
            analysis = msc.analyze_meaning_background(prompt)
            if analysis.get("valid", False):
                vec = msc.get_embedding(prompt)
                msc.save_node(username, prompt, analysis, "AI对话", vec)
                if "radar_scores" in analysis: msc.update_radar_score(username, analysis["radar_scores"])
        
        time.sleep(0.5)
        st.rerun()

# ==========================================
# 💬 页面：好友社交 (严格对齐版)
# ==========================================
def render_friends_page(username, unread_counts):
    col_list, col_chat = st.columns([0.3, 0.7])
    
    # 1. 好友列表
    with col_list:
        st.caption("CONTACTS")
        users = msc.get_all_users(username)
        if users:
            for u in users:
                is_online = msc.check_is_online(u.get('last_seen'))
                color = "#4CAF50" if is_online else "#DDD"
                unread = unread_counts.get(u['username'], 0)
                label = f"{u['nickname']}"
                if unread > 0: label += f" 🔴 {unread}"
                
                if st.button(label, key=f"f_{u['username']}", use_container_width=True):
                    st.session_state.current_chat_partner = u['username']
                    msc.mark_messages_read(u['username'], username)
                    st.rerun()
        else:
            st.caption("No friends yet.")

    # 2. 聊天窗口
    with col_chat:
        partner = st.session_state.current_chat_partner
        if partner:
            # 顶部栏
            c_name, c_switch = st.columns([0.8, 0.2])
            with c_name: st.markdown(f"**{partner}**")
            with c_switch: 
                if st.button("🤖", help="AI Observer"):
                    # 简化处理，实际可复用 msc.get_ai_interjection
                    pass 

            history = msc.get_direct_messages(username, partner)
            my_nodes = msc.get_active_nodes_map(username)

            with st.container(height=500, border=False):
                for msg in history:
                    # 🌟 核心：逐行渲染，确保对齐
                    c_msg, c_dot = st.columns([0.92, 0.08])
                    
                    with c_msg:
                        if msg['sender'] == 'AI':
                            st.markdown(f"<div class='chat-bubble-ai'>🤖 {msg['content']}</div>", unsafe_allow_html=True)
                        elif msg['sender'] == username:
                            st.markdown(f"<div class='chat-bubble-me'>{msg['content']}</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div class='chat-bubble-other'>{msg['content']}</div>", unsafe_allow_html=True)
                    
                    with c_dot:
                        # 只有我自己发的、有意义的消息，才在同一行显示点
                        if msg['sender'] == username and msg['content'] in my_nodes:
                            node = my_nodes[msg['content']]
                            st.markdown('<div class="meaning-dot-btn">', unsafe_allow_html=True)
                            with st.popover("●"):
                                st.info(node['insight'])
                            st.markdown('</div>', unsafe_allow_html=True)

            if prompt := st.chat_input("Type..."):
                msc.send_direct_message(username, partner, prompt)
                with st.spinner(""):
                    analysis = msc.analyze_meaning_background(prompt)
                    if analysis.get("valid", False):
                        vec = msc.get_embedding(prompt)
                        msc.save_node(username, prompt, analysis, "私聊", vec)
                        match = msc.find_resonance(vec, username, analysis)
                        if match: st.toast("Resonance!", icon="⚡")
                st.rerun()
        else:
            st.info("👈 Select a friend")

# ==========================================
# 🌍 页面：世界
# ==========================================
def render_world_page():
    st.caption("MSC GLOBAL VIEW")
    global_nodes = msc.get_global_nodes()
    t1, t2 = st.tabs(["2D MAP", "3D GALAXY"])
    with t1: msc.render_2d_world_map(global_nodes)
    with t2: msc.render_3d_galaxy(global_nodes)

# ==========================================
# 🪐 页面：星团
# ==========================================
def render_cluster_page(username):
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
