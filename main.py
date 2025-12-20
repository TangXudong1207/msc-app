### msc_main.py ###
import streamlit as st
import streamlit_antd_components as sac
import msc_lib as msc
import msc_viz as viz
import msc_pages as pages
import json
import msc_forest as forest
import msc_i18n as i18n 
import time
import random
import msc_config as config # 引入 config 以获取轴定义

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
        
        /* 每日洞察卡片 */
        .daily-card {
            border: 1px solid #DDD; 
            background: #F0F2F6; 
            padding: 24px;
            border-radius: 4px;
            text-align: center;
            margin-top: 10px;
            margin-bottom: 20px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 14px;
            color: #333;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }
        .daily-label {
            font-size: 10px; text-transform: uppercase; letter-spacing: 4px; color: #999; margin-bottom: 16px;
            border-bottom: 1px solid #DDD; padding-bottom: 8px;
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
if "viz_clicked" not in st.session_state: st.session_state.viz_clicked = None
if "daily_clicked" not in st.session_state: st.session_state.daily_clicked = None # 新增：每日洞察点击状态

# ==========================================
# ⚡ 核心修复：防止死循环的回调
# ==========================================
def on_viz_change():
    st.session_state.viz_clicked = st.session_state.viz_main_btn
    st.session_state.viz_main_btn = None

def on_daily_change():
    # 核心修复：捕获点击并清空原始状态
    st.session_state.daily_clicked = st.session_state.daily_main_btn
    st.session_state.daily_main_btn = None

# ==========================================
# 📚 本地备选语录库 (Fallback Library)
# ==========================================
LOCAL_INSIGHTS = {
    "en": [
        "What constitutes the boundary of your self?",
        "Is your current silence a form of speech?",
        "If memory is a vector, where is it pointing now?",
        "Are you observing the world, or is the world observing you?",
        "Structure is the solidified form of meaning.",
        "Chaos is just a pattern we haven't recognized yet."
    ],
    "zh": [
        "构成你“自我”边界的究竟是什么？",
        "你此刻的沉默，是否也是一种表达？",
        "如果记忆是一个向量，它现在指向哪里？",
        "是你正在观察世界，还是世界正在观察你？",
        "结构，是意义凝固后的形态。",
        "混乱，只是我们尚未识别出的模式。"
    ]
}

def get_fallback_insight():
    lang = st.session_state.language
    pool = LOCAL_INSIGHTS.get(lang, LOCAL_INSIGHTS['en'])
    return random.choice(pool)

# ==========================================
# 🔭 每日洞察弹窗 (Robust Version)
# ==========================================
@st.dialog("⚡ DAILY INSIGHT")
def daily_insight_dialog(username, radar):
    # 1. 状态管理
    if "daily_content" not in st.session_state:
        st.session_state.daily_content = None

    # 2. 生成逻辑
    if st.session_state.daily_content is None:
        with st.container():
            st.markdown("<div style='text-align:center; padding:20px; color:#888;'>Connecting to Void...</div>", unsafe_allow_html=True)
            with st.spinner(""):
                try:
                    insight = msc.generate_daily_question(username, radar)
                    if not insight or "error" in str(insight).lower() or len(str(insight)) < 5:
                        raise ValueError("Invalid AI Response")
                    st.session_state.daily_content = insight
                except:
                    st.session_state.daily_content = get_fallback_insight()
            st.rerun()

    # 3. 显示内容
    content = st.session_state.daily_content
    st.markdown(
        f"""
        <div class='daily-card'>
            <div class='daily-label'>REFLECTION PROTOCOL</div>
            <div style='font-size: 1.2em; line-height: 1.6; font-weight: 600; color: #222;'>
                {content}
            </div>
        </div>
        """, 
        unsafe_allow_html=True
    )
    st.caption("Generated based on your cognitive topology.")
    
    if st.button("Regenerate Signal", use_container_width=True):
        st.session_state.daily_content = None
        st.rerun()

# --- 登录逻辑 ---
if not st.session_state.logged_in:
    pages.render_login_page()

# --- 主界面 ---
else:
    msc.update_heartbeat(st.session_state.username)
    my_nodes_list = list(msc.get_active_nodes_map(st.session_state.username).values())
    node_count = len(my_nodes_list)
    
    if node_count == 0 and not st.session_state.is_admin and "onboarding_complete" not in st.session_state:
        pages.render_onboarding(st.session_state.username)
        st.stop()
    
    user_profile = msc.get_user_profile(st.session_state.username)
    raw_radar = user_profile.get('radar_profile')
    if isinstance(raw_radar, str): radar_dict = json.loads(raw_radar)
    else: radar_dict = raw_radar if raw_radar else {k:3.0 for k in config.RADAR_AXES}
    
    total_unread, unread_counts = msc.get_unread_counts(st.session_state.username)
    lang = st.session_state.language

    MENU_TEXT = {
        "en": {
            "AI": "AI_PARTNER", "Chat": "SIGNAL_LINK", "World": "WORLD_LAYER", 
            "God": "OVERSEER", "Sys": "SYSTEM", "Logout": "DISCONNECT", 
            "Map": "STAR_MAP", "DNA": "DNA_SEQ", "Ins": "INSIGHT", "Ref": "REFRESH"
        },
        "zh": {
            "AI": "AI 伴侣", "Chat": "信号频段", "World": "世界层", 
            "God": "上帝视角", "Sys": "系统", "Logout": "断开连接", 
            "Map": "星图投影", "DNA": "基因序列", "Ins": "每日洞察", "Ref": "刷新"
        }
    }
    T = MENU_TEXT[lang]

    # === 侧边栏导航 ===
    with st.sidebar:
        c_av, c_info = st.columns([0.25, 0.75])
        with c_av:
            rank_name, rank_icon = msc.calculate_rank(radar_dict)
            st.markdown(f"<div style='font-size:24px; text-align:center;'>{rank_icon}</div>", unsafe_allow_html=True)
        with c_info:
            st.markdown(f"**{st.session_state.nickname}**")
            st.caption(f"ID: {st.session_state.username} | {rank_name}")

        st.divider()

        # 每日洞察触发器 (增加回调函数 on_change)
        sac.buttons([
            sac.ButtonsItem(label=T['Ins'], icon='lightning-charge')
        ], align='center', variant='outline', radius='sm', use_container_width=True, index=None, color='#FF4B4B', key="daily_main_btn", on_change=on_daily_change)
        
        # 逻辑判定
        if st.session_state.daily_clicked == T['Ins']:
            st.session_state.daily_clicked = None # 立即销毁，防止下次 rerun 再次进入
            daily_insight_dialog(st.session_state.username, radar_dict)

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        forest.render_forest_scene(radar_dict, my_nodes_list)
        
        # 可视化工具栏
        sac.buttons([
            sac.ButtonsItem(label=T['DNA'], icon='diagram-2'), 
            sac.ButtonsItem(label=T['Map'], icon='stars')      
        ], align='center', variant='outline', radius='sm', use_container_width=True, index=None, color='#FF4B4B', key="viz_main_btn", on_change=on_viz_change)
        
        if st.session_state.viz_clicked == T['DNA']:
             viz.view_radar_details(radar_dict, st.session_state.username)
             st.session_state.viz_clicked = None
             
        elif st.session_state.viz_clicked == T['Map']: 
            all_nodes_list = msc.get_all_nodes_for_map(st.session_state.username)
            viz.view_fullscreen_map(all_nodes_list, st.session_state.nickname)
            st.session_state.viz_clicked = None

        st.divider()
        
        menu_items = [
            sac.MenuItem(T['AI'], icon='robot'),
            sac.MenuItem(T['Chat'], icon='chat-dots', tag=sac.Tag(str(total_unread), color='red') if total_unread > 0 else None),
            sac.MenuItem(T['World'], icon='globe-americas'), 
        ]
        if st.session_state.is_admin:
            menu_items.append(sac.MenuItem(T['God'], icon='eye-fill'))
        menu_items.append(sac.MenuItem(T['Sys'], type='group', children=[sac.MenuItem(T['Logout'], icon='box-arrow-right')]))

        selected_menu = sac.menu(menu_items, index=0, format_func='title', size='sm', variant='light', open_all=True)
        
        st.divider()
        lang_opts = ['EN', '中文']
        curr_idx = 0 if st.session_state.language == 'en' else 1
        lang_choice = sac.segmented(items=lang_opts, align='center', size='xs', index=curr_idx, key="sidebar_lang_selector")
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
