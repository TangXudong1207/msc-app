### page__social.py ###
import streamlit as st
import streamlit_antd_components as sac
import msc_lib as msc
import msc_viz as viz
import msc_i18n as i18n

# ==========================================
# 💬 好友页面 (视觉升级版)
# ==========================================
def render_friends_page(username, unread_counts):
    try:
        from streamlit_autorefresh import st_autorefresh
        st_autorefresh(interval=10000, key="msg_refresh") 
    except: pass
    
    msc.update_heartbeat(username)
    all_nodes = msc.get_all_nodes_for_map(username)
    node_count = len(all_nodes)
    
    # 🔒 锁定界面优化
    if node_count < 50 and not st.session_state.is_admin:
        c1, c2, c3 = st.columns([1, 6, 1]) # 使用更宽的中间列
        with c2:
            st.markdown("<div style='height:80px'></div>", unsafe_allow_html=True)
            
            # CSS 注入：只针对这个页面的样式
            st.markdown("""
            <style>
                .lock-container {
                    text-align: center;
                    color: #555;
                    font-family: 'Inter', sans-serif;
                }
                .lock-icon { font-size: 3em; color: #EEE; margin-bottom: 20px; }
                .lock-title { 
                    font-size: 1.2em; 
                    font-weight: 600; 
                    letter-spacing: 1px; 
                    text-transform: uppercase;
                    margin-bottom: 30px;
                    color: #333;
                }
                .lock-quote {
                    font-family: 'Noto Serif SC', serif;
                    font-size: 1.1em;
                    line-height: 2.0;
                    color: #666;
                    margin-bottom: 40px;
                    font-style: italic;
                }
                .lock-stat-number {
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 4em;
                    font-weight: 700;
                    color: #222;
                }
                .lock-stat-label {
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 0.8em;
                    letter-spacing: 2px;
                    color: #BBB;
                    text-transform: uppercase;
                    margin-top: -10px;
                    margin-bottom: 20px;
                }
            </style>
            
            <div class='lock-container'>
                <div class='lock-icon'>🔒</div>
                <div class='lock-title'>Signal Transmitter Locked</div>
                <div class='lock-quote'>
                    深度的连接 · 始于深度的自我<br>
                    在邀请他人进入之前，请先耕耘你自己的灵魂森林<br>
                    这是为了确保每一次连接都是信号，而非噪音
                </div>
                <div class='lock-stat-number'>{count} / 50</div>
                <div class='lock-stat-label'>Meaning Nodes Generated</div>
            </div>
            """.format(count=node_count), unsafe_allow_html=True)
            
            st.progress(node_count / 50)
        return

    # === 解锁后的正常界面 ===
    col_list, col_chat = st.columns([0.25, 0.75])
    user_map = {}

    with col_list:
        st.markdown(f"### 📡 {i18n.get_text('chat_signals')}")
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
                menu_items.append(sac.MenuItem(label=display_name, icon=sac.BsIcon(name=icon_name, color=icon_color), tag=tag_val))
            
            selected_nickname = sac.menu(menu_items, index=0, size='md', variant='light', open_all=True)
            if selected_nickname and selected_nickname in user_map:
                st.session_state.current_chat_partner = user_map[selected_nickname]
        else:
            st.caption(i18n.get_text('chat_no_res'))

    with col_chat:
        partner = st.session_state.current_chat_partner
        if partner:
            msc.mark_messages_read(partner, username)
            st.markdown(f"#### ⚡ {msc.get_nickname(partner)}")
            history = msc.get_direct_messages(username, partner)
            my_nodes = msc.get_active_nodes_map(username)

            with st.container(height=600, border=True):
                if not history:
                    st.markdown(f"<div style='text-align:center; color:#ccc; margin-top:50px;'>{i18n.get_text('chat_no_data')}</div>", unsafe_allow_html=True)
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
                                st.caption("Insight")
                                st.info(node.get('insight', ''))
                            st.markdown('</div>', unsafe_allow_html=True)

            if prompt := st.chat_input(f"{i18n.get_text('chat_transmit')} {msc.get_nickname(partner)}..."):
                msc.send_direct_message(username, partner, prompt)
                with st.spinner("Analyzing..."):
                    analysis = msc.analyze_meaning_background(prompt)
                    if analysis.get("valid", False):
                        vec = msc.get_embedding(prompt)
                        msc.save_node(username, prompt, analysis, "私聊", vec)
                st.rerun()
        else:
            st.info(i18n.get_text('chat_sel'))

# ==========================================
# 🌍 世界页面
# ==========================================
def render_world_page():
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    username = st.session_state.username
    has_access, count = msc.check_world_access(username)
    
    if not has_access and not st.session_state.is_admin:
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            st.warning(f"🔒 {i18n.get_text('world_lock')}")
            st.markdown(f"**Contribution:** {count} / 20 Nodes")
            st.progress(count / 20)
            st.caption(i18n.get_text('world_only'))
        return

    if "privacy_accepted" not in st.session_state: st.session_state.privacy_accepted = False
    if not st.session_state.privacy_accepted:
        with st.container(border=True):
            st.markdown(f"### 📜 {i18n.get_text('world_proto_title')}")
            st.markdown(i18n.get_text('world_proto_text'))
            if st.button(i18n.get_text('world_accept')):
                st.session_state.privacy_accepted = True
                st.rerun()
        return

    nodes = msc.get_global_nodes()
    viz.render_3d_particle_map(nodes, st.session_state.username)
