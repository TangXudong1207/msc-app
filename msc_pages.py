import streamlit as st
import msc_lib as msc
import time

# ==========================================
# 🤖 页面 A：AI 伴侣 (经典模式)
# ==========================================
def render_ai_page(username):
    st.subheader("🤖 AI 深度伴侣")
    
    # 1. 获取历史 (chats表)
    chat_history = msc.get_active_chats(username)
    nodes_map = msc.get_active_nodes_map(username)
    
    # 2. 渲染对话流
    for msg in chat_history:
        # 布局：左对话，右圆点
        c_chat, c_node = st.columns([0.85, 0.15])
        
        with c_chat:
            with st.chat_message(msg['role']):
                st.markdown(msg['content'])
        
        with c_node:
            # 如果是用户发的消息，且有意义节点，显示灰点
            if msg['role'] == 'user' and msg['content'] in nodes_map:
                node = nodes_map[msg['content']]
                with st.popover("●", help="查看我的深层意义"):
                    st.caption(f"Care: {node['care_point']}")
                    st.info(node['insight'])
                    st.caption(f"Structure: {node['meaning_layer']}")

    # 3. 输入处理
    if prompt := st.chat_input("与 AI 深聊..."):
        # 存用户
        msc.save_chat(username, "user", prompt)
        
        # AI 回复
        full_history = chat_history + [{'role':'user', 'content':prompt}]
        try:
            resp = msc.get_normal_response(full_history)
            reply = resp.choices[0].message.content
            msc.save_chat(username, "assistant", reply)
        except: pass
        
        # 意义分析
        with st.spinner(""):
            analysis = msc.analyze_meaning_background(prompt)
            if analysis.get("valid", False):
                vec = msc.get_embedding(prompt)
                msc.save_node(username, prompt, analysis, "AI对话", vec)
                if "radar_scores" in analysis: msc.update_radar_score(username, analysis["radar_scores"])
        
        st.rerun()

# ==========================================
# 💬 页面 B：好友社交 (微信模式)
# ==========================================
def render_friends_page(username, unread_counts):
    col_list, col_chat = st.columns([0.3, 0.7])
    
    # --- 左侧：通讯录 ---
    with col_list:
        st.caption("通讯录")
        users = msc.get_all_users(username)
        if users:
            for u in users:
                is_online = msc.check_is_online(u['last_seen'])
                status_icon = "🟢" if is_online else "⚪"
                unread = unread_counts.get(u['username'], 0)
                
                label = f"{status_icon} {u['nickname']}"
                if unread > 0: label += f" 🔴{unread}"
                
                if st.button(label, key=f"f_{u['username']}", use_container_width=True):
                    st.session_state.current_chat_partner = u['username']
                    msc.mark_messages_read(u['username'], username)
                    st.rerun()
        else:
            st.info("暂无其他居民")

    # --- 右侧：聊天窗 ---
    with col_chat:
        partner = st.session_state.get('current_chat_partner')
        if partner:
            st.markdown(f"**{partner}**")
            history = msc.get_direct_messages(username, partner)
            my_nodes = msc.get_active_nodes_map(username)
            
            # 聊天容器
            with st.container(height=500):
                chat_text_context = "" # 用于 AI 观察
                for msg in history:
                    chat_text_context += f"{msg['sender']}: {msg['content']}\n"
                    
                    # 布局：消息体 + 意义点
                    c_msg, c_dot = st.columns([0.9, 0.1])
                    
                    with c_msg:
                        if msg['sender'] == 'AI': # AI 插话
                            st.markdown(f"<div class='chat-bubble-ai'>🤖 {msg['content']}</div>", unsafe_allow_html=True)
                        elif msg['sender'] == username: # 我发的
                            st.markdown(f"<div class='chat-bubble-me'>{msg['content']}</div>", unsafe_allow_html=True)
                        else: # 对方发的
                            st.markdown(f"<div class='chat-bubble-other'>{msg['content']}</div>", unsafe_allow_html=True)
                    
                    with c_dot:
                        # 🌟 隐私保护：只显示我自己的意义点
                        if msg['sender'] == username and msg['content'] in my_nodes:
                            node = my_nodes[msg['content']]
                            with st.popover("●", help="私密意义"):
                                st.caption(node['care_point'])
                                st.info(node['insight'])

            # 功能栏：AI 插话按钮
            if st.button("🤖 AI 观察者插话", help="让 DeepSeek 评价当前对话", use_container_width=True):
                with st.spinner("AI 正在吃瓜..."):
                    comment = msc.get_ai_interjection(chat_text_context)
                    if comment:
                        # 这里的逻辑：存入 direct_messages，sender='AI'
                        # 为了让双方都看到，需要存两条，或者数据库支持群组ID。
                        # 简单起见：给双方各发一条
                        msc.send_direct_message('AI', username, comment)
                        msc.send_direct_message('AI', partner, comment)
                        st.rerun()

            # 输入框
            if prompt := st.chat_input(f"发给 {partner}..."):
                msc.send_direct_message(username, partner, prompt)
                
                # 静默意义分析
                with st.spinner(""):
                    analysis = msc.analyze_meaning_background(prompt)
                    if analysis.get("valid", False):
                        vec = msc.get_embedding(prompt)
                        msc.save_node(username, prompt, analysis, "私聊", vec)
                        match = msc.find_resonance(vec, username, analysis)
                        if match: st.toast("私聊中产生共鸣！", icon="⚡")
                st.rerun()
        else:
            st.info("👈 请选择一位好友")

# ==========================================
# 🪐 页面 C：星团群组
# ==========================================
def render_cluster_page(username):
    st.subheader("🌌 意义自组织星团")
    rooms = msc.get_available_rooms()
    if rooms:
        for room in rooms:
            with st.expander(f"{room['name']}", expanded=True):
                st.caption(room['description'])
                if st.button("进入星团", key=f"join_{room['id']}"):
                    msc.join_room(room['id'], username)
                    msc.view_group_chat(room, username)
    else:
        st.info("暂无星团，等待意义汇聚...")

# ==========================================
# 🌍 页面 D：世界 (World)
# ==========================================
def render_world_page():
    st.title("🌍 MSC World")
    global_nodes = msc.get_global_nodes()
    t1, t2 = st.tabs(["2D Earth", "3D Galaxy"])
    with t1: msc.render_2d_world_map(global_nodes)
    with t2: msc.render_3d_galaxy(global_nodes)
