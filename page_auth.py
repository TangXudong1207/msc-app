import streamlit as st
import streamlit_antd_components as sac
import msc_lib as msc
import time
import msc_i18n as i18n 

# ==========================================
# 🔐 登录页 (Browser-Friendly Edition)
# ==========================================
def render_login_page():
    # 注入登录页专用 CSS
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
        /* 调整表单按钮宽度，使其填满容器 */
        [data-testid="stForm"] button { 
            width: 100%; 
            border-radius: 4px;
            font-family: 'JetBrains Mono', monospace;
        }
    </style>
    """, unsafe_allow_html=True)

    # 1. 语言记忆逻辑 (基于 URL 参数)
    # 检查 URL 是否有 lang 参数
    qp = st.query_params
    url_lang = qp.get("lang", "en")
    
    # 如果 session 中还没有设置，就用 URL 的
    if "language" not in st.session_state:
        st.session_state.language = url_lang

    c1, c2, c3 = st.columns([1, 2, 1])
    
    with c2:
        st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
        
        # 语言切换器
        lang_options = ['English', '中文']
        # 根据当前 session 状态决定 index
        current_idx = 0 if st.session_state.language == 'en' else 1
        
        selected_lang_label = sac.segmented(
            items=lang_options, 
            align='center', size='xs', index=current_idx, key="login_lang_selector"
        )
        
        # 状态更新逻辑：同步到 URL，实现刷新不丢失
        new_lang_code = 'en' if selected_lang_label == 'English' else 'zh'
        if new_lang_code != st.session_state.language:
            st.session_state.language = new_lang_code
            st.query_params["lang"] = new_lang_code
            st.rerun()

        # 标题区域
        st.markdown("""
        <div style='text-align: center;'>
            <div class='login-title'>MSC</div>
            <div class='login-subtitle'>MEANING · STRUCTURE · CARE</div>
        </div>
        <div style='height: 40px;'></div>
        """, unsafe_allow_html=True)
        
        # 登录/注册 Tab
        with st.container(border=True):
            tab = sac.tabs([i18n.get_text('login_tab'), i18n.get_text('signup_tab')], align='center', size='md', variant='outline')
            st.write("") 

            if tab == i18n.get_text('login_tab'):
                # ✨ 核心修改：使用 st.form 包裹登录框
                # 这会让浏览器识别出这是一个登录表单，从而触发 "保存密码"
                with st.form(key="login_form", clear_on_submit=False):
                    u = st.text_input(i18n.get_text('identity'), placeholder="Username", label_visibility="collapsed")
                    p = st.text_input(i18n.get_text('key'), type='password', placeholder="Password", label_visibility="collapsed")
                    st.write("")
                    
                    # Form 内的提交按钮
                    submit_clicked = st.form_submit_button(i18n.get_text('connect'), type="primary")
                
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
                # 注册表单也用 st.form，提升体验
                with st.form(key="signup_form"):
                    nu = st.text_input(i18n.get_text('new_id'), label_visibility="collapsed", placeholder="Username")
                    np = st.text_input(i18n.get_text('new_pw'), type='password', label_visibility="collapsed", placeholder="Password")
                    nn = st.text_input(i18n.get_text('nick'), label_visibility="collapsed", placeholder="Display Name")
                    nc = st.selectbox(i18n.get_text('region'), ["China", "USA", "UK", "Other"], label_visibility="collapsed")
                    st.write("")
                    signup_clicked = st.form_submit_button(i18n.get_text('init'))
                
                if signup_clicked:
                    if msc.add_user(nu, np, nn, nc): 
                        st.success(i18n.get_text('created'))
                    else: 
                        st.error("Initialization Failed: User already exists.")

# ==========================================
# 🚀 新手引导：降临风格 (Arrival Aesthetic)
# ==========================================
def render_onboarding(username):
    # CSS: 极简主义，左对齐，打字机风格
    st.markdown("""
    <style>
        /* 隐藏侧边栏，营造全屏沉浸感 */
        [data-testid="stSidebar"] {display: none;}
        
        .stApp {
            background-color: #FAFAFA !important;
            color: #222 !important;
        }
        
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400&family=Noto+Serif+SC:wght@300;400;600&display=swap');
        
        /* 核心容器：左侧边框线，类似日志 */
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
            line-height: 2.4; /* 大行高，诗意 */
            color: #333;
            margin-bottom: 40px;
            white-space: pre-wrap; /* 保留换行 */
        }
        
        .highlight {
            background: #F0F0F0;
            padding: 2px 6px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9em;
            color: #000;
        }

        /* 极简按钮：纯文字链接感 */
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
            padding-left: 30px !important; /* 悬停右移效果 */
        }
        
    </style>
    """, unsafe_allow_html=True)
    
    if "onboarding_step" not in st.session_state: st.session_state.onboarding_step = 0
    step = st.session_state.onboarding_step
    
    # 使用列布局来控制内容宽度，但保持左对齐视觉
    c_space, c_content, c_right = st.columns([1, 6, 3])
    
    with c_content:
        # 🟢 Log 00: 欢迎
        if step == 0:
            st.markdown(f"""
            <div class='log-container'>
                <div class='log-header'>LOG: 000 // ARRIVAL</div>
                <div class='main-verse'>{i18n.get_text('s0_main').replace('<br>', '\n')}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            if st.button(f"/// {i18n.get_text('s0_btn')}", use_container_width=False):
                st.session_state.onboarding_step = 1
                st.rerun()

        # 🟢 Log 01: 观察
        elif step == 1:
            st.markdown(f"""
            <div class='log-container'>
                <div class='log-header'>LOG: 001 // PROTOCOL</div>
                <div class='main-verse'>{i18n.get_text('s1_main').replace('<br>', '\n')}
                <br><br><span class='highlight'>{i18n.get_text('s1_sub').replace('<br>', ' ')}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            if st.button(f"/// {i18n.get_text('s1_btn')}", use_container_width=False):
                st.session_state.onboarding_step = 2
                st.rerun()

        # 🟢 Log 02: 意义 (分支)
        elif step == 2:
            st.markdown(f"""
            <div class='log-container'>
                <div class='log-header'>LOG: 002 // FILTER</div>
                <div class='main-verse'>{i18n.get_text('s2_main').replace('<br>', '\n')}</div>
            </div>
            """, unsafe_allow_html=True)
            
            col_a, col_b = st.columns([1, 2])
            with col_a:
                if st.button(i18n.get_text('s2_btn1')):
                    st.session_state.onboarding_step = 3
                    st.rerun()
            with col_b:
                if st.button(i18n.get_text('s2_btn2')):
                    st.session_state.onboarding_step = 3
                    st.rerun()

        # 🟢 Log 03: AI 角色
        elif step == 3:
            st.markdown(f"""
            <div class='log-container'>
                <div class='log-header'>LOG: 003 // PARTNER</div>
                <div class='main-verse'>{i18n.get_text('s3_main').replace('<br>', '\n')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            if st.button(f"/// {i18n.get_text('s3_btn')}", use_container_width=False):
                st.session_state.onboarding_step = 4
                st.rerun()

        # 🟢 Log 04: 卡片 (分支)
        elif step == 4:
            st.markdown(f"""
            <div class='log-container'>
                <div class='log-header'>LOG: 004 // RECORD</div>
                <div class='main-verse'>{i18n.get_text('s4_main').replace('<br>', '\n')}</div>
            </div>
            """, unsafe_allow_html=True)
            
            col_a, col_b = st.columns([1, 2])
            with col_a:
                if st.button(i18n.get_text('s4_btn1')):
                    st.session_state.onboarding_step = 5
                    st.rerun()
            with col_b:
                if st.button(i18n.get_text('s4_btn2')):
                    st.session_state.onboarding_step = 5
                    st.rerun()

        # 🟢 Log 05: 社交
        elif step == 5:
            st.markdown(f"""
            <div class='log-container'>
                <div class='log-header'>LOG: 005 // CONNECT</div>
                <div class='main-verse'>{i18n.get_text('s5_main').replace('<br>', '\n')}
                <br><br><span class='highlight'>{i18n.get_text('s5_sub').replace('<br>', ' ')}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            if st.button(f"/// {i18n.get_text('s5_btn')}", use_container_width=False):
                st.session_state.onboarding_step = 6
                st.rerun()

        # 🟢 Log 06: 世界
        elif step == 6:
            st.markdown(f"""
            <div class='log-container'>
                <div class='log-header'>LOG: 006 // FOREST</div>
                <div class='main-verse'>{i18n.get_text('s6_main').replace('<br>', '\n')}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            if st.button(f"/// {i18n.get_text('s6_btn')}", use_container_width=False):
                st.session_state.onboarding_step = 7
                st.rerun()

        # 🟢 Log 07: 结束 (触发初始化)
        elif step == 7:
            st.markdown(f"""
            <div class='log-container'>
                <div class='log-header'>LOG: 007 // TRANSMIT</div>
                <div class='main-verse'>{i18n.get_text('s7_main').replace('<br>', '\n')}
                <br>{i18n.get_text('s7_sub').replace('<br>', ' ')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 真正的进入点
            st.write("")
            if st.button(f">>> {i18n.get_text('s7_btn')}", use_container_width=False, type="primary"):
                # 初始化默认数据
                msc.update_radar_score(username, {
                    "Reflection": 5.0, "Rationality": 5.0, "Curiosity": 5.0,
                    "Agency": 5.0, "Empathy": 5.0, "Care": 5.0
                })
                # 标记引导完成
                st.session_state.onboarding_complete = True
                st.rerun()
