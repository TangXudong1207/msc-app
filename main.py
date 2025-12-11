import streamlit as st
import streamlit_antd_components as sac
import msc_lib as msc
import time
import json

# ==========================================
# 🎨 CSS：极简科技风
# ==========================================
def inject_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        .stApp { background-color: #FFFFFF; font-family: 'Roboto', sans-serif; color: #1F1F1F; }
        [data-testid="stSidebar"] { background-color: #F8F9FA; border-right: 1px solid #E0E0E0; }
        
        /* 聊天气泡：我的 */
        .chat-bubble-me {
            background-color: #95EC69;
            color: #000;
            padding: 10px 14px;
            border-radius: 8px;
            border-top-right-radius: 2px;
            margin-bottom: 10px;
            display: inline-block;
            float: right;
            clear: both;
            max-width: 80%;
        }
        /* 聊天气泡：对方 */
        .chat-bubble-other {
            background-color: #FFFFFF;
            color: #000;
            padding: 10px 14px;
            border-radius: 8px;
            border-top-left-radius: 2px;
            margin-bottom: 10px;
            display: inline-block;
            float: left;
            clear: both;
            border: 1px solid #eee;
            max-width: 80%;
        }
        
        /* 意义卡片 */
        .meaning-card {
            background-color: #FFFFFF;
            border: 1px solid #DADCE0;
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 12px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        .card-header { font-size: 11px; color: #1A73E8; margin-bottom: 8px; font-weight: bold; text-transform: uppercase; }
        .card-body { font-size: 14px; color: #202124; margin-bottom: 8px; font-weight: 500; }
        .card-insight { font-size: 13px; color: #5F6368; font-style: italic; border-left: 2px solid #E8F0FE; padding-left: 8px; }
    </style>
    """, unsafe_allow_html=True)

st.set_page_config(page_title="MSC v41.0 Fusion", layout="wide", initial_sidebar_state="expanded")
inject_custom_css()

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "current_chat_partner" not in st.session_state: st.session_state.current_chat_partner = None

# --- 登录注册逻辑 ---
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

# --- 主系统逻辑 ---
else:
    # 加载用户画像
    user_profile = msc.get_user_profile(st.session_state.username)
    raw_radar = user_profile.get('radar_profile')
    if isinstance(raw_radar, str): radar_dict = json.loads(raw_radar)
    else: radar_dict = raw_radar if raw_radar else {k:3.0 for k in ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]}
    rank_name, rank_icon = msc.calculate_rank(radar_dict)

    # --- 侧边栏 ---
    with st.sidebar:
        st.markdown(f"### {rank_icon} {st.session_state.nickname}")
        msc.render_radar_chart(radar_dict, height="150px")
        
        # 🌟 核心菜单：三轨并行
        menu = sac.menu([
            sac.MenuItem('AI 伴侣', icon='robot', description='与 DeepSeek 深聊'),
            sac.MenuItem('好友', icon='chat-dots', description='私信聊天'),
            sac.MenuItem('星团', icon='people', description='意义群组'),
            sac.MenuItem('世界', icon='globe'),
            sac.MenuItem('系统', type='group', children=[
                sac.MenuItem('退出登录', icon='box-arrow-right'),
            ]),
        ], index=0, format_func='title', open_all=True)

        st.divider()
        if st.button("🔭 全屏星云", use_container_width=True): 
            all_nodes = msc.get_all_nodes_for_map(st.session_state.username)
            msc.view_fullscreen_map(all_nodes, st.session_state.nickname)

    if menu == '退出登录': st.session_state.logged_in = False; st.rerun()

    # ==========================================
    # 🤖 模式 A：AI 伴侣 (恢复原来的功能)
    # ==========================================
    elif menu == 'AI 伴侣':
        st.subheader("🤖 AI 意义构建")
        
        # 获取 AI 聊天记录 (chats 表)
        chat_history = msc.get_active_chats(st.session_state.username)
        nodes_map = msc.get_active_nodes_map(st.session_state.username)
        
        # 双流布局
        col_chat, col_node = st.columns([0.65, 0.35], gap="small")
        
        with col_chat:
            for msg in chat_history:
                with st.chat_message(msg['role']):
                    st.markdown(msg['content'])
        
        with col_node:
            # 对应的节点卡片
            for msg in chat_history:
                if msg['role'] == 'user' and msg['content'] in nodes_map:
                    node = nodes_map[msg['content']]
                    logic_score = node.get('logic_score', 0.5)
                    card_class = "card-high-logic" if logic_score > 0.8 else "card-mid-logic"
                    # HTML 卡片渲染
                    card_html = f"""
                    <div class="meaning-card {card_class}">
                        <div class="card-header">#{node['id']} SCORE: {logic_score}</div>
                        <div class="card-body">{node['care_point']}</div>
                        <div class="card-insight">“{node['insight']}”</div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)

        if prompt := st.chat_input("与 AI 对话..."):
            msc.save_chat(st.session_state.username, "user", prompt)
            
            # 生成 AI 回复
            full_history = chat_history + [{'role':'user', 'content':prompt}]
            stream = msc.get_normal_response(full_history)
            reply_text = st.write_stream(stream) # 临时流式显示
            msc.save_chat(st.session_state.username, "assistant", reply_text)
            
            # 意义分析
            with st.spinner("⚡ 分析中..."):
                analysis = msc.analyze_meaning_background(prompt)
                if analysis.get("valid", False):
                    vec = msc.get_embedding(prompt)
                    msc.save_node(st.session_state.username, prompt, analysis, "日常", vec)
                    if "radar_scores" in analysis: msc.update_radar_score(st.session_state.username, analysis["radar_scores"])
            st.rerun()

    # ==========================================
    # 💬 模式 B：好友私聊 (新功能)
    # ==========================================
    elif menu == '好友':
        col_list, col_chat = st.columns([0.3, 0.7])
        
        with col_list:
            st.caption("通讯录")
            users = msc.get_all_users(st.session_state.username)
            if users:
                for u in users:
                    if st.button(f"{u['nickname']}", key=f"friend_{u['username']}", use_container_width=True):
                        st.session_state.current_chat_partner = u['username']
                        st.rerun()
            else: st.info("暂无其他用户")

        with col_chat:
            partner = st.session_state.current_chat_partner
            if partner:
                st.caption(f"与 {partner} 对话中")
                history = msc.get_direct_messages(st.session_state.username, partner)
                
                # 聊天容器
                with st.container(height=500):
                    for msg in history:
                        if msg['sender'] == st.session_state.username:
                            st.markdown(f"<div class='chat-bubble-me'>{msg['content']}</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div class='chat-bubble-other'>{msg['content']}</div>", unsafe_allow_html=True)
                
                if prompt := st.chat_input(f"发给 {partner}..."):
                    msc.send_direct_message(st.session_state.username, partner, prompt)
                    
                    # 🌟 私聊也能触发意义分析 (静默模式)
                    with st.spinner("⚡"):
                        analysis = msc.analyze_meaning_background(prompt)
                        if analysis.get("valid", False):
                            vec = msc.get_embedding(prompt)
                            msc.save_node(st.session_state.username, prompt, analysis, "私聊", vec)
                            match = msc.find_resonance(vec, st.session_state.username, analysis)
                            if match: st.toast(f"私聊中产生共鸣！", icon="⚡")
                    st.rerun()
            else:
                st.info("👈 请在左侧选择一位好友开始聊天")

    # ==========================================
    # 🪐 模式 C：星团群组 (新功能预留)
    # ==========================================
    elif menu == '星团':
        st.subheader("🌌 意义自组织星团")
        rooms = msc.get_available_rooms()
        if rooms:
            for room in rooms:
                with st.expander(f"{room['name']}", expanded=True):
                    st.caption(room['description'])
                    if st.button("进入星团", key=f"join_{room['id']}"):
                        msc.join_room(room['id'], st.session_state.username)
                        msc.view_group_chat(room, st.session_state.username)
        else:
            st.info("暂无自发形成的意义星团。当多人产生强烈共鸣时，星团会自动诞生。")

    # ==========================================
    # 🌍 模式 D：世界
    # ==========================================
    elif menu == '世界':
        st.title("🌍 MSC World")
        global_nodes = msc.get_global_nodes()
        t1, t2 = st.tabs(["2D Earth", "3D Galaxy"])
        with t1: msc.render_2d_world_map(global_nodes)
        with t2: msc.render_3d_galaxy(global_nodes)
