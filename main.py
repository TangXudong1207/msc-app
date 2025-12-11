import streamlit as st
import streamlit_antd_components as sac
import msc_lib as msc
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
        
        /* 意义小圆点 */
        .meaning-dot {
            font-size: 10px;
            color: #999;
            cursor: pointer;
            margin-top: 5px;
        }
        
        /* 弹窗内的卡片 */
        .popover-card {
            background-color: #fff;
            border-left: 3px solid #1A73E8;
            padding: 15px;
            border-radius: 4px;
        }
    </style>
    """, unsafe_allow_html=True)

st.set_page_config(page_title="MSC v45.0 Minimal", layout="wide", initial_sidebar_state="expanded")
inject_custom_css()

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "current_chat_partner" not in st.session_state: st.session_state.current_chat_partner = None

# --- 登录 ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
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
                    st.session_state.messages = [] 
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
    user_profile = msc.get_user_profile(st.session_state.username)
    raw_radar = user_profile.get('radar_profile')
    if isinstance(raw_radar, str): radar_dict = json.loads(raw_radar)
    else: radar_dict = raw_radar if raw_radar else {k:3.0 for k in ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]}
    rank_name, rank_icon = msc.calculate_rank(radar_dict)
    total_unread, unread_counts = msc.get_unread_counts(st.session_state.username)

    with st.sidebar:
        st.markdown(f"### {rank_icon} {st.session_state.nickname}")
        
        if "daily_q" not in st.session_state: st.session_state.daily_q = None
        if st.session_state.daily_q is None:
            if st.button("📅 生成今日追问", use_container_width=True):
                with st.spinner("..."):
                    st.session_state.daily_q = msc.generate_daily_question(st.session_state.username, radar_dict)
                    st.rerun()
        else:
            st.info(st.session_state.daily_q)
            if st.button("🔄"): st.session_state.daily_q = None; st.rerun()

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
        
        # 使用 8:2 的比例，右侧留给小圆点
        col_chat, col_node = st.columns([0.8, 0.2])
        
        with col_chat:
            for msg in chat_history_ai:
                with st.chat_message(msg['role']): st.markdown(msg['content'])
        
        with col_node:
            # 🌟 极简脚注模式
            for msg in chat_history_ai:
                if msg['role'] == 'user' and msg['content'] in nodes_map:
                    node = nodes_map[msg['content']]
                    # 使用 Popover 作为一个小点
                    with st.popover("✨", help="点击查看意义"):
                        st.caption(f"SCORE: {node.get('logic_score', 0.5)}")
                        st.markdown(f"**{node['care_point']}**")
                        st.info(node['insight'])
                        st.caption(node['meaning_layer'])
                else:
                    # 占位符，保持对齐
                    st.write("") 

        if prompt := st.chat_input("..."):
            msc.save_chat(st.session_state.username, "user", prompt)
            full_history = chat_history_ai + [{'role':'user', 'content':prompt}]
            stream = msc.get_normal_response(full_history)
            try:
                reply = stream.choices[0].message.content
                msc.save_chat(st.session_state.username, "assistant", reply)
            except: pass
            
            with st.spinner(""): # 静默分析
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
            users = msc.get_all_users(st.session_state.username)
            if users:
                for u in users:
                    unread = unread_counts.get(u['username'], 0)
                    label = f"{u['nickname']} 🔴 {unread}" if unread > 0 else u['nickname']
                    if st.button(label, key=f"f_{u['username']}", use_container_width=True):
                        st.session_state.current_chat_partner = u['username']
                        msc.mark_messages_read(u['username'], st.session_state.username)
                        st.rerun()

        with col_chat:
            partner = st.session_state.current_chat_partner
            if partner:
                st.caption(f"与 {partner} 对话中")
                history = msc.get_direct_messages(st.session_state.username, partner)
                my_nodes = msc.get_active_nodes_map(st.session_state.username)
                
                # 🌟 同样采用 8:2 布局
                sub_chat, sub_node = st.columns([0.8, 0.2])
                
                with sub_chat:
                    with st.container(height=500):
                        for msg in history:
                            role = "user" if msg['sender'] == st.session_state.username else "assistant"
                            with st.chat_message(role):
                                st.markdown(msg['content'])
                
                with sub_node:
                    # 倒序遍历显示
                    for msg in reversed(history):
                        if msg['sender'] == st.session_state.username and msg['content'] in my_nodes:
                            node = my_nodes[msg['content']]
                            with st.popover("✨"):
                                st.markdown(f"**{node['care_point']}**")
                                st.caption(node['insight'])
                        else:
                            st.write("") # 占位

                if prompt := st.chat_input("..."):
                    msc.send_direct_message(st.session_state.username, partner, prompt)
                    with st.spinner(""):
                        analysis = msc.analyze_meaning_background(prompt)
                        if analysis.get("valid", False):
                            vec = msc.get_embedding(prompt)
                            msc.save_node(st.session_state.username, prompt, analysis, "私聊", vec)
                            match = msc.find_resonance(vec, st.session_state.username, analysis)
                            if match: st.toast("共鸣！", icon="⚡")
                    st.rerun()

    # --- C. 星团 & 世界 (略) ---
    elif menu == '星团':
        rooms = msc.get_available_rooms()
        if rooms:
            for room in rooms:
                if st.button(f"🌌 {room['name']}", use_container_width=True):
                    msc.join_room(room['id'], st.session_state.username)
                    msc.view_group_chat(room, st.session_state.username)
        else: st.info("暂无星团")

    elif menu == '世界':
        global_nodes = msc.get_global_nodes()
        t1, t2 = st.tabs(["2D", "3D"])
        with t1: msc.render_2d_world_map(global_nodes)
        with t2: msc.render_3d_galaxy(global_nodes)
