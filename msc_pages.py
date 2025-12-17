import streamlit as st
import streamlit_antd_components as sac
import msc_lib as msc
import msc_viz as viz
import msc_sim as sim
import time
import pandas as pd
import json

# ==========================================
# 🔐 登录页：极简大门
# ==========================================
def render_login_page():
    # 使用 3列布局将内容居中
    c1, c2, c3 = st.columns([1, 2, 1])
    
    with c2:
        st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
        # 标题设计
        st.markdown("""
        <div style='text-align: center;'>
            <h1 style='font-family: "JetBrains Mono", monospace; font-weight: 700; font-size: 3em; margin-bottom: 0;'>MSC</h1>
            <p style='color: #888; letter-spacing: 3px; font-size: 0.9em; margin-top: 10px;'>MEANING · STRUCTURE · CARE</p>
        </div>
        <div style='height: 40px;'></div>
        """, unsafe_allow_html=True)
        
        # 登录卡片
        with st.container(border=True):
            tab = sac.tabs(['LOGIN', 'SIGN UP'], align='center', size='md', variant='outline')
            st.write("") 

            if tab == 'LOGIN':
                u = st.text_input("IDENTITY", placeholder="Username", label_visibility="collapsed")
                p = st.text_input("KEY", type='password', placeholder="Password", label_visibility="collapsed")
                st.write("")
                if st.button("CONNECT UPLINK", use_container_width=True, type="primary"):
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
                    else: st.error("Access Denied")
            else:
                nu = st.text_input("NEW ID", label_visibility="collapsed", placeholder="Username")
                np = st.text_input("NEW PW", type='password', label_visibility="collapsed", placeholder="Password")
                nn = st.text_input("NICK", label_visibility="collapsed", placeholder="Display Name")
                nc = st.selectbox("REGION", ["China", "USA", "UK"], label_visibility="collapsed")
                st.write("")
                if st.button("INITIALIZE PROTOCOL", use_container_width=True):
                    if msc.add_user(nu, np, nn, nc): st.success("Identity Created. Please Login.")
                    else: st.error("Initialization Failed")

# ==========================================
# 👁️ 上帝视角 (Admin)
# ==========================================
def render_admin_dashboard():
    st.markdown("## 👁️ Overseer Terminal")
    st.caption("v75.3 Data-Hologram / System Status: ONLINE")
    
    all_users = msc.get_all_users("admin")
    global_nodes = msc.get_global_nodes()
    
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Citizens", len(all_users), delta="Live")
    k2.metric("Nodes", len(global_nodes), delta="Global")
    
    avg_care = 0
    if global_nodes:
        total_care = sum([float(n.get('logic_score', 0)) for n in global_nodes])
        avg_care = total_care / len(global_nodes)
    k3.metric("Avg. Meaning", f"{avg_care:.2f}", delta="Quality")
    k4.metric("Engine", "Vertex/DeepSeek", delta="Active")
    
    st.divider()
    
    tabs = st.tabs(["🌍 Global Pulse", "🛠️ Genesis Engine", "👥 Citizen Registry", "🧬 Node Inspector"])
    
    with tabs[0]:
        c1, c2 = st.columns([0.7, 0.3])
        with c1:
            st.markdown("### 🌌 Real-time Connection Map")
            viz.render_cyberpunk_map(global_nodes, height="500px", is_fullscreen=False)
        with c2:
            st.markdown("### 🎨 Spectrum")
            st.info("Spectrum Analysis Module loading...")
            st.caption("Dominant Vibe: **Searching...**")

    with tabs[1]:
        st.markdown("### ⚡ Genesis Protocol")
        c_gen1, c_gen2 = st.columns(2)
        with c_gen1:
            with st.container(border=True):
                st.markdown("#### 1. Summon Archetypes")
                count_sim = st.slider("Quantity", 1, 5, 2)
                if st.button("👥 Summon Virtual Citizens", use_container_width=True):
                    n = sim.create_virtual_citizens(count_sim)
                    st.success(f"Summoned {n} entities.")
                    time.sleep(1)
                    st.rerun()
        with c_gen2:
            with st.container(border=True):
                st.markdown("#### 2. Inject Thoughts")
                count_thought = st.slider("Thought Batch Size", 1, 3, 1)
                if st.button("💉 Inject Semantic Flow", use_container_width=True, type="primary"):
                    with st.status("Simulating neural activity...", expanded=True):
                        logs = sim.inject_thoughts(count_thought)
                        for log in logs: st.text(log)
    
    with tabs[2]:
        st.markdown("### 👥 Registry")
        if all_users:
            df_users = pd.DataFrame(all_users)
            st.dataframe(df_users[['username', 'nickname', 'last_seen']], use_container_width=True, hide_index=True)

    with tabs[3]:
        st.markdown("### 🧬 Data Inspector")
        if global_nodes:
            debug_data = []
            for n in global_nodes:
                loc_str = "-"
                try:
                    l = json.loads(n.get('location')) if isinstance(n.get('location'), str) else n.get('location')
                    if l: loc_str = f"{l.get('city','Unknown')}"
                except: pass
                debug_data.append({"User": n['username'], "Content": n['content'], "Score": n.get('logic_score'), "Loc": loc_str})
            st.dataframe(pd.DataFrame(debug_data), use_container_width=True, height=500)

# ==========================================
# 🤖 AI Partner (沉浸式优化)
# ==========================================
def render_ai_page(username):
    # 顶部留白
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    # 1. 加载历史 (此时是极速的，因为读数据库有缓存了！)
    chat_history = msc.get_active_chats(username)
    nodes_map = msc.get_active_nodes_map(username)
    
    # 2. 渲染历史消息
    for msg in chat_history:
        c_msg, c_dot = st.columns([0.92, 0.08])
        with c_msg:
            if msg['role'] == 'user':
                st.markdown(f"<div class='chat-bubble-me'>{msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-bubble-ai'>{msg['content']}</div>", unsafe_allow_html=True)
        
        # 小圆点 (保持不变)
        with c_dot:
            if msg['role'] == 'user' and msg['content'] in nodes_map:
                node = nodes_map.get(msg['content'])
                if node:
                    st.markdown('<div class="meaning-dot-btn">', unsafe_allow_html=True)
                    with st.popover("●"):
                        try: score_val = float(node.get('m_score') or 0.5)
                        except: score_val = 0.5
                        st.caption(f"Score: {score_val:.2f}")
                        st.markdown(f"**{node.get('care_point', 'Unknown')}**")
                        st.info(node.get('insight', 'No insight'))
                    st.markdown('</div>', unsafe_allow_html=True)

    # 3. 底部输入框
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    
    if prompt := st.chat_input("Reflect on your thoughts..."):
        # A. 立即显示用户输入 (本地乐观更新)
        st.markdown(f"<div class='chat-bubble-me'>{prompt}</div>", unsafe_allow_html=True)
        
        # B. 构造完整历史
        full_history = chat_history + [{'role':'user', 'content':prompt}]
        
        # C. 流式输出 AI 回复
        with st.chat_message("assistant"):
            # 使用 write_stream 渲染生成器
            response_stream = msc.get_stream_response(full_history)
            full_response = st.write_stream(response_stream)
        
        # D. 存入数据库
        # 注意：这里我们只在最后存一次
        msc.save_chat(username, "user", prompt)
        msc.save_chat(username, "assistant", full_response)

        # E. 后台进行意义分析 (这步还是得等，但因为 AI 已经聊完了，用户心理等待感降低)
        # 或者：我们可以把这一步放到线程里，但在 Streamlit 里不好做。
        # 现状：用户看到 AI 回复完，然后才会弹出 Toast。
        analysis = msc.analyze_meaning_background(prompt)
        if analysis.get("valid", False):
            vec = msc.get_embedding(prompt)
            msc.save_node(username, prompt, analysis, "AI对话", vec)
            if "radar_scores" in analysis: msc.update_radar_score(username, analysis["radar_scores"])
            st.toast("Meaning Captured & Vectorized", icon="🧬")
        
        time.sleep(0.5)
        st.rerun()
# ==========================================
# 💬 好友页面 (布局优化)
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
        st.markdown("### 📡 Signals")
        users = msc.get_all_users(username)
        
        if users:
            menu_items = []
            for u in users:
                user_map[u['nickname']] = u['username']
                is_online = msc.check_is_online(u.get('last_seen'))
                icon_name = "circle-fill" if is_online else "circle"
                icon_color = "#4CAF50" if is_online else "#DDD"
                
                unread = unread_counts.get(u['username'], 0)
                tag_val = sac.Tag(str(unread), color='red', bordered=False) if unread > 0 else None
                
                # 截断过长昵称
                display_name = u['nickname'][:12] + ".." if len(u['nickname']) > 12 else u['nickname']

                menu_items.append(sac.MenuItem(
                    label=display_name, 
                    icon=sac.BsIcon(name=icon_name, color=icon_color),
                    tag=tag_val
                ))
            
            selected_nickname = sac.menu(menu_items, index=0, size='md', variant='light', open_all=True)
            if selected_nickname and selected_nickname in user_map:
                st.session_state.current_chat_partner = user_map[selected_nickname]
        else:
            st.caption("No resonance detected.")

    with col_chat:
        partner = st.session_state.current_chat_partner
        if partner:
            msc.mark_messages_read(partner, username)
            st.markdown(f"#### ⚡ {msc.get_nickname(partner)}")
            
            history = msc.get_direct_messages(username, partner)
            my_nodes = msc.get_active_nodes_map(username)

            with st.container(height=600, border=True):
                if not history:
                    st.markdown("<div style='text-align:center; color:#ccc; margin-top:50px;'>No data exchange yet.</div>", unsafe_allow_html=True)
                
                for msg in history:
                    c_msg, c_dot = st.columns([0.94, 0.06])
                    with c_msg:
                        if msg['sender'] == 'AI':
                            st.markdown(f"<div class='chat-bubble-ai'>🤖 {msg['content']}</div>", unsafe_allow_html=True)
                        elif msg['sender'] == username:
                            st.markdown(f"<div class='chat-bubble-me'>{msg['content']}</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div class='chat-bubble-other'>{msg['content']}</div>", unsafe_allow_html=True)
                    
                    if msg['sender'] == username and msg['content'] in my_nodes:
                        node = my_nodes.get(msg['content'])
                        if node:
                            st.markdown('<div class="meaning-dot-btn">', unsafe_allow_html=True)
                            with st.popover("●"):
                                st.caption("Insight Node")
                                st.info(node.get('insight', ''))
                            st.markdown('</div>', unsafe_allow_html=True)

            if prompt := st.chat_input(f"Transmit to {msc.get_nickname(partner)}..."):
                msc.send_direct_message(username, partner, prompt)
                
                with st.spinner("Analyzing meaning..."):
                    analysis = msc.analyze_meaning_background(prompt)
                    if analysis.get("valid", False):
                        vec = msc.get_embedding(prompt)
                        msc.save_node(username, prompt, analysis, "私聊", vec)
                        match = msc.find_resonance(vec, username, analysis)
                        if match: st.toast(f"Resonance detected with {match['user']}!", icon="⚡")
                st.rerun()
        else:
            st.info("Select a frequency channel to begin.")

# ==========================================
# 🌍 世界页面
# ==========================================
def render_world_page():
    # 顶部添加一点空间
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    
    username = st.session_state.username
    has_access, count = msc.check_world_access(username)
    
    if not has_access and not st.session_state.is_admin:
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            st.warning(f"🔒 GLOBAL LAYER LOCKED")
            st.markdown(f"**Current Contribution:** {count} / 20 Nodes")
            st.progress(count / 20)
            st.caption("Only those who cultivate their own garden may view the forest.")
        return

    if "privacy_accepted" not in st.session_state: st.session_state.privacy_accepted = False
    if not st.session_state.privacy_accepted:
        with st.container(border=True):
            st.markdown("### 📜 The Protocol")
            st.markdown("You are entering the **Collective Mind Layer**. Identities are masked. Only meaning is visible.")
            if st.button("Accept Protocol"):
                st.session_state.privacy_accepted = True
                st.rerun()
        return

    nodes = msc.get_global_nodes()
    viz.render_3d_particle_map(nodes, username)
