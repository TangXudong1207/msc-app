### msc_main.py ###
import streamlit as st
import streamlit_antd_components as sac
import msc_lib as msc
import msc_viz as viz
import msc_pages as pages
import json
import msc_soul_viz as soul_viz
import msc_i18n as i18n 
import time
import random
import msc_config as config 
from datetime import datetime

# ==========================================
# 🛠️ 配置与初始化
# ==========================================
APP_ICON_URL = "https://raw.githubusercontent.com/TangXudong1207/msc-app/main/app%E5%9B%BE%E6%A0%87.png"

st.set_page_config(
    page_title="MSC v75.5", 
    page_icon=APP_ICON_URL,
    layout="wide", 
    initial_sidebar_state="expanded"
)

# ==========================================
# 🎨 CSS：Cyber-Zen 极简主义设计系统
# ==========================================
def inject_custom_css():
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=JetBrains+Mono:wght@400;700&display=swap');
        
        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
            color: #2D3436;
            background-color: #FAFAFA;
        }}
        
        [data-testid="stDecoration"] {{ display: none !important; }}
        #MainMenu {{ visibility: hidden; }}
        footer {{ visibility: hidden; }}

        .stApp {{ background-color: #FAFAFA; }}
        
        [data-testid="stSidebar"] {{
            background-color: #FFFFFF;
            border-right: 1px solid #F0F0F0;
            box-shadow: 2px 0 10px rgba(0,0,0,0.02);
        }}
        
        .stButton > button {{
            width: 100%;
            border-radius: 6px;
            font-weight: 500;
            border: 1px solid #E0E0E0;
            background: #FFFFFF;
            color: #444;
            padding: 0.5rem 1rem;
            transition: all 0.2s;
            font-family: 'JetBrains Mono', monospace;
            font-size: 14px;
        }}
        .stButton > button:hover {{
            border-color: #FF4B4B;
            color: #FF4B4B;
            background: #FFF5F5;
            transform: translateY(-1px);
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        }}
        .stButton > button:active {{
            background: #FFE0E0;
            transform: translateY(0px);
        }}
        
        .chat-bubble-me {{
            background-color: #2D2D2D; color: #FFFFFF; padding: 14px 18px; border-radius: 2px; 
            border-bottom-right-radius: 12px; align-self: flex-end; max-width: 80%; 
            font-size: 15px; font-weight: 300; box-shadow: 0 2px 8px rgba(0,0,0,0.1); 
            position: relative; float: right; clear: both; margin-bottom: 8px;
        }}
        
        .chat-bubble-other {{
            background-color: #FFFFFF; color: #333; padding: 14px 18px; border-radius: 2px; 
            border-bottom-left-radius: 12px; border: 1px solid #EAEAEA; align-self: flex-start; 
            max-width: 80%; font-size: 15px; line-height: 1.6; box-shadow: 0 1px 4px rgba(0,0,0,0.03); 
            float: left; clear: both; margin-bottom: 8px;
        }}
        
        .chat-bubble-ai {{
            background: #F8F9FA; color: #666; border-left: 3px solid #00CCFF; padding: 12px 20px; 
            font-family: 'Inter', sans-serif; font-size: 0.9em; margin: 10px 0; width: 100%; 
            clear: both; border-radius: 0 4px 4px 0;
        }}
        
        .daily-card {{
            border: 1px solid #DDD; background: #F0F2F6; padding: 24px; border-radius: 4px; 
            text-align: center; margin-top: 10px; margin-bottom: 20px; 
            font-family: 'JetBrains Mono', monospace; font-size: 14px; color: #333; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }}
        .daily-label {{
            font-size: 10px; text-transform: uppercase; letter-spacing: 4px; color: #999; 
            margin-bottom: 16px; border-bottom: 1px solid #DDD; padding-bottom: 8px;
        }}
        
        .stToast {{ background-color: #333 !important; color: #fff !important; border-radius: 0px !important; }}
        code, .stCode, .monospaced {{ font-family: 'JetBrains Mono', monospace !important; }}
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# ==========================================
# ⚙️ 状态管理
# ==========================================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "is_admin" not in st.session_state: st.session_state.is_admin = False
if "current_chat_partner" not in st.session_state: st.session_state.current_chat_partner = None
if "language" not in st.session_state: st.session_state.language = "en" 

# ==========================================
# 📚 功能函数
# ==========================================
LOCAL_INSIGHTS = {
    "en": ["What constitutes the boundary of your self?", "Is silence a form of speech?"],
    "zh": ["构成你“自我”边界的究竟是什么？", "你此刻的沉默，是否也是一种表达？"]
}
def get_fallback_insight():
    lang = st.session_state.language
    return random.choice(LOCAL_INSIGHTS.get(lang, LOCAL_INSIGHTS['en']))

@st.dialog("⚡ DAILY INSIGHT")
def daily_insight_dialog(username, radar):
    if "daily_content" not in st.session_state or st.session_state.daily_content is None:
        with st.container():
            st.markdown("<div style='text-align:center; padding:20px; color:#888;'>Connecting to Void...</div>", unsafe_allow_html=True)
            with st.spinner(""):
                try:
                    insight = msc.generate_daily_question(username, radar)
                    if not insight or len(str(insight)) < 5: raise ValueError()
                    st.session_state.daily_content = insight
                except:
                    st.session_state.daily_content = get_fallback_insight()
            st.rerun()

    content = st.session_state.daily_content
    st.markdown(f"<div class='daily-card'><div class='daily-label'>REFLECTION PROTOCOL</div><div style='font-size: 1.2em; font-weight: 600; color: #222;'>{content}</div></div>", unsafe_allow_html=True)
    if st.button("Regenerate Signal", use_container_width=True):
        st.session_state.daily_content = None; st.rerun()

@st.dialog("📦 MEANING BOX", width="large")
def meaning_box_dialog(username):
    nodes = msc.get_all_nodes_for_map(username)
    if not nodes:
        st.info("No meaning collected yet.")
        return

    # 按时间倒序
    nodes = sorted(nodes, key=lambda x: x['id'], reverse=True)
    
    st.caption(f"Total Cards: {len(nodes)}")
    
    for n in nodes:
        with st.container(border=True):
            # 时间格式化
            ts = n.get('created_at', '')[:16].replace('T', ' ')
            
            c1, c2 = st.columns([0.2, 0.8])
            with c1:
                st.caption(ts)
                kw = n.get('keywords', [])
                if isinstance(kw, str): 
                    try: kw = json.loads(kw)
                    except: kw = []
                if kw: st.markdown(f"**#{kw[0]}**")
                
            with c2:
                # 核心意义点
                st.markdown(f"#### {n.get('care_point', 'Unknown')}")
                # AI Insight
                st.info(n.get('insight', ''))
                # 原文折叠
                with st.expander("Original Context / 原文"):
                    st.write(n.get('content', ''))

def check_and_send_first_contact(username):
    history = msc.get_active_chats(username)
    if not history:
        lang = st.session_state.language
        msg = "先说清楚一件事：\n这里就是一个和 AI 聊天的对话框。\n那就从最简单的开始吧——\n吃了吗？" if lang == 'zh' else "Let's start simple.\nHow is your day going?"
        msc.save_chat(username, "assistant", msg)

# --- 1. 登录注册 ---
if not st.session_state.logged_in:
    pages.render_login_page()

# --- 2. 主界面 ---
else:
    msc.update_heartbeat(st.session_state.username)
    my_nodes_list = list(msc.get_active_nodes_map(st.session_state.username).values())
    node_count = len(my_nodes_list)
    
    if node_count == 0 and not st.session_state.is_admin and "onboarding_complete" not in st.session_state:
        pages.render_onboarding(st.session_state.username); st.stop()
    
    if node_count == 0 and not st.session_state.is_admin:
        check_and_send_first_contact(st.session_state.username)

    user_profile = msc.get_user_profile(st.session_state.username)
    raw_radar = user_profile.get('radar_profile')
    radar_dict = json.loads(raw_radar) if isinstance(raw_radar, str) else (raw_radar or {k:3.0 for k in config.RADAR_AXES})
    
    total_unread, unread_counts = msc.get_unread_counts(st.session_state.username)
    lang = st.session_state.language

    MENU_TEXT = {
        "en": {"AI": "AI_PARTNER", "Chat": "SIGNAL_LINK", "World": "WORLD_LAYER", "God": "OVERSEER", "Sys": "SYSTEM", "Logout": "DISCONNECT", "Box": "MEANING BOX", "Ins": "INSIGHT"},
        "zh": {"AI": "AI 伴侣", "Chat": "信号频段", "World": "世界层", "God": "上帝视角", "Sys": "系统", "Logout": "断开连接", "Box": "意义盒子", "Ins": "每日洞察"}
    }
    T = MENU_TEXT[lang]

    # === 侧边栏 ===
    with st.sidebar:
        c_av, c_info = st.columns([0.25, 0.75])
        with c_av:
            rank_name, rank_icon = msc.calculate_rank(radar_dict)
            st.markdown(f"<div style='font-size:24px; text-align:center;'>{rank_icon}</div>", unsafe_allow_html=True)
        with c_info:
            st.markdown(f"**{st.session_state.nickname}**")
            st.caption(f"ID: {st.session_state.username} | {rank_name}")

        st.divider()

        # 功能按钮区
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button(f"⚡ {T['Ins']}", use_container_width=True):
                daily_insight_dialog(st.session_state.username, radar_dict)
        with col_btn2:
            # 🟢 新增：意义盒子按钮
            if st.button(f"📦 {T['Box']}", use_container_width=True):
                meaning_box_dialog(st.session_state.username)
        
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        soul_viz.render_soul_scene(radar_dict, my_nodes_list)
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

        st.divider()
        
        menu_items = [
            sac.MenuItem(T['AI'], icon='robot'),
            sac.MenuItem(T['Chat'], icon='chat-dots', tag=sac.Tag(str(total_unread), color='red') if total_unread > 0 else None),
            sac.MenuItem(T['World'], icon='globe-americas'), 
        ]
        
        if st.session_state.is_admin: menu_items.append(sac.MenuItem(T['God'], icon='eye-fill'))
        menu_items.append(sac.MenuItem(T['Sys'], type='group', children=[sac.MenuItem(T['Logout'], icon='box-arrow-right')]))

        selected_menu = sac.menu(menu_items, index=0, format_func='title', size='sm', variant='light', open_all=True)
        
        st.divider()
        
        lang_opts = ['EN', '中文']
        curr_idx = 0 if st.session_state.language == 'en' else 1
        lang_choice = sac.segmented(items=lang_opts, align='center', size='xs', index=curr_idx, key="sidebar_lang_selector")
        mapped_lang = 'en' if lang_choice == 'EN' else 'zh'
        if mapped_lang != st.session_state.language:
            st.session_state.language = mapped_lang; st.rerun()

    # === 页面路由 ===
    if selected_menu == T['Logout']: st.session_state.clear(); st.rerun()
    elif selected_menu == T['AI']: pages.render_ai_page(st.session_state.username)
    elif selected_menu == T['Chat']: pages.render_friends_page(st.session_state.username, unread_counts)
    elif selected_menu == T['World']: pages.render_world_page()
    elif selected_menu == T['God']: pages.render_admin_dashboard()
