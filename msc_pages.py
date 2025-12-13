### msc_pages.py (修复 TypeError & Admin 权限版) ###

import streamlit as st
import streamlit_antd_components as sac
import msc_lib as msc
import msc_viz as viz
import msc_sim as sim
import time

# ==========================================
# 🔐 登录页 (含管理员后门)
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
                # === 👑 管理员后门：直接绕过数据库，硬编码登录 ===
                # 账号: admin / 密码: msc (你可以自己改)
                if u == "admin" and p == "msc": # 注意这里，如果你改了密码，请同步修改
                    st.session_state.logged_in = True
                    st.session_state.username = "admin"
                    st.session_state.nickname = "The Architect"
                    st.session_state.is_admin = True # 标记为管理员
                    st.rerun()

                # 普通用户登录 (查询数据库)
                elif msc.login_user(u, p):
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.session_state.nickname = msc.get_nickname(u)
                    st.session_state.is_admin = False # 普通用户
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
# 👁️ 上帝视角控制台 (Admin Only)
# ==========================================
def render_admin_dashboard():
    st.markdown("## 👁️ God Mode: The Architect's View")
    
    # 1. 关键指标
    all_users = msc.get_all_users("admin") # 获取所有用户，包括 sim_users
    global_nodes = msc.get_global_nodes()
    
    k1, k2, k3 = st.columns(3)
    k1.metric("Citizens", len(all_users))
    k2.metric("Nodes", len(global_nodes))
    k3.metric("Status", "Online", delta="Vertex AI")
    
    st.divider()
    
    c1, c2 = st.columns([0.4, 0.6])
    
    with c1:
        st.markdown("### 🛠️ Genesis Engine")
        with st.container(border=True):
            if st.button("👥 Summon Archetypes (Batch)", use_container_width=True):
                n = sim.create_virtual_citizens()
                if n == 0: st.warning("All archetypes already exist.")
                else: st.success(f"Born: {n}")
                
            if st.button("💉 Inject Thoughts (Auto)", use_container_width=True, type="primary"):
                with st.status("Simulating consciousness...", expanded=True) as status:
                    logs = sim.inject_thoughts(3)
                    for log in logs: st.write(log)
                    status.update(label="Injection Complete!", state="complete", expanded=False)
                    time.sleep(1)
                    st.rerun()

        st.markdown("### 📊 Clusters")
        st.caption("Based on current vectors:")
        st.info("Cluster 0: 🔴 High Emotion\n\nCluster 1: 🔵 Logic & Tech\n\nCluster 2: 🟢 Daily Life")

    with c2:
        st.markdown("### 🌌 Real-time Galaxy")
        viz.render_cyberpunk_map(global_nodes, height="600px", is_fullscreen=False)

# ==========================================
# 🤖 AI Partner 页面
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
            # === 修复 TypeError: 严格检查 node 是否存在 ===
            if msg['role'] == 'user' and msg['content'] in nodes_map and nodes_map[msg['content']] is not None:
                node = nodes_map[msg['content']]
                st.markdown('<div class="meaning-dot-btn">', unsafe_allow_html=True)
                with st.popover("●", help="Deep Meaning"):
                    st.caption(f"MSC Score: {node.get('m_score',0.5):.2f}")
                    st.markdown(f"**{node['care_point']}**")
                    st.info(node.get('insight', 'No insight'))
                    st.caption(f"Structure: {node.get('meaning_layer', '-')}")
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
            except Exception as e:
                st.error(f"AI Connect Error: {e}")
        
        with st.spinner("Analyzing meaning..."):
            analysis = msc.analyze_meaning_background(prompt)
            if analysis.get("valid", False):
                vec = msc.get_embedding(prompt)
                msc.save_node(username, prompt, analysis, "AI对话", vec)
                if "radar_scores" in analysis: msc.update_radar_score(username, analysis["radar_scores"])
                st.toast("Meaning Captured", icon="🌱")
        
        time.sleep(0.5)
        st.rerun()

# ==========================================
# 💬 好友页面
# ==========================================
def render_friends_page(username, unread_counts):
    try:
        from streamlit_autorefresh import st_autorefresh
        st_autorefresh(interval=5000, key="msg_refresh")
    except: pass
    
    msc.update_heartbeat(username)

    col_list, col_chat = st.columns([0.25, 0.75])
    user_map = {}

    with col_list:
        st.markdown("### 💬")
        users = msc.get_all_users(username)
        
        if users:
            menu_items = []
            for u in users:
                user_map[u['nickname']] = u['username']
                is_online = msc.check_is_online(u.get('last_seen'))
                icon_name = "circle-fill" if is_online else "circle"
                icon_color = "#4CAF50" if is_online else "#CCCCCC"
                
                unread = unread_counts.get(u['username'], 0)
                tag_val = sac.Tag(str(unread), color='red', bordered=False) if unread > 0 else None
                desc = "Online" if is_online else "Offline"

                menu_items.append(sac.MenuItem(
                    label=u['nickname'], 
                    icon=sac.BsIcon(name=icon_name, color=icon_color),
                    tag=tag_val,
                    description=desc
                ))
            
            selected_nickname = sac.menu(
                menu_items, 
                index=0, 
                format_func='title', 
                size='md', 
                variant='light',
                indent=10,
                open_all=True
            )
            
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
                    
                    if msg['sender'] == username and msg['content'] in nodes_map and nodes_map[msg['content']] is not None:
                        node = nodes_map[msg['content']]
                        st.markdown('<div class="meaning-dot-btn">', unsafe_allow_html=True)
                        with st.popover("●"):
                            st.caption(f"Score: {node.get('m_score',0.5):.2f}")
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
# 🌍 世界页面
# ==========================================
def render_world_page():
    st.caption("MSC GLOBAL VIEW")
    global_nodes = msc.get_global_nodes()
    
    t1, t2 = st.tabs(["2D MAP", "3D GALAXY"])
    
    with t1:
        viz.render_2d_world_map(global_nodes)
        
    with t2:
        viz.render_3d_galaxy(global_nodes)
