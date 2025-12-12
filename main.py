import streamlit as st
import streamlit_antd_components as sac
import msc_lib as msc
import msc_viz as viz
import msc_pages as pages
import json

# ==========================================
# 🎨 CSS：极简科技风 (v72.0 柔和版)
# ==========================================
def inject_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        
        .stApp { background-color: #FFFFFF; font-family: 'Roboto', sans-serif; color: #222; }
        [data-testid="stSidebar"] { background-color: #FAFAFA; border-right: 1px solid #E0E0E0; }
        
        /* 隐藏头像 */
        .stChatMessage .stChatMessageAvatarBackground { display: none !important; }
        [data-testid="stChatMessageAvatar"] { display: none !important; }
        
        /* 聊天气泡：我 (颜色变浅了) */
        .chat-bubble-me {
            background-color: #555555; /* 🌟 之前是 #222 (太黑)，现在是 #555 (高级灰) */
            color: #fff; 
            padding: 12px 16px; 
            border-radius: 18px; 
            border-bottom-right-radius: 4px;
            margin-bottom: 8px; 
            display: inline-block; 
            float: right; 
            clear: both; 
            max-width: 85%;
            font-size: 15px; 
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }
        
        /* 聊天气泡：对方 */
        .chat-bubble-other {
            background-color: #F7F7F7; 
            color: #333; 
            padding: 12px 16px; 
            border-radius: 18px; 
            border-bottom-left-radius: 4px;
            margin-bottom: 8px; 
            display: inline-block; 
            float: left; 
            clear: both; 
            max-width: 85%;
            font-size: 15px; 
            border: 1px solid #EAEAEA;
        }
        
        .chat-bubble-ai {
            background: transparent; color: #888; border: 1px dashed #ddd; 
            padding: 8px 12px; border-radius: 12px; margin: 15px auto; 
            text-align: center; font-size: 0.85em; width: fit-content; clear: both;
        }
        
        .meaning-dot-btn { display: flex; align-items: center; justify-content: center; height: 100%; padding-top: 10px; }
        .meaning-dot-btn button { border: none !important; background: transparent !important; color: #CCC !important; font-size: 18px !important; }
        .meaning-dot-btn button:hover { color: #1A73E8 !important; transform: scale(1.2); }
        
        .daily-card { border: 1px solid #eee; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 20px; background: #fff; }
        .daily-title { font-size: 10px; color: #999; letter-spacing: 1px; margin-bottom: 5px; }
        .daily-question { font-size: 14px; color: #333; font-weight: 500; }
        
        .login-card { background: white; padding: 2rem; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.set_page_config(page_title="MSC v72.0 Soft", layout="wide", initial_sidebar_state="expanded")
inject_custom_css()

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "current_chat_partner" not in st.session_state: st.session_state.current_chat_partner = None

# --- 1. 登录注册 ---
if not st.session_state.logged_in:
    pages.render_login_page()

# --- 2. 主界面 ---
else:
    msc.update_heartbeat(st.session_state.username)
    user_profile = msc.get_user_profile(st.session_state.username)
    raw_radar = user_profile.get('radar_profile')
    if isinstance(raw_radar, str): radar_dict = json.loads(raw_radar)
    else: radar_dict = raw_radar if raw_radar else {k:3.0 for k in ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]}
   rank_name, rank_icon = msc.calculate_rank(radar_dict) # 改为 msc
    total_unread, unread_counts = msc.get_unread_counts(st.session_state.username)

    with st.sidebar:
        st.markdown(f"### {rank_icon} {st.session_state.nickname}")
        
        if "daily_q" not in st.session_state: st.session_state.daily_q = None
        if st.session_state.daily_q is None:
            if st.button("📅 Insight", use_container_width=True):
                with st.spinner("."):
                    # 改为 msc 调用
                    st.session_state.daily_q = msc.generate_daily_question(st.session_state.username, radar_dict)
                    st.rerun()
        else:
            st.markdown(f"<div class='daily-card'><div class='daily-title'>DAILY</div>{st.session_state.daily_q}</div>", unsafe_allow_html=True)
            if st.button("🔄"): st.session_state.daily_q = None; st.rerun()

        viz.render_radar_chart(radar_dict, height="180px")
        
        menu = sac.menu([
            sac.MenuItem('AI Partner', icon='robot'),
            sac.MenuItem('Chat', icon='chat-dots', tag=sac.Tag(str(total_unread), color='red') if total_unread > 0 else None),
            sac.MenuItem('World', icon='globe'),
            sac.MenuItem('System', type='group', children=[sac.MenuItem('Logout', icon='box-arrow-right')]),
        ], index=0, format_func='title', size='sm', variant='light', open_all=True)

        st.divider()
        all_nodes = msc.get_all_nodes_for_map(st.session_state.username)
        if st.button("🔭 Full View", use_container_width=True): 
            viz.view_fullscreen_map(all_nodes, st.session_state.nickname)

    if menu == 'Logout': st.session_state.logged_in = False; st.rerun()
    elif menu == 'AI Partner': pages.render_ai_page(st.session_state.username)
    elif menu == 'Chat': pages.render_friends_page(st.session_state.username, unread_counts)
    elif menu == 'World': pages.render_world_page()
