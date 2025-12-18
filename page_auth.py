import streamlit as st
import streamlit_antd_components as sac
import msc_lib as msc
import time
import msc_i18n as i18n # 引用语言包

# ==========================================
# 🔐 登录页 (保持不变)
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
# 🚀 新手引导：降临 (The Arrival - Philosophy Ver.)
# ==========================================
def render_onboarding(username):
    # CSS: 极简主义，衬线体，呼吸感
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        
        .stApp {
            background-color: #FDFDFD !important; /* 雾白 */
            color: #2D3436 !important;
        }
        
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Noto+Serif+SC:wght@300;400;600&family=Lora:ital,wght@0,400;1,400&display=swap');
        
        .fade-in {
            animation: fadeIn 1.2s ease-in-out;
        }
        @keyframes fadeIn {
            0% { opacity: 0; transform: translateY(10px); }
            100% { opacity: 1; transform: translateY(0); }
        }

        .main-text {
            font-family: 'Noto Serif SC', 'Lora', serif;
            font-size: 1.6em;
            font-weight: 400;
            line-height: 1.8;
            text-align: center;
            color: #333;
            margin-bottom: 40px;
            letter-spacing: 1px;
        }
        
        .sub-text {
            font-family: 'Noto Serif SC', 'Lora', serif;
            font-size: 0.95em;
            font-weight: 300;
            line-height: 1.6;
            text-align: center;
            color: #888;
            margin-bottom: 60px;
            font-style: italic;
        }

        /* 按钮样式微调：更轻盈 */
        .stButton button {
            background-color: transparent !important;
            border: 1px solid #E0E0E0 !important;
            color: #555 !important;
            border-radius: 20px !important;
            padding: 8px 24px !important;
            transition: all 0.3s !important;
        }
        .stButton button:hover {
            border-color: #333 !important;
            color: #000 !important;
            background-color: #FAFAFA !important;
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
            st.markdown(
                """
                <div class='main-text'>
                欢迎。<br><br>
                这里不是催促你得出结论的地方。<br><br>
                更多时候，<br>
                我们只是把事情<br>
                放慢一点。
                </div>
                """, unsafe_allow_html=True
            )
            if st.button("继续", use_container_width=True):
                st.session_state.onboarding_step = 1
                st.rerun()

        # 🟢 Screen 1: MSC 的方式
        elif step == 1:
            st.markdown(
                """
                <div class='main-text'>
                你说话。<br><br>
                我们不急着回答。<br><br>
                我们先看看，<br>
                你在乎的是什么。
                </div>
                <div class='sub-text'>
                放心，<br>
                不会给你打分。
                </div>
                """, unsafe_allow_html=True
            )
            if st.button("下一步", use_container_width=True):
                st.session_state.onboarding_step = 2
                st.rerun()

        # 🟢 Screen 2: 关于意义
        elif step == 2:
            st.markdown(
                """
                <div class='main-text'>
                有些话<br>
                会慢慢变得重要。<br><br>
                有些不会。<br><br>
                这不是筛选。<br>
                只是时间<br>
                在做它该做的事。
                </div>
                <div class='sub-text'>
                你不用担心说错。<br>
                大多数时候，<br>
                意义只是<br>
                还没来。
                </div>
                """, unsafe_allow_html=True
            )
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("我明白了", use_container_width=True):
                    st.session_state.onboarding_step = 3
                    st.rerun()
            with col_b:
                if st.button("我再看看", use_container_width=True):
                    st.session_state.onboarding_step = 3
                    st.rerun()

        # 🟢 Screen 3: 关于 AI
        elif step == 3:
            st.markdown(
                """
                <div class='main-text'>
                我不会替你思考。<br><br>
                我只是<br>
                在你思考的时候，<br>
                把轮廓<br>
                放在一旁。
                </div>
                <div class='sub-text'>
                如果你觉得这些轮廓<br>
                并不准确，<br>
                忽略它们就好。<br><br>
                它们本来也不是结论。
                </div>
                """, unsafe_allow_html=True
            )
            if st.button("继续", use_container_width=True):
                st.session_state.onboarding_step = 4
                st.rerun()

        # 🟢 Screen 4: 关于意义卡
        elif step == 4:
            st.markdown(
                """
                <div class='main-text'>
                有些话<br>
                会变成一张卡片。<br><br>
                它们不会评判你。<br><br>
                只是记录：<br>
                你曾经在这里想过。
                </div>
                <div class='sub-text'>
                当然，<br>
                大多数话<br>
                什么也不会发生。
                </div>
                """, unsafe_allow_html=True
            )
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("很好", use_container_width=True):
                    st.session_state.onboarding_step = 5
                    st.rerun()
            with col_b:
                if st.button("有点残忍", use_container_width=True):
                    st.session_state.onboarding_step = 5
                    st.rerun()

        # 🟢 Screen 5: 关于他人
        elif step == 5:
            st.markdown(
                """
                <div class='main-text'>
                你不会被推着社交。<br><br>
                也不会被突然配对。<br><br>
                如果有人靠近你，<br>
                通常是因为<br>
                你们在乎过<br>
                相似的东西。
                </div>
                <div class='sub-text'>
                是的，<br>
                这比“兴趣相同”<br>
                麻烦一点。
                </div>
                """, unsafe_allow_html=True
            )
            if st.button("继续", use_container_width=True):
                st.session_state.onboarding_step = 6
                st.rerun()

        # 🟢 Screen 6: 关于世界
        elif step == 6:
            st.markdown(
                """
                <div class='main-text'>
                当你积累了一些意义卡，<br><br>
                你会看到一个世界。<br><br>
                那不是新闻，<br>
                也不是发生了什么。<br><br>
                更像是——<br>
                你在乎的东西<br>
                在这里亮了起来。
                </div>
                <div class='sub-text'>
                有些地方<br>
                会一直模糊。<br><br>
                那也很正常。
                </div>
                """, unsafe_allow_html=True
            )
            if st.button("继续", use_container_width=True):
                st.session_state.onboarding_step = 7
                st.rerun()

        # 🟢 Screen 7: 结束
        elif step == 7:
            st.markdown(
                """
                <div class='main-text'>
                你可以现在就说点什么。<br><br>
                也可以什么都不说。<br><br>
                MSC 都不会介意。
                </div>
                <div class='sub-text'>
                毕竟，<br>
                意义这件事，<br>
                从来不是强求来的。
                </div>
                """, unsafe_allow_html=True
            )
            
            # 这里是真正的进入点
            if st.button("开始对话", use_container_width=True, type="primary"):
                # 初始化用户数据（如果还没初始化）
                # 这里简单给一个默认雷达，因为新引导流程不再做性格测试
                msc.update_radar_score(username, {
                    "Reflection": 5.0, "Rationality": 5.0, "Curiosity": 5.0,
                    "Agency": 5.0, "Empathy": 5.0, "Care": 5.0
                })
                
                st.session_state.onboarding_complete = True
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True) # End fade-in
