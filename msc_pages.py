import streamlit as st
import msc_lib as msc
import time
import json
import streamlit_antd_components as sac

# ==========================================
# 🔐 页面：极简登录
# ==========================================
def render_login_page():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("""
        <h1 style='text-align: center; font-weight: 300; letter-spacing: 4px; color: #333;'>MSC</h1>
        <div style='text-align: center; color: #999; font-size: 0.8em; margin-bottom: 30px; letter-spacing: 1px;'>
        MEANING · STRUCTURE · CARE
        </div>
        """, unsafe_allow_html=True)
        
        tab = sac.tabs([sac.TabsItem('LOGIN'), sac.TabsItem('SIGN UP')], align='center', size='sm', variant='outline')
        st.write("") 

        if tab == 'LOGIN':
            u = st.text_input("ID", placeholder="Username", label_visibility="collapsed")
            p = st.text_input("PASSWORD", type='password', placeholder="Password", label_visibility="collapsed")
            st.write("")
            if st.button("CONNECT", use_container_width=True, type="primary"):
                res = msc.login_user(u, p)
                if res:
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.session_state.nickname = res[0]['nickname']
                    st.session_state.messages = [] 
                    st.rerun()
                else: sac.alert("Access Denied", color='red')
        else:
            nu = st.text_input("NEW ID", placeholder="New Username", label_visibility="collapsed")
            np = st.text_input("NEW PASSWORD", type='password', placeholder="New Password", label_visibility="collapsed")
            nn = st.text_input("NICKNAME", placeholder="Display Name", label_visibility="collapsed")
            nc = st.selectbox("REGION", ["China", "USA", "UK", "Other"], label_visibility="collapsed")
            st.write("")
            if st.button("INITIALIZE", use_container_width=True):
                if msc.add_user(nu, np, nn, nc): sac.alert("Created", color='success')
                else: sac.alert("Failed", color='error')

# ==========================================
# 🤖 页面：AI 伴侣 (修复流式输出)
# ==========================================
def render_ai_page(username):
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    chat_history = msc.get_active_chats(username)
    nodes_map = msc.get_active_nodes_map(username)
    
    # 渲染历史记录
    for msg in chat_history:
        c_msg, c_dot = st.columns([0.92, 0.08])
        with c_msg:
            role = "user" if msg['role'] == "user" else "assistant"
            # 根据角色应用不同样式
            if role == "user":
                st.markdown(f"<div class='chat-bubble-me'>{msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-bubble-other'>{msg['content']}</div>", unsafe_allow_html=True)
        
        with c_dot:
            if msg['role'] == 'user' and msg['content'] in nodes_map:
                node = nodes_map[msg['content']]
                st.markdown('<div class="meaning-dot-btn">', unsafe_allow_html=True)
                with st.popover("●", help="Deep Meaning"):
                    raw_score = node.get('m_score')
                    score_val = float(raw_score) if raw_score is not None else 0.0
                    st.caption(f"MSC Score: {score_val:.2f}")
                    st.markdown(f"**{node['care_point']}**")
                    st.info(node['insight'])
                    st.caption(f"Structure: {node['meaning_layer']}")
                st.markdown('</div>', unsafe_allow_html=True)

    # 输入处理
    if prompt := st.chat_input("Input..."):
        # 1. 存用户输入
        msc.save_chat(username, "user", prompt)
        
        # 2. 乐观更新：显示用户气泡
        with st.container():
             st.markdown(f"<div class='chat-bubble-me'>{prompt}</div>", unsafe_allow_html=True)
        
        # 3. 🌟 修复：正确处理 AI 流式回复
        full_history = chat_history + [{'role':'user', 'content':prompt}]
        
        # 创建一个空容器来放 AI 的正在输入的状态
        with st.container():
            with st.chat_message("assistant"): # 临时使用官方组件显示流动画
                try:
                    stream = msc.get_normal_response(full_history)
                    # write_stream 会自动处理生成器，并返回最终文本
                    response_text = st.write_stream(stream) 
                    # 4. 存 AI 回复
                    msc.save_chat(username, "assistant", response_text)
                except Exception as e:
                    st.error(f"AI 连接中断: {e}")
        
        # 5. 意义分析
        with st.spinner(""):
            analysis = msc.analyze_meaning_background(prompt)
            if analysis.get("valid", False):
                vec = msc.get_embedding(prompt)
                msc.save_node(username, prompt, analysis, "AI对话", vec)
                if "radar_scores" in analysis: msc.update_radar_score(username, analysis["radar_scores"])
                st.toast("Meaning Captured", icon="🌱")
        
        # 刷新页面以显示最终样式
        time.sleep(0.5)
        st.rerun()

# ==========================================
# 💬 页面：好友社交
# ==========================================
def render_friends_page(username, unread_counts):
    col_list, col_chat = st.columns([0.3, 0.7])
    
    with col_list:
        st.caption("CONTACTS")
        users = msc.get_all_users(username)
        if users:
            for u in users:
                is_online = msc.check_is_online(u.get('last_seen'))
                status_char = "🟢" if is_online else "⚪"
                unread = unread_counts.get(u['username'], 0)
                final_label = f"{status_char} {u['nickname']}"
                if unread > 0: final_label += f" 🔴 {unread}"
                
                if st.button(final_label, key=f"f_{u['username']}", use_container_width=True):
                    st.session_state.current_chat_partner = u['username']
                    msc.mark_messages_read(u['username'], username)
                    st.rerun()
        else:
            st.caption("No friends yet.")

    with col_chat:
        partner = st.session_state.current_chat_partner
        if partner:
            c1, c2 = st.columns([0.8, 0.2])
            with c1: st.markdown(f"**{partner}**")
            with c2: 
                if st.button("🤖", help="AI Observer"):
                    pass 

            history = msc.get_direct_messages(username, partner)
            my_nodes = msc.get_active_nodes_map(username)

            with st.container(height=500, border=False):
                chat_str = ""
                for msg in history:
                    chat_str += f"{msg['sender']}: {msg['content']}\n"
                    c_msg, c_dot = st.columns([0.92, 0.08])
                    
                    with c_msg:
                        if msg['sender'] == 'AI':
                            st.markdown(f"<div class='chat-bubble-ai'>🤖 {msg['content']}</div>", unsafe_allow_html=True)
                        elif msg['sender'] == username:
                            st.markdown(f"<div class='chat-bubble-me'>{msg['content']}</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div class='chat-bubble-other'>{msg['content']}</div>", unsafe_allow_html=True)
                    
                    with c_dot:
                        if msg['sender'] == username and msg['content'] in my_nodes:
                            node = my_nodes[msg['content']]
                            st.markdown('<div class="meaning-dot-btn">', unsafe_allow_html=True)
                            with st.popover("●"):
                                st.info(node['insight'
