import streamlit as st
import msc_lib as msc
import msc_ai as ai
import msc_viz as viz
import time
import json
import streamlit_antd_components as sac

# ==========================================
# 🔐 登录页
# ==========================================
def render_login_page():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br><br><h1 style='text-align:center;font-weight:300;letter-spacing:4px'>MSC</h1>", unsafe_allow_html=True)
        st.markdown("<div style='text-align:center;color:#999;font-size:0.8em;letter-spacing:1px;margin-bottom:30px'>MEANING · STRUCTURE · CARE</div>", unsafe_allow_html=True)
        
        tab = sac.tabs(['LOGIN', 'SIGN UP'], align='center', size='sm', variant='outline')
        st.write("") 

        if tab == 'LOGIN':
            u = st.text_input("ID", placeholder="Username", label_visibility="collapsed")
            p = st.text_input("PASSWORD", type='password', placeholder="Password", label_visibility="collapsed")
            st.write("")
            if st.button("CONNECT", use_container_width=True, type="primary"):
                if msc.login_user(u, p):
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.session_state.nickname = msc.get_nickname(u)
                    st.rerun()
                else: sac.alert("Access Denied", color='red')
        else:
            nu = st.text_input("NEW ID", label_visibility="collapsed")
            np = st.text_input("NEW PW", type='password', label_visibility="collapsed")
            nn = st.text_input("NICK", label_visibility="collapsed")
            nc = st.selectbox("REGION", ["China", "USA", "UK"], label_visibility="collapsed")
            st.write("")
            if st.button("INITIALIZE", use_container_width=True):
                if msc.add_user(nu, np, nn, nc): sac.alert("Created", color='success')
                else: sac.alert("Failed", color='error')

# ==========================================
# 🤖 页面：AI 伴侣 (严格对齐版)
# ==========================================
def render_ai_page(username):
    # 顶部留白
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    # 1. 获取数据
    chat_history = msc.get_active_chats(username)
    nodes_map = msc.get_active_nodes_map(username)
    
    # 2. 逐行渲染：确保气泡和圆点在同一行
    for msg in chat_history:
        # 定义一行：左宽右窄
        c_msg, c_dot = st.columns([0.92, 0.08])
        
        with c_msg:
            if msg['role'] == 'user':
                # 用户：使用 CSS 右对齐气泡
                st.markdown(f"<div class='chat-bubble-me'>{msg['content']}</div>", unsafe_allow_html=True)
            else:
                # AI：使用 CSS 左对齐气泡
                st.markdown(f"<div class='chat-bubble-other'>{msg['content']}</div>", unsafe_allow_html=True)
        
        with c_dot:
            # 只有当这是【用户】发送的，且【有意义】时，才显示圆点
            if msg['role'] == 'user' and msg['content'] in nodes_map:
                node = nodes_map[msg['content']]
                # 包裹 div 方便垂直居中
                st.markdown('<div class="meaning-dot-wrapper">', unsafe_allow_html=True)
                with st.popover("●", help="Deep Meaning"):
                    st.caption(f"Score: {node.get('m_score', 0.5):.2f}")
                    st.markdown(f"**{node['care_point']}**")
                    st.info(node['insight'])
                    st.caption(f"Structure: {node['meaning_layer']}")
                st.markdown('</div>', unsafe_allow_html=True)

    # 3. 输入区
    if prompt := st.chat_input("Input..."):
        msc.save_chat(username, "user", prompt)
        
        # 乐观更新显示
        with st.container():
             st.markdown(f"<div class='chat-bubble-me'>{prompt}</div>", unsafe_allow_html=True)
        
        # AI 流式回复
        full_history = chat_history + [{'role':'user', 'content':prompt}]
        
        # 占位符显示正在思考
        with st.container():
            placeholder = st.empty()
            placeholder.markdown(f"<div class='chat-bubble-other'><span class='ai-thinking'>Thinking...</span></div>", unsafe_allow_html=True)
            
            try:
                # 调用 AI
                stream = ai.get_normal_response(full_history)
                # Streamlit 的 write_stream 需要在 chat_message 容器里才最好用，但我们自定义了 CSS
                # 所以这里我们手动收集流
                collected_text = ""
                for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        collected_text += content
                        # 实时更新气泡内容
                        placeholder.markdown(f"<div class='chat-bubble-other'>{collected_text}</div>", unsafe_allow_html=True)
                
                # 存入数据库
                msc.save_chat(username, "assistant", collected_text)
            except: 
                placeholder.markdown(f"<div class='chat-bubble-other'>Connection Error</div>", unsafe_allow_html=True)

        # 意义分析
        with st.spinner(""):
            analysis = ai.analyze_meaning_background(prompt)
            if analysis.get("valid", False):
                vec = ai.get_embedding(prompt)
                msc.save_node(username, prompt, analysis, "AI", vec)
                if "radar_scores" in analysis: msc.update_radar_score(username, analysis["radar_scores"])
                st.toast("Meaning Captured", icon="🌱")
        
        time.sleep(0.5)
        st.rerun()

# ==========================================
# 💬 页面：好友社交 (对齐版)
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
                label = f"{u['nickname']} {'🔴'+str(unread) if unread>0 else ''}"
                
                if st.button(f"{status_char} {label}", key=f"f_{u['username']}", use_container_width=True):
                    st.session_state.current_chat_partner = u['username']
                    msc.mark_messages_
