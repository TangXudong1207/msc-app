import streamlit as st
import msc_lib as msc
import time
import json

# ==========================================
# 🎨 1. 注入赛博艺术 CSS (UI 灵魂)
# ==========================================
def inject_custom_css():
    st.markdown("""
    <style>
        /* --- 全局背景：深空星尘 --- */
        .stApp {
            background-color: #050510;
            background-image: radial-gradient(circle at 50% 0%, #1a1c2e 0%, #000000 80%);
            color: #e0e0e0;
        }
        
        /* --- 侧边栏：驾驶舱仪表盘 --- */
        [data-testid="stSidebar"] {
            background-color: rgba(10, 12, 20, 0.95);
            border-right: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        /* --- 标题：流光渐变 --- */
        h1, h2, h3 {
            font-family: 'Helvetica Neue', sans-serif;
            font-weight: 300;
            letter-spacing: 2px;
            background: linear-gradient(90deg, #00d2ff, #ff00d4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 20px rgba(0, 210, 255, 0.3);
        }
        
        /* --- 按钮：霓虹边框 --- */
        .stButton button {
            background: transparent;
            border: 1px solid rgba(0, 255, 242, 0.3);
            color: #00fff2;
            border-radius: 4px;
            transition: all 0.3s ease;
        }
        .stButton button:hover {
            border-color: #00fff2;
            box-shadow: 0 0 15px rgba(0, 255, 242, 0.4);
            color: #fff;
        }

        /* --- 核心：意义卡片 (悬浮水晶) --- */
        .meaning-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-left: 3px solid #00d2ff;
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 20px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .meaning-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 40px rgba(0, 210, 255, 0.15);
            border-left-color: #ff00d4;
            background: rgba(255, 255, 255, 0.05);
        }
        
        .card-header {
            font-size: 0.85em;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
        }
        
        .card-care {
            font-size: 1.1em;
            color: #fff;
            font-weight: 500;
            margin-bottom: 12px;
        }
        
        .card-insight {
            font-family: 'Georgia', serif; /* 衬线体增加人文感 */
            font-style: italic;
            color: #00d2ff;
            font-size: 1.05em;
            line-height: 1.5;
            padding-top: 10px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .card-structure {
            font-size: 0.85em;
            color: #aaa;
            margin-top: 8px;
        }

        /* --- 聊天气泡优化 --- */
        .stChatMessage {
            background-color: transparent !important;
        }
        [data-testid="stChatMessageContent"] {
            border-radius: 12px;
            padding: 15px;
            font-size: 1.05em;
        }
        /* 用户气泡 */
        div[data-testid="stChatMessage"]:nth-child(odd) [data-testid="stChatMessageContent"] {
            background: linear-gradient(135deg, rgba(50, 20, 80, 0.6), rgba(20, 20, 40, 0.6));
            border: 1px solid rgba(255, 0, 212, 0.2);
            color: #f0f0f0;
        }
        /* AI 气泡 */
        div[data-testid="stChatMessage"]:nth-child(even) [data-testid="stChatMessageContent"] {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(0, 255, 242, 0.2);
        }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 🖥️ 主界面逻辑
# ==========================================

st.set_page_config(page_title="MSC v32.0 Art", layout="wide", initial_sidebar_state="expanded")
inject_custom_css() # 注入皮肤

if "logged_in" not in st.session_state: st.session_state.logged_in = False

# --- 场景 1: 登录注册 ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<h1 style='text-align: center; margin-bottom: 50px;'>🌌 MSC</h1>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["登录 · Login", "注册 · Sign Up"])
        with tab1:
            u = st.text_input("用户名")
            p = st.text_input("密码", type='password')
            if st.button("🚀 进入宇宙", use_container_width=True):
                res = msc.login_user(u, p)
                if res:
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.session_state.nickname = res[0]['nickname']
                    st.session_state.messages = [] 
                    st.rerun()
                else: st.error("识别失败")
        with tab2:
            nu = st.text_input("新用户名")
            np_pass = st.text_input("新密码", type='password')
            nn = st.text_input("昵称")
            if st.button("📝 注册身份", use_container_width=True):
                if msc.add_user(nu, np_pass, nn): st.success("注册成功")
                else: st.error("注册失败")

# --- 场景 2: 主应用 ---
else:
    chat_history = msc.get_active_chats(st.session_state.username)
    nodes_map = msc.get_active_nodes_map(st.session_state.username)
    all_nodes_list = msc.get_all_nodes_for_map(st.session_state.username)
    user_profile = msc.get_user_profile(st.session_state.username)
    
    raw_radar = user_profile.get('radar_profile')
    if isinstance(raw_radar, str): radar_dict = json.loads(raw_radar)
    else: radar_dict = raw_radar if raw_radar else {k:3.0 for k in ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]}

    # --- 侧边栏 (仪表盘) ---
    with st.sidebar:
        rank_name, rank_icon = msc.calculate_rank(radar_dict)
        st.markdown(f"### {rank_icon} {st.session_state.nickname}")
        
        msc.render_radar_chart(radar_dict)
        
        # 弹窗功能区
        col_btn1, col_btn2 = st.columns(2)
        
        @st.dialog("🧬 画像分析")
        def show_persona():
            if st.button("生成报告"):
                with st.spinner("分析中..."):
                    res = msc.analyze_persona_report(radar_dict)
                    st.write(res)
        if col_btn1.button("🧬 画像"): show_persona()
        
        @st.dialog("🌍 MSC World", width="large")
        def show_world():
            global_nodes = msc.get_global_nodes()
            t1, t2 = st.tabs(["2D Earth", "3D Galaxy"])
            with t1: msc.render_2d_world_map(global_nodes)
            with t2: msc.render_3d_galaxy(global_nodes)
        if col_btn2.button("🌍 世界"): show_world()
            
        @st.dialog("🧪 仿真实验室")
        def show_sim():
            topic = st.text_input("话题")
            if st.button("开始注入"):
                cnt, msg = msc.simulate_civilization(topic, 3)
                st.success(msg)
        with st.expander("🛠️ 控制台"):
            if st.button("打开实验室"): show_sim()

        st.divider()
        msc.render_cyberpunk_map(all_nodes_list, height="200px")
        
        @st.dialog("🔭 全屏", width="large")
        def show_full_map():
            msc.render_cyberpunk_map(all_nodes_list, height="600px", is_fullscreen=True)
        if st.button("🔭 全屏星云", use_container_width=True): show_full_map()
        
        if st.button("退出连接", use_container_width=True): st.session_state.logged_in = False; st.rerun()

    # --- 主对话区 ---
    st.subheader("💬 意义流")
    
    for msg in chat_history:
        col_chat, col_node = st.columns([0.6, 0.4], gap="medium") # 调整比例
        
        with col_chat:
            c_msg, c_del = st.columns([0.9, 0.1])
            with c_msg:
                with st.chat_message(msg['role']): st.markdown(msg['content'], unsafe_allow_html=True)
            with c_del:
                if msg['role'] == 'user':
                    if st.button("✕", key=f"del_{msg['id']}"):
                        if msc.soft_delete_chat_and_node(msg['id'], msg['content'], st.session_state.username): st.rerun()

        with col_node:
            if msg['role'] == 'user' and msg['content'] in nodes_map:
                node = nodes_map[msg['content']]
                
                # 🔥 渲染精美的 HTML 卡片
                logic_score = node.get('logic_score', 0.5)
                # 根据分数改变边框颜色
                border_color = "#00d2ff" if logic_score < 0.8 else "#ff00d4"
                
                card_html = f"""
                <div class="meaning-card" style="border-left-color: {border_color};">
                    <div class="card-header">
                        <span>#{node['id']} NODE</span>
                        <span>M-SCORE: {logic_score}</span>
                    </div>
                    <div class="card-care">{node['care_point']}</div>
                    <div class="card-structure">{node['meaning_layer']}</div>
                    <div class="card-insight">“{node['insight']}”</div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)

    if prompt := st.chat_input("输入思考..."):
        msc.save_chat(st.session_state.username, "user", prompt)
        
        full_history = chat_history + [{'role':'user', 'content':prompt}]
        stream = msc.get_normal_response(full_history)
        reply_text = st.write_stream(stream)
        msc.save_chat(st.session_state.username, "assistant", reply_text)
        
        with st.spinner("⚡ 捕捉意义..."):
            analysis = msc.analyze_meaning_background(prompt)
            if analysis.get("valid", False):
                vec = msc.get_embedding(prompt)
                msc.save_node(st.session_state.username, prompt, analysis, "日常", vec)
                if "radar_scores" in analysis: msc.update_radar_score(st.session_state.username, analysis["radar_scores"])
                
                match = msc.find_resonance(vec, st.session_state.username, analysis)
                if match: st.toast(f"🔔 发现共鸣！(MLS={match['score']})", icon="⚡")
                
                msc.check_group_formation(analysis, vec, st.session_state.username)
        st.rerun()
