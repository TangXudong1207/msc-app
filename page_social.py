### page_social.py ###
import streamlit as st
import streamlit_antd_components as sac
import msc_lib as msc
import msc_viz as viz
import msc_i18n as i18n

# ==========================================
# 💬 好友页面
# ==========================================
def render_friends_page(username, unread_counts):
    try:
        from streamlit_autorefresh import st_autorefresh
        st_autorefresh(interval=10000, key="msg_refresh") 
    except: pass
    
    msc.update_heartbeat(username)
    all_nodes = msc.get_all_nodes_for_map(username)
    node_count = len(all_nodes)
    
    if node_count < 50 and not st.session_state.is_admin:
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.markdown("<div style='height:50px'></div>", unsafe_allow_html=True)
            st.warning(i18n.get_text('lock_title'))
            st.markdown(
                f"""
                <div style='text-align:center; color:#666;'>
                <h3 style='font-family: "Inter", sans-serif;'>{i18n.get_text('lock_msg')}</h3>
                <h1 style='font-size:3em; margin:30px 0; font-family: "JetBrains Mono";'>{node_count} / 50</h1>
                <p style='color:#999; text-transform:uppercase; letter-spacing:2px; font-size:0.8em;'>{i18n.get_text('lock_stat')}</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
            st.progress(node_count / 50)
        return

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
