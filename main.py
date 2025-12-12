import streamlit as st
import streamlit_antd_components as sac
import msc_lib as msc
import time
import json

# ==========================================
# 🎨 CSS：极简科技风 (黑白灰 + 隐藏头像)
# ==========================================
def inject_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        
        /* 1. 全局基调 */
        .stApp { background-color: #FFFFFF; font-family: 'Roboto', sans-serif; color: #222; }
        [data-testid="stSidebar"] { background-color: #FAFAFA; border-right: 1px solid #E0E0E0; }
        
        /* 2. 隐藏 Streamlit 原生头像 (关键一步) */
        .stChatMessage .stChatMessageAvatarBackground { display: none !important; }
        [data-testid="stChatMessageAvatar"] { display: none !important; }
        
        /* 3. 聊天气泡：极简色块 */
        
        /* 我 (右侧，深黑，直角硬朗风格) */
        .chat-bubble-me {
            background-color: #222; 
            color: #fff; 
            padding: 10px 16px; 
            border-radius: 12px; 
            border-bottom-right-radius: 2px;
            margin-bottom: 8px; 
            display: inline-block; 
            float: right; 
            clear: both; 
            max-width: 85%;
            font-size: 15px; 
            line-height: 1.5;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        /* 对方/AI (左侧，浅灰，柔和风格) */
        .chat-bubble-other {
            background-color: #F2F2F2; 
            color: #222; 
            padding: 10px 16px; 
            border-radius: 12px; 
            border-bottom-left-radius: 2px;
            margin-bottom: 8px; 
            display: inline-block; 
            float: left; 
            clear: both; 
            max-width: 85%;
            font-size: 15px; 
            line-height: 1.5;
            border: 1px solid #E5E5E5;
        }
        
        /* AI 思考时的临时状态 */
        .chat-bubble-ai-thinking {
            color: #999; font-style: italic; font-size: 0.9em; margin-left: 10px;
        }

        /* 4. 意义小圆点 (垂直居中，极简) */
        .meaning-dot-wrapper {
            display: flex; 
            align-items: center; 
            justify-content: center; 
            height: 100%; 
            padding-top: 10px; /* 微调对齐 */
        }
        
        /* 5. 每日卡片 & 登录卡片 */
        .daily-card { border: 1px solid #eee; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 20px; background: #fff; }
        .login-card { background: white; padding: 2rem; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); text-align: center; }
        
        /* 6. 消除列间距，让点紧贴气泡 */
        [data-testid="column"] { padding: 0 !important; }
    </style>
    """, unsafe_allow_html=True)

st.set_page_config(page_title="MSC v70.2 Aligned", layout="wide", initial_sidebar_state="expanded")
inject_custom_css()

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "current_chat_partner" not in st.session_state: st.session_state.current_chat_partner = None

# --- 1. 登录注册 ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        st.markdown("<br><h1 style='text-align: center; color: #1A73E8; font-weight:300; letter-spacing:2px;'>MSC</h1>", unsafe_allow_html=True)
        tab = sac.tabs([sac.TabsItem('LOGIN'), sac.TabsItem('SIGN UP')], align='center', variant='outline')
        
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
            nu = st.text_input("NEW ID", label_visibility="collapsed")
            np = st.text_input("NEW PASSWORD", type='password', label_visibility="collapsed")
            nn = st.text_input("NICKNAME", label_visibility="collapsed")
            nc = st.selectbox("REGION", ["China", "USA", "UK", "Other"], label_visibility="collapsed")
            st.write("")
            if st.button("INITIALIZE", use_container_width=True):
                if msc.add_user(nu, np, nn, nc): sac.alert("Success", color='success')
                else: sac.alert("Failed", color='error')

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
            if st.button("📅 Insight", use_container_width=True):
                with st.spinner("."):
                    st.session_state.daily_q = msc.generate_daily_question(st.session_state.username, radar_dict)
                    st.rerun()
        else:
            st.markdown(f"<div class='daily-card'><div style='font-size:10px;color:#999'>DAILY Q</div>{st.session_state.daily_q}</div>", unsafe_allow_html=True)
            if st.button("🔄"): st.session_state.daily_q = None; st.rerun()

        msc.render_radar_chart(radar_dict, height="160px")
        
        menu = sac.menu([
            sac.MenuItem('AI Partner', icon='robot'),
            sac.MenuItem('Chat', icon='chat-dots', tag=sac.Tag(str(total_unread), color='red') if total_unread > 0 else None),
            sac.MenuItem('World', icon='globe'),
            sac.MenuItem('System', type='group', children=[sac.MenuItem('Logout', icon='box-arrow-right')]),
        ], index=0, format_func='title', size='sm', variant='light', open_all=True)

        st.divider()
        all_nodes = msc.get_all_nodes_for_map(st.session_state.username)
        if st.button("🔭 Full View", use_container_width=True): 
            msc.view_fullscreen_map(all_nodes, st.session_state.nickname)

    if menu == 'Logout': st.session_state.logged_in = False; st.rerun()

    # ==========================================
    # A. AI 伴侣 (重构：自定义气泡 + 绝对对齐)
    # ==========================================
    elif menu == 'AI Partner':
        st.caption("🤖 DEEPSEEK PARTNER")
        chat_history_ai = msc.get_active_chats(st.session_state.username)
        nodes_map = msc.get_active_nodes_map(st.session_state.username)
        
        # 遍历每一条消息，严格按行渲染
        for msg in chat_history_ai:
            # 布局：左(92%)对话，右(8%)圆点
            # 这样保证了每一行的高度是自适应的，圆点永远跟着气泡走
            c_msg, c_dot = st.columns([0.92, 0.08])
            
            with c_msg:
                if msg['role'] == 'user': 
                    # 用户：右对齐黑气泡
                    st.markdown(f"<div class='chat-bubble-me'>{msg['content']}</div>", unsafe_allow_html=True)
                else: 
                    # AI：左对齐灰气泡 (带个小机器人emoji)
                    st.markdown(f"<div class='chat-bubble-other'>🤖 {msg['content']}</div>", unsafe_allow_html=True)
            
            with c_dot:
                # 只有用户有意义的消息，才显示圆点
                if msg['role'] == 'user' and msg['content'] in nodes_map:
                    node = nodes_map[msg['content']]
                    # 居中显示
                    st.markdown('<div class="meaning-dot-wrapper">', unsafe_allow_html=True)
                    with st.popover("●", help="Deep Meaning"):
                        # 展开后的详细内容
                        score = node.get('m_score') if node.get('m_score') is not None else node.get('logic_score', 0.5)
                        st.caption(f"MSC Score: {float(score):.2f}")
                        st.markdown(f"**{node['care_point']}**")
                        st.info(node['insight'])
                        st.caption(f"Structure: {node['meaning_layer']}")
                    st.markdown('</div>', unsafe_allow_html=True)

        # 输入框
        if prompt := st.chat_input("Input..."):
            msc.save_chat(st.session_state.username, "user", prompt)
            
            # 乐观渲染：立刻把用户的话画出来
            c1, c2 = st.columns([0.92, 0.08])
            with c1: st.markdown(f"<div class='chat-bubble-me'>{prompt}</div>", unsafe_allow_html=True)
            
            # AI 回复
            full_history = chat_history_ai + [{'role':'user', 'content':prompt}]
            try:
                # 模拟流式加载的占位符
                with c1: placeholder = st.empty()
                placeholder.markdown(f"<div class='chat-bubble-other'>🤖 <i>Thinking...</i></div>", unsafe_allow_html=True)
                
                resp = msc.get_normal_response(full_history) # 返回 response 对象
                reply = resp.choices[0].message.content
                
                # 替换占位符为真实回复
                placeholder.markdown(f"<div class='chat-bubble-other'>🤖 {reply}</div>", unsafe_allow_html=True)
                msc.save_chat(st.session_state.username, "assistant", reply)
            except: pass
            
            # 意义分析
            with st.spinner(""):
                analysis = msc.analyze_meaning_background(prompt)
                if analysis.get("valid", False):
                    vec = msc.get_embedding(prompt)
                    msc.save_node(st.session_state.username, prompt, analysis, "日常", vec)
                    if "radar_scores" in analysis: msc.update_radar_score(st.session_state.username, analysis["radar_scores"])
                    st.toast("Captured", icon="🌱")
            
            # 刷新以对齐圆点
            time.sleep(0.5)
            st.rerun()

    # --- B. 好友 (同样应用新样式) ---
    elif menu == 'Chat':
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
            else: st.info("No friends")

        with col_chat:
            partner = st.session_state.current_chat_partner
            if partner:
                c1, c2 = st.columns([0.8, 0.2])
                with c1: st.markdown(f"**{partner}**")
                with c2: 
                    if st.button("🤖", help="AI Observer"): pass
                
                history = msc.get_direct_messages(st.session_state.username, partner)
                my_nodes = msc.get_active_nodes_map(st.session_state.username)
                
                # 同样的逐行渲染逻辑
                with st.container(height=500, border=False):
                    for msg in history:
                        c_msg, c_dot = st.columns([0.92, 0.08])
                        with c_msg:
                            if msg['sender'] == 'AI': 
                                st.markdown(f"<div class='chat-bubble-ai'>🤖 {msg['content']}</div>", unsafe_allow_html=True)
                            elif msg['sender'] == st.session_state.username:
                                st.markdown(f"<div class='chat-bubble-me'>{msg['content']}</div>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<div class='chat-bubble-other'>{msg['content']}</div>", unsafe_allow_html=True)
                        with c_dot:
                            if msg['sender'] == st.session_state.username and msg['content'] in my_nodes:
                                node = my_nodes[msg['content']]
                                st.markdown('<div class="meaning-dot-wrapper">', unsafe_allow_html=True)
                                with st.popover("●"):
                                    st.info(node['insight'])
                                st.markdown('</div>', unsafe_allow_html=True)
                
                if prompt := st.chat_input(f"To {partner}..."):
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
