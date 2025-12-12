import streamlit as st
import msc_db as db   # 🌟 引用数据库
import msc_ai as ai   # 🌟 引用 AI
import msc_viz as viz # 🌟 引用绘图
import time
import json
import streamlit_antd_components as sac

# ... (CSS 保持 v53.3 的极简风，此处省略以节省篇幅，实际应保留 inject_custom_css) ...
def inject_custom_css():
    st.markdown("""<style>
    .stApp { background-color: #FFFFFF; font-family: 'Roboto', sans-serif; color: #222; }
    [data-testid="stSidebar"] { background-color: #FAFAFA; border-right: 1px solid #EEE; }
    .chat-bubble-me { background-color: #222; color: #fff; padding: 10px 16px; border-radius: 18px; float: right; }
    .chat-bubble-other { background-color: #F2F2F2; color: #222; padding: 10px 16px; border-radius: 18px; float: left; }
    .meaning-dot-btn button { border: none !important; color: #BBB !important; font-size: 18px !important; }
    .meaning-dot-btn button:hover { color: #1A73E8 !important; }
    </style>""", unsafe_allow_html=True)

# 🔐 登录页
def render_login_page():
    inject_custom_css()
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br><br><h1 style='text-align:center'>MSC</h1>", unsafe_allow_html=True)
        tab = sac.tabs(['LOGIN', 'SIGN UP'], align='center', size='sm', variant='outline')
        st.write("") 
        if tab == 'LOGIN':
            u = st.text_input("ID", label_visibility="collapsed")
            p = st.text_input("PASSWORD", type='password', label_visibility="collapsed")
            st.write("")
            if st.button("CONNECT", use_container_width=True, type="primary"):
                if db.login_user(u, p):
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.session_state.nickname = db.get_nickname(u)
                    st.rerun()
                else: sac.alert("Access Denied", color='red')
        else:
            nu = st.text_input("NEW ID", label_visibility="collapsed")
            np = st.text_input("NEW PW", type='password', label_visibility="collapsed")
            nn = st.text_input("NICK", label_visibility="collapsed")
            nc = st.selectbox("REGION", ["China", "USA"], label_visibility="collapsed")
            st.write("")
            if st.button("INIT", use_container_width=True):
                if db.add_user(nu, np, nn, nc): sac.alert("Created", color='success')
                else: sac.alert("Failed", color='error')

# 🤖 AI 页面
def render_ai_page(username):
    inject_custom_css()
    chat_history = db.get_active_chats(username)
    nodes_map = db.get_active_nodes_map(username)
    
    for msg in chat_history:
        c_msg, c_dot = st.columns([0.92, 0.08])
        with c_msg:
            if msg['role'] == 'user': st.markdown(f"<div class='chat-bubble-me'>{msg['content']}</div>", unsafe_allow_html=True)
            else: st.markdown(f"<div class='chat-bubble-other'>{msg['content']}</div>", unsafe_allow_html=True)
        with c_dot:
            if msg['role'] == 'user' and msg['content'] in nodes_map:
                node = nodes_map[msg['content']]
                st.markdown('<div class="meaning-dot-btn">', unsafe_allow_html=True)
                with st.popover("●"):
                    st.markdown(f"**{node['care_point']}**")
                    st.info(node['insight'])
                st.markdown('</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Input..."):
        db.save_chat(username, "user", prompt)
        with st.container(): st.markdown(f"<div class='chat-bubble-me'>{prompt}</div>", unsafe_allow_html=True)
        
        full_history = chat_history + [{'role':'user', 'content':prompt}]
        with st.chat_message("assistant"):
            try:
                stream = ai.get_normal_response(full_history)
                resp = st.write_stream(stream)
                db.save_chat(username, "assistant", resp)
            except: pass
        
        with st.spinner(""):
            analysis = ai.analyze_meaning_background(prompt)
            if analysis.get("valid", False):
                vec = ai.get_embedding(prompt)
                db.save_node(username, prompt, analysis, "AI", vec)
                if "radar_scores" in analysis: db.update_radar_score(username, analysis["radar_scores"])
                st.toast("Captured", icon="🌱")
        time.sleep(0.5); st.rerun()

# 💬 好友页面
def render_friends_page(username, unread_counts):
    inject_custom_css()
    col_list, col_chat = st.columns([0.3, 0.7])
    with col_list:
        st.caption("CONTACTS")
        users = db.get_all_users(username)
        if users:
            for u in users:
                unread = unread_counts.get(u['username'], 0)
                label = f"{u['nickname']} {'🔴'+str(unread) if unread>0 else ''}"
                if st.button(label, key=f"f_{u['username']}", use_container_width=True):
                    st.session_state.current_chat_partner = u['username']
                    db.mark_messages_read(u['username'], username)
                    st.rerun()

    with col_chat:
        partner = st.session_state.current_chat_partner
        if partner:
            c1, c2 = st.columns([0.8, 0.2])
            with c1: st.markdown(f"**{partner}**")
            
            history = db.get_direct_messages(username, partner)
            my_nodes = db.get_active_nodes_map(username)
            
            with st.container(height=500, border=False):
                for msg in history:
                    c_msg, c_dot = st.columns([0.92, 0.08])
                    with c_msg:
                        if msg['sender'] == 'AI': st.markdown(f"<div class='chat-bubble-other'>🤖 {msg['content']}</div>", unsafe_allow_html=True)
                        elif msg['sender'] == username: st.markdown(f"<div class='chat-bubble-me'>{msg['content']}</div>", unsafe_allow_html=True)
                        else: st.markdown(f"<div class='chat-bubble-other'>{msg['content']}</div>", unsafe_allow_html=True)
                    with c_dot:
                        if msg['sender'] == username and msg['content'] in my_nodes:
                            node = my_nodes[msg['content']]
                            st.markdown('<div class="meaning-dot-btn">', unsafe_allow_html=True)
                            with st.popover("●"): st.info(node['insight'])
                            st.markdown('</div>', unsafe_allow_html=True)
            
            if prompt := st.chat_input("Type..."):
                db.send_direct_message(username, partner, prompt)
                with st.spinner(""):
                    analysis = ai.analyze_meaning_background(prompt)
                    if analysis.get("valid", False):
                        vec = ai.get_embedding(prompt)
                        db.save_node(username, prompt, analysis, "私聊", vec)
                        match = ai.find_resonance(vec, username, analysis)
                        if match: st.toast("Resonance!", icon="⚡")
                st.rerun()

# 🌍 世界
def render_world_page():
    nodes = db.get_global_nodes()
    t1, t2 = st.tabs(["2D", "3D"])
    with t1: viz.render_2d_world_map(nodes)
    with t2: viz.render_3d_galaxy(nodes)
