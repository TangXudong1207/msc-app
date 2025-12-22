### page_social.py ###
import streamlit as st
import streamlit_antd_components as sac
import msc_lib as msc
import msc_viz as viz
import msc_i18n as i18n
import msc_config as config
import time
import json

# ==========================================
# 🔒 统一的锁定界面
# ==========================================
def render_lock_screen(current_count, target_count, title, message):
    c1, c2, c3 = st.columns([1, 6, 1])
    with c2:
        st.markdown("<div style='height:80px'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='text-align: center; color: #555;'>
            <div style='font-size: 3em; margin-bottom: 20px;'>🔒</div>
            <div style='font-weight: 600; text-transform: uppercase; margin-bottom: 30px; color: #333;'>{title}</div>
            <div style='font-family: "Noto Serif SC"; font-size: 1.1em; line-height: 2.0; color: #666; font-style: italic;'>{message}</div>
            <div style='font-family: "JetBrains Mono"; font-size: 4em; font-weight: 700; color: #222; margin-top:40px;'>{current_count} / {target_count}</div>
            <div style='font-size: 0.8em; letter-spacing: 2px; color: #BBB; text-transform: uppercase; margin-bottom: 20px;'>{i18n.get_text('lock_stat')}</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(min(current_count / target_count, 1.0))

# ==========================================
# 🚀 升空动画 (永久一次性)
# ==========================================
def render_ascension_animation(username):
    # 动画 HTML
    st.markdown("""
    <style>
        @keyframes floatUp { 0% { opacity: 0; transform: translateY(50px); } 100% { opacity: 1; transform: translateY(0); } }
        .ascension-msg {
            position: fixed; top: 40%; left: 50%; transform: translate(-50%, -50%);
            background: rgba(255,255,255,0.98); padding: 40px; border-radius: 8px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1); text-align: center; animation: floatUp 2s ease-out; z-index: 9999;
        }
    </style>
    <div class='ascension-msg'>
        <div style='font-size: 2em; font-family: "Noto Serif SC";'>阈值突破</div>
        <div style='font-size: 0.8em; letter-spacing: 3px; color: #999; margin-top:10px;'>THRESHOLD BREACHED</div>
        <div style='margin-top:20px; color: #00CCFF;'>Global Layer Access: GRANTED</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 🟢 关键：写入数据库日志，标记已播放
    msc.log_ascension_event(username)
    time.sleep(3.0)
    st.rerun()

# ==========================================
# 📡 信号分析对话框
# ==========================================
@st.dialog("📡 SIGNAL ANALYSIS", width="large")
def render_scan_dialog(username):
    st.caption("Scanning cognitive frequencies...")
    
    # 扫描缓存
    if "scan_results" not in st.session_state:
        with st.spinner("Triangulating soul coordinates..."):
            res = msc.get_match_candidates(username)
            st.session_state.scan_results = res
            st.session_state.selected_near = []
            st.session_state.selected_far = []
            
    res = st.session_state.scan_results
    
    st.markdown("""
    <style>
        .match-card { border: 1px solid #EEE; padding: 10px; margin-bottom: 8px; border-radius: 4px; background: #FAFAFA; }
        .match-meta { font-size: 0.8em; color: #888; font-style: italic; }
        .section-header { font-family: 'JetBrains Mono'; font-size: 0.9em; font-weight: bold; color: #333; margin-bottom: 15px; border-bottom: 1px solid #EEE; padding-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

    c_near, c_far = st.columns(2)
    
    # NEAR
    with c_near:
        st.markdown("<div class='section-header'>RESONANCE // 共鸣 (Max 2)</div>", unsafe_allow_html=True)
        if not res['near']: st.caption("No signals in range.")
        for u in res['near']:
            checked = u['username'] in st.session_state.selected_near
            disabled = len(st.session_state.selected_near) >= 2 and not checked
            if st.checkbox(f"{u['nickname']}", value=checked, key=f"n_{u['username']}", disabled=disabled):
                if not checked: st.session_state.selected_near.append(u['username'])
            elif checked:
                st.session_state.selected_near.remove(u['username'])
            st.markdown(f"<div class='match-meta'>Mirror Soul detected.</div>", unsafe_allow_html=True)
            st.write("")

    # FAR
    with c_far:
        st.markdown("<div class='section-header'>TENSION // 张力 (Max 2)</div>", unsafe_allow_html=True)
        if not res['far']: st.caption("No signals in range.")
        for u in res['far']:
            checked = u['username'] in st.session_state.selected_far
            disabled = len(st.session_state.selected_far) >= 2 and not checked
            if st.checkbox(f"{u['nickname']}", value=checked, key=f"f_{u['username']}", disabled=disabled):
                if not checked: st.session_state.selected_far.append(u['username'])
            elif checked:
                st.session_state.selected_far.remove(u['username'])
            st.markdown(f"<div class='match-meta'>Necessary conflict.</div>", unsafe_allow_html=True)
            st.write("")

    st.divider()
    st.markdown("**Manual Calibration // 手动锁定**")
    manual_target = st.text_input("Target Username", placeholder="Enter specific ID...")
    
    targets = []
    for t in st.session_state.selected_near: targets.append({'u': t, 'type': 'Resonance'})
    for t in st.session_state.selected_far: targets.append({'u': t, 'type': 'Tension'})
    if manual_target: targets.append({'u': manual_target, 'type': 'Manual'})
    
    btn_disabled = len(targets) == 0
    if st.button("TRANSMIT SIGNALS", type="primary", use_container_width=True, disabled=btn_disabled):
        progress_bar = st.progress(0)
        logs = st.empty()
        for i, target in enumerate(targets):
            logs.caption(f"Analyzing link with {target['u']}...")
            metaphor = msc.generate_relationship_metaphor(username, target['u'], target['type'])
            success, msg = msc.send_friend_request(username, target['u'], target['type'], metaphor)
            progress_bar.progress((i + 1) / len(targets))
        st.success("All signals transmitted to the Ether.")
        time.sleep(1.5)
        st.rerun()

# ==========================================
# 💬 Main Page
# ==========================================
def render_friends_page(username, unread_counts):
    try:
        from streamlit_autorefresh import st_autorefresh
        st_autorefresh(interval=10000, key="msg_refresh") 
    except: pass
    
    msc.update_heartbeat(username)
    all_nodes = msc.get_all_nodes_for_map(username)
    node_count = len(all_nodes)
    
    # 🟢 阈值检查与升空动画 (利用数据库永久标记)
    if node_count >= config.WORLD_UNLOCK_THRESHOLD and not st.session_state.is_admin:
        # 检查数据库是否已有记录
        if not msc.check_if_ascended_permanently(username):
            render_ascension_animation(username)
            return 

    if node_count < config.WORLD_UNLOCK_THRESHOLD and not st.session_state.is_admin:
        render_lock_screen(node_count, config.WORLD_UNLOCK_THRESHOLD, i18n.get_text('lock_title'), i18n.get_text('lock_msg'))
        return

    col_list, col_chat = st.columns([0.25, 0.75])
    
    with col_list:
        st.markdown(f"### 📡 {i18n.get_text('chat_signals')}")
        
        # 🟢 A. 扫描按钮
        if st.button("📡 SCAN", use_container_width=True):
             # 每次点击重置缓存，确保是最新的
            if "scan_results" in st.session_state: del st.session_state.scan_results
            render_scan_dialog(username)
        
        st.divider()

        # 🟢 B. 待处理请求
        pending = msc.get_pending_requests(username)
        if pending:
            st.caption(f"Incoming: {len(pending)}")
            for req in pending:
                with st.container(border=True):
                    st.markdown(f"**From: {req['sender']}**")
                    st.caption(f"Type: {req['match_type']}")
                    st.info(f"\"{req['metaphor']}\"")
                    c_yes, c_no = st.columns(2)
                    if c_yes.button("Connect", key=f"y_{req['id']}"):
                        msc.handle_friend_request(req['id'], 'accepted')
                        st.rerun()
                    if c_no.button("Ignore", key=f"n_{req['id']}"):
                        msc.handle_friend_request(req['id'], 'rejected')
                        st.rerun()
            st.divider()

        # 🟢 C. 好友列表
        friends = msc.get_my_friends(username)
        
        if friends:
            menu_items = []
            user_map = {}
            for f in friends:
                fname = f['username']
                user_map[fname] = fname 
                unread = unread_counts.get(fname, 0)
                tag = sac.Tag(str(unread), color='red') if unread > 0 else None
                desc = (f['metaphor'][:15] + '..') if f['metaphor'] else "Connected"
                menu_items.append(sac.MenuItem(label=fname, description=desc, icon='person-fill', tag=tag))
            
            sel = sac.menu(menu_items, index=0, size='md', variant='light', open_all=True)
            if sel: st.session_state.current_chat_partner = sel
        else:
            st.caption("No connections established.")

    with col_chat:
        partner = st.session_state.current_chat_partner
        if partner:
            msc.mark_messages_read(partner, username)
            st.markdown(f"#### ⚡ {partner}") 
            history = msc.get_direct_messages(username, partner)
            my_nodes = msc.get_active_nodes_map(username)

            with st.container(height=600, border=True):
                if not history:
                    st.markdown(f"<div style='text-align:center; color:#ccc; margin-top:50px;'>链路已建立。现在，你们可以开始交换意义了。</div>", unsafe_allow_html=True)
                for msg in history:
                    c_msg, c_dot = st.columns([0.94, 0.06])
                    with c_msg:
                        if msg['sender'] == username:
                            st.markdown(f"<div class='chat-bubble-me'>{msg['content']}</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div class='chat-bubble-other'>{msg['content']}</div>", unsafe_allow_html=True)
                    if msg['sender'] == username and msg['content'] in my_nodes:
                        node = my_nodes.get(msg['content'])
                        if node:
                            st.markdown('<div class="meaning-dot-btn">●</div>', unsafe_allow_html=True)

            if prompt := st.chat_input(f"Transmit to {partner}..."):
                msc.send_direct_message(username, partner, prompt)
                st.rerun()
        else:
            st.info(i18n.get_text('chat_sel'))

# ==========================================
# 🌍 2. 世界页面
# ==========================================
def render_world_page():
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    unlocked, count = msc.check_world_access(st.session_state.username)
    if st.session_state.is_admin: unlocked = True
    if not unlocked:
        render_lock_screen(count, config.WORLD_UNLOCK_THRESHOLD, i18n.get_text('world_lock'), i18n.get_text('world_only'))
        return
    st.markdown(f"### 🌍 {i18n.get_text('World')}")
    viz.render_3d_particle_map(msc.get_global_nodes(), st.session_state.username)
    viz.render_spectrum_legend()
