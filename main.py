### msc_main.py (最终整合版) ###

import streamlit as st
import streamlit_antd_components as sac
import msc_lib as msc
import msc_viz as viz
import msc_pages as pages
import json
# 注意：这里不需要再显式 import msc_sim 了，因为 sim 逻辑封装在 pages 里了

# ==========================================
# 🎨 CSS
# ==========================================
def inject_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        .stApp { background-color: #FFFFFF; font-family: 'Roboto', sans-serif; color: #222; }
        [data-testid="stSidebar"] { background-color: #FAFAFA; border-right: 1px solid #E0E0E0; }
        .chat-bubble-me { background-color: #555555; color: #fff; padding: 12px 16px; border-radius: 18px; border-bottom-right-radius: 4px; margin-bottom: 8px; display: inline-block; float: right; clear: both; max-width: 85%; font-size: 15px; }
        .chat-bubble-other { background-color: #F7F7F7; color: #333; padding: 12px 16px; border-radius: 18px; border-bottom-left-radius: 4px; margin-bottom: 8px; display: inline-block; float: left; clear: both; max-width: 85%; font-size: 15px; border: 1px solid #EAEAEA; }
        .daily-card { border: 1px solid #eee; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 20px; background: #fff; }
        .daily-title { font-size: 10px; color: #999; letter-spacing: 1px; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.set_page_config(page_title="MSC v72.0 Soft", layout="wide", initial_sidebar_state="expanded")
inject_custom_css()

# 初始化 Session State
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "is_admin" not in st.session_state: st.session_state.is_admin = False
if "current_chat_partner" not in st.session_state: st.session_state.current_chat_partner = None

# --- 1. 登录注册 ---
if not st.session_state.logged_in:
    pages.render_login_page()

# --- 2. 主界面 ---
else:
    msc.update_heartbeat(st.session_state.username)
    user_profile = msc.get_user_profile(st.session_state.username)
    
    # 获取雷达数据
    raw_radar = user_profile.get('radar_profile')
    if isinstance(raw_radar, str): radar_dict = json.loads(raw_radar)
    else: radar_dict = raw_radar if raw_radar else {k:3.0 for k in ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]}
    
    rank_name, rank_icon = msc.calculate_rank(radar_dict)
    total_unread, unread_counts = msc.get_unread_counts(st.session_state.username)

    with st.sidebar:
        st.markdown(f"### {rank_icon} {st.session_state.nickname}")
        
        # 每日一问
        if "daily_q" not in st.session_state: st.session_state.daily_q = None
        if st.session_state.daily_q is None:
            if st.button("📅 Insight", use_container_width=True):
                with st.spinner("."):
                    st.session_state.daily_q = msc.generate_daily_question(st.session_state.username, radar_dict)
                    st.rerun()
        else:
            st.markdown(f"<div class='daily-card'><div class='daily-title'>DAILY</div>{st.session_state.daily_q}</div>", unsafe_allow_html=True)
            if st.button("🔄"): st.session_state.daily_q = None; st.rerun()

        # 雷达图与深度画像
        viz.render_radar_chart(radar_dict, height="180px")
        if st.button("🧬 Deep Profile", use_container_width=True):
            viz.view_radar_details(radar_dict, st.session_state.nickname)
        
        # === 动态构建菜单 ===
        menu_items = [
            sac.MenuItem('AI Partner', icon='robot'),
            sac.MenuItem('Chat', icon='chat-dots', tag=sac.Tag(str(total_unread), color='red') if total_unread > 0 else None),
            sac.MenuItem('World', icon='globe'),
        ]
        
        # 👑 只有管理员能看到 God Mode
        if st.session_state.is_admin:
            menu_items.append(sac.MenuItem('God Mode', icon='eye-fill', type='group'))
        
        menu_items.append(sac.MenuItem('System', type='group', children=[sac.MenuItem('Logout', icon='box-arrow-right')]))

        menu = sac.menu(menu_items, index=0, format_func='title', size='sm', variant='light', open_all=True)

        st.divider()
        all_nodes = msc.get_all_nodes_for_map(st.session_state.username)
        if st.button("🔭 Full View", use_container_width=True): 
            viz.view_fullscreen_map(all_nodes, st.session_state.nickname)

    # === 页面路由 ===
    if menu == 'Logout': 
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.rerun()
    elif menu == 'AI Partner': pages.render_ai_page(st.session_state.username)
    elif menu == 'Chat': pages.render_friends_page(st.session_state.username, unread_counts)
    elif menu == 'World': pages.render_world_page()
    elif menu == 'God Mode': pages.render_admin_dashboard() # 管理员专属页面
