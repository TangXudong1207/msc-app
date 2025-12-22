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

        /* 🔴 核心修复：删除了隐藏 Header 的代码，以便能找回侧边栏 */
        /* header[data-testid="stHeader"] {{ visibility: hidden !important; height: 0 !important; }} */
        
        [data-testid="stDecoration"] {{ display: none !important; }}
        #MainMenu {{ visibility: hidden; }}
        footer {{ visibility: hidden; }}

        .stApp {{ background-color: #FAFAFA; }}
        
        [data-testid="stSidebar"] {{
            background-color: #FFFFFF;
            border-right: 1px solid #F0F0F0;
            box-shadow: 2px 0 10px rgba(0,0,0,0.02);
        }}
        
        /* 🛠️ 核心修改：美化原生 st.button，使其看起来像卡片 */
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
        
        /* 每日洞察卡片 */
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

# 执行 CSS 注入
inject_custom_css()

# ==========================================
# ⚙️ 状态管理
# ==========================================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "is_admin" not in st.session_state: st.session_state.is_admin = False
if "current_chat_partner" not in st.session_state: st.session_state.current_chat_partner = None
if "language" not in st.session_state: st.session_state.language = "en" 

# ==========================================
# 📚 本地备选语录库 (Fallback)
# ==========================================
LOCAL_INSIGHTS = {
    "en": [
        "What constitutes the boundary of your self?",
        "Is your current silence a form of speech?",
        "If memory is a vector, where is it pointing now?",
        "Are you observing the world, or is the world observing you?"
    ],
    "zh": [
        "构成你“自我”边界的究竟是什么？",
        "你此刻的沉默，是否也是一种表达？",
        "如果记忆是一个向量，它现在指向哪里？",
        "是你正在观察世界，还是世界正在观察你？"
    ]
}

def get_fallback_insight():
    lang = st.session_state.language
    pool = LOCAL_INSIGHTS.get(lang, LOCAL_INSIGHTS['en'])
    return random.choice(pool)

# ==========================================
# 🔭 每日洞察弹窗
# ==========================================
@st.dialog("⚡ DAILY INSIGHT")
def daily_insight_dialog(username, radar):
    # 确保有内容可显示
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

# ==========================================
# 🆕 首次接触逻辑
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

    my_nodes_list = list(msc.get_active_nodes_map(st.session_state.username).values())
    node_count = len(my_nodes_list)
    
    # 引导检查
    if node_count == 0 and not st.session_state.is_admin and "onboarding_complete" not in st.session_state:
        pages.render_onboarding(st.session_state.username)
        st.stop()
    
    # 首次进入自动发送消息
    if node_count == 0 and not st.session_state.is_admin:
        check_and_send_first_contact(st.session_state.username)

    user_profile = msc.get_user_profile(st.session_state.username)
    raw_radar = user_profile.get('radar_profile')
    if isinstance(raw_radar, str): radar_dict = json.loads(raw_radar)
    else: 
        radar_dict = raw_radar if raw_radar else {k:3.0 for k in config.RADAR_AXES}
    
    total_unread, unread_counts = msc.get_unread_counts(st.session_state.username)
    lang = st.session_state.language

    # 翻译字典
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

        # 1. 每日一问按钮 (使用最稳定的原生 st.button)
        # 通过 CSS 美化成了白色卡片样式
        if st.button(f"⚡ {T['Ins']}", use_container_width=True):
            daily_insight_dialog(st.session_state.username, radar_dict)
        
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        soul_viz.render_soul_scene(radar_dict, my_nodes_list)
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        
        # 2. 可视化工具栏 (原生 st.button)
        col_viz1, col_viz2 = st.columns(2)
        with col_viz1:
            if st.button(f"🧬 {T['DNA']}", use_container_width=True):
                viz.view_radar_details(radar_dict, st.session_state.username)
        with col_viz2:
            if st.button(f"🔭 {T['Map']}", use_container_width=True):
                all_nodes_list = msc.get_all_nodes_for_map(st.session_state.username)
                viz.view_fullscreen_map(all_nodes_list, st.session_state.nickname)

        st.divider()
        
        # 核心菜单 (导航保留 sac.menu，因为它适合做 Tab 切换)
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
        
        # 语言切换
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
            
        # 📱 移动端安装引导 (折叠在最下方)
        st.divider()
        with st.expander("📲 Install App / 安装到桌面"):
            st.caption("Add to Home Screen for fullscreen mode.")
            if lang == 'zh':
                st.markdown("""
                **iOS (Safari):**
                1. 点击分享按钮 <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Apple_Share_Icon.png/640px-Apple_Share_Icon.png" width="12"/>
                2. 选择 **“添加到主屏幕”**
                
                **Android (Chrome):**
                1. 点击菜单 (⋮)
                2. 选择 **“安装应用”** 或 **“添加到主屏幕”**
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                **iOS (Safari):**
                1. Click Share <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Apple_Share_Icon.png/640px-Apple_Share_Icon.png" width="12"/>
                2. Select **'Add to Home Screen'**
                
                **Android:**
                1. Click Menu (⋮)
                2. Select **'Install App'**
                """, unsafe_allow_html=True)

    # === 页面路由 ===
    if selected_menu == T['Logout']: 
        st.session_state.clear()
        st.rerun()
    elif selected_menu == T['AI']: pages.render_ai_page(st.session_state.username)
    elif selected_menu == T['Chat']: pages.render_friends_page(st.session_state.username, unread_counts)
    elif selected_menu == T['World']: pages.render_world_page()
    elif selected_menu == T['God']: pages.render_admin_dashboard()
