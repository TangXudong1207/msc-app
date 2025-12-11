import streamlit as st
import streamlit_antd_components as sac # 🌟 UI 革命的核心库
import msc_lib as msc
import time
import json

# ==========================================
# 🎨 1. 注入 Ant Design 风格增强 CSS
# ==========================================
def inject_custom_css():
    st.markdown("""
    <style>
        /* 隐藏原生汉堡菜单和页脚，更像 App */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* 全局字体优化 */
        .stApp {
            background-color: #ffffff;
        }

        /* 优化聊天区域的内边距 */
        .stChatMessage {
            padding: 1rem;
            margin-bottom: 0.5rem;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        
        /* 意义卡片精致化 */
        .meaning-card {
            background: #fff;
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 12px;
            transition: all 0.3s;
            position: relative;
            overflow: hidden;
        }
        .meaning-card:hover {
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
            transform: translateY(-2px);
            border-color: #3b82f6;
        }
        .card-tag {
            font-size: 0.75rem;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 4px;
            background: #eff6ff;
            color: #3b82f6;
            margin-bottom: 8px;
            display: inline-block;
        }
        .card-body {
            font-size: 0.95rem;
            color: #374151;
            line-height: 1.6;
        }
        .card-insight {
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px dashed #e5e7eb;
            font-style: italic;
            color: #6b7280;
            font-size: 0.9rem;
        }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 🖥️ 主界面逻辑
# ==========================================

st.set_page_config(page_title="MSC v34.0 UI Revolution", layout="wide", initial_sidebar_state="expanded")
inject_custom_css()

if "logged_in" not in st.session_state: st.session_state.logged_in = False

# --- 场景 1: 登录注册 (使用原生组件保持简单稳定性) ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        # 使用 SAC 的警告框做标题背景
        sac.alert(label="MSC 意义协作系统", description="Intelligent Humanism OS · v34.0", icon="stars", color="blue", radius="lg")
        
        tab = sac.tabs([
            sac.TabsItem('登录', icon='box-arrow-in-right'),
            sac.TabsItem('注册', icon='person-plus-fill'),
        ], align='center', variant='outline')
        
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
                if msc.add_user(nu, np, nn): 
                    sac.alert("注册成功，请切换至登录页", color='success')
                else: 
                    sac.alert("注册失败，用户可能已存在", color='error')

# --- 场景 2: 主应用 (UI 革命) ---
else:
    # 数据加载
    chat_history = msc.get_active_chats(st.session_state.username)
    nodes_map = msc.get_active_nodes_map(st.session_state.username)
    all_nodes_list = msc.get_all_nodes_for_map(st.session_state.username)
    user_profile = msc.get_user_profile(st.session_state.username)
    
    raw_radar = user_profile.get('radar_profile')
    if isinstance(raw_radar, str): radar_dict = json.loads(raw_radar)
    else: radar_dict = raw_radar if raw_radar else {k:3.0 for k in ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]}
    
    rank_name, rank_icon = msc.calculate_rank(radar_dict)

    # --- 侧边栏：专业级导航 ---
    with st.sidebar:
        # 用户信息卡片
        sac.result(label=st.session_state.nickname, description=f"{rank_icon} {rank_name}", status="success")
        
        # 雷达图
        msc.render_radar_chart(radar_dict, height="200px")
        
        # 核心导航菜单 (SAC Menu)
        menu = sac.menu([
            sac.MenuItem('控制台', icon='house-fill'),
            sac.MenuItem('实验室', icon='box-seam', children=[
                sac.MenuItem('画像分析', icon='person-bounding-box'),
                sac.MenuItem('虚拟文明', icon='robot'),
            ]),
            sac.MenuItem('世界观', icon='globe', children=[
                sac.MenuItem('MSC World', icon='earth'),
                sac.MenuItem('全屏星云', icon='stars'),
            ]),
            sac.MenuItem('系统', type='group', children=[
                sac.MenuItem('回收站', icon='trash'),
                sac.MenuItem('退出登录', icon='box-arrow-right'),
            ]),
        ], index=0, format_func='title', open_all=True)

        # 侧边栏底部的小地图
        st.divider()
        st.caption("Mini Map")
        msc.render_cyberpunk_map(all_nodes_list, height="180px")

    # --- 菜单逻辑响应 ---
    if menu == '退出登录':
        st.session_state.logged_in = False
        st.rerun()
        
    elif menu == '画像分析':
        @st.dialog("🧬 深度画像", width="large")
        def show_persona():
            if st.button("开始 AI 分析", type="primary"):
                with st.spinner("DeepSeek 正在侧写..."):
                    res = msc.analyze_persona_report(radar_dict)
                    sac.alert(label="静态画像", description=res.get('static_portrait'), color='info', icon='person')
                    sac.alert(label="动态成长", description=res.get('dynamic_growth'), color='success', icon='graph-up-arrow')
        show_persona()
        
    elif menu == '虚拟文明':
        @st.dialog("🧪 仿真实验室")
        def show_sim():
            topic = st.text_input("设定社会话题", value="人类的本质是复读机吗？")
            if st.button("注入 3 个智能体", type="primary"):
                with st.spinner("造物中..."):
                    cnt, msg = msc.simulate_civilization(topic, 3)
                    sac.alert(msg, color='success')
        show_sim()

    elif menu == 'MSC World':
        @st.dialog("🌍 MSC World", width="large")
        def show_world():
            global_nodes = msc.get_global_nodes()
            # SAC 分段控制器替代 Tabs
            seg = sac.segmented(
                items=[
                    sac.SegmentedItem(label='地球夜景', icon='globe'),
                    sac.SegmentedItem(label='意义星河', icon='stars'),
                    sac.SegmentedItem(label='全球脉动', icon='activity'),
                ], align='center', use_container_width=True
            )
            if seg == '地球夜景': msc.render_2d_world_map(global_nodes)
            elif seg == '意义星河': msc.render_3d_galaxy(global_nodes)
            elif seg == '全球脉动':
                st.info("📡 实时监听全球信号...")
                # 这里可以展示全球流，为了代码简洁暂略
        show_world()

    elif menu == '全屏星云':
        @st.dialog("🔭 浩荡宇宙", width="large")
        def show_full():
            msc.render_cyberpunk_map(all_nodes_list, height="600px", is_fullscreen=True)
        show_full()

    # --- 主对话区 (仅当菜单在'控制台'时显示) ---
    if menu == '控制台':
        # 顶部模式切换 (SAC Segmented)
        mode = sac.segmented(
            items=[
                sac.SegmentedItem(label='日常社交', icon='cup-hot'),
                sac.SegmentedItem(label='学术研讨', icon='book'),
                sac.SegmentedItem(label='艺术共创', icon='palette'),
            ], size='sm', align='center'
        )
        
        st.write("") # Spacer

        # 逐行对齐渲染
        for msg in chat_history:
            col_chat, col_node = st.columns([0.65, 0.35], gap="medium")
            
            with col_chat:
                c_msg, c_del = st.columns([0.92, 0.08])
                with c_msg:
                    # 针对不同角色使用不同头像
                    avatar = "🧑‍💻" if msg['role']=='user' else "🤖"
                    with st.chat_message(msg['role'], avatar=avatar):
                        st.markdown(msg['content'], unsafe_allow_html=True)
                with c_del:
                    if msg['role'] == 'user':
                        if st.button("✕", key=f"del_{msg['id']}", help="删除"):
                            if msc.soft_delete_chat_and_node(msg['id'], msg['content'], st.session_state.username): st.rerun()

            with col_node:
                if msg['role'] == 'user' and msg['content'] in nodes_map:
                    node = nodes_map[msg['content']]
                    logic_score = node.get('logic_score', 0.5)
                    
                    # HTML 智能卡片渲染
                    card_html = f"""
                    <div class="meaning-card">
                        <div class="card-tag">M-SCORE: {logic_score}</div>
                        <div class="card-body">
                            <strong>{node['care_point']}</strong>
                            <div class="card-insight">{node['insight']}</div>
                        </div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)

        # 底部输入
        if prompt := st.chat_input("输入思考..."):
            msc.save_chat(st.session_state.username, "user", prompt)
            
            full_history = chat_history + [{'role':'user', 'content':prompt}]
            stream = msc.get_normal_response(full_history)
            reply_text = st.write_stream(stream)
            msc.save_chat(st.session_state.username, "assistant", reply_text)
            
            with st.spinner("⚡ 意义计算中..."):
                analysis = msc.analyze_meaning_background(prompt)
                if analysis.get("valid", False):
                    vec = msc.get_embedding(prompt)
                    # 传入当前选择的 mode
                    msc.save_node(st.session_state.username, prompt, analysis, mode, vec)
                    
                    if "radar_scores" in analysis: msc.update_radar_score(st.session_state.username, analysis["radar_scores"])
                    match = msc.find_resonance(vec, st.session_state.username, analysis)
                    if match: 
                        sac.alert(f"发现共鸣！与 {match['user']} (MLS={match['score']})", color='success', icon='lightning-charge')
                    
                    msc.check_group_formation(analysis, vec, st.session_state.username)
            st.rerun()
