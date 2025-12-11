import streamlit as st
import streamlit_antd_components as sac
import msc_lib as msc
import msc_pages as pages
import json

# ==========================================
# 🎨 CSS：极简科技风 (无头像、黑白灰、线条感)
# ==========================================
def inject_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        
        /* 1. 全局去色 */
        .stApp { background-color: #FFFFFF; font-family: 'Roboto', sans-serif; color: #222; }
        [data-testid="stSidebar"] { background-color: #FAFAFA; border-right: 1px solid #EEE; }
        
        /* 2. 隐藏 Streamlit 原生头像 */
        .stChatMessage .stChatMessageAvatarBackground { display: none !important; }
        
        /* 3. 聊天气泡：极简色块 */
        /* 我 (右侧，深黑) */
        .chat-bubble-me {
            background-color: #222; color: #fff; 
            padding: 10px 16px; border-radius: 18px; border-bottom-right-radius: 4px;
            margin-bottom: 2px; display: inline-block; float: right; clear: both; max-width: 85%;
            font-size: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        /* 对方/AI (左侧，浅灰) */
        .chat-bubble-other {
            background-color: #F2F2F2; color: #222; 
            padding: 10px 16px; border-radius: 18px; border-bottom-left-radius: 4px;
            margin-bottom: 2px; display: inline-block; float: left; clear: both; max-width: 85%;
            font-size: 15px; border: 1px solid #E5E5E5;
        }
        /* AI 插话 (居中) */
        .chat-bubble-ai {
            background: transparent; color: #666; border: 1px dashed #ccc;
            padding: 8px 12px; border-radius: 12px; margin: 15px auto;
            text-align: center; font-size: 0.85em; width: fit-content;
        }

        /* 4. 意义小圆点 (垂直居中调整) */
        .meaning-dot-btn {
            display: flex; align-items: center; justify-content: center; height: 100%;
        }
        .meaning-dot-btn button {
            border: none !important; background: transparent !important; color: #BBB !important;
            padding: 0 !important; font-size: 18px !important; line-height: 1 !important;
        }
        .meaning-dot-btn button:hover { color: #1A73E8 !important; transform: scale(1.2); }

        /* 5. 每日卡片 */
        .daily-card {
            border: 1px solid #eee; padding: 15px; border-radius: 8px;
            text-align: center; margin-bottom: 20px; background: #fff;
        }
        .daily-title { font-size: 10px; color: #999; letter-spacing: 1px; margin-bottom: 5px; }
        .daily-question { font-size: 14px; color: #333; font-weight: 500; }
    </style>
    """, unsafe_allow_html=True)

st.set_page_config(page_title="MSC v53.3", layout="wide", initial_sidebar_state="expanded")
inject_custom_css()

# --- 状态初始化 ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "current_chat_partner" not in st.session_state: st.session_state.current_chat_partner = None

# ==========================================
# 🚀 路由分发
# ==========================================

# 场景 1: 未登录 -> 渲染登录页
if not st.session_state.logged_in:
    pages.render_login_page()

# 场景 2: 已登录 -> 渲染主界面
else:
    # 1. 后台心跳与数据加载
    msc.update_heartbeat(st.session_state.username)
    user_profile = msc.get_user_profile(st.session_state.username)
    
    raw_radar = user_profile.get('radar_profile')
    if isinstance(raw_radar, str): radar_dict = json.loads(raw_radar)
    else: radar_dict = raw_radar if raw_radar else {k:3.0 for k in ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]}
    
    rank_name, rank_icon = msc.calculate_rank(radar_dict)
    total_unread, unread_counts = msc.get_unread_counts(st.session_state.username)

    # 2. 侧边栏导航
    with st.sidebar:
        # 用户头衔
        st.markdown(f"**{st.session_state.nickname}**")
        st.caption(f"{rank_icon} {rank_name} | ID: {user_profile.get('uid', '--')}")
        
        # 每日追问
        if "daily_q" not in st.session_state: st.session_state.daily_q = None
        if st.session_state.daily_q is None:
            if st.button("📅 Insight", use_container_width=True):
                with st.spinner("."):
                    st.session_state.daily_q = msc.generate_daily_question(st.session_state.username, radar_dict)
                    st.rerun()
        else:
            st.markdown(f"<div class='daily-card'><div class='daily-title'>DAILY</div>{st.session_state.daily_q}</div>", unsafe_allow_html=True)

        msc.render_radar_chart(radar_dict, height="180px")
        
        # 核心菜单
        menu = sac.menu([
            sac.MenuItem('AI Partner', icon='robot'),
            sac.MenuItem('Chat', icon='chat-dots', tag=sac.Tag(str(total_unread), color='red') if total_unread > 0 else None),
            sac.MenuItem('Groups', icon='people'),
            sac.MenuItem('World', icon='globe'),
            sac.MenuItem('System', type='group', children=[sac.MenuItem('Logout', icon='box-arrow-right')]),
        ], index=0, format_func='title', size='sm', variant='light', open_all=True)

        st.divider()
        if st.button("🔭 Full View", use_container_width=True): 
            all_nodes = msc.get_all_nodes_for_map(st.session_state.username)
            msc.view_fullscreen_map(all_nodes, st.session_state.nickname)

    # 3. 页面路由
    if menu == 'Logout': st.session_state.logged_in = False; st.rerun()
    
    elif menu == 'AI Partner':
        pages.render_ai_page(st.session_state.username)
        
    elif menu == 'Chat':
        pages.render_friends_page(st.session_state.username, unread_counts)
        
    elif menu == 'Groups':
        pages.render_cluster_page(st.session_state.username)
        
    elif menu == 'World':
        pages.render_world_page()
