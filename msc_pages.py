import streamlit as st
import streamlit_antd_components as sac
import msc_lib as msc
import time
import json

# ==========================================
# 🔐 页面：极简登录 (v48 风格回归)
# ==========================================
def render_login_page():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        # 极简标题，无背景卡片
        st.markdown("""
        <h1 style='text-align: center; font-weight: 300; letter-spacing: 4px; color: #333;'>MSC</h1>
        <div style='text-align: center; color: #999; font-size: 0.8em; margin-bottom: 30px; letter-spacing: 1px;'>
        MEANING · STRUCTURE · CARE
        </div>
        """, unsafe_allow_html=True)
        
        # 使用 SAC Tabs，线条风格
        tab = sac.tabs([
            sac.TabsItem('LOGIN', icon='box-arrow-in-right'),
            sac.TabsItem('SIGN UP', icon='person-plus'),
        ], align='center', size='sm', variant='outline')
        
        st.write("") # 留白

        if tab == 'LOGIN':
            u = st.text_input("ID", placeholder="Username", label_visibility="collapsed")
            p = st.text_input("PASSWORD", type='password', placeholder="Password", label_visibility="collapsed")
            
            st.write("")
            if st.button("CONNECT SYSTEM", use_container_width=True):
                res = msc.login_user(u, p)
                if res:
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.session_state.nickname = res[0]['nickname']
                    st.session_state.messages = [] 
                    st.rerun()
                else:
                    sac.alert("Access Denied", color='red', banner=True, icon='x-circle')

        else:
            nu = st.text_input("NEW ID", placeholder="New Username", label_visibility="collapsed")
            np = st.text_input("NEW PASSWORD", type='password', placeholder="New Password", label_visibility="collapsed")
            nn = st.text_input("NICKNAME", placeholder="Display Name", label_visibility="collapsed")
            nc = st.selectbox("REGION", ["China", "USA", "UK", "Japan", "Other"], label_visibility="collapsed")
            
            st.write("")
            if st.button("INITIALIZE IDENTITY", use_container_width=True):
                if msc.add_user(nu, np, nn, nc): 
                    sac.alert("Identity Created", color='success', banner=True, icon='check-circle')
                else: 
                    sac.alert("Creation Failed", color='error', banner=True, icon='x-circle')

# ==========================================
# 🤖 页面：AI 伴侣
# ==========================================
def render_ai_page(username):
    st.caption("🤖 DEEPSEEK LINKED")
    
    chat_history = msc.get_active_chats(username)
    nodes_map = msc.get_active_nodes_map(username)
    
    col_chat, col_node = st.columns([0.85, 0.15])
    
    with col_chat:
        for msg in chat_history:
            with st.chat_message(msg['role']): st.markdown(msg['content'])
    
    with col_node:
        for msg in chat_history:
            if msg['role'] == 'user' and msg['content'] in nodes_map:
                node = nodes_map[msg['content']]
                with st.popover("●", help="Meaning Structure"):
                    st.caption(f"Score: {node.get('logic_score', 0.5)}")
                    st.info(node['insight'])
                    st.caption(node['meaning_layer'])
            else:
                st.write("") # 占位保持对齐

    if prompt := st.chat_input("Input..."):
        msc.save_chat(username, "user", prompt)
        # 乐观更新
        full_history = chat_history + [{'role':'user', 'content':prompt}]
        
        # 调用 AI 回复
        stream = msc.get_normal_response(full_history)
        try:
            reply = stream.choices[0].message.content
            msc.save_chat(username, "assistant", reply)
        except: pass
        
        # 异步分析
        with st.spinner(""):
            analysis = msc.analyze_meaning_background(prompt)
            if analysis.get("valid", False):
                vec = msc.get_embedding(prompt)
                msc.save_node(username, prompt, analysis, "日常", vec)
                # 更新雷达
                if "radar_scores" in analysis: msc.update_radar_score(username, analysis["radar_scores"])
        
        st.rerun()

# ==========================================
# 💬 页面：好友私聊 (带实时刷新)
# ==========================================
def render_friends_page(username, unread_counts):
    col_list, col_chat = st.columns([0.3, 0.7])
    
    # 1. 好友列表
    with col_list:
        # 搜索框极简风
        st.text_input("🔍", placeholder="Search UID...", label_visibility="collapsed")
        
        users = msc.get_all_users(username)
        if users:
            st.markdown("---")
            for u in users:
                is_online = msc.check_is_online(u.get('last_seen'))
                # 极简状态点
                status_color = "#4CAF50" if is_online else "#E0E0E0"
                status_html = f"<span style='color:{status_color}; font-size:1.2em;'>•</span>"
                
                unread = unread_counts.get(u['username'], 0)
                unread_badge = f" <span style='background:#FF4B4B;color:white;padding:1px 6px;border-radius:10px;font-size:0.7em'>{unread}</span>" if unread > 0 else ""
                
                # 自定义按钮样式比较难，还是用原生按钮，但在label上做文章
                btn_label = f"{u['nickname']} {unread * '🔴'}" 
                
                if st.button(btn_label, key=f"f_{u['username']}", use_container_width=True):
                    st.session_state.current_chat_partner = u['username']
                    msc.mark_messages_read(u['username'], username)
                    st.rerun()
        else:
            st.caption("No connections yet.")

    # 2. 聊天窗口
    with col_chat:
        partner = st.session_state.current_chat_partner
        if partner:
            # 顶部栏：名字 + 实时开关
            c_name, c_switch = st.columns([0.8, 0.2])
            with c_name: st.markdown(f"**{partner}**")
            with c_switch: 
                # 实时开关
                auto_refresh = st.toggle("Live", value=False)
            
            if auto_refresh:
                time.sleep(3)
                st.rerun()

            history = msc.get_direct_messages(username, partner)
            my_nodes = msc.get_active_nodes_map(username)

            with st.container(height=500, border=False): # 无边框容器
                chat_str = ""
                for msg in history:
                    chat_str += f"{msg['sender']}: {msg['content']}\n"
                    
                    c_msg, c_dot = st.columns([0.9, 0.1])
                    if msg['sender'] == 'AI':
                         st.markdown(f"<div class='chat-bubble-ai'>🤖 {msg['content']}</div>", unsafe_allow_html=True)
                    elif msg['sender'] == username:
                        with c_msg: st.markdown(f"<div class='chat-bubble-me'>{msg['content']}</div>", unsafe_allow_html=True)
                        with c_dot:
                            if msg['content'] in my_nodes:
                                node = my_nodes[msg['content']]
                                with st.popover("●"): st.info(node['insight'])
                    else:
                        with c_msg: st.markdown(f"<div class='chat-bubble-other'>{msg['content']}</div>", unsafe_allow_html=True)

            # AI 插话
            if st.button("🤖 AI Observer", use_container_width=True, help="Invoke DeepSeek"):
                 with st.spinner("Analyzing..."):
                    comment = msc.get_ai_interjection(chat_str)
                    if comment:
                        msc.send_direct_message('AI', username, comment)
                        msc.send_direct_message('AI', partner, comment)
                        st.rerun()

            if prompt := st.chat_input("Type a message..."):
                msc.send_direct_message(username, partner, prompt)
                # 静默分析
                analysis = msc.analyze_meaning_background(prompt)
                if analysis.get("valid", False):
                    vec = msc.get_embedding(prompt)
                    msc.save_node(username, prompt, analysis, "私聊", vec)
                    match = msc.find_resonance(vec, username, analysis)
                    if match: st.toast("Resonance Detected", icon="⚡")
                st.rerun()
        else:
            st.caption("Select a contact to start.")

# ==========================================
# 🌍 页面：世界
# ==========================================
def render_world_page():
    st.caption("MSC GLOBAL VIEW")
    global_nodes = msc.get_global_nodes()
    t1, t2 = st.tabs(["2D MAP", "3D GALAXY"])
    with t1: msc.render_2d_world_map(global_nodes)
    with t2: msc.render_3d_galaxy(global_nodes)
