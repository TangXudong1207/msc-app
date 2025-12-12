import streamlit as st
import streamlit_antd_components as sac
import msc_db as db
import msc_ai as ai
import msc_viz as viz
import msc_pages as pages
import json

st.set_page_config(page_title="MSC v60.1 Fixed", layout="wide", initial_sidebar_state="expanded")

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "current_chat_partner" not in st.session_state: st.session_state.current_chat_partner = None

if not st.session_state.logged_in:
    pages.render_login_page()
else:
    # 心跳
    if "username" in st.session_state:
        db.update_heartbeat(st.session_state.username)
        user_profile = db.get_user_profile(st.session_state.username)
    else:
        st.session_state.logged_in = False # 强制登出
        st.rerun()
        
    raw_radar = user_profile.get('radar_profile')
    if isinstance(raw_radar, str): radar_dict = json.loads(raw_radar)
    else: radar_dict = raw_radar if raw_radar else {k:3.0 for k in ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]}
    
    rank_name, rank_icon = ai.calculate_rank(radar_dict)
    total_unread, unread_counts = db.get_unread_counts(st.session_state.username)

    # 🌟 安全获取昵称
    nickname = st.session_state.get('nickname', 'User')

    with st.sidebar:
        st.markdown(f"### {rank_icon} {nickname}")
        
        if "daily_q" not in st.session_state: st.session_state.daily_q = None
        if st.session_state.daily_q is None:
            if st.button("📅 Insight", use_container_width=True):
                with st.spinner("."):
                    st.session_state.daily_q = ai.generate_daily_question(st.session_state.username, radar_dict)
                    st.rerun()
        else:
            st.info(st.session_state.daily_q)

        viz.render_radar_chart(radar_dict, height="160px")
        
        menu = sac.menu([
            sac.MenuItem('AI Partner', icon='robot'),
            sac.MenuItem('Chat', icon='chat-dots', tag=sac.Tag(str(total_unread), color='red') if total_unread > 0 else None),
            sac.MenuItem('World', icon='globe'),
            sac.MenuItem('System', type='group', children=[sac.MenuItem('Logout', icon='box-arrow-right')]),
        ], index=0, format_func='title', size='sm', variant='light', open_all=True)

        st.divider()
        all_nodes = db.get_all_nodes_for_map(st.session_state.username)
        if st.button("🔭 Full View", use_container_width=True): 
            viz.view_fullscreen_map(all_nodes, nickname)

    if menu == 'Logout': st.session_state.logged_in = False; st.rerun()
    elif menu == 'AI Partner': pages.render_ai_page(st.session_state.username)
    elif menu == 'Chat': pages.render_friends_page(st.session_state.username, unread_counts)
    elif menu == 'World': pages.render_world_page()
