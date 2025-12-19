### page_social.py ###
import streamlit as st
import streamlit_antd_components as sac
import msc_lib as msc
import msc_viz as viz
import msc_i18n as i18n
import msc_config as config

# ==========================================
# 🔒 统一的锁定界面组件
# ==========================================
def render_lock_screen(current_count, target_count, title, message):
    c1, c2, c3 = st.columns([1, 6, 1])
    with c2:
        st.markdown("<div style='height:80px'></div>", unsafe_allow_html=True)
        
        # 注入 CSS
        st.markdown("""
        <style>
            .lock-container { text-align: center; color: #555; font-family: 'Inter', sans-serif; }
            .lock-icon { font-size: 3em; color: #EEE; margin-bottom: 20px; }
            .lock-title { font-size: 1.2em; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 30px; color: #333; }
            .lock-quote { font-family: 'Noto Serif SC', serif; font-size: 1.1em; line-height: 2.0; color: #666; margin-bottom: 40px; font-style: italic; }
            .lock-stat-number { font-family: 'JetBrains Mono', monospace; font-size: 4em; font-weight: 700; color: #222; }
            .lock-stat-label { font-family: 'JetBrains Mono', monospace; font-size: 0.8em; letter-spacing: 2px; color: #BBB; text-transform: uppercase; margin-top: -10px; margin-bottom: 20px; }
        </style>
        """, unsafe_allow_html=True)
        
        # 渲染 HTML
        st.markdown(f"""
        <div class='lock-container'>
            <div class='lock-icon'>🔒</div>
            <div class='lock-title'>{title}</div>
            <div class='lock-quote'>{message}</div>
            <div class='lock-stat-number'>{current_count} / {target_count}</div>
            <div class='lock-stat-label'>{i18n.get_text('lock_stat')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.progress(min(current_count / target_count, 1.0))

# ==========================================
# 💬 1. 好友 / 信号页面
# ==========================================
def render_friends_page(username, unread_counts):
    try:
        from streamlit_autorefresh import st_autorefresh
        st_autorefresh(interval=10000, key="msg_refresh") 
    except: pass
    
    msc.update_heartbeat(username)
    all_nodes = msc.get_all_nodes_for_map(username)
    node_count = len(all_nodes)
    
    # 🔒 锁定界面
    if node_count < 50 and not st.session_state.is_admin:
        render_lock_screen(
            node_count, 
            50, 
            i18n.get_text('lock_title'), 
            i18n.get_text('lock_msg')
        )
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
# 🌍 2. 世界 / 全球层 (必须顶格写，不要有空格)
# ==========================================
def render_world_page():
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    
    # 检查权限
    unlocked, count = msc.check_world_access(st.session_state.username)
    
    # 如果是管理员，直接放行
    if st.session_state.is_admin:
        unlocked = True

    # 🔒 锁定界面 (复用漂亮样式)
    if not unlocked:
        render_lock_screen(
            count, 
            config.WORLD_UNLOCK_THRESHOLD, 
            i18n.get_text('world_lock'), 
            i18n.get_text('world_only')
        )
        return

    # 🔓 解锁后的世界视图
    st.markdown(f"### 🌍 {i18n.get_text('World')}")
    
    # 选项卡切换视图
    view_type = sac.tabs([
        sac.TabsItem(label='Planet', icon='globe'),
        sac.TabsItem(label='Galaxy', icon='stars'),
    ], size='sm', variant='outline')
    
    # 获取全球数据
    global_nodes = msc.get_global_nodes()
    
    if view_type == 'Planet':
        st.caption("Real-time cognitive topology mapping...")
        viz.render_3d_particle_map(global_nodes, st.session_state.username)
    else:
        st.caption("Semantic clustering in vector space...")
        viz.render_3d_galaxy(global_nodes)
    
    # 底部显示一些统计信息
    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Active Signals", len(global_nodes))
    with c2: st.metric("Observer Status", "Connected")
    with c3: st.metric("Your Contribution", count)
