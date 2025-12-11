import streamlit as st
import streamlit_antd_components as sac
import msc_lib as msc
import msc_config as config
import time
import json

# ==========================================
# 🎨 CSS
# ==========================================
def inject_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        .stApp { background-color: #F0F2F5; font-family: 'Roboto', sans-serif; color: #1F1F1F; }
        [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #E0E0E0; }
        
        .chat-bubble-me {
            background-color: #95EC69; color: #000; padding: 10px 14px; border-radius: 8px; 
            margin-bottom: 5px; display: inline-block; float: right; clear: both; max-width: 80%;
            box-shadow: 0 1px 1px rgba(0,0,0,0.1);
        }
        .chat-bubble-other {
            background-color: #FFFFFF; color: #000; padding: 10px 14px; border-radius: 8px; 
            margin-bottom: 5px; display: inline-block; float: left; clear: both; 
            border: 1px solid #eee; max-width: 80%;
        }
        .chat-bubble-ai {
            background-color: #E3F2FD; color: #0D47A1; padding: 8px 12px; border-radius: 12px;
            margin: 10px 40px; display: block; clear: both; text-align: center; font-size: 0.9em;
            border: 1px dashed #90CAF9;
        }
        
        /* 意义小圆点 (Tooltip) */
        .meaning-dot {
            float: right; margin-right: 5px; margin-top: 15px; 
            color: #ccc; cursor: help; font-size: 12px;
        }
        .meaning-dot:hover { color: #1A73E8; }
    </style>
    """, unsafe_allow_html=True)

st.set_page_config(page_title="MSC v47.0 Social", layout="wide", initial_sidebar_state="expanded")
inject_custom_css()

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "current_chat_partner" not in st.session_state: st.session_state.current_chat_partner = None

# --- 登录 ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: #1A73E8;'>🔷 MSC</h1>", unsafe_allow_html=True)
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
                    st.rerun()
                else: sac.alert("错误", color='red')
        else:
            nu = st.text_input("新账号")
            np = st.text_input("新密码", type='password')
            nn = st.text_input("昵称")
            if st.button("注册", use_container_width=True):
                if msc.add_user(nu, np, nn): sac.alert("成功", color='success')
                else: sac.alert("失败", color='error')

# --- 主界面 ---
else:
    msc.update_heartbeat(st.session_state.username)
    user_profile = msc.get_user_profile(st.session_state.username)
    total_unread, unread_counts = msc.get_unread_counts(st.session_state.username)

    # --- 侧边栏 ---
    with st.sidebar:
        st.markdown(f"### {st.session_state.nickname}")
        
        menu = sac.menu([
            sac.MenuItem('好友', icon='chat-dots', tag=sac.Tag(str(total_unread), color='red') if total_unread > 0 else None),
            sac.MenuItem('星团', icon='people'),
            sac.MenuItem('世界', icon='globe'),
            sac.MenuItem('系统', type='group', children=[sac.MenuItem('退出登录', icon='box-arrow-right')]),
        ], index=0, format_func='title', open_all=True)

        if menu == '好友':
            st.divider()
            # 每日追问 (仅在好友页显示)
            if "daily_q" not in st.session_state: st.session_state.daily_q = None
            if st.session_state.daily_q is None:
                if st.button("📅 生成今日追问", use_container_width=True):
                    with st.spinner("..."):
                        # 简单的 radar 默认值，防止报错
                        radar = {"Care":3} 
                        st.session_state.daily_q = msc.generate_daily_question(st.session_state.username, radar)
                        st.rerun()
            else:
                st.info(st.session_state.daily_q)

    if menu == '退出登录': st.session_state.logged_in = False; st.rerun()

    # --- A. 好友聊天 (核心重构) ---
    elif menu == '好友':
        col_list, col_chat = st.columns([0.3, 0.7])
        
        # 1. 好友列表
        with col_list:
            st.caption("通讯录")
            users = msc.get_all_users(st.session_state.username)
            if users:
                for u in users:
                    is_online = msc.check_is_online(u['last_seen'])
                    status_icon = "🟢" if is_online else "⚪"
                    unread = unread_counts.get(u['username'], 0)
                    btn_label = f"{status_icon} {u['nickname']}"
                    if unread > 0: btn_label += f" 🔴 {unread}"
                    
                    if st.button(btn_label, key=f"f_{u['username']}", use_container_width=True):
                        st.session_state.current_chat_partner = u['username']
                        msc.mark_messages_read(u['username'], st.session_state.username)
                        st.rerun()

        # 2. 聊天窗口
        with col_chat:
            partner = st.session_state.current_chat_partner
            if partner:
                st.markdown(f"**{partner}**")
                
                # 获取历史和节点
                history = msc.get_direct_messages(st.session_state.username, partner)
                my_nodes = msc.get_active_nodes_map(st.session_state.username)

                # 渲染聊天记录
                with st.container(height=500):
                    chat_text_for_ai = "" # 用于发给 AI 观察者
                    
                    for msg in history:
                        chat_text_for_ai += f"{msg['sender']}: {msg['content']}\n"
                        
                        # 渲染 AI 插话 (Role = 'assistant')
                        if msg.get('role') == 'assistant': # 假设我们在 save_chat 时区分了
                            # 但目前的 direct_messages 表只有 sender/receiver
                            # 我们用 sender='AI' 来标记 AI 插话
                            pass

                        if msg['sender'] == 'AI':
                             st.markdown(f"<div class='chat-bubble-ai'>🤖 {msg['content']}</div>", unsafe_allow_html=True)
                        elif msg['sender'] == st.session_state.username:
                            # 🌟 私密意义点：如果这句话有意义，显示小圆点 Popover
                            extra_html = ""
                            if msg['content'] in my_nodes:
                                node = my_nodes[msg['content']]
                                with st.popover("●", help="点击查看我的私密意义"):
                                    st.caption(f"Care: {node['care_point']}")
                                    st.info(node['insight'])
                            
                            st.markdown(f"<div class='chat-bubble-me'>{msg['content']}</div>", unsafe_allow_html=True)
                        else:
                            # 对方的消息，不显示意义点
                            st.markdown(f"<div class='chat-bubble-other'>{msg['content']}</div>", unsafe_allow_html=True)

                # 🤖 AI 观察者按钮
                if st.button("🤖 AI 插话", help="让 DeepSeek 评价一下你们的对话", use_container_width=True):
                    with st.spinner("AI 正在吃瓜..."):
                        comment = msc.get_ai_interjection(chat_text_for_ai)
                        if comment:
                            # 存入数据库，sender 设为 'AI'
                            msc.send_direct_message('AI', st.session_state.username, comment) 
                            # 注意：这里只发给了自己看，还是双方看？通常是双方
                            # 如果要双方看，需要 sender='AI', receiver=room_id? 
                            # 简化起见，我们把 AI 的话分别发给两个人
                            msc.send_direct_message('AI', partner, comment)
                            st.rerun()

                # 发送框
                if prompt := st.chat_input("..."):
                    msc.send_direct_message(st.session_state.username, partner, prompt)
                    
                    # 静默意义分析
                    with st.spinner(""):
                        analysis = msc.analyze_meaning_background(prompt)
                        if analysis.get("valid", False):
                            vec = msc.get_embedding(prompt)
                            msc.save_node(st.session_state.username, prompt, analysis, "私聊", vec)
                    st.rerun()
            else:
                st.info("👈 请选择好友")

    # --- C. 星团 ---
    elif menu == '星团':
        st.subheader("🌌 意义星团")
        rooms = msc.get_available_rooms()
        if rooms:
            for room in rooms:
                if st.button(f"🌌 {room['name']}", use_container_width=True):
                    msc.join_room(room['id'], st.session_state.username)
                    msc.view_group_chat(room, st.session_state.username)

    # --- D. 世界 ---
    elif menu == '世界':
        st.title("🌍 MSC World")
        global_nodes = msc.get_global_nodes()
        t1, t2 = st.tabs(["2D Earth", "3D Galaxy"])
        with t1: msc.render_2d_world_map(global_nodes)
        with t2: msc.render_3d_galaxy(global_nodes)
