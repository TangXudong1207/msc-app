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
    # 使用 CSS 稍微调整登录页的氛围
    st.markdown("""
    <style>
        .login-title { font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 3em; color: #333; }
        .login-subtitle { color: #888; letter-spacing: 4px; font-size: 0.8em; margin-top: -10px; font-weight: 300; }
    </style>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 2, 1])
    
    with c2:
        st.markdown("<div style='height: 120px;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align: center;'>
            <div class='login-title'>MSC</div>
            <div class='login-subtitle'>MEANING · STRUCTURE · CARE</div>
        </div>
        <div style='height: 50px;'></div>
        """, unsafe_allow_html=True)
        
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
                    else: st.error("Signal Lost: Invalid Credentials")
            else:
                nu = st.text_input("NEW ID", label_visibility="collapsed", placeholder="Username")
                np = st.text_input("NEW PW", type='password', label_visibility="collapsed", placeholder="Password")
                nn = st.text_input("NICK", label_visibility="collapsed", placeholder="Display Name")
                # 增加邀请码逻辑 (预留)
                # invite_code = st.text_input("INVITE CODE", label_visibility="collapsed", placeholder="Invitation Code")
                nc = st.selectbox("REGION", ["China", "USA", "UK", "Other"], label_visibility="collapsed")
                st.write("")
                if st.button("INITIALIZE PROTOCOL", use_container_width=True):
                    # if invite_code != "ARRIVAL": st.error("Invalid Invitation Code"); return
                    if msc.add_user(nu, np, nn, nc): st.success("Identity Created. Please Login.")
                    else: st.error("Initialization Failed")

# ==========================================
# 🚀 新手引导：降临 (The Arrival)
# ==========================================
def render_onboarding(username):
    # 🎨 注入“降临”风格 CSS：迷雾灰背景，衬线字体，圆形构图
    st.markdown("""
    <style>
        /* 强制覆盖全局背景 */
        [data-testid="stSidebar"] {display: none;}
        .stApp {
            background: radial-gradient(circle at center, #2b2e31 0%, #1a1a1d 100%) !important;
            color: #dcdcdc !important;
        }
        
        /* 字体：使用衬线体营造神秘、史诗感 */
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Lora:ital,wght@0,400;1,400&display=swap');
        
        .arrival-title {
            font-family: 'Cinzel', serif;
            font-size: 2.5em;
            text-align: center;
            color: #f0f0f0;
            text-shadow: 0 0 20px rgba(255,255,255,0.2);
            margin-bottom: 20px;
        }
        
        .arrival-text {
            font-family: 'Lora', serif;
            font-size: 1.2em;
            text-align: center;
            color: #aaa;
            line-height: 1.8;
            max-width: 600px;
            margin: 0 auto 40px auto;
        }
        
        /* 输入框样式重写：玻璃质感 */
        .stTextInput > div > div > input {
            background-color: rgba(255,255,255,0.05) !important;
            color: #fff !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            text-align: center;
            font-family: 'Lora', serif;
            font-size: 1.2em;
        }
        .stTextInput > div > div > input:focus {
            border-color: #555 !important;
            box-shadow: 0 0 15px rgba(255,255,255,0.05);
        }
        
        /* 按钮重写 */
        .stButton > button {
            background: transparent !important;
            border: 1px solid rgba(255,255,255,0.2) !important;
            color: #ccc !important;
            font-family: 'Cinzel', serif !important;
            letter-spacing: 2px;
        }
        .stButton > button:hover {
            background: rgba(255,255,255,0.05) !important;
            border-color: #fff !important;
            color: #fff !important;
        }
        
        /* 进度圆点 */
        .step-dots { text-align:center; margin-top:50px; color:#444; letter-spacing:10px;}
        .active-dot { color: #fff; text-shadow: 0 0 10px #fff; }
    </style>
    """, unsafe_allow_html=True)
    
    if "onboarding_step" not in st.session_state: st.session_state.onboarding_step = 0
    step = st.session_state.onboarding_step
    
    # 垂直居中容器
    c1, c2, c3 = st.columns([1, 3, 1])
    with c2:
        st.markdown("<div style='height:20vh'></div>", unsafe_allow_html=True)
        
        # --- Step 0: The Signal (建立锚点) ---
        if step == 0:
            st.markdown("<div class='arrival-title'>THE SIGNAL</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='arrival-text'>In the vast silence of data, who are you?<br>"
                "To exist here, you must transmit your first frequency.</div>", 
                unsafe_allow_html=True
            )
            
            anchor = st.text_input("ANCHOR POINT", placeholder="Type a thought that is truly yours...", label_visibility="collapsed")
            
            st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
            if anchor:
                if st.button("TRANSMIT", use_container_width=True):
                    with st.spinner("Analyzing Waveform..."):
                        # 分析并存下第一颗种子
                        analysis = msc.analyze_meaning_background(anchor)
                        vec = msc.get_embedding(anchor)
                        # 强制有效，作为第一颗种子
                        analysis['valid'] = True
                        if "care_point" not in analysis: analysis['care_point'] = "First Thought"
                        msc.save_node(username, anchor, analysis, "Genesis", vec)
                        # 初始化雷达
                        if "radar_scores" in analysis: msc.update_radar_score(username, analysis["radar_scores"])
                        time.sleep(1.5) # 稍微停顿，营造仪式感
                    
                    st.session_state.onboarding_step = 1
                    st.rerun()
            
            st.markdown("<div class='step-dots'><span class='active-dot'>•</span> • •</div>", unsafe_allow_html=True)

        # --- Step 1: Calibration (哲学二选一) ---
        elif step == 1:
            st.markdown("<div class='arrival-title'>CALIBRATION</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='arrival-text'>The nature of your weapon is determined by how you face the void.<br>"
                "Choose your orientation.</div>", 
                unsafe_allow_html=True
            )
            
            # 使用自定义样式的 Radio 或 Columns 按钮
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("DISSECT (Internal)", use_container_width=True):
                    msc.update_radar_score(username, {"Reflection": 7.0, "Rationality": 6.0})
                    st.session_state.onboarding_step = 2
                    st.rerun()
                st.caption("When in pain, you analyze it.")
                
            with col_b:
                if st.button("CONQUER (External)", use_container_width=True):
                    msc.update_radar_score(username, {"Agency": 7.0, "Conflict": 6.0})
                    st.session_state.onboarding_step = 2
                    st.rerun()
                st.caption("When in pain, you fight it.")

            st.markdown("<div class='step-dots'>• <span class='active-dot'>•</span> •</div>", unsafe_allow_html=True)

        # --- Step 2: Contact (完成) ---
        elif step == 2:
            st.markdown("<div class='arrival-title'>CONTACT ESTABLISHED</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='arrival-text'>Your frequency has been registered in the collective mind.<br>"
                "You are no longer silence.<br>Welcome to the forest.</div>", 
                unsafe_allow_html=True
            )
            
            st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
            if st.button("ENTER THE GRID", type="primary", use_container_width=True):
                st.session_state.onboarding_complete = True
                st.rerun()
                
            st.markdown("<div class='step-dots'>• • <span class='active-dot'>•</span></div>", unsafe_allow_html=True)

# ==========================================
# 👁️ 上帝视角 (Admin)
# ==========================================
def render_admin_dashboard():
    st.markdown("## 👁️ Overseer Terminal")
    st.caption("v75.5 Arrival / System Status: ONLINE")
    
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
                    with st.spinner("Fabricating souls..."):
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
            # 简单展示
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
# 🤖 AI Partner (流式对话)
# ==========================================
def render_ai_page(username):
    # 顶部留白
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    chat_history = msc.get_active_chats(username)
    nodes_map = msc.get_active_nodes_map(username)
    
    # 渲染历史
    for msg in chat_history:
        c_msg, c_dot = st.columns([0.92, 0.08])
        with c_msg:
            if msg['role'] == 'user':
                st.markdown(f"<div class='chat-bubble-me'>{msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-bubble-ai'>{msg['content']}</div>", unsafe_allow_html=True)
        with c_dot:
            if msg['role'] == 'user' and msg['content'] in nodes_map:
                node = nodes_map.get(msg['content'])
                if node:
                    st.markdown('<div class="meaning-dot-btn">', unsafe_allow_html=True)
                    with st.popover("●", help="Meaning Extracted"):
                        try: score_val = float(node.get('m_score') or 0.5)
                        except: score_val = 0.5
                        st.caption(f"Score: {score_val:.2f}")
                        st.markdown(f"**{node.get('care_point', 'Unknown')}**")
                        st.info(node.get('insight', 'No insight'))
                    st.markdown('</div>', unsafe_allow_html=True)

    # 输入框
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    if prompt := st.chat_input("Reflect on your thoughts..."):
        # 1. 立即上屏
        st.markdown(f"<div class='chat-bubble-me'>{prompt}</div>", unsafe_allow_html=True)
        
        full_history = chat_history + [{'role':'user', 'content':prompt}]
        
        # 2. 流式回复
        with st.chat_message("assistant"):
            try:
                response_stream = msc.get_stream_response(full_history)
                full_response = st.write_stream(response_stream)
                
                # 3. 存储
                msc.save_chat(username, "user", prompt)
                msc.save_chat(username, "assistant", full_response)
            except Exception as e:
                st.error(f"AI Error: {e}")

        # 4. 意义分析
        analysis = msc.analyze_meaning_background(prompt)
        if analysis.get("valid", False):
            vec = msc.get_embedding(prompt)
            msc.save_node(username, prompt, analysis, "AI对话", vec)
            if "radar_scores" in analysis: msc.update_radar_score(username, analysis["radar_scores"])
            st.toast("Meaning Captured", icon="🧬")
        
        time.sleep(0.5)
        st.rerun()

# ==========================================
# 💬 好友页面 (带 50 卡锁 & 完整列表)
# ==========================================
def render_friends_page(username, unread_counts):
    try:
        from streamlit_autorefresh import st_autorefresh
        st_autorefresh(interval=10000, key="msg_refresh") # 延长刷新时间，减少卡顿
    except: pass
    
    msc.update_heartbeat(username)

    # === 1. 门槛检查 (50卡) ===
    all_nodes = msc.get_all_nodes_for_map(username)
    node_count = len(all_nodes)
    
    # 如果节点少于 50 且不是管理员，显示锁定界面
    if node_count < 50 and not st.session_state.is_admin:
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.markdown("<div style='height:50px'></div>", unsafe_allow_html=True)
            st.warning("🔒 SIGNAL TRANSMITTER LOCKED")
            st.markdown(
                f"""
                <div style='text-align:center; color:#666;'>
                <h3 style='font-family: "Inter", sans-serif;'>Deep Connection requires Deep Self.</h3>
                <p style='font-size:0.9em; margin-top:10px;'>
                    You need to cultivate a denser forest before you can invite others in.<br>
                    This is to ensure every connection here is meaningful, not noise.
                </p>
                <h1 style='font-size:3em; margin:30px 0; font-family: "JetBrains Mono";'>{node_count} / 50</h1>
                <p style='color:#999; text-transform:uppercase; letter-spacing:2px; font-size:0.8em;'>Meaning Nodes Generated</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
            st.progress(node_count / 50)
        return

    # === 2. 解锁后的正常界面 ===
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
                
                # 私聊也进行分析
                with st.spinner("Analyzing meaning..."):
                    analysis = msc.analyze_meaning_background(prompt)
                    if analysis.get("valid", False):
                        vec = msc.get_embedding(prompt)
                        msc.save_node(username, prompt, analysis, "私聊", vec)
                        match = msc.find_resonance(vec, username, analysis)
                        if match: st.toast(f"Resonance with {match['user']}!", icon="⚡")
                st.rerun()
        else:
            st.info("Select a frequency channel to begin.")

# ==========================================
# 🌍 世界页面 (复用)
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
    viz.render_3d_particle_map(nodes, st.session_state.username)
