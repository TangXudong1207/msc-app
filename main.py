import streamlit as st
import streamlit_antd_components as sac
import msc_lib as msc
import msc_pages as pages # 🌟 引入新页面文件
import json

# ==========================================
# 🎨 CSS
# ==========================================
def inject_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        .stApp { background-color: #F0F2F5; font-family: 'Roboto', sans-serif; color: #1F1F1F; }
        
        /* 聊天气泡 */
        .chat-bubble-me {
            background-color: #95EC69; color: #000; padding: 10px 14px; 
            border-radius: 8px; border-top-right-radius: 2px; margin-bottom: 5px; 
            display: inline-block; float: right; clear: both; max-width: 80%;
            box-shadow: 0 1px 1px rgba(0,0,0,0.1);
        }
        .chat-bubble-other {
            background-color: #FFFFFF; color: #000; padding: 10px 14px; 
            border-radius: 8px; border-top-left-radius: 2px; margin-bottom: 5px; 
            display: inline-block; float: left; clear: both; border: 1px solid #eee; max-width: 80%;
        }
        .chat-bubble-ai {
            background-color: #E3F2FD; color: #0D47A1; padding: 8px 12px; border-radius: 12px;
            margin: 10px 40px; display: block; clear: both; text-align: center; font-size: 0.9em;
            border: 1px dashed #90CAF9;
        }
        
        /* 侧边栏 */
        [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #E0E0E0; }
        
        /* 每日追问 */
        .daily-card {
            background: linear-gradient(135deg, #e8f0fe 0%, #ffffff 100%);
            border: 1px solid #d2e3fc; border-radius: 12px; padding: 15px; 
            margin-bottom: 20px; text-align: center;
        }
    </style>
    """, unsafe_allow_html=True)

st.set_page_config(page_title="MSC v48.0 Modular", layout="wide", initial_sidebar_state="expanded")
inject_custom_css()

if "logged_in" not in st.session_state: st.session_state.logged_in = False

# --- 登录 ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        st.markdown("<br><h1 style='text-align: center; color: #1A73E8;'>🔷 MSC</h1>", unsafe_allow_html=True)
        tab = sac.tabs([sac.TabsItem('登录'), sac.TabsItem('注册')], align='center', variant='outline')
        if tab == '登录':
            u = st.text_input("账号")
            p = st.text_input("密码", type='password')
            if st.button("登录", use_container_width=True, type="primary"):
                res = msc.login_user(u, p)
                if res:
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.session_state.nickname = res[0]['nickname']
                    st.rerun()
                else: sac.alert("错误", color='red')
        else:
            nu = st.text_input("新账号")
            np = st.text_input("新密码", type='password')
            nn = st.text_input("昵称")
            if st.button("注册", use_container_width=True):
                if msc.add_user(nu, np, nn): sac.alert("成功", color='success')
                else: sac.alert("失败", color='error')

# --- 主界面 ---
else:
    # 心跳与通知
    msc.update_heartbeat(st.session_state.username)
    total_unread, unread_counts = msc.get_unread_counts(st.session_state.username)
    
    # 侧边栏数据
    user_profile = msc.get_user_profile(st.session_state.username)
    radar_dict = json.loads(user_profile.get('radar_profile')) if user_profile.get('radar_profile') else {}
    rank_name, rank_icon = msc.calculate_rank(radar_dict)

    with st.sidebar:
        st.markdown(f"### {rank_icon} {st.session_state.nickname}")
        
        # 每日追问
        if "daily_q" not in st.session_state: st.session_state.daily_q = None
        if st.session_state.daily_q is None:
            if st.button("📅 生成今日追问", use_container_width=True):
                with st.spinner("..."):
                    st.session_state.daily_q = msc.generate_daily_question(st.session_state.username, radar_dict)
                    st.rerun()
        else:
            st.markdown(f"<div class='daily-card'><small>DAILY Q</small><br>{st.session_state.daily_q}</div>", unsafe_allow_html=True)

        msc.render_radar_chart(radar_dict, height="180px")
        
        # 🌟 核心导航：四轨并行
        menu = sac.menu([
            sac.MenuItem('AI 伴侣', icon='robot'),
            sac.MenuItem('好友', icon='chat-dots', tag=sac.Tag(str(total_unread), color='red') if total_unread > 0 else None),
            sac.MenuItem('星团', icon='people'),
            sac.MenuItem('世界', icon='globe'),
            sac.MenuItem('系统', type='group', children=[sac.MenuItem('退出登录', icon='box-arrow-right')]),
        ], index=0, format_func='title', open_all=True)

        st.divider()
        if st.button("🔭 全屏星云", use_container_width=True): 
            all_nodes = msc.get_all_nodes_for_map(st.session_state.username)
            msc.view_fullscreen_map(all_nodes, st.session_state.nickname)

    # 🌟 路由分发：去不同的房间
    if menu == '退出登录': st.session_state.logged_in = False; st.rerun()
    
    elif menu == 'AI 伴侣':
        pages.render_ai_page(st.session_state.username)
        
    elif menu == '好友':
        pages.render_friends_page(st.session_state.username, unread_counts)
        
    elif menu == '星团':
        pages.render_cluster_page(st.session_state.username)
        
    elif menu == '世界':
        pages.render_world_page()
