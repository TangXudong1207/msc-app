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
        
        /* 🛠️ 按钮样式修改：灰底，类似聊天框 */
        .stButton > button {
            border-radius: 4px; /* 稍微圆角一点，为了匹配 st.chat_input */
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85em;
            font-weight: 500;
            border: 1px solid #E0E0E0; /* 边框淡化 */
            background: #F0F2F6; /* 核心修改：变灰 */
            color: #444;
            transition: all 0.2s;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .stButton > button:hover {
            border-color: #BBB;
            color: #000;
            background: #E8EAED; /* 悬停时稍微变深一点点的灰 */
            transform: translateY(-1px); 
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
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
        
        /* 每日洞察卡片：保持灰底风格 */
        .daily-card {
            border: 1px solid #DDD; 
            background: #F0F2F6; /* 也变灰 */
            padding: 20px;
            border-radius: 4px;
            text-align: center;
            margin-bottom: 20px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            color: #333;
        }
        .daily-label {
            font-size: 9px; text-transform: uppercase; letter-spacing: 3px; color: #999; margin-bottom: 12px;
            border-bottom: 1px solid #DDD; padding-bottom: 5px;
        }
        
        header, [data-testid="stHeader"] {
            visibility: visible !important;
            background-color: transparent !important;
            z-index: 100000 !important;
        }
        [data-testid="stDecoration"] { display: none !important; visibility: hidden !important; }
        [data-testid="stHeader"] button { color: #222 !important; border-color: transparent !important; }
        [data-testid="stHeader"] button:hover { background-color: rgba(0,0,0,0.05) !important; }
        [data-testid="stHeader"] svg { fill: #333 !important; }
        .stToast { background-color: #333 !important; color: #fff !important; border-radius: 0px !important; }
    </style>
    """, unsafe_allow_html=True)

st.set_page_config(page_title="MSC v75.5", layout="wide", initial_sidebar_state="expanded")
inject_custom_css()

# === 全局状态初始化 ===
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "is_admin" not in st.session_state: st.session_state.is_admin = False
if "current_chat_partner" not in st.session_state: st.session_state.current_chat_partner = None
if "language" not in st.session_state: st.session_state.language = "en" 

# ==========================================
# 🆕 首次接触逻辑 (First Contact Logic)
# ==========================================
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

    # === 🚀 新手引导拦截 ===
    my_nodes_list = list(msc.get_active_nodes_map(st.session_state.username).values())
    node_count = len(my_nodes_list)
    
    if node_count == 0 and not st.session_state.is_admin and "onboarding_complete" not in st.session_state:
        pages.render_onboarding(st.session_state.username)
        st.stop()
    
    if node_count == 0 and not st.session_state.is_admin:
        check_and_send_first_contact(st.session_state.username)

    # === 正常界面 ===
    user_profile = msc.get_user_profile(st.session_state.username)
    raw_radar = user_profile.get('radar_profile')
    if isinstance(raw_radar, str): radar_dict = json.loads(raw_radar)
    else: radar_dict = raw_radar if raw_radar else {k:3.0 for k in ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]}
    
    total_unread, unread_counts = msc.get_unread_counts(st.session_state.username)
    lang = st.session_state.language

    # 翻译字典
    MENU_TEXT = {
        "en": {
            "AI": "AI_PARTNER", "Chat": "SIGNAL_LINK", "World": "WORLD_LAYER", 
            "God": "OVERSEER", "Sys": "SYSTEM", "Logout": "DISCONNECT", 
            "Map": "[ STAR_MAP ]", "DNA": "[ DNA_SEQ ]", "Ins": "[ INSIGHT ]", "Ref": "[ REFRESH ]"
        },
        "zh": {
            "AI": "AI 伴侣", "Chat": "信号频段", "World": "世界层", 
            "God": "上帝视角", "Sys": "系统", "Logout": "断开连接", 
            "Map": "[ 星图投影 ]", "DNA": "[ 基因序列 ]", "Ins": "[ 每日洞察 ]", "Ref": "[ 刷新 ]"
        }
    }
    T = MENU_TEXT[lang]

    # === 侧边栏导航 (Sidebar Navigation) ===
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

        # 每日一问
        if "daily_q" not in st.session_state: st.session_state.daily_q = None
        if st.session_state.daily_q is None:
            if st.button(f"{T['Ins']}", use_container_width=True):
                with st.spinner("Extracting meaning..."):
                    st.session_state.daily_q = msc.generate_daily_question(st.session_state.username, radar_dict)
                    st.rerun()
        else:
            st.markdown(
                f"""
                <div class='daily-card'>
                    <div class='daily-label'>DAILY_PROTOCOL</div>
                    {st.session_state.daily_q}
                </div>
                """, 
                unsafe_allow_html=True
            )
            if st.button(f"{T['Ref']}", key="refresh_daily"): st.session_state.daily_q = None; st.rerun()

        # === 森林 (3D 灵魂形态) ===
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        forest.render_forest_scene(radar_dict, my_nodes_list)
        
        # 按钮：增加了具体的小图标
        c_b1, c_b2 = st.columns(2)
        with c_b1:
            if st.button(f"🧬 {T['DNA']}", use_container_width=True):
                viz.view_radar_details(radar_dict, st.session_state.username)
        with c_b2:
            all_nodes_list = msc.get_all_nodes_for_map(st.session_state.username)
            if st.button(f"🔭 {T['Map']}", use_container_width=True): 
                viz.view_fullscreen_map(all_nodes_list, st.session_state.nickname)
        
        st.divider()
        
        # 核心菜单：World 图标更新为 globe-americas
        menu_items = [
            sac.MenuItem(T['AI'], icon='robot'),
            sac.MenuItem(T['Chat'], icon='chat-dots', tag=sac.Tag(str(total_unread), color='red') if total_unread > 0 else None),
            sac.MenuItem(T['World'], icon='globe-americas'), # 改为美洲地球，线条更丰富
        ]
        
        if st.session_state.is_admin:
            menu_items.append(sac.MenuItem(T['God'], icon='eye-fill'))
        
        menu_items.append(sac.MenuItem(T['Sys'], type='group', children=[sac.MenuItem(T['Logout'], icon='box-arrow-right')]))

        selected_menu = sac.menu(menu_items, index=0, format_func='title', size='sm', variant='light', open_all=True)
        
        # 语言切换 (侧边栏底部)
        st.divider()
        lang_opts = ['EN', '中文']
        curr_idx = 0 if st.session_state.language == 'en' else 1
        lang_choice = sac.segmented(
            items=lang_opts, 
            align='center', size='xs', index=curr_idx, key="sidebar_lang_selector"
        )
        mapped_lang = 'en' if lang_choice == 'EN' else 'zh'
        if mapped_lang != st.session_state.language:
            st.session_state.language = mapped_lang
            st.rerun()

    # === 页面路由 ===
    if selected_menu == T['Logout']: 
        st.session_state.clear()
        st.rerun()
    elif selected_menu == T['AI']: pages.render_ai_page(st.session_state.username)
    elif selected_menu == T['Chat']: pages.render_friends_page(st.session_state.username, unread_counts)
    elif selected_menu == T['World']: pages.render_world_page()
    elif selected_menu == T['God']: pages.render_admin_dashboard()
