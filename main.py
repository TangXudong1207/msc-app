import streamlit as st
import streamlit_antd_components as sac
import msc_lib as msc
import msc_ai as ai
import msc_viz as viz
import msc_pages as pages
import json

# ==========================================
# 🎨 CSS：极简科技风 (v71.0 定制版)
# ==========================================
def inject_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        
        /* 1. 全局设置 */
        .stApp { background-color: #FFFFFF; font-family: 'Roboto', sans-serif; color: #222; }
        [data-testid="stSidebar"] { background-color: #FAFAFA; border-right: 1px solid #F0F0F0; }
        
        /* 2. 隐藏原生头像 (关键) */
        .stChatMessage .stChatMessageAvatarBackground { display: none !important; }
        [data-testid="stChatMessageAvatar"] { display: none !important; }
        
        /* 3. 聊天气泡：柔和黑白 */
        /* 我 (右侧) */
        .chat-bubble-me {
            background-color: #333333; /* 柔和黑 */
            color: #FFFFFF; 
            padding: 12px 18px; 
            border-radius: 20px; 
            border-bottom-right-radius: 4px;
            margin-bottom: 12px; /* 增加间距 */
            display: inline-block; 
            float: right; 
            clear: both; 
            max-width: 85%;
            font-size: 15px; 
            line-height: 1.6;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        
        /* 对方/AI (左侧) */
        .chat-bubble-other {
            background-color: #F7F7F7; /* 极淡灰 */
            color: #333333; 
            padding: 12px 18px; 
            border-radius: 20px; 
            border-bottom-left-radius: 4px;
            margin-bottom: 12px; /* 增加间距 */
            display: inline-block; 
            float: left; 
            clear: both; 
            max-width: 85%;
            font-size: 15px; 
            line-height: 1.6;
            border: 1px solid #EAEAEA;
        }
        
        /* AI 思考状态 */
        .ai-thinking {
            color: #999; font-style: italic; font-size: 0.9em; margin-left: 15px;
        }

        /* 4. 意义小圆点 (垂直居中) */
        .meaning-dot-wrapper {
            display: flex; 
            align-items: center; 
            justify-content: center; 
            height: 100%; 
            padding-top: 15px; /* 对齐气泡中心 */
        }
        .meaning-dot-btn button {
            border: none !important; background: transparent !important; color: #CCC !important;
            padding: 0 !important; font-size: 16px !important;
        }
        .meaning-dot-btn button:hover { color: #1A73E8 !important; transform: scale(1.2); }

        /* 5. 每日卡片 */
        .daily-card {
            border: 1px solid #eee; padding: 16px; border-radius: 12px;
            text-align: center; margin-bottom: 20px; background: #fff;
            box-shadow: 0 2px 10px rgba(0,0,0,0.02);
        }
        .daily-title { font-size: 10px; color: #1A73E8; letter-spacing: 1.5px; font-weight: 700; margin-bottom: 8px; text-transform: uppercase; }
        .daily-question { font-size: 15px; color: #333; font-weight: 400; line-height: 1.5; }
    </style>
    """, unsafe_allow_html=True)

st.set_page_config(page_title="MSC v71.0 Pro", layout="wide", initial_sidebar_state="expanded")
inject_custom_css()

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "current_chat_partner" not in st.session_state: st.session_state.current_chat_partner = None

# --- 1. 登录路由 ---
if not st.session_state.logged_in:
    pages.render_login_page()

# --- 2. 主界面路由 ---
else:
    msc.update_heartbeat(st.session_state.username)
    user_profile = msc.get_user_profile(st.session_state.username)
    raw_radar = user_profile.get('radar_profile')
    if isinstance(raw_radar, str): radar_dict = json.loads(raw_radar)
    else: radar_dict = raw_radar if raw_radar else {k:3.0 for k in ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]}
    
    rank_name, rank_icon = msc.calculate_rank(radar_dict)
    total_unread, unread_counts = msc.get_unread_counts(st.session_state.username)

    with st.sidebar:
        # 用户信息
        st.markdown(f"**{st.session_state.nickname}**")
        st.caption(f"{rank_icon} {rank_name}")
        
        # 每日追问
        if "daily_q" not in st.session_state: st.session_state.daily_q = None
        if st.session_state.daily_q is None:
            if st.button("📅 Insight", use_container_width=True):
                with st.spinner("."):
                    st.session_state.daily_q = msc.generate_daily_question(st.session_state.username, radar_dict)
                    st.rerun()
        else:
            st.markdown(f"<div class='daily-card'><div class='daily-title'>Daily Inquiry</div><div class='daily-question'>{st.session_state.daily_q}</div></div>", unsafe_allow_html=True)

        msc.render_radar_chart(radar_dict, height="180px")
        
        # 导航
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

    # 路由
    if menu == 'Logout': st.session_state.logged_in = False; st.rerun()
    elif menu == 'AI Partner': pages.render_ai_page(st.session_state.username)
    elif menu == 'Chat': pages.render_friends_page(st.session_state.username, unread_counts)
    elif menu == 'World': pages.render_world_page()
