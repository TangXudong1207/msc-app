import streamlit as st
import msc_lib as msc
import time
import json
import streamlit_antd_components as sac

# ==========================================
# 🔐 页面：极简登录
# ==========================================
def render_login_page():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br><br><h1 style='text-align:center;font-weight:300;letter-spacing:4px'>MSC</h1>", unsafe_allow_html=True)
        st.markdown("<div style='text-align:center;color:#999;font-size:0.8em;letter-spacing:1px;margin-bottom:30px'>MEANING · STRUCTURE · CARE</div>", unsafe_allow_html=True)
        
        tab = sac.tabs(['LOGIN', 'SIGN UP'], align='center', size='sm', variant='outline')
        st.write("") 

        if tab == 'LOGIN':
            u = st.text_input("ID", placeholder="Username", label_visibility="collapsed")
            p = st.text_input("PASSWORD", type='password', placeholder="Password", label_visibility="collapsed")
            st.write("")
            if st.button("CONNECT", use_container_width=True, type="primary"):
                if msc.login_user(u, p):
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.session_state.nickname = msc.get_nickname(u)
                    st.rerun()
                else: sac.alert("Access Denied", color='red')
        else:
            nu = st.text_input("NEW ID", label_visibility="collapsed")
            np = st.text_input("NEW PW", type='password', label_visibility="collapsed")
            nn = st.text_input("NICK", label_visibility="collapsed")
            nc = st.selectbox("REGION", ["China", "USA", "UK"], label_visibility="collapsed")
            st.write("")
            if st.button("INITIALIZE", use_container_width=True):
                if msc.add_user(nu, np, nn, nc): sac.alert("Created", color='success')
                else: sac.alert("Failed", color='error')

# ==========================================
# 🤖 页面：AI 伴侣 (修复数值报错)
# ==========================================
def render_ai_page(username):
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    chat_history = msc.get_active_chats(username)
    nodes_map = msc.get_active_nodes_map(username)
    
    for msg in chat_history:
        c_msg, c_dot = st.columns([0.92, 0.08])
        
        with c_msg:
            if msg['role'] == 'user':
                st.markdown(f"<div class='chat-bubble-me'>{msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-bubble-other'>{msg['content']}</div>", unsafe_allow_html=True)
        
        with c_dot:
            if msg['role'] == 'user' and msg['content'] in nodes_map:
                node = nodes_map[msg['content']]
                st.markdown('<div class="meaning-dot-btn">', unsafe_allow_html=True)
                with st.popover("●", help="Deep Meaning"):
                    # 🌟 核心修复：强制类型转换，处理 None 值
                    try:
                        raw_m = node.get('m_score')
                        raw_l = node.get('logic_score')
                        # 优先取 m_score，如果没有则取 logic_score，如果还没有则 0.5
                        score_val = float(raw_m) if raw_m is not None else (float(raw_l) if raw_l is not None else 0.5)
                    except:
                        score_val = 0.5
                    
                    st.caption(f"MSC Score: {score_val:.2f}")
                    st.markdown(f"**{node['care_point']}**")
                    st.info(node['insight'])
                    st.caption(f"Structure: {node['meaning_layer']}")
                st.markdown('</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Input..."):
        msc.save_chat(username, "user", prompt)
        with st.container(): st.markdown(f"<div class='chat-bubble-me'>{prompt}</div>", unsafe_allow_html=True)
        
        full_history = chat_history + [{'role':'user', 'content':prompt}]
        with st.chat_message("assistant"):
            try:
                stream = msc.get_normal_response(full_history)
                resp = st.write_stream(stream)
                msc.save_chat(username, "assistant", resp)
            except: pass
        
        with st.spinner(""):
            analysis = msc.analyze_meaning_background(prompt)
            if analysis.get("valid", False):
                vec = msc.get_embedding(prompt)
                msc.save_node(username, prompt, analysis, "AI对话", vec)
                if "radar_scores" in analysis: msc.update_radar_score(username, analysis["radar_scores"])
                st.toast("Meaning Captured", icon="🌱")
        time.sleep(0.5); st.rerun()

# ==========================================
# 💬 页面：好友社交 (同步修复)
# ==========================================
def render_friends_page(username, unread_counts):
    col_list, col_chat = st.columns([0.3, 0.7])
    
    with col_list:
        st.caption("CONTACTS")
        users = msc.get_all_users(username)
        if users:
            for u in users:
                is_online = msc.check_is_online(u.get('last_seen'))
                status = "🟢" if is_online else "⚪"
                unread = unread_counts.get(u['username'], 0)
                label = f"{status} {u['nickname']} {'🔴'+str(unread) if unread>0 else ''}"
                
                if st.button(label, key=f"f_{u['username']}", use_container_width=True):
                    st.session_state.current_chat_partner = u['username']
                    msc.mark_messages_read(u['username'], username)
                    st.rerun()
        else:
            st.caption("No friends yet.")

    with col_chat:
        partner = st.session_state.current_chat_partner
        if partner:
            c1, c2 = st.columns([0.8, 0.2])
            with c1: st.markdown(f"**{partner}**")
            with c2: 
                if st.button("🤖", help="AI Observer"): pass 

            history = msc.get_direct_messages(username, partner)
            my_nodes = msc.get_active_nodes_map(username)

            with st.container(height=500, border=False):
                for msg in history:
                    c_msg, c_dot = st.columns([0.92, 0.08])
                    with c_msg:
                        if msg['sender'] == 'AI':
                            st.markdown(f"<div class='chat-bubble-ai'>🤖 {msg['content']}</div>", unsafe_allow_html=True)
                        elif msg['sender'] == username:
                            st.markdown(f"<div class='chat-bubble-me'>{msg['content']}</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div class='chat-bubble-other'>{msg['content']}</div>", unsafe_allow_html=True)
                    with c_dot:
                        if msg['sender'] == username and msg['content'] in my_nodes:
                            node = my_nodes[msg['content']]
                            st.markdown('<div class="meaning-dot-btn">', unsafe_allow_html=True)
                            with st.popover("●"):
                                # 🌟 同样的修复
                                try:
                                    raw_m = node.get('m_score')
                                    score_val = float(raw_m) if raw_m is not None else 0.5
                                except: score_val = 0.5
                                
                                st.caption(f"Score: {score_val:.2f}")
                                st.markdown(f"**{node['care_point']}**")
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

# ... (世界和星团页面保持不变) ...
def render_world_page():
    st.caption("MSC GLOBAL VIEW")
    global_nodes = msc.get_global_nodes()
    t1, t2 = st.tabs(["2D MAP", "3D GALAXY"])
    with t1: msc.render_2d_world_map(global_nodes)
    with t2: msc.render_3d_galaxy(global_nodes)

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
