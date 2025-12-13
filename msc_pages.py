### msc_pages.py (全功能完整版) ###

import streamlit as st
import streamlit_antd_components as sac
import msc_lib as msc
import msc_viz as viz
import msc_sim as sim
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
                # === 👑 强制 Admin 调试逻辑 ===
                if u == "admin": 
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
# 👁️ 上帝视角 (Admin)
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
# 🤖 页面：AI 伴侣 (防弹版)
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
            # 只有当消息对应有节点数据时才显示
            if msg['role'] == 'user' and msg['content'] in nodes_map:
                node = nodes_map.get(msg['content'])
                
                # === 修复核心：绝对安全的数值处理 ===
                if node:
                    st.markdown('<div class="meaning-dot-btn">', unsafe_allow_html=True)
                    with st.popover("●", help="Deep Meaning"):
                        # 1. 尝试获取分数
                        raw_score = node.get('m_score')
                        
                        # 2. 强制类型转换，如果是 None 或非数字，直接给默认值
                        try:
                            score_val = float(raw_score)
                        except (TypeError, ValueError):
                            score_val = 0.5
                        
                        # 3. 安全格式化
                        st.caption(f"MSC Score: {score_val:.2f}")
                        
                        # 4. 其他信息
                        care_point = node.get('care_point') or "Unknown"
                        insight = node.get('insight') or "No insight generated"
                        layer = node.get('meaning_layer') or "-"
                        
                        st.markdown(f"**{care_point}**")
                        st.info(insight)
                        st.caption(f"Structure: {layer}")
                    st.markdown('</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Input..."):
        msc.save_chat(username, "user", prompt)
        with st.container(): st.markdown(f"<div class='chat-bubble-me'>{prompt}</div>", unsafe_allow_html=True)
        
        full_history = chat_history + [{'role':'user', 'content':prompt}]
        with st.chat_message("assistant"):
            try:
                # 非流式调用
                stream = msc.get_normal_response(full_history)
                # 检查是否为字符串错误
                if isinstance(stream, str) and stream.startswith(("⚠️", "❌")):
                    st.error(stream)
                    resp = stream
                else:
                    # 如果是普通字符串，直接显示
                    st.write(stream)
                    resp = stream
                
                msc.save_chat(username, "assistant", resp)
            except Exception as e:
                st.error(f"AI Error: {e}")
        
        with st.spinner("Analyzing..."):
            analysis = msc.analyze_meaning_background(prompt)
            if analysis.get("valid", False):
                vec = msc.get_embedding(prompt)
                msc.save_node(username, prompt, analysis, "AI对话", vec)
                if "radar_scores" in analysis: msc.update_radar_score(username, analysis["radar_scores"])
                st.toast("Meaning Captured", icon="🌱")
        
        time.sleep(0.5)
        st.rerun()
# ==========================================
# 💬 好友页面 (已修复报错)
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
                unread = unread_counts.get(u['username'], 0)
                tag_val = sac.Tag(str(unread), color='red') if unread > 0 else None
                menu_items.append(sac.MenuItem(label=u['nickname'], icon=sac.BsIcon(name=icon_name, color="#4CAF50"), tag=tag_val))
            
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
                        # === 修复核心：好友页面也加上了安全检查 ===
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
                with st.spinner("Analyzing..."):
                    analysis = msc.analyze_meaning_background(prompt)
                    if analysis.get("valid", False):
                        vec = msc.get_embedding(prompt)
                        msc.save_node(username, prompt, analysis, "私聊", vec)
                        match = msc.find_resonance(vec, username, analysis)
                        if match: st.toast(f"Resonance!", icon="⚡")
                st.rerun()
        else:
            st.info("👈 Select a friend.")

# ==========================================
# 🌍 世界页面 (完整功能版)
# ==========================================
def render_world_page():
    st.caption("MSC GLOBAL VIEW")
    global_nodes = msc.get_global_nodes()
    
    t1, t2 = st.tabs(["2D MAP", "3D GALAXY"])
    
    with t1:
        viz.render_2d_world_map(global_nodes)
        
    with t2:
        viz.render_3d_galaxy(global_nodes)
