import streamlit as st
import streamlit_antd_components as sac
import msc_lib as msc
import time
import msc_i18n as i18n # 引用语言包

# ==========================================
# 🔐 登录页
# ==========================================
def render_login_page():
    st.markdown("""
    <style>
        .login-title { font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 3em; color: #333; }
        .login-subtitle { color: #888; letter-spacing: 4px; font-size: 0.8em; margin-top: -10px; font-weight: 300; }
        .stButton button { font-family: 'Inter', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 2, 1])
    
    with c2:
        st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
        
        # 语言切换
        if "language" not in st.session_state: st.session_state.language = "en"
        lang_options = ['English', '中文']
        current_idx = 0 if st.session_state.language == 'en' else 1
        
        selected_lang_label = sac.segmented(
            items=lang_options, 
            align='center', size='xs', index=current_idx, key="login_lang_selector"
        )
        
        new_lang_code = 'en' if selected_lang_label == 'English' else 'zh'
        if new_lang_code != st.session_state.language:
            st.session_state.language = new_lang_code
            st.rerun()

        st.markdown("""
        <div style='text-align: center;'>
            <div class='login-title'>MSC</div>
            <div class='login-subtitle'>MEANING · STRUCTURE · CARE</div>
        </div>
        <div style='height: 40px;'></div>
        """, unsafe_allow_html=True)
        
        with st.container(border=True):
            tab = sac.tabs([i18n.get_text('login_tab'), i18n.get_text('signup_tab')], align='center', size='md', variant='outline')
            st.write("") 

            if tab == i18n.get_text('login_tab'):
                u = st.text_input(i18n.get_text('identity'), placeholder="Username", label_visibility="collapsed")
                p = st.text_input(i18n.get_text('key'), type='password', placeholder="Password", label_visibility="collapsed")
                st.write("")
                if st.button(i18n.get_text('connect'), use_container_width=True, type="primary"):
                    if u == "admin" and p == "msc": 
                        st.session_state.logged_in = True
                        st.session_state.username = "admin"
                        st.session_state.nickname = "The Architect"
                        st.session_state.is_admin = True 
                        st.toast("👑 Architect Mode Activated")
                        time.sleep(0.5)
                        st.rerun()
                    elif msc.login_user(u, p):
                        st.session_state.logged_in = True
                        st.session_state.username = u
                        st.session_state.nickname = msc.get_nickname(u)
                        st.session_state.is_admin = False 
                        st.rerun()
                    else: st.error(i18n.get_text('signal_lost'))
            else:
                nu = st.text_input(i18n.get_text('new_id'), label_visibility="collapsed", placeholder="Username")
                np = st.text_input(i18n.get_text('new_pw'), type='password', label_visibility="collapsed", placeholder="Password")
                nn = st.text_input(i18n.get_text('nick'), label_visibility="collapsed", placeholder="Display Name")
                nc = st.selectbox(i18n.get_text('region'), ["China", "USA", "UK", "Other"], label_visibility="collapsed")
                st.write("")
                if st.button(i18n.get_text('init'), use_container_width=True):
                    if msc.add_user(nu, np, nn, nc): st.success(i18n.get_text('created'))
                    else: st.error("Initialization Failed")

# ==========================================
# 🚀 新手引导：降临 (The Arrival - Refined)
# ==========================================
def render_onboarding(username):
    # CSS: 极致的克制与留白
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        
        .stApp {
            background-color: #F8F9FA !important; /* 极淡的灰白 */
            color: #444 !important;
        }
        
        /* 引入衬线体，营造文学感 */
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Noto+Serif+SC:wght@300;400;600&family=Lora:ital,wght@0,400;1,400&display=swap');
        
        .fade-in {
            animation: fadeIn 1.0s ease-out;
        }
        @keyframes fadeIn {
            0% { opacity: 0; transform: translateY(8px); }
            100% { opacity: 1; transform: translateY(0); }
        }

        .main-text {
            font-family: 'Noto Serif SC', 'Lora', serif;
            font-size: 1.15em;     /* 缩小字号，精致化 */
            font-weight: 400;
            line-height: 2.2;      /* 增加行高，呼吸感 */
            text-align: center;
            color: #333;
            margin-bottom: 30px;
            letter-spacing: 1.5px; /* 增加字间距 */
        }
        
        .sub-text {
            font-family: 'Noto Serif SC', 'Lora', serif;
            font-size: 0.85em;    /* 极小的副标题 */
            font-weight: 300;
            line-height: 1.8;
            text-align: center;
            color: #999;          /* 极淡的灰色 */
            margin-bottom: 50px;
            font-style: italic;
        }

        /* 按钮：极简线框 */
        .stButton button {
            background-color: transparent !important;
            border: 1px solid #DDD !important;
            color: #666 !important;
            border-radius: 4px !important;
            padding: 6px 20px !important;
            font-size: 0.85em !important;
            font-family: 'Inter', sans-serif !important;
            transition: all 0.3s !important;
        }
        .stButton button:hover {
            border-color: #333 !important;
            color: #000 !important;
            background-color: #FFF !important;
        }
        .stButton button:active {
            transform: scale(0.98);
        }
    </style>
    """, unsafe_allow_html=True)
    
    if "onboarding_step" not in st.session_state: st.session_state.onboarding_step = 0
    step = st.session_state.onboarding_step
    
    # 垂直居中容器
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<div style='height: 15vh;'></div>", unsafe_allow_html=True)
        
        # 容器类
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)

        # 🟢 Screen 0: 欢迎
        if step == 0:
            st.markdown(f"<div class='main-text'>{i18n.get_text('s0_main')}</div>", unsafe_allow_html=True)
            if st.button(i18n.get_text('s0_btn'), use_container_width=True):
                st.session_state.onboarding_step = 1
                st.rerun()

        # 🟢 Screen 1: MSC 的方式
        elif step == 1:
            st.markdown(f"<div class='main-text'>{i18n.get_text('s1_main')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='sub-text'>{i18n.get_text('s1_sub')}</div>", unsafe_allow_html=True)
            if st.button(i18n.get_text('s1_btn'), use_container_width=True):
                st.session_state.onboarding_step = 2
                st.rerun()

        # 🟢 Screen 2: 关于意义
        elif step == 2:
            st.markdown(f"<div class='main-text'>{i18n.get_text('s2_main')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='sub-text'>{i18n.get_text('s2_sub')}</div>", unsafe_allow_html=True)
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button(i18n.get_text('s2_btn1'), use_container_width=True):
                    st.session_state.onboarding_step = 3
                    st.rerun()
            with col_b:
                if st.button(i18n.get_text('s2_btn2'), use_container_width=True):
                    st.session_state.onboarding_step = 3
                    st.rerun()

        # 🟢 Screen 3: 关于 AI
        elif step == 3:
            st.markdown(f"<div class='main-text'>{i18n.get_text('s3_main')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='sub-text'>{i18n.get_text('s3_sub')}</div>", unsafe_allow_html=True)
            if st.button(i18n.get_text('s3_btn'), use_container_width=True):
                st.session_state.onboarding_step = 4
                st.rerun()

        # 🟢 Screen 4: 关于意义卡
        elif step == 4:
            st.markdown(f"<div class='main-text'>{i18n.get_text('s4_main')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='sub-text'>{i18n.get_text('s4_sub')}</div>", unsafe_allow_html=True)
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button(i18n.get_text('s4_btn1'), use_container_width=True):
                    st.session_state.onboarding_step = 5
                    st.rerun()
            with col_b:
                if st.button(i18n.get_text('s4_btn2'), use_container_width=True):
                    st.session_state.onboarding_step = 5
                    st.rerun()

        # 🟢 Screen 5: 关于他人
        elif step == 5:
            st.markdown(f"<div class='main-text'>{i18n.get_text('s5_main')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='sub-text'>{i18n.get_text('s5_sub')}</div>", unsafe_allow_html=True)
            if st.button(i18n.get_text('s5_btn'), use_container_width=True):
                st.session_state.onboarding_step = 6
                st.rerun()

        # 🟢 Screen 6: 关于世界
        elif step == 6:
            st.markdown(f"<div class='main-text'>{i18n.get_text('s6_main')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='sub-text'>{i18n.get_text('s6_sub')}</div>", unsafe_allow_html=True)
            if st.button(i18n.get_text('s6_btn'), use_container_width=True):
                st.session_state.onboarding_step = 7
                st.rerun()

        # 🟢 Screen 7: 结束
        elif step == 7:
            st.markdown(f"<div class='main-text'>{i18n.get_text('s7_main')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='sub-text'>{i18n.get_text('s7_sub')}</div>", unsafe_allow_html=True)
            
            # 这里是真正的进入点
            if st.button(i18n.get_text('s7_btn'), use_container_width=True):
                # 初始化用户数据
                msc.update_radar_score(username, {
                    "Reflection": 5.0, "Rationality": 5.0, "Curiosity": 5.0,
                    "Agency": 5.0, "Empathy": 5.0, "Care": 5.0
                })
                st.session_state.onboarding_complete = True
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True) # End fade-in
