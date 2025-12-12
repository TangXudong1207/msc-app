### msc_pages.py (修复版) ###

import streamlit as st
import streamlit_antd_components as sac
import msc_lib as msc
import msc_viz as viz  # 确保引用了视觉库
import time
import json

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
# 🤖 页面：AI 伴侣
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
                    try:
                        raw_m = node.get('m_score')
                        raw_l = node.get('logic_score')
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
# 💬 页面：好友社交 (修复版)
# ==========================================
def render_friends_page(username, unread_counts):
    # 尝试引入自动刷新，如果没安装插件则跳过
    try:
        from streamlit_autorefresh import st_autorefresh
        st_autorefresh(interval=5000, key="msg_refresh")
    except: pass
    
    msc.update_heartbeat(username)

    col_list, col_chat = st.columns([0.25, 0.75])
    
    # 建立一个字典，用于通过昵称反查 username
    user_map = {}

    with col_list:
        st.markdown("### 💬")
        users = msc.get_all_users(username)
        
        if users:
            menu_items = []
            for u in users:
                # 记录映射关系：昵称 -> 用户名
                # 注意：如果昵称重复，这里会有 Bug，建议后期强制昵称唯一
                user_map[u['nickname']] = u['username']

                is_online = msc.check_is_online(u.get('last_seen'))
                icon_name = "circle-fill" if is_online else "circle"
                icon_color = "#4CAF50" if is_online else "#CCCCCC"
                
                unread = unread_counts.get(u['username'], 0)
                tag_val = sac.Tag(str(unread), color='red', bordered=False) if unread > 0 else None
                desc = "Online" if is_online else "Offline"

                # 🔧 修复点：去掉了 key 参数
                menu_items.append(sac.MenuItem(
                    label=u['nickname'], 
                    icon=sac.BsIcon(name=icon_name, color=icon_color),
                    tag=tag_val,
                    description=desc
                ))
            
            # sac.menu 返回的是 label (即昵称)
            selected_nickname = sac.menu(
                menu_items, 
                index=0, 
                format_func='title', 
                size='md', 
                variant='light',
                indent=10,
                open_all=True
            )
            
            # 通过字典反查真正的 username
            if selected_nickname and selected_nickname in user_map:
                st.session_state.current_chat_partner = user_map[selected_nickname]

        else:
            st.caption("No citizens found.")

    with col_chat:
        partner = st.session_state.current_chat_partner
        if partner:
            msc.mark_messages_read(partner, username)
            
            header_col1, header_col2 = st.columns([0.9, 0.1])
            with header_col1: 
                # 显示对方昵称
                st.markdown(f"#### {msc.get_nickname(partner)}")
            with header_col2: 
                if st.button("👁️", help="AI Insight"): 
                    st.toast("DeepSeek is observing...", icon="🧠")

            history = msc.get_direct_messages(username, partner)
            my_nodes = msc.get_active_nodes_map(username)

            with st.container(height=600, border=True):
                if not history:
                    st.caption("No messages yet. Say hi!")
                
                for msg in history:
                    c_msg, c_dot = st.columns([0.94, 0.06])
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
                                try: score_val = float(node.get('m_score', 0.5))
                                except: score_val = 0.5
                                st.caption(f"MSC Score: {score_val:.2f}")
                                st.markdown(f"**{node['care_point']}**")
                                st.info(node.get('insight', ''))
                            st.markdown('</div>', unsafe_allow_html=True)

            if prompt := st.chat_input(f"Message {msc.get_nickname(partner)}..."):
                msc.send_direct_message(username, partner, prompt)
                with st.spinner("Analyzing meaning..."):
                    analysis = msc.analyze_meaning_background(prompt)
                    if analysis.get("valid", False):
                        vec = msc.get_embedding(prompt)
                        msc.save_node(username, prompt, analysis, "私聊", vec)
                        match = msc.find_resonance(vec, username, analysis)
                        if match: st.toast(f"Resonance with {match['user']}!", icon="⚡")
                st.rerun()
        else:
            st.info("👈 Select a friend from the left to connect.")

# ==========================================
# 🌍 页面：世界视图 (修复版)
# ==========================================
def render_world_page():
    st.caption("MSC GLOBAL VIEW")
    # 🔧 修复点：改用 msc (lib) 获取数据，用 viz (visualizer) 画图
    global_nodes = msc.get_global_nodes()
    
    t1, t2 = st.tabs(["2D MAP", "3D GALAXY"])
    
    with t1:
        # 🔧 修复点：调用 viz 而不是 msc
        viz.render_2d_world_map(global_nodes)
        
    with t2:
        # 🔧 修复点：调用 viz 而不是 msc
        viz.render_3d_galaxy(global_nodes)

# ==========================================
# 🌌 页面：星团
# ==========================================
def render_cluster_page(username):
    st.caption("SPONTANEOUS CLUSTERS")
    st.info("Coming soon...")
