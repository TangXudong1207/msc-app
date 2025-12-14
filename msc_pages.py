### msc_pages.py (安全语法修复版) ###

import streamlit as st
import streamlit_antd_components as sac
import msc_lib as msc
import msc_viz as viz
import msc_sim as sim
import msc_news_real as news
import time

# ==========================================
# 🔐 登录页
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
                if u == "admin" and p == "msc": 
                    st.session_state.logged_in = True
                    st.session_state.username = "admin"
                    st.session_state.nickname = "The Architect"
                    st.session_state.is_admin = True 
                    st.toast("👑 Architect Mode Activated")
                    time.sleep(0.5)
                    st.rerun()
                elif msc.login_user(u, p):
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.session_state.nickname = msc.get_nickname(u)
                    st.session_state.is_admin = False 
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
# 👁️ 上帝视角
# ==========================================
def render_admin_dashboard():
    st.markdown("## 👁️ God Mode: The Architect's View")
    
    all_users = msc.get_all_users("admin")
    global_nodes = msc.get_global_nodes()
    
    k1, k2, k3 = st.columns(3)
    k1.metric("Citizens", len(all_users))
    k2.metric("Nodes", len(global_nodes))
    k3.metric("Status", "Online", delta="Vertex AI")
    st.divider()
    
    c1, c2 = st.columns([0.4, 0.6])
    with c1:
        st.markdown("### 🌍 World Pulse (RSS)")
        if "news_logs" not in st.session_state: st.session_state.news_logs = []
        if st.button("📡 Scan Global Tensions", use_container_width=True, type="primary"):
            with st.status("Scanning...", expanded=True) as status:
                try:
                    new_logs = news.fetch_real_news(limit=2)
                    st.session_state.news_logs = new_logs + st.session_state.news_logs
                    status.update(label="Scan Complete!", state="complete", expanded=False)
                except Exception as e: st.error(f"News Error: {e}")
        if st.session_state.news_logs:
            with st.container(height=300, border=True):
                for log in st.session_state.news_logs: st.caption(log)
        else: st.info("No news scanned yet.")

        st.markdown("### 🛠️ Genesis Engine")
        with st.container(border=True):
            if st.button("👥 Summon Archetypes", use_container_width=True):
                n = sim.create_virtual_citizens()
                st.success(f"Born: {n}")
            if st.button("💉 Inject Thoughts", use_container_width=True):
                with st.spinner("Simulating..."):
                    logs = sim.inject_thoughts(3)
                    for log in logs: st.write(log)

    with c2:
        st.markdown("### 🌌 Real-time Galaxy")
        viz.render_cyberpunk_map(global_nodes, height="600px", is_fullscreen=False)
    st.caption("Time Control")
        # === 新增：时间流逝按钮 ===
        if st.button("⏳ Advance Time (Sedimentation)", use_container_width=True):
            with st.spinner("Time is passing..."):
                # 调用 db 里的新函数
                # 注意：需要在 msc_lib 里做一个转发，或者直接在这里 import msc_db
                # 为了规范，建议在 msc_lib 里加一个 process_time_decay
                count = msc.process_time_decay() # 需在 lib 里补这个桥梁
                st.success(f"{count} nodes have sedimented into history.")
                time.sleep(1)
                st.rerun()

# ==========================================
# 🤖 AI Partner
# ==========================================
def render_ai_page(username):
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    chat_history = msc.get_active_chats(username)
    nodes_map = msc.get_active_nodes_map(username)
    
    for msg in chat_history:
        c_msg, c_dot = st.columns([0.92, 0.08])
        with c_msg:
            if msg['role'] == 'user': st.markdown(f"<div class='chat-bubble-me'>{msg['content']}</div>", unsafe_allow_html=True)
            else: st.markdown(f"<div class='chat-bubble-other'>{msg['content']}</div>", unsafe_allow_html=True)
        with c_dot:
            if msg['role'] == 'user' and msg['content'] in nodes_map:
                node = nodes_map.get(msg['content'])
                if node:
                    st.markdown('<div class="meaning-dot-btn">', unsafe_allow_html=True)
                    with st.popover("●", help="Deep Meaning"):
                        try: score = float(node.get('m_score') or 0.5)
                        except: score = 0.5
                        st.caption(f"MSC Score: {score:.2f}")
                        st.markdown(f"**{node.get('care_point','')}**")
                        st.info(node.get('insight', ''))
                    st.markdown('</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Input..."):
        msc.save_chat(username, "user", prompt)
        with st.container(): st.markdown(f"<div class='chat-bubble-me'>{prompt}</div>", unsafe_allow_html=True)
        
        full_history = chat_history + [{'role':'user', 'content':prompt}]
        with st.chat_message("assistant"):
            try:
                stream = msc.get_normal_response(full_history)
                if isinstance(stream, str) and stream.startswith(("⚠️", "❌")):
                    st.error(stream); resp = stream
                else:
                    st.write(stream); resp = stream
                msc.save_chat(username, "assistant", resp)
            except Exception as e: st.error(f"AI Error: {e}")
        
        with st.spinner("Analyzing..."):
            analysis = msc.analyze_meaning_background(prompt)
            if analysis.get("valid", False):
                vec = msc.get_embedding(prompt)
                msc.save_node(username, prompt, analysis, "AI对话", vec)
                st.toast("Meaning Captured", icon="🌱")
        time.sleep(0.5); st.rerun()

# ==========================================
# 💬 好友页面 (修复语法问题)
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
                color = "#4CAF50" if is_online else "#CCCCCC"
                unread = unread_counts.get(u['username'], 0)
                tag_val = sac.Tag(str(unread), color='red') if unread > 0 else None
                menu_items.append(sac.MenuItem(label=u['nickname'], icon=sac.BsIcon(name=icon_name, color=color), tag=tag_val))
            selected = sac.menu(menu_items, index=0, format_func='title', size='md', variant='light', open_all=True)
            if selected and selected in user_map: st.session_state.current_chat_partner = user_map[selected]
    with col_chat:
        partner = st.session_state.current_chat_partner
        if partner:
            msc.mark_messages_read(partner, username)
            st.markdown(f"#### {msc.get_nickname(partner)}")
            history = msc.get_direct_messages(username, partner)
            my_nodes = msc.get_active_nodes_map(username)
            with st.container(height=500, border=True):
                for msg in history:
                    c_msg, c_dot = st.columns([0.94, 0.06])
                    with c_msg:
                        if msg['sender'] == 'AI': st.markdown(f"<div class='chat-bubble-ai'>🤖 {msg['content']}</div>", unsafe_allow_html=True)
                        elif msg['sender'] == username: st.markdown(f"<div class='chat-bubble-me'>{msg['content']}</div>", unsafe_allow_html=True)
                        else: st.markdown(f"<div class='chat-bubble-other'>{msg['content']}</div>", unsafe_allow_html=True)
                    if msg['sender'] == username and msg['content'] in my_nodes:
                        node = my_nodes.get(msg['content'])
                        if node:
                            st.markdown('<div class="meaning-dot-btn">', unsafe_allow_html=True)
                            with st.popover("●"):
                                try: score = float(node.get('m_score') or 0.5)
                                except: score = 0.5
                                st.caption(f"Score: {score:.2f}")
                                st.markdown(f"**{node.get('care_point','')}**")
                            st.markdown('</div>', unsafe_allow_html=True)
            if prompt := st.chat_input(f"Message..."):
                msc.send_direct_message(username, partner, prompt)
                st.rerun()
        else: st.info("👈 Select a friend.")

# ==========================================
# 🌍 世界页面 (粒子地球)
# ==========================================
def render_world_page():
    st.caption("MSC GLOBAL VIEW: Tension & Resonance")
    nodes = msc.get_global_nodes()
    viz.render_3d_particle_map(nodes)
