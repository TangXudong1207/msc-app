import streamlit as st
import streamlit_antd_components as sac
import msc_lib as msc
import msc_pages as pages # 🌟 引用新的页面库
import json

# ==========================================
# 🎨 CSS：极简科技风 (v48 风格回归)
# ==========================================
def inject_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        
        /* 全局去色，回归黑白灰 */
        .stApp { background-color: #FFFFFF; font-family: 'Roboto', sans-serif; color: #222; }
        
        /* 侧边栏：纯净白 */
        [data-testid="stSidebar"] { background-color: #FAFAFA; border-right: 1px solid #EEE; }
        
        /* 输入框：极细边框 */
        .stTextInput input {
            border: 1px solid #E0E0E0; border-radius: 4px; padding: 10px;
            color: #333; background: #fff;
        }
        .stTextInput input:focus { border-color: #333; box-shadow: none; }
        
        /* 按钮：黑白极简 */
        .stButton button {
            border: 1px solid #E0E0E0; background: #fff; color: #333;
            border-radius: 4px; font-weight: 400; font-size: 14px;
        }
        .stButton button:hover { border-color: #333; color: #000; background: #F9F9F9; }
        
        /* 聊天气泡：回归线条感 */
        .chat-bubble-me {
            background-color: #333; color: #fff; /* 我是深色块 */
            padding: 10px 15px; border-radius: 18px; border-bottom-right-radius: 2px;
            margin-bottom: 5px; display: inline-block; float: right; clear: both; max-width: 80%;
            font-size: 14px;
        }
        .chat-bubble-other {
            background-color: #F2F2F2; color: #333; /* 对方是浅灰块 */
            padding: 10px 15px; border-radius: 18px; border-bottom-left-radius: 2px;
            margin-bottom: 5px; display: inline-block; float: left; clear: both; max-width: 80%;
            font-size: 14px;
        }
        .chat-bubble-ai {
            background: transparent; color: #666; border: 1px solid #ddd;
            padding: 8px 12px; border-radius: 12px; margin: 15px auto;
            text-align: center; font-size: 0.85em; width: fit-content;
        }
        
        /* 每日追问卡片 */
        .daily-card {
            border: 1px solid #eee; padding: 15px; border-radius: 8px;
            text-align: center; margin-bottom: 20px; background: #fff;
        }
        .daily-title { font-size: 10px; color: #999; letter-spacing: 1px; margin-bottom: 5px; }
        .daily-question { font-size: 14px; color: #333; font-weight: 500; }
    </style>
    """, unsafe_allow_html=True)

st.set_page_config(page_title="MSC v52.0 Minimal", layout="wide", initial_sidebar_state="expanded")
inject_custom_css()

if "logged_in" not in st.session_state: st.session_state.logged_in = False

# --- 1. 登录路由 ---
if not st.session_state.logged_in:
    pages.render_login_page()

# --- 2. 主界面路由 ---
else:
    # 基础数据加载
    msc.update_heartbeat(st.session_state.username)
    user_profile = msc.get_user_profile(st.session_state.username)
    raw_radar = user_profile.get('radar_profile')
    if isinstance(raw_radar, str): radar_dict = json.loads(raw_radar)
    else: radar_dict = raw_radar if raw_radar else {k:3.0 for k in ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]}
    
    total_unread, unread_counts = msc.get_unread_counts(st.session_state.username)

    # --- 侧边栏 ---
    with st.sidebar:
        # 用户信息 (极简)
        st.markdown(f"**{st.session_state.nickname}**")
        st.caption(f"ID: {user_profile.get('uid', '---')}")
        
        # 每日追问
        if "daily_q" not in st.session_state: st.session_state.daily_q = None
        if st.session_state.daily_q is None:
            if st.button("Daily Inquiry", use_container_width=True):
                with st.spinner("."):
                    st.session_state.daily_q = msc.generate_daily_question(st.session_state.username, radar_dict)
                    st.rerun()
        else:
            st.markdown(f"<div class='daily-card'><div class='daily-title'>DAILY</div><div class='daily-question'>{st.session_state.daily_q}</div></div>", unsafe_allow_html=True)

        msc.render_radar_chart(radar_dict, height="160px")
        
        # 导航
        menu = sac.menu([
            sac.MenuItem('Chat', icon='chat-dots', tag=sac.Tag(str(total_unread), color='red') if total_unread > 0 else None),
            sac.MenuItem('AI Partner', icon='robot'),
            sac.MenuItem('World', icon='globe'),
            sac.MenuItem('System', type='group', children=[sac.MenuItem('Logout', icon='box-arrow-right')]),
        ], index=0, format_func='title', size='sm', variant='light', open_all=True)

        st.divider()
        if st.button("🔭 Full View", use_container_width=True): 
            all_nodes = msc.get_all_nodes_for_map(st.session_state.username)
            msc.view_fullscreen_map(all_nodes, st.session_state.nickname)

    # --- 路由逻辑 ---
    if menu == 'Logout': st.session_state.logged_in = False; st.rerun()
    
    elif menu == 'AI Partner':
        pages.render_ai_page(st.session_state.username)
        
    elif menu == 'Chat':
        pages.render_friends_page(st.session_state.username, unread_counts)
        
    elif menu == 'World':
        pages.render_world_page()
