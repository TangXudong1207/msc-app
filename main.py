import streamlit as st
import streamlit_antd_components as sac
import msc_lib as msc
import msc_viz as viz
import msc_pages as pages
import json
import msc_forest as forest 

# ==========================================
# 🎨 CSS：Cyber-Zen 极简主义设计系统
# ==========================================
def inject_custom_css():
    st.markdown("""
    <style>
        /* 1. 字体系统：引入 Inter 和 JetBrains Mono */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=JetBrains+Mono:wght@400;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: #2D3436;
        }
        code, .stCode, .monospaced {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* 2. 全局背景与容器 */
        .stApp { background-color: #FAFAFA; }
        
        /* 侧边栏优化 */
        [data-testid="stSidebar"] {
            background-color: #FFFFFF;
            border-right: 1px solid #F0F0F0;
            box-shadow: 2px 0 10px rgba(0,0,0,0.02);
        }
        
        /* 按钮微整形：去圆角，科技感 */
        .stButton > button {
            border-radius: 4px;
            font-weight: 500;
            border: 1px solid #E0E0E0;
            background: #fff;
            color: #333;
            transition: all 0.2s;
        }
        .stButton > button:hover {
            border-color: #000;
            color: #000;
            background: #F8F9FA;
            transform: translateY(-1px);
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        
        /* 3. 聊天气泡：数据块风格 */
        .chat-container {
            display: flex;
            flex-direction: column;
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .chat-bubble-me {
            background-color: #2D2D2D; 
            color: #FFFFFF; 
            padding: 14px 18px; 
            border-radius: 2px; /* 锐利边缘 */
            border-bottom-right-radius: 12px;
            align-self: flex-end;
            max-width: 80%;
            font-size: 15px;
            font-weight: 300;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            position: relative;
            float: right; clear: both;
        }
        
        .chat-bubble-other {
            background-color: #FFFFFF; 
            color: #333; 
            padding: 14px 18px; 
            border-radius: 2px;
            border-bottom-left-radius: 12px;
            border: 1px solid #EAEAEA;
            align-self: flex-start;
            max-width: 80%;
            font-size: 15px;
            line-height: 1.6;
            box-shadow: 0 1px 4px rgba(0,0,0,0.03);
            float: left; clear: both;
        }
        
        .chat-bubble-ai {
            background: #F8F9FA;
            color: #666;
            border-left: 3px solid #00CCFF; /* AI 标识色 */
            padding: 12px 20px;
            font-family: 'Inter', sans-serif;
            font-size: 0.9em;
            margin: 10px 0;
            width: 100%;
            clear: both;
            border-radius: 0 4px 4px 0;
        }
        
        /* 4. 意义卡片与微交互 */
        .meaning-dot-btn { 
            display: flex; align-items: center; justify-content: center; height: 100%; 
            opacity: 0.6; transition: opacity 0.3s;
        }
        .meaning-dot-btn:hover { opacity: 1.0; }
        
        .daily-card {
            border: 1px solid #E0E0E0;
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            margin-bottom: 20px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 14px;
            color: #444;
            box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        }
        .daily-label {
            font-size: 10px; text-transform: uppercase; letter-spacing: 2px; color: #AAA; margin-bottom: 8px;
        }
        
        /* 去除 Streamlit 默认头部红线 */
        header {visibility: hidden;}
        
        /* 调整 Toasts */
        .stToast {
            background-color: #333 !important;
            color: #fff !important;
            border-radius: 4px !important;
        }
    </style>
    """, unsafe_allow_html=True)

st.set_page_config(page_title="MSC v75.0", layout="wide", initial_sidebar_state="expanded")
inject_custom_css()

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "is_admin" not in st.session_state: st.session_state.is_admin = False
if "current_chat_partner" not in st.session_state: st.session_state.current_chat_partner = None

# --- 1. 登录注册 ---
if not st.session_state.logged_in:
    pages.render_login_page()
else:
    msc.update_heartbeat(st.session_state.username)
    
    # === 🚀 新手引导入口判断 ===
    # 获取用户节点数
    my_nodes_list = msc.get_active_nodes_map(st.session_state.username).values()
    node_count = len(my_nodes_list)
    
    # 如果节点数为 0 (全新用户)，且不是管理员，且还没完成本次引导
    if node_count == 0 and not st.session_state.is_admin and "onboarding_complete" not in st.session_state:
        pages.render_onboarding(st.session_state.username)
        st.stop() # 🛑 停止渲染主界面，只显示引导页
        
    # === 以下是正常主界面 ===
# --- 2. 主界面 ---
else:
    msc.update_heartbeat(st.session_state.username)
    user_profile = msc.get_user_profile(st.session_state.username)
    
    raw_radar = user_profile.get('radar_profile')
    if isinstance(raw_radar, str): radar_dict = json.loads(raw_radar)
    else: radar_dict = raw_radar if raw_radar else {k:3.0 for k in ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]}
    
    # 获取用户的真实节点
    my_nodes = msc.get_active_nodes_map(st.session_state.username).values()
    
    total_unread, unread_counts = msc.get_unread_counts(st.session_state.username)

    with st.sidebar:
        # 用户信息区
        c_av, c_info = st.columns([0.25, 0.75])
        with c_av:
            rank_name, rank_icon = msc.calculate_rank(radar_dict)
            st.markdown(f"<div style='font-size:24px; text-align:center;'>{rank_icon}</div>", unsafe_allow_html=True)
        with c_info:
            st.markdown(f"**{st.session_state.nickname}**")
            st.caption(f"ID: {st.session_state.username} | {rank_name}")

        st.divider()

        # 每日一问 (卡片式设计)
        if "daily_q" not in st.session_state: st.session_state.daily_q = None
        if st.session_state.daily_q is None:
            if st.button("📅 Insight Generator", use_container_width=True):
                with st.spinner("Extracting meaning..."):
                    st.session_state.daily_q = msc.generate_daily_question(st.session_state.username, radar_dict)
                    st.rerun()
        else:
            st.markdown(
                f"""
                <div class='daily-card'>
                    <div class='daily-label'>DAILY REFLECTION</div>
                    {st.session_state.daily_q}
                </div>
                """, 
                unsafe_allow_html=True
            )
            if st.button("↻ Refresh", key="refresh_daily"): st.session_state.daily_q = None; st.rerun()

        # === 森林 (3D 灵魂形态) ===
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        forest.render_forest_scene(radar_dict, list(my_nodes))
        
        c_b1, c_b2 = st.columns(2)
        with c_b1:
            if st.button("🧬 DNA", use_container_width=True, help="View Radar Analysis"):
                viz.view_radar_details(radar_dict, st.session_state.username)
        with c_b2:
            all_nodes_list = msc.get_all_nodes_for_map(st.session_state.username)
            if st.button("🔭 Map", use_container_width=True, help="View Fullscreen Map"): 
                viz.view_fullscreen_map(all_nodes_list, st.session_state.nickname)
        
        st.divider()
        
        # 菜单
        menu_items = [
            sac.MenuItem('AI Partner', icon='robot'),
            sac.MenuItem('Chat', icon='chat-dots', tag=sac.Tag(str(total_unread), color='red') if total_unread > 0 else None),
            sac.MenuItem('World', icon='globe'),
        ]
        
        if st.session_state.is_admin:
            menu_items.append(sac.MenuItem('God Mode', icon='eye-fill'))
        
        menu_items.append(sac.MenuItem('System', type='group', children=[sac.MenuItem('Logout', icon='box-arrow-right')]))

        menu = sac.menu(menu_items, index=0, format_func='title', size='sm', variant='light', open_all=True)

    if menu == 'Logout': 
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.rerun()
    elif menu == 'AI Partner': pages.render_ai_page(st.session_state.username)
    elif menu == 'Chat': pages.render_friends_page(st.session_state.username, unread_counts)
    elif menu == 'World': pages.render_world_page()
    elif menu == 'God Mode': pages.render_admin_dashboard()
