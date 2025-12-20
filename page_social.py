### page__social.py ###
import streamlit as st
import streamlit_antd_components as sac
import msc_lib as msc
import msc_viz as viz
import msc_i18n as i18n
import msc_config as config
import time

# ==========================================
# 🔒 统一的锁定界面组件
# ==========================================
def render_lock_screen(current_count, target_count, title, message):
    c1, c2, c3 = st.columns([1, 6, 1])
    with c2:
        st.markdown("<div style='height:80px'></div>", unsafe_allow_html=True)
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
# 🚀 升空动画 (Ascension) - 解锁时播放
# ==========================================
def render_ascension_animation():
    st.markdown("""
    <style>
        @keyframes floatUp {
            0% { transform: translateY(100px); opacity: 0; }
            50% { opacity: 1; }
            100% { transform: translateY(-50px); opacity: 0; }
        }
        .particle {
            position: fixed; bottom: 0;
            width: 4px; height: 4px; background: #00CCFF; border-radius: 50%;
            animation: floatUp 3s infinite linear;
            z-index: 9999;
        }
        .ascension-msg {
            position: fixed; top: 40%; left: 50%; transform: translate(-50%, -50%);
            color: #333; font-family: 'Noto Serif SC', serif; font-size: 2em;
            text-align: center; z-index: 10000;
            background: rgba(255,255,255,0.95); padding: 40px; border-radius: 8px;
            box-shadow: 0 10px 50px rgba(0,200,255,0.2);
            border: 1px solid #E0E0E0;
        }
        .guide-arrow {
            position: fixed; top: 80px; left: 20px; /* 调整位置指向左上角菜单 */
            font-size: 2em; color: #FF2B2B; z-index: 10001;
            font-weight: bold;
            animation: bounce 1s infinite;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        @keyframes bounce {
            0%, 100% { transform: translateX(0); }
            50% { transform: translateX(10px); }
        }
    </style>
    
    <div class='ascension-msg'>
        <div>阈值突破</div>
        <div style='font-size:0.5em; margin-top:10px; color:#666; letter-spacing: 2px;'>THRESHOLD BREACHED</div>
        <div style='font-size:0.4em; margin-top:20px; font-family:monospace; color: #00CCFF;'>World Layer Access: GRANTED</div>
    </div>
    
    <div class='particle' style='left:10%; animation-duration: 4s;'></div>
    <div class='particle' style='left:30%; animation-duration: 2.5s;'></div>
    <div class='particle' style='left:60%; animation-duration: 3.2s;'></div>
    <div class='particle' style='left:80%; animation-duration: 4.5s;'></div>
    
    <div class='guide-arrow'>⬅ CLICK 'WORLD'</div>
    """, unsafe_allow_html=True)
    
    time.sleep(4.0) 
    st.session_state.has_shown_ascension = True 
    st.rerun()

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
    
    if node_count >= config.WORLD_UNLOCK_THRESHOLD and not st.session_state.is_admin:
        if "has_shown_ascension" not in st.session_state:
            render_ascension_animation()
            return 

    if node_count < config.WORLD_UNLOCK_THRESHOLD and not st.session_state.is_admin:
        render_lock_screen(
            node_count, 
            config.WORLD_UNLOCK_THRESHOLD, 
            i18n.get_text('lock_title'), 
            i18n.get_text('lock_msg')
        )
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
# 🌍 2. 世界页面 (World Layer)
# ==========================================
def render_world_page():
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    
    unlocked, count = msc.check_world_access(st.session_state.username)
    if st.session_state.is_admin: unlocked = True

    if not unlocked:
        render_lock_screen(
            count, 
            config.WORLD_UNLOCK_THRESHOLD, 
            i18n.get_text('world_lock'), 
            i18n.get_text('world_only')
        )
        return

    st.markdown(f"### 🌍 {i18n.get_text('World')}")
    
    view_type = sac.tabs([
        sac.TabsItem(label='Planet', icon='globe'),
        sac.TabsItem(label='Galaxy', icon='stars'), 
    ], size='sm', variant='outline')
    
    global_nodes = msc.get_global_nodes()
    
    if view_type == 'Planet':
        st.caption("Real-time cognitive topology mapping...")
        viz.render_3d_particle_map(global_nodes, st.session_state.username)
    else:
        st.markdown("""
        <div style='background-color: #F8F8F8; border: 1px dashed #CCC; padding: 40px; text-align: center; border-radius: 4px; margin-top: 20px;'>
            <div style='font-size: 3em; color: #DDD; margin-bottom: 20px;'>🌌</div>
            <div style='font-family: "JetBrains Mono", monospace; font-size: 1.2em; color: #888; letter-spacing: 2px;'>
                GALAXY_VIEW_COMPUTING...
            </div>
            <div style='font-size: 0.9em; color: #AAA; margin-top: 10px; font-style: italic;'>
                Vector dimensionality reduction in progress. Check back in future cycles.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Query Status", key="galaxy_query"):
            st.toast("Module [Galaxy] is currently under construction by The Architect.", icon="🚧")
    
    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Active Signals", len(global_nodes))
    with c2: st.metric("Observer Status", "Connected")
    with c3: st.metric("Your Contribution", count)
    
    # 新增：光谱图例
    viz.render_spectrum_legend())
