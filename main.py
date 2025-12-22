### page_auth.py ###
import streamlit as st
import streamlit_antd_components as sac
import msc_lib as msc
import time
import msc_i18n as i18n 

# ==========================================
# 🔐 登录页
# ==========================================
def render_login_page():
    st.markdown("""
    <style>
        .login-title { 
            font-family: 'JetBrains Mono', monospace; 
            font-weight: 700; 
            font-size: 3em; 
            color: #333; 
        }
        .login-subtitle { 
            color: #888; 
            letter-spacing: 4px; 
            font-size: 0.8em; 
            margin-top: -10px; 
            font-weight: 300; 
        }
        [data-testid="stFormSubmitButton"] button { 
            border-radius: 4px !important;
            font-family: 'JetBrains Mono', monospace !important;
            background-color: #FF4B4B !important; 
            color: white !important;
            border: none !important;
            height: 45px !important;
            font-size: 14px !important;
            letter-spacing: 1px !important;
            font-weight: 600 !important;
            padding-left: 30px !important;
            padding-right: 30px !important;
        }
        [data-testid="stFormSubmitButton"] button:hover {
            background-color: #FF2B2B !important;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(255, 75, 75, 0.2);
        }
    </style>
    """, unsafe_allow_html=True)

    qp = st.query_params
    url_lang = qp.get("lang", "en")
    
    if "language" not in st.session_state:
        st.session_state.language = url_lang

    c1, c2, c3 = st.columns([1, 2, 1])
    
    with c2:
        st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
        
        lang_options = ['English', '中文']
        current_idx = 0 if st.session_state.language == 'en' else 1
        
        selected_lang_label = sac.segmented(
            items=lang_options, 
            align='center', size='xs', index=current_idx, key="login_lang_selector"
        )
        
        new_lang_code = 'en' if selected_lang_label == 'English' else 'zh'
        if new_lang_code != st.session_state.language:
            st.session_state.language = new_lang_code
            st.query_params["lang"] = new_lang_code
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
                with st.form(key="login_form", clear_on_submit=False):
                    u = st.text_input(i18n.get_text('identity'), placeholder="Username", label_visibility="collapsed")
                    p = st.text_input(i18n.get_text('key'), type='password', placeholder="Password", label_visibility="collapsed")
                    st.write("")
                    fc1, fc2, fc3 = st.columns([1, 2, 1])
                    with fc2:
                        submit_clicked = st.form_submit_button(i18n.get_text('connect'), use_container_width=True)
                
                if submit_clicked:
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
                    else: 
                        st.error(i18n.get_text('signal_lost'))
            else:
                with st.form(key="signup_form"):
                    nu = st.text_input(i18n.get_text('new_id'), label_visibility="collapsed", placeholder="Username")
                    np = st.text_input(i18n.get_text('new_pw'), type='password', label_visibility="collapsed", placeholder="Password")
                    nn = st.text_input(i18n.get_text('nick'), label_visibility="collapsed", placeholder="Display Name")
                    nc = st.selectbox(i18n.get_text('region'), ["China", "USA", "UK", "Other"], label_visibility="collapsed")
                    st.write("")
                    fc1, fc2, fc3 = st.columns([1, 2, 1])
                    with fc2:
                        signup_clicked = st.form_submit_button(i18n.get_text('init'), use_container_width=True)
                
                if signup_clicked:
                    if msc.add_user(nu, np, nn, nc): st.success(i18n.get_text('created'))
                    else: st.error("Initialization Failed")

# ==========================================
# 🚀 新手引导 (v2.0 Poetic Edition)
# ==========================================
def render_onboarding(username):
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .stApp { background-color: #FAFAFA !important; color: #222 !important; }
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400&family=Noto+Serif+SC:wght@300;400;600&display=swap');
        
        .log-container {
            border-left: 2px solid #E0E0E0; 
            padding-left: 24px; 
            margin-left: 20px; 
            margin-top: 50px;
            animation: fadeIn 1.2s ease-out;
        }
        @keyframes fadeIn { 
            0% { opacity: 0; margin-left: 10px; } 
            100% { opacity: 1; margin-left: 20px; } 
        }
        .log-header { 
            font-family: 'JetBrains Mono', monospace; 
            font-size: 0.75em; 
            color: #AAA; 
            letter-spacing: 2px; 
            margin-bottom: 20px; 
            text-transform: uppercase; 
        }
        .main-verse { 
            font-family: 'Noto Serif SC', serif; 
            font-size: 1.1em; 
            font-weight: 400; 
            line-height: 2.4; 
            color: #333; 
            margin-bottom: 40px; 
        }
        
        .stButton button { 
            background-color: transparent !important; 
            border: 1px solid #CCC !important; 
            color: #444 !important; 
            border-radius: 0px !important; 
            padding: 8px 24px !important; 
            font-family: 'JetBrains Mono', monospace !important; 
            font-size: 0.8em !important; 
            transition: all 0.3s !important; 
            text-transform: uppercase; 
            letter-spacing: 1px; 
            display: inline-block; 
        }
        .stButton button:hover { 
            border-color: #000 !important; 
            color: #000 !important; 
            background-color: #FFF !important; 
            padding-left: 30px !important; 
        }
    </style>
    """, unsafe_allow_html=True)
    
    if "onboarding_step" not in st.session_state: st.session_state.onboarding_step = 0
    step = st.session_state.onboarding_step
    
    c_space, c_content, c_right = st.columns([1, 6, 3])
    
    with c_content:
        # PAGE 1: SPACE
        if step == 0:
            st.markdown(f"<div class='log-container'><div class='log-header'>MSC // SPACE</div><div class='main-verse'>{i18n.get_text('s1_main')}</div></div>", unsafe_allow_html=True)
            st.write("")
            if st.button(f"> {i18n.get_text('s1_btn')}", use_container_width=False): 
                st.session_state.onboarding_step = 1; st.rerun()
        
        # PAGE 2: PEOPLE
        elif step == 1:
            st.markdown(f"<div class='log-container'><div class='log-header'>MSC // PEOPLE</div><div class='main-verse'>{i18n.get_text('s2_main')}</div></div>", unsafe_allow_html=True)
            st.write("")
            if st.button(f"> {i18n.get_text('s2_btn')}", use_container_width=False): 
                st.session_state.onboarding_step = 2; st.rerun()

        # PAGE 3: FUTURE (FINAL)
        elif step == 2:
            st.markdown(f"<div class='log-container'><div class='log-header'>MSC // FUTURE</div><div class='main-verse'>{i18n.get_text('s3_main')}</div></div>", unsafe_allow_html=True)
            st.write("")
            if st.button(f">> {i18n.get_text('s3_btn')}", use_container_width=False):
                # 初始化默认雷达数据
                msc.update_radar_score(username, {
                    "Reflection": 5.0, "Rationality": 5.0, "Curiosity": 5.0,
                    "Agency": 5.0, "Empathy": 5.0, "Care": 5.0, "Transcendence": 3.0
                })
                st.session_state.onboarding_complete = True
                st.rerun()
