import streamlit as st
import streamlit_antd_components as sac
import msc_lib as msc
import time
import json

# ==========================================
# 🎨 CSS：极简科技风 (登录页优化)
# ==========================================
def inject_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        .stApp { background-color: #FFFFFF; font-family: 'Roboto', sans-serif; color: #1F1F1F; }
        [data-testid="stSidebar"] { background-color: #F8F9FA; border-right: 1px solid #E0E0E0; }
        
        /* 登录卡片 */
        .login-card {
            background: white;
            padding: 2rem;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            border: 1px solid #EAEAEA;
            text-align: center;
        }
        
        /* 聊天气泡 */
        .chat-bubble-me {
            background-color: #95EC69; color: #000; padding: 10px 14px; border-radius: 8px; 
            margin-bottom: 5px; display: inline-block; float: right; clear: both; max-width: 80%;
        }
        .chat-bubble-other {
            background-color: #F5F5F5; color: #000; padding: 10px 14px; border-radius: 8px; 
            margin-bottom: 5px; display: inline-block; float: left; clear: both; max-width: 80%;
        }
        
        /* 意义小圆点 */
        .meaning-dot { color: #ccc; cursor: pointer; font-size: 14px; margin-left: 5px; }
        .meaning-dot:hover { color: #1A73E8; }
    </style>
    """, unsafe_allow_html=True)

st.set_page_config(page_title="MSC v49.0 Global", layout="wide", initial_sidebar_state="expanded")
inject_custom_css()

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "current_chat_partner" not in st.session_state: st.session_state.current_chat_partner = None

# --- 场景 1: 极简登录 ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1,1.2,1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        # 登录卡片容器
        with st.container(border=True):
            st.markdown("<h1 style='text-align: center; color: #1A73E8; margin-bottom:0;'>🔷 MSC</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #888; font-size: 0.9em;'>MEANING · STRUCTURE · CARE</p>", unsafe_allow_html=True)
            
            tab = sac.tabs([sac.TabsItem('登录'), sac.TabsItem('注册')], align='center', size='sm')
            
            if tab == '登录':
                u = st.text_input("账号 / UID", placeholder="请输入用户名")
                p = st.text_input("密码", type='password', placeholder="请输入密码")
                if st.button("进入系统", use_container_width=True, type="primary"):
                    res = msc.login_user(u, p)
                    if res:
                        st.session_state.logged_in = True
                        st.session_state.username = u
                        st.session_state.nickname = res[0]['nickname']
                        st.session_state.messages = [] 
                        st.rerun()
                    else: st.error("账号或密码错误")
            else:
                nu = st.text_input("设置账号 (英文)", placeholder="例如: alice")
                np = st.text_input("设置密码", type='password')
                nn = st.text_input("你的昵称", placeholder="例如: 爱丽丝")
                # 🌟 新增：国籍选择
                nc = st.selectbox("选择地区 (将在地球上点亮)", ["China", "USA", "UK", "Japan", "Germany", "France", "Canada", "Australia", "Russia", "India", "Brazil", "Other"])
                
                if st.button("创建公民身份", use_container_width=True):
                    if msc.add_user(nu, np, nn, nc): 
                        st.success("注册成功！请切换到登录页。")
                        st.balloons()
                    else: st.error("注册失败，用户可能已存在")

# --- 场景 2: 主应用 ---
else:
    # 心跳
    msc.update_heartbeat(st.session_state.username)
    
    # 数据加载
    user_profile = msc.get_user_profile(st.session_state.username)
    raw_radar = user_profile.get('radar_profile')
    if isinstance(raw_radar, str): radar_dict = json.loads(raw_radar)
    else: radar_dict = raw_radar if raw_radar else {k:3.0 for k in ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]}
    
    rank_name, rank_icon = msc.calculate_rank(radar_dict)
    total_unread, unread_counts = msc.get_unread_counts(st.session_state.username)

    # --- 侧边栏 ---
    with st.sidebar:
        c_avatar, c_info = st.columns([0.3, 0.7])
        with c_info:
            st.markdown(f"**{st.session_state.nickname}**")
            # 显示 UID 和段位
            st.caption(f"UID: `{user_profile.get('uid', '---')}`")
            st.caption(f"{rank_icon} {rank_name}")
        
        if "daily_q" not in st.session_state: st.session_state.daily_q = None
        if st.button("📅 今日追问", use_container_width=True):
             with st.spinner("..."):
                st.session_state.daily_q = msc.generate_daily_question(st.session_state.username, radar_dict)
        if st.session_state.daily_q:
            st.info(st.session_state.daily_q)

        msc.render_radar_chart(radar_dict, height="180px")
        
        menu = sac.menu([
            sac.MenuItem('AI 伴侣', icon='robot'),
            sac.MenuItem('好友', icon='chat-dots', tag=sac.Tag(str(total_unread), color='red') if total_unread > 0 else None),
            sac.MenuItem('世界', icon='globe'),
            sac.MenuItem('系统', type='group', children=[sac.MenuItem('退出登录', icon='box-arrow-right')]),
        ], index=0, format_func='title', open_all=True)

    if menu == '退出登录': st.session_state.logged_in = False; st.rerun()

    # --- A. AI 伴侣 ---
    elif menu == 'AI 伴侣':
        st.caption("🤖 AI 深度伴侣 (独立记忆)")
        chat_history_ai = msc.get_active_chats(st.session_state.username)
        nodes_map = msc.get_active_nodes_map(st.session_state.username)
        
        # 8:2 布局
        col_chat, col_node = st.columns([0.85, 0.15])
        
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

    # --- B. 好友 (通讯录) ---
    elif menu == '好友':
        col_list, col_chat = st.columns([0.35, 0.65])
        
        with col_list:
            # 🌟 新增：添加好友搜索框
            search_uid = st.text_input("🔍 搜索 UID 添加", placeholder="输入8位数字")
            if search_uid:
                # 简单实现：在所有用户里搜
                st.caption(f"搜索结果: {search_uid}")
                # (实际应该去数据库查，这里暂时还是显示列表)

            st.caption("我的好友")
            users = msc.get_all_users(st.session_state.username)
            
            if users:
                for u in users:
                    # 在线状态
                    is_online = msc.check_is_online(u['last_seen'])
                    status_dot = "🟢" if is_online else "⚪"
                    
                    unread = unread_counts.get(u['username'], 0)
                    
                    # 列表项设计
                    bg_color = "#e6f7ff" if st.session_state.current_chat_partner == u['username'] else "white"
                    with st.container(border=True):
                        c1, c2 = st.columns([0.8, 0.2])
                        with c1:
                            st.markdown(f"**{u['nickname']}**")
                            st.caption(f"{status_icon} | UID: {u.get('uid', '---')}")
                        with c2:
                            if unread > 0: st.markdown(f"🔴 {unread}")
                            if st.button("聊", key=f"chat_{u['username']}"):
                                st.session_state.current_chat_partner = u['username']
                                msc.mark_messages_read(u['username'], st.session_state.username)
                                st.rerun()
            else: st.info("暂无好友")

        # 聊天窗
        with col_chat:
            partner = st.session_state.current_chat_partner
            if partner:
                st.markdown(f"**{partner}**")
                history = msc.get_direct_messages(st.session_state.username, partner)
                my_nodes = msc.get_active_nodes_map(st.session_state.username)

                # 聊天容器
                with st.container(height=500):
                    for msg in history:
                        col_msg, col_dot = st.columns([0.9, 0.1])
                        
                        if msg['sender'] == st.session_state.username: # 我发的
                            with col_msg:
                                st.markdown(f"<div class='chat-bubble-me'>{msg['content']}</div>", unsafe_allow_html=True)
                            with col_dot:
                                # 私密小圆点
                                if msg['content'] in my_nodes:
                                    node = my_nodes[msg['content']]
                                    with st.popover("●", help="私密意义"):
                                        st.caption("仅自己可见")
                                        st.info(node['insight'])
                        else: # 对方发的
                            with col_msg:
                                st.markdown(f"<div class='chat-bubble-other'>{msg['content']}</div>", unsafe_allow_html=True)

                if prompt := st.chat_input(f"To {partner}..."):
                    msc.send_direct_message(st.session_state.username, partner, prompt)
                    with st.spinner(""):
                        analysis = msc.analyze_meaning_background(prompt)
                        if analysis.get("valid", False):
                            vec = msc.get_embedding(prompt)
                            msc.save_node(st.session_state.username, prompt, analysis, "私聊", vec)
                            # 共鸣逻辑...
                    st.rerun()
            else:
                st.info("👈 请在左侧选择一位好友")

    # --- D. 世界 ---
    elif menu == '世界':
        st.caption("🌍 上帝视角")
        global_nodes = msc.get_global_nodes()
        # 🌟 默认显示 2D 地图，因为有了坐标，它会很漂亮
        msc.render_2d_world_map(global_nodes)
