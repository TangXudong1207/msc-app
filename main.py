import streamlit as st
import streamlit_antd_components as sac
import msc_lib as msc
import time
import json

# ==========================================
# 🎨 CSS：极简科技风
# ==========================================
def inject_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        .stApp { background-color: #FFFFFF; font-family: 'Roboto', sans-serif; color: #1F1F1F; }
        [data-testid="stSidebar"] { background-color: #FAFAFA; border-right: 1px solid #E0E0E0; }
        .chat-bubble-me { background-color: #222; color: #fff; padding: 10px 16px; border-radius: 18px; float: right; margin-bottom: 5px; max-width: 85%; }
        .chat-bubble-other { background-color: #F2F2F2; color: #222; padding: 10px 16px; border-radius: 18px; float: left; margin-bottom: 5px; max-width: 85%; }
        .chat-bubble-ai { background: transparent; color: #666; border: 1px dashed #ccc; padding: 8px 12px; border-radius: 12px; margin: 15px auto; text-align: center; font-size: 0.85em; width: fit-content; }
        .meaning-dot-btn { display: flex; align-items: center; justify-content: center; height: 100%; }
        .meaning-dot-btn button { border: none !important; background: transparent !important; color: #BBB !important; font-size: 18px !important; }
        .meaning-dot-btn button:hover { color: #1A73E8 !important; transform: scale(1.2); }
        .daily-card { border: 1px solid #eee; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 20px; background: #fff; }
        .login-card { background: white; padding: 2rem; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.set_page_config(page_title="MSC v71.0 Final", layout="wide", initial_sidebar_state="expanded")
inject_custom_css()

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "current_chat_partner" not in st.session_state: st.session_state.current_chat_partner = None

# --- 1. 登录注册 ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        st.markdown("<br><h1 style='text-align: center; color: #1A73E8;'>🔷 MSC</h1>", unsafe_allow_html=True)
        tab = sac.tabs([sac.TabsItem('登录'), sac.TabsItem('注册')], align='center', variant='outline')
        
        if tab == '登录':
            u = st.text_input("账号")
            p = st.text_input("密码", type='password')
            if st.button("进入系统", use_container_width=True, type="primary"):
                res = msc.login_user(u, p)
                if res:
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.session_state.nickname = res[0]['nickname']
                    st.session_state.messages = [] 
                    st.rerun()
                else: sac.alert("账号或密码错误", color='red')
        else:
            nu = st.text_input("新账号")
            np = st.text_input("新密码", type='password')
            nn = st.text_input("昵称")
            nc = st.selectbox("地区", ["China", "USA", "UK", "Other"])
            if st.button("创建身份", use_container_width=True):
                if msc.add_user(nu, np, nn, nc): sac.alert("成功", color='success')
                else: sac.alert("失败", color='error')

# --- 2. 主界面 ---
else:
    # 基础数据
    msc.update_heartbeat(st.session_state.username)
    user_profile = msc.get_user_profile(st.session_state.username)
    raw_radar = user_profile.get('radar_profile')
    if isinstance(raw_radar, str): radar_dict = json.loads(raw_radar)
    else: radar_dict = raw_radar if raw_radar else {k:3.0 for k in ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]}
    
    rank_name, rank_icon = msc.calculate_rank(radar_dict)
    total_unread, unread_counts = msc.get_unread_counts(st.session_state.username)

    # 侧边栏
    with st.sidebar:
        st.markdown(f"### {rank_icon} {st.session_state.nickname}")
        
        if "daily_q" not in st.session_state: st.session_state.daily_q = None
        if st.session_state.daily_q is None:
            if st.button("📅 生成今日追问", use_container_width=True):
                with st.spinner("..."):
                    st.session_state.daily_q = msc.generate_daily_question(st.session_state.username, radar_dict)
                    st.rerun()
        else:
            st.markdown(f"<div class='daily-card'><div class='daily-title'>DAILY</div>{st.session_state.daily_q}</div>", unsafe_allow_html=True)
            if st.button("🔄"): st.session_state.daily_q = None; st.rerun()

        msc.render_radar_chart(radar_dict, height="160px")
        
        menu = sac.menu([
            sac.MenuItem('AI 伴侣', icon='robot'),
            sac.MenuItem('好友', icon='chat-dots', tag=sac.Tag(str(total_unread), color='red') if total_unread > 0 else None),
            sac.MenuItem('World', icon='globe'),
            sac.MenuItem('System', type='group', children=[sac.MenuItem('Logout', icon='box-arrow-right')]),
        ], index=0, format_func='title', size='sm', variant='light', open_all=True)

        st.divider()
        all_nodes = msc.get_all_nodes_for_map(st.session_state.username)
        if st.button("🔭 Full View", use_container_width=True): 
            msc.view_fullscreen_map(all_nodes, st.session_state.nickname)

    if menu == 'Logout': st.session_state.logged_in = False; st.rerun()

    # --- A. AI 伴侣 ---
    elif menu == 'AI 伴侣':
        st.subheader("🤖 AI 意义构建")
        chat_history_ai = msc.get_active_chats(st.session_state.username)
        nodes_map = msc.get_active_nodes_map(st.session_state.username)
        
        col_chat, col_node = st.columns([0.92, 0.08])
        with col_chat:
            for msg in chat_history_ai:
                with st.chat_message(msg['role']): st.markdown(msg['content'])
        with col_node:
            for msg in chat_history_ai:
                if msg['role'] == 'user' and msg['content'] in nodes_map:
                    node = nodes_map[msg['content']]
                    st.markdown('<div class="meaning-dot-btn">', unsafe_allow_html=True)
                    with st.popover("●", help="Deep Meaning"):
                        score = node.get('m_score') if node.get('m_score') is not None else node.get('logic_score', 0.5)
                        st.caption(f"Score: {float(score):.2f}")
                        st.markdown(f"**{node['care_point']}**")
                        st.info(node['insight'])
                    st.markdown('</div>', unsafe_allow_html=True)

        if prompt := st.chat_input("与 AI 对话..."):
            msc.save_chat(st.session_state.username, "user", prompt)
            
            with st.container(): st.markdown(f"<div class='chat-bubble-me'>{prompt}</div>", unsafe_allow_html=True)
            
            full_history = chat_history_ai + [{'role':'user', 'content':prompt}]
            
            # 🌟 核心修复：确保使用 write_stream 显示流式回复
            with st.chat_message("assistant"):
                try:
                    stream = msc.get_normal_response(full_history)
                    resp = st.write_stream(stream)
                    msc.save_chat(st.session_state.username, "assistant", resp)
                except Exception as e: st.error(f"Error: {e}")
            
            with st.spinner(""):
                analysis = msc.analyze_meaning_background(prompt)
                if analysis.get("valid", False):
                    vec = msc.get_embedding(prompt)
                    msc.save_node(st.session_state.username, prompt, analysis, "日常", vec)
                    if "radar_scores" in analysis: msc.update_radar_score(st.session_state.username, analysis["radar_scores"])
                    st.toast("Captured", icon="🌱")
            time.sleep(0.5); st.rerun()

    # --- B. 好友 ---
    elif menu == '好友':
        col_list, col_chat = st.columns([0.3, 0.7])
        with col_list:
            st.caption("CONTACTS")
            users = msc.get_all_users(st.session_state.username)
            if users:
                for u in users:
                    is_online = msc.check_is_online(u.get('last_seen'))
                    status = "🟢" if is_online else "⚪"
                    unread = unread_counts.get(u['username'], 0)
                    label = f"{status} {u['nickname']} {'🔴'+str(unread) if unread>0 else ''}"
                    if st.button(label, key=f"f_{u['username']}", use_container_width=True):
                        st.session_state.current_chat_partner = u['username']
                        msc.mark_messages_read(u['username'], st.session_state.username)
                        st.rerun()

        with col_chat:
            partner = st.session_state.current_chat_partner
            if partner:
                c1, c2 = st.columns([0.8, 0.2])
                with c1: st.markdown(f"**{partner}**")
                
                history = msc.get_direct_messages(st.session_state.username, partner)
                my_nodes = msc.get_active_nodes_map(st.session_state.username)
                
                with st.container(height=500, border=False):
                    for msg in history:
                        c_msg, c_dot = st.columns([0.92, 0.08])
                        with c_msg:
                            if msg['sender'] == 'AI': st.markdown(f"<div class='chat-bubble-other'>🤖 {msg['content']}</div>", unsafe_allow_html=True)
                            elif msg['sender'] == st.session_state.username: st.markdown(f"<div class='chat-bubble-me'>{msg['content']}</div>", unsafe_allow_html=True)
                            else: st.markdown(f"<div class='chat-bubble-other'>{msg['content']}</div>", unsafe_allow_html=True)
                        with c_dot:
                            if msg['sender'] == st.session_state.username and msg['content'] in my_nodes:
                                node = my_nodes[msg['content']]
                                st.markdown('<div class="meaning-dot-btn">', unsafe_allow_html=True)
                                with st.popover("●"): st.info(node['insight'])
                                st.markdown('</div>', unsafe_allow_html=True)
                
                if prompt := st.chat_input("Type..."):
                    msc.send_direct_message(st.session_state.username, partner, prompt)
                    with st.spinner(""):
                        analysis = msc.analyze_meaning_background(prompt)
                        if analysis.get("valid", False):
                            vec = msc.get_embedding(prompt)
                            msc.save_node(st.session_state.username, prompt, analysis, "私聊", vec)
                            match = msc.find_resonance(vec, st.session_state.username, analysis)
                            if match: st.toast("Resonance!", icon="⚡")
                    st.rerun()
            else: st.info("👈 Select a friend")

    # --- C. 世界 ---
    elif menu == 'World':
        st.title("🌍 MSC World")
        global_nodes = msc.get_global_nodes()
        t1, t2 = st.tabs(["2D MAP", "3D GALAXY"])
        with t1: msc.render_2d_world_map(global_nodes)
        with t2: msc.render_3d_galaxy(global_nodes)
