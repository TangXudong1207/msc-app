### msc_main.py ###

import streamlit as st
import streamlit_antd_components as sac
import msc_lib as msc
import msc_viz as viz
import msc_pages as pages
import json
import msc_forest as forest
import msc_i18n as i18n 

# ==========================================
# 🎨 CSS：Cyber-Zen 极简主义设计系统
# ==========================================
def inject_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=JetBrains+Mono:wght@400;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: #2D3436;
        }
        code, .stCode, .monospaced {
            font-family: 'JetBrains Mono', monospace !important;
        }

        .stApp { background-color: #FAFAFA; }
        
        [data-testid="stSidebar"] {
            background-color: #FFFFFF;
            border-right: 1px solid #F0F0F0;
            box-shadow: 2px 0 10px rgba(0,0,0,0.02);
        }
        
        /* 移动端优化：顶部导航卡片 */
        .nav-card {
            border: 1px solid #EEE;
            background: white;
            padding: 10px;
            border-radius: 8px;
            text-align: center;
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            transition: all 0.2s;
            margin-bottom: 5px;
        }
        .nav-card:hover {
            border-color: #CCC;
            transform: translateY(-2px);
        }
        .nav-icon { font-size: 20px; margin-bottom: 5px; }
        .nav-text { font-size: 12px; font-weight: 600; color: #555; }
        
        .chat-bubble-me {
            background-color: #2D2D2D; 
            color: #FFFFFF; 
            padding: 14px 18px; 
            border-radius: 2px; 
            border-bottom-right-radius: 12px;
            align-self: flex-end;
            max-width: 80%;
            font-size: 15px;
            font-weight: 300;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            position: relative;
            float: right; clear: both; margin-bottom: 8px;
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
            float: left; clear: both; margin-bottom: 8px;
        }
        
        .chat-bubble-ai {
            background: #F8F9FA;
            color: #666;
            border-left: 3px solid #00CCFF; 
            padding: 12px 20px;
            font-family: 'Inter', sans-serif;
            font-size: 0.9em;
            margin: 10px 0;
            width: 100%;
            clear: both;
            border-radius: 0 4px 4px 0;
        }
        
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
        
        header {visibility: hidden;}
        
        .stToast {
            background-color: #333 !important;
            color: #fff !important;
            border-radius: 4px !important;
        }
    </style>
    """, unsafe_allow_html=True)

st.set_page_config(page_title="MSC v75.5", layout="wide", initial_sidebar_state="collapsed") # 默认收起侧边栏，适应手机
inject_custom_css()

# === 全局状态初始化 ===
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "is_admin" not in st.session_state: st.session_state.is_admin = False
if "current_chat_partner" not in st.session_state: st.session_state.current_chat_partner = None
if "language" not in st.session_state: st.session_state.language = "en" 
if "nav_selection" not in st.session_state: st.session_state.nav_selection = "AI" # 默认页面

def check_and_send_first_contact(username):
    history = msc.get_active_chats(username)
    if not history:
        lang = st.session_state.language
        if lang == 'zh':
            first_msg = """先说清楚一件事：\n这里就是一个和 AI 聊天的对话框，\n和你用过的那些差不多。\n\n如果你现在不知道该从哪开始，\n那也正常。\n\n那就从最简单的开始吧——\n吃了吗？"""
        else:
            first_msg = """Let's get one thing clear:\nThis is just a chat box where you talk to an AI.\n\nLet's start with something simple—\nHow is your day going?"""
        msc.save_chat(username, "assistant", first_msg)

# --- 1. 登录注册 ---
if not st.session_state.logged_in:
    pages.render_login_page()

# --- 2. 主界面 ---
else:
    msc.update_heartbeat(st.session_state.username)
    
    # 引导拦截
    my_nodes_list = list(msc.get_active_nodes_map(st.session_state.username).values())
    node_count = len(my_nodes_list)
    if node_count == 0 and not st.session_state.is_admin and "onboarding_complete" not in st.session_state:
        pages.render_onboarding(st.session_state.username)
        st.stop()
    
    if node_count == 0 and not st.session_state.is_admin:
        check_and_send_first_contact(st.session_state.username)

    user_profile = msc.get_user_profile(st.session_state.username)
    raw_radar = user_profile.get('radar_profile')
    if isinstance(raw_radar, str): radar_dict = json.loads(raw_radar)
    else: radar_dict = raw_radar if raw_radar else {k:3.0 for k in ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]}
    
    total_unread, unread_counts = msc.get_unread_counts(st.session_state.username)
    lang = st.session_state.language

    # 翻译
    MENU_TEXT = {
        "en": {"AI": "AI", "Chat": "Signal", "World": "World", "God": "God", "Map": "Map"},
        "zh": {"AI": "AI", "Chat": "信号", "World": "世界", "God": "上帝", "Map": "星图"}
    }
    T = MENU_TEXT[lang]

    # === 📱 移动端/桌面通用导航栏 (顶部) ===
    # 这样手机用户不用开侧边栏也能切页面
    nav_c1, nav_c2, nav_c3, nav_c4 = st.columns(4)
    
    # 辅助函数：生成按钮样式
    def nav_btn(col, key, label, icon, active_key):
        is_active = st.session_state.nav_selection == active_key
        style = "border: 1px solid #333; background: #333; color: white;" if is_active else "border: 1px solid #EEE;"
        if col.button(f"{icon} {label}", key=f"nav_{key}", use_container_width=True):
            st.session_state.nav_selection = active_key
            st.rerun()

    nav_btn(nav_c1, "ai", T['AI'], "🤖", "AI")
    
    # 聊天按钮带红点
    chat_label = T['Chat']
    if total_unread > 0: chat_label += f" ({total_unread})"
    nav_btn(nav_c2, "chat", chat_label, "📡", "Chat")
    
    nav_btn(nav_c3, "world", T['World'], "🌍", "World")
    
    if st.session_state.is_admin:
        nav_btn(nav_c4, "god", T['God'], "👁️", "God")
    else:
        # 普通用户第四个按钮是 Logout
        if nav_c4.button("🚪 Out", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    st.markdown("<hr style='margin: 10px 0; border: none; border-top: 1px solid #EEE;'>", unsafe_allow_html=True)

    # === 侧边栏 (保留作为详细信息区) ===
    with st.sidebar:
        c_av, c_info = st.columns([0.25, 0.75])
        with c_av:
            rank_name, rank_icon = msc.calculate_rank(radar_dict)
            st.markdown(f"<div style='font-size:24px; text-align:center;'>{rank_icon}</div>", unsafe_allow_html=True)
        with c_info:
            st.markdown(f"**{st.session_state.nickname}**")
            st.caption(f"ID: {st.session_state.username}")

        st.divider()
        
        # 每日一问
        if "daily_q" not in st.session_state: st.session_state.daily_q = None
        if st.session_state.daily_q is None:
            if st.button(f"📅 Daily Insight", use_container_width=True):
                with st.spinner("..."):
                    st.session_state.daily_q = msc.generate_daily_question(st.session_state.username, radar_dict)
                    st.rerun()
        else:
            st.info(st.session_state.daily_q)
            if st.button("↻", key="ref_d"): st.session_state.daily_q = None; st.rerun()

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        forest.render_forest_scene(radar_dict, my_nodes_list)
        
        st.divider()
        # 语言切换
        lang_opts = ['EN', '中文']
        curr_idx = 0 if st.session_state.language == 'en' else 1
        lang_choice = sac.segmented(items=lang_opts, align='center', size='xs', index=curr_idx, key="sb_lang")
        mapped_lang = 'en' if lang_choice == 'EN' else 'zh'
        if mapped_lang != st.session_state.language:
            st.session_state.language = mapped_lang
            st.rerun()

    # === 页面路由 (基于 session_state) ===
    current_page = st.session_state.nav_selection

    if current_page == 'AI': 
        pages.render_ai_page(st.session_state.username)
    elif current_page == 'Chat': 
        pages.render_friends_page(st.session_state.username, unread_counts)
    elif current_page == 'World': 
        pages.render_world_page()
    elif current_page == 'God': 
        pages.render_admin_dashboard()
