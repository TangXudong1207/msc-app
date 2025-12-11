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
        h1, h2, h3 { font-family: 'Roboto', sans-serif; font-weight: 500; color: #202124; letter-spacing: -0.5px; }
        
        /* 每日追问卡片 */
        .daily-card {
            background: linear-gradient(135deg, #e8f0fe 0%, #ffffff 100%);
            border: 1px solid #d2e3fc;
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 20px;
            text-align: center;
        }
        .daily-title { color: #174ea6; font-size: 0.8em; font-weight: bold; text-transform: uppercase; margin-bottom: 5px; }
        .daily-question { color: #202124; font-size: 1.1em; font-weight: 500; line-height: 1.4; }
        
        /* 聊天气泡 */
        [data-testid="stChatMessageContent"] { border-radius: 16px; padding: 16px; font-size: 15px; line-height: 1.6; }
        div[data-testid="stChatMessage"]:nth-child(odd) [data-testid="stChatMessageContent"] { background-color: #E8F0FE; color: #174EA6; }
        div[data-testid="stChatMessage"]:nth-child(even) [data-testid="stChatMessageContent"] { background-color: #F1F3F4; color: #202124; }

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

st.set_page_config(page_title="MSC v39.0 Dual World", layout="wide", initial_sidebar_state="expanded")
inject_custom_css()

if "logged_in" not in st.session_state: st.session_state.logged_in = False

# --- 场景 1: 登录注册 ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: #1A73E8;'>🔷 MSC</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #5F6368;'>智能人文主义 · 意义协作系统</p>", unsafe_allow_html=True)
        st.divider()
        tab = sac.tabs([sac.TabsItem('登录', icon='box-arrow-in-right'), sac.TabsItem('注册', icon='person-plus-fill')], align='center', variant='outline')
        if tab == '登录':
            u = st.text_input("用户名")
            p = st.text_input("密码", type='password')
            if st.button("进入系统", use_container_width=True, type="primary"):
                res = msc.login_user(u, p)
                if res:
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.session_state.nickname = res[0]['nickname']
                    st.session_state.messages = [] 
                    st.rerun()
                else: sac.alert("账号或密码错误", color='red')
        else:
            nu = st.text_input("新用户名")
            np = st.text_input("新密码", type='password')
            nn = st.text_input("昵称")
            if st.button("创建身份", use_container_width=True):
                if msc.add_user(nu, np, nn): sac.alert("注册成功，请切换至登录页", color='success')
                else: sac.alert("注册失败", color='error')

# --- 场景 2: 主应用 ---
else:
    # 全局数据预加载
    chat_history = msc.get_active_chats(st.session_state.username)
    nodes_map = msc.get_active_nodes_map(st.session_state.username)
    all_nodes_list = msc.get_all_nodes_for_map(st.session_state.username)
    user_profile = msc.get_user_profile(st.session_state.username)
    raw_radar = user_profile.get('radar_profile')
    if isinstance(raw_radar, str): radar_dict = json.loads(raw_radar)
    else: radar_dict = raw_radar if raw_radar else {k:3.0 for k in ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]}
    rank_name, rank_icon = msc.calculate_rank(radar_dict)

    # --- 侧边栏 (导航) ---
    with st.sidebar:
        sac.result(label=st.session_state.nickname, description=f"{rank_icon} {rank_name}", status="success")
        
        # 核心导航
        menu = sac.menu([
            sac.MenuItem('Home', icon='house-fill', description='个人主页'),
            sac.MenuItem('Matrix', icon='cpu-fill', description='造物主模拟'),
            sac.MenuItem('World', icon='globe', description='全网观察'),
            sac.MenuItem('System', type='group', children=[sac.MenuItem('退出', icon='power')]),
        ], index=0, format_func='title', size='md', variant='light', open_all=True)

        st.divider()
        
        # 每日追问 (只在 Home 显示)
        if menu == 'Home':
            if "daily_q" not in st.session_state: st.session_state.daily_q = None
            if st.session_state.daily_q is None:
                if st.button("📅 生成今日追问", use_container_width=True):
                    with st.spinner("..."):
                        q = msc.generate_daily_question(st.session_state.username, radar_dict)
                        st.session_state.daily_q = q
                        st.rerun()
            else:
                st.markdown(f"<div class='daily-card'><div class='daily-title'>DAILY INQUIRY</div><div class='daily-question'>{st.session_state.daily_q}</div></div>", unsafe_allow_html=True)
        
        # 迷你地图
        st.caption("Mini Map")
        msc.render_cyberpunk_map(all_nodes_list, height="150px")

    if menu == '退出': st.session_state.logged_in = False; st.rerun()

    # --- 🌌 Matrix 模式 (造物主) ---
    elif menu == 'Matrix':
        st.header("🧬 Matrix Simulation")
        st.caption("在这里，你可以扮演上帝，创造文明并观察其意义的演化。")
        
        c1, c2 = st.columns([2, 1])
        with c1:
            topic = st.text_input("设定社会话题 / 剧本主题", value="科技进步是否必然导致人类异化？")
            count = st.slider("生成智能体数量", 1, 10, 3)
            
            if st.button("🚀 注入虚拟文明", type="primary", use_container_width=True):
                with st.status("正在编织剧本...", expanded=True) as status:
                    st.write("📝 正在撰写剧本...")
                    script = msc.generate_simulation_script(topic, count)
                    if script:
                        st.write(f"🎭 剧本已生成 ({len(script)} 角色)，正在演绎...")
                        progress_bar = st.progress(0)
                        
                        # 逐个演绎
                        for i, agent in enumerate(script):
                            msc.process_simulation_turn(agent)
                            progress_bar.progress((i + 1) / len(script))
                            time.sleep(0.5)
                        
                        status.update(label="✅ 文明注入完成", state="complete", expanded=False)
                        st.success(f"成功注入 {len(script)} 个智能体！请前往 World 观察。")
                    else:
                        st.error("剧本生成失败")

    # --- 🌍 World 模式 (全网) ---
    elif menu == 'World':
        st.header("🌍 MSC World")
        global_nodes = msc.get_global_nodes()
        t1, t2 = st.tabs(["2D Earth", "3D Galaxy"])
        with t1: msc.render_2d_world_map(global_nodes)
        with t2: msc.render_3d_galaxy(global_nodes)

    # --- 🏠 Home 模式 (个人) ---
    else:
        st.subheader("💬 意义流")
        
        for msg in chat_history:
            col_chat, col_node = st.columns([0.6, 0.4], gap="medium")
            
            with col_chat:
                c_msg, c_del = st.columns([0.9, 0.1])
                with c_msg:
                    with st.chat_message(msg['role'], avatar=None):
                        st.markdown(msg['content'], unsafe_allow_html=True)
                with c_del:
                    if msg['role'] == 'user':
                        if st.button("✕", key=f"del_{msg['id']}", help="Delete"):
                            if msc.soft_delete_chat_and_node(msg['id'], msg['content'], st.session_state.username): st.rerun()

            with col_node:
                if msg['role'] == 'user' and msg['content'] in nodes_map:
                    node = nodes_map[msg['content']]
                    logic_score = node.get('logic_score', 0.5)
                    card_class = "card-high-logic" if logic_score > 0.8 else "card-mid-logic"
                    
                    with st.expander(f"✨ 发现意义：{node['care_point'][:10]}...", expanded=False):
                        card_html = f"""
                        <div class="meaning-card {card_class}">
                            <div class="card-header">
                                <span style="color: #1A73E8;">#{node['id']}</span>
                                <span>SCORE: {logic_score}</span>
                            </div>
                            <div class="card-body">{node['care_point']}</div>
                            <div class="card-insight">“{node['insight']}”</div>
                            <div class="card-structure" style="margin-top:8px;font-size:12px;color:#777;">{node['meaning_layer']}</div>
                        </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)

        if prompt := st.chat_input("输入..."):
            msc.save_chat(st.session_state.username, "user", prompt)
            
            full_history = chat_history + [{'role':'user', 'content':prompt}]
            stream = msc.get_normal_response(full_history)
            reply_text = st.write_stream(stream)
            msc.save_chat(st.session_state.username, "assistant", reply_text)
            
            with st.spinner("Processing..."):
                analysis = msc.analyze_meaning_background(prompt)
                if analysis.get("valid", False):
                    vec = msc.get_embedding(prompt)
                    msc.save_node(st.session_state.username, prompt, analysis, "日常", vec)
                    if "radar_scores" in analysis: msc.update_radar_score(st.session_state.username, analysis["radar_scores"])
                    match = msc.find_resonance(vec, st.session_state.username, analysis)
                    if match: st.toast(f"🔔 发现共鸣！(MLS={match['score']})", icon="⚡")
                    msc.check_group_formation(analysis, vec, st.session_state.username)
            st.rerun()
