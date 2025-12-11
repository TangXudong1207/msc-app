import streamlit as st
import streamlit_antd_components as sac
import msc_lib as msc
import time
import json
import random

# ==========================================
# 🎨 CSS
# ==========================================
def inject_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        .stApp { background-color: #F0F2F5; font-family: 'Roboto', sans-serif; color: #1F1F1F; }
        [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #E0E0E0; }
        .chat-bubble-me { background-color: #95EC69; color: #000; padding: 10px 14px; border-radius: 8px; margin-bottom: 5px; display: inline-block; float: right; clear: both; max-width: 80%; }
        .chat-bubble-other { background-color: #FFFFFF; color: #000; padding: 10px 14px; border-radius: 8px; margin-bottom: 5px; display: inline-block; float: left; clear: both; border: 1px solid #eee; max-width: 80%; }
        .chat-bubble-ai { background-color: #E3F2FD; color: #0D47A1; padding: 8px 12px; border-radius: 12px; margin: 10px 40px; display: block; clear: both; text-align: center; font-size: 0.9em; border: 1px dashed #90CAF9; }
        .meaning-dot { float: right; margin-right: 5px; margin-top: 15px; color: #ccc; cursor: help; font-size: 12px; }
        .meaning-dot:hover { color: #1A73E8; }
        .daily-card { background: linear-gradient(135deg, #e8f0fe 0%, #ffffff 100%); border: 1px solid #d2e3fc; border-radius: 12px; padding: 15px; margin-bottom: 20px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.set_page_config(page_title="MSC v50.0 Stable", layout="wide", initial_sidebar_state="expanded")
inject_custom_css()

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "current_chat_partner" not in st.session_state: st.session_state.current_chat_partner = None

# --- 登录 ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        st.markdown("<br><h1 style='text-align: center; color: #1A73E8;'>🔷 MSC</h1>", unsafe_allow_html=True)
        tab = sac.tabs([sac.TabsItem('登录'), sac.TabsItem('注册')], align='center', variant='outline')
        if tab == '登录':
            u = st.text_input("账号")
            p = st.text_input("密码", type='password')
            if st.button("登录", use_container_width=True, type="primary"):
                res = msc.login_user(u, p)
                if res:
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.session_state.nickname = res[0]['nickname']
                    st.session_state.messages = [] 
                    st.rerun()
                else: sac.alert("错误", color='red')
        else:
            nu = st.text_input("新账号")
            np = st.text_input("新密码", type='password')
            nn = st.text_input("昵称")
            nc = st.selectbox("地区", ["China", "USA", "UK", "Other"])
            if st.button("注册", use_container_width=True):
                if msc.add_user(nu, np, nn, nc): sac.alert("成功", color='success')
                else: sac.alert("失败", color='error')

# --- 主界面 ---
else:
    msc.update_heartbeat(st.session_state.username)
    user_profile = msc.get_user_profile(st.session_state.username)
    raw_radar = user_profile.get('radar_profile')
    if isinstance(raw_radar, str): radar_dict = json.loads(raw_radar)
    else: radar_dict = raw_radar if raw_radar else {k:3.0 for k in ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]}
    rank_name, rank_icon = msc.calculate_rank(radar_dict)
    total_unread, unread_counts = msc.get_unread_counts(st.session_state.username)

    with st.sidebar:
        st.markdown(f"### {rank_icon} {st.session_state.nickname}")
        st.caption(f"UID: {user_profile.get('uid', '---')}")
        
        if "daily_q" not in st.session_state: st.session_state.daily_q = None
        if st.session_state.daily_q is None:
            if st.button("📅 生成今日追问", use_container_width=True):
                with st.spinner("..."):
                    st.session_state.daily_q = msc.generate_daily_question(st.session_state.username, radar_dict)
                    st.rerun()
        else:
            st.markdown(f"<div class='daily-card'>{st.session_state.daily_q}</div>", unsafe_allow_html=True)

        msc.render_radar_chart(radar_dict, height="180px")
        
        menu = sac.menu([
            sac.MenuItem('AI 伴侣', icon='robot'),
            sac.MenuItem('好友', icon='chat-dots', tag=sac.Tag(str(total_unread), color='red') if total_unread > 0 else None),
            sac.MenuItem('星团', icon='people'),
            sac.MenuItem('世界', icon='globe'),
            sac.MenuItem('系统', type='group', children=[sac.MenuItem('退出登录', icon='box-arrow-right')]),
        ], index=0, format_func='title', open_all=True)

        st.divider()
        if st.button("🔭 全屏星云", use_container_width=True): 
            all_nodes = msc.get_all_nodes_for_map(st.session_state.username)
            msc.view_fullscreen_map(all_nodes, st.session_state.nickname)

    if menu == '退出登录': st.session_state.logged_in = False; st.rerun()

    # --- A. AI 伴侣 ---
    elif menu == 'AI 伴侣':
        st.subheader("🤖 AI 意义构建")
        chat_history_ai = msc.get_active_chats(st.session_state.username)
        nodes_map = msc.get_active_nodes_map(st.session_state.username)
        
        col_chat, col_node = st.columns([0.8, 0.2])
        with col_chat:
            for msg in chat_history_ai:
                with st.chat_message(msg['role']): st.markdown(msg['content'])
        with col_node:
            for msg in chat_history_ai:
                if msg['role'] == 'user' and msg['content'] in nodes_map:
                    node = nodes_map[msg['content']]
                    with st.popover("●", help="查看意义"):
                        st.caption(f"Score: {node.get('logic_score', 0.5)}")
                        st.info(node['insight'])
                else: st.write("")

        if prompt := st.chat_input("与 AI 对话..."):
            msc.save_chat(st.session_state.username, "user", prompt)
            full_history = chat_history_ai + [{'role':'user', 'content':prompt}]
            stream = msc.get_normal_response(full_history)
            try:
                reply = stream.choices[0].message.content
                msc.save_chat(st.session_state.username, "assistant", reply)
            except: pass
            
            with st.spinner(""):
                analysis = msc.analyze_meaning_background(prompt)
                if analysis.get("valid", False):
                    vec = msc.get_embedding(prompt)
                    msc.save_node(st.session_state.username, prompt, analysis, "日常", vec)
                    if "radar_scores" in analysis: msc.update_radar_score(st.session_state.username, analysis["radar_scores"])
            st.rerun()

    # --- B. 好友 ---
    elif menu == '好友':
        col_list, col_chat = st.columns([0.3, 0.7])
        with col_list:
            # 添加好友
            search_uid = st.text_input("🔍 UID", label_visibility="collapsed", placeholder="搜索 UID")
            st.caption("通讯录")
            users = msc.get_all_users(st.session_state.username)
            if users:
                for u in users:
                    # 🌟 修复：先获取状态，再渲染
                    is_online = msc.check_is_online(u.get('last_seen'))
                    status_icon = "🟢" if is_online else "⚪"
                    unread = unread_counts.get(u['username'], 0)
                    btn_label = f"{status_icon} {u['nickname']}"
                    if unread > 0: btn_label += f" 🔴 {unread}"
                    
                    if st.button(btn_label, key=f"f_{u['username']}", use_container_width=True):
                        st.session_state.current_chat_partner = u['username']
                        msc.mark_messages_read(u['username'], st.session_state.username)
                        st.rerun()
            else: st.info("暂无好友")

        with col_chat:
            partner = st.session_state.current_chat_partner
            if partner:
                st.markdown(f"**{partner}**")
                history = msc.get_direct_messages(st.session_state.username, partner)
                my_nodes = msc.get_active_nodes_map(st.session_state.username)

                with st.container(height=500):
                    chat_text_for_ai = ""
                    for msg in history:
                        chat_text_for_ai += f"{msg['sender']}: {msg['content']}\n"
                        col_msg, col_dot = st.columns([0.9, 0.1])
                        if msg['sender'] == 'AI':
                             st.markdown(f"<div class='chat-bubble-ai'>🤖 {msg['content']}</div>", unsafe_allow_html=True)
                        elif msg['sender'] == st.session_state.username:
                            with col_msg: st.markdown(f"<div class='chat-bubble-me'>{msg['content']}</div>", unsafe_allow_html=True)
                            with col_dot:
                                if msg['content'] in my_nodes:
                                    node = my_nodes[msg['content']]
                                    with st.popover("●"): st.info(node['insight'])
                        else:
                            with col_msg: st.markdown(f"<div class='chat-bubble-other'>{msg['content']}</div>", unsafe_allow_html=True)

                if st.button("🤖 AI 插话", use_container_width=True):
                    # 这里的 AI 插话逻辑可以在 msc_lib 里实现
                    pass 

                if prompt := st.chat_input(f"To {partner}..."):
                    msc.send_direct_message(st.session_state.username, partner, prompt)
                    with st.spinner(""):
                        analysis = msc.analyze_meaning_background(prompt)
                        if analysis.get("valid", False):
                            vec = msc.get_embedding(prompt)
                            msc.save_node(st.session_state.username, prompt, analysis, "私聊", vec)
                            match = msc.find_resonance(vec, st.session_state.username, analysis)
                            if match: st.toast("共鸣！", icon="⚡")
                    st.rerun()
            else: st.info("👈 选择好友")

    # --- C. 世界 ---
    elif menu == '世界':
        st.title("🌍 MSC World")
        global_nodes = msc.get_global_nodes()
        t1, t2 = st.tabs(["2D Earth", "3D Galaxy"])
        with t1: msc.render_2d_world_map(global_nodes)
        with t2: msc.render_3d_galaxy(global_nodes)
