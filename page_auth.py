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
# 🚀 新手引导：降临
# ==========================================
def render_onboarding(username):
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .stApp { background-color: #F7F9FB !important; color: #2D3436 !important; }
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Lora:ital,wght@0,400;1,400&display=swap');
        .arrival-card { background: #FFFFFF; padding: 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); border: 1px solid #EAEAEA; margin-top: 5vh; }
        .arrival-title { font-family: 'Cinzel', serif; font-size: 2.2em; text-align: center; color: #333; margin-bottom: 10px; font-weight: 700; }
        .arrival-subtitle { font-family: 'Lora', serif; font-size: 1.1em; text-align: center; color: #666; margin-bottom: 30px; font-style: italic; }
        .arrival-text { font-family: 'Lora', serif; font-size: 1.05em; text-align: center; color: #444; line-height: 1.8; margin-bottom: 30px; }
        .stTextInput > div > div > input { background-color: #FAFAFA !important; color: #333 !important; border: 1px solid #DDD !important; text-align: center; font-family: 'Lora', serif; font-size: 1.1em; padding: 10px; border-radius: 6px; }
        .step-dots { text-align:center; margin-top:30px; color:#CCC; letter-spacing:8px;}
        .active-dot { color: #333; font-weight:bold; }
        .hint-text { font-size: 0.85em; color: #888; text-align: center; margin-top: 8px; }
    </style>
    """, unsafe_allow_html=True)
    
    if "onboarding_step" not in st.session_state: st.session_state.onboarding_step = 0
    step = st.session_state.onboarding_step
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<div class='arrival-card'>", unsafe_allow_html=True)
        
        if step == 0:
            st.markdown(f"<div class='arrival-title'>{i18n.get_text('ob_0_title')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='arrival-subtitle'>{i18n.get_text('ob_0_sub')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='arrival-text'>{i18n.get_text('ob_0_text')}</div>", unsafe_allow_html=True)
            anchor = st.text_input("SIGNAL INPUT", placeholder=i18n.get_text('ob_0_ph'), label_visibility="collapsed")
            st.markdown(f"<div class='hint-text'>{i18n.get_text('ob_0_hint')}</div>", unsafe_allow_html=True)
            st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
            if anchor:
                if st.button(i18n.get_text('ob_btn'), use_container_width=True, type="primary"):
                    with st.spinner("Parsing Soul Data..."):
                        analysis = msc.analyze_meaning_background(anchor)
                        vec = msc.get_embedding(anchor)
                        analysis['valid'] = True
                        if "care_point" not in analysis: analysis['care_point'] = "First Spark"
                        msc.save_node(username, anchor, analysis, "Genesis", vec)
                        if "radar_scores" in analysis: msc.update_radar_score(username, analysis["radar_scores"])
                        time.sleep(1.0) 
                    st.session_state.onboarding_step = 1
                    st.rerun()
            st.markdown("<div class='step-dots'><span class='active-dot'>●</span> ○ ○</div>", unsafe_allow_html=True)

        elif step == 1:
            st.markdown(f"<div class='arrival-title'>{i18n.get_text('ob_1_title')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='arrival-subtitle'>{i18n.get_text('ob_1_sub')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='arrival-text'>{i18n.get_text('ob_1_text')}</div>", unsafe_allow_html=True)
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button(i18n.get_text('ob_1_a'), use_container_width=True):
                    msc.update_radar_score(username, {"Reflection": 7.0, "Rationality": 6.0, "Curiosity": 5.0})
                    st.session_state.onboarding_step = 2
                    st.rerun()
                st.markdown(f"<div class='hint-text'>{i18n.get_text('ob_1_a_hint')}</div>", unsafe_allow_html=True)
            with col_b:
                if st.button(i18n.get_text('ob_1_b'), use_container_width=True):
                    msc.update_radar_score(username, {"Agency": 7.0, "Conflict": 5.0, "Empathy": 4.0})
                    st.session_state.onboarding_step = 2
                    st.rerun()
                st.markdown(f"<div class='hint-text'>{i18n.get_text('ob_1_b_hint')}</div>", unsafe_allow_html=True)
            st.markdown("<div class='step-dots'>○ <span class='active-dot'>●</span> ○</div>", unsafe_allow_html=True)

        elif step == 2:
            st.markdown(f"<div class='arrival-title'>{i18n.get_text('ob_2_title')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='arrival-subtitle'>{i18n.get_text('ob_2_sub')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='arrival-text'>{i18n.get_text('ob_2_text')}</div>", unsafe_allow_html=True)
            st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
            if st.button(i18n.get_text('ob_enter'), type="primary", use_container_width=True):
                st.session_state.onboarding_complete = True
                st.rerun()
            st.markdown("<div class='step-dots'>○ ○ <span class='active-dot'>●</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
