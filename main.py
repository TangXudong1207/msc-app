import streamlit as st
import msc_lib as msc
import time
import json

st.set_page_config(page_title="MSC v31.0 Global", layout="wide", initial_sidebar_state="expanded")

if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌌 MSC 意义协作系统")
    tab1, tab2 = st.tabs(["登录", "注册"])
    with tab1:
        u = st.text_input("用户名")
        p = st.text_input("密码", type='password')
        if st.button("登录", use_container_width=True):
            res = msc.login_user(u, p)
            if res:
                st.session_state.logged_in = True
                st.session_state.username = u
                st.session_state.nickname = res[0]['nickname']
                st.session_state.messages = [] 
                st.rerun()
            else: st.error("错误")
    with tab2:
        nu = st.text_input("新用户名")
        np_pass = st.text_input("新密码", type='password')
        nn = st.text_input("昵称")
        if st.button("注册", use_container_width=True):
            if msc.add_user(nu, np_pass, nn): st.success("成功")
            else: st.error("失败")

else:
    chat_history = msc.get_active_chats(st.session_state.username)
    nodes_map = msc.get_active_nodes_map(st.session_state.username)
    all_nodes_list = msc.get_all_nodes_for_map(st.session_state.username)
    user_profile = msc.get_user_profile(st.session_state.username)
    
    raw_radar = user_profile.get('radar_profile')
    if isinstance(raw_radar, str): radar_dict = json.loads(raw_radar)
    else: radar_dict = raw_radar if raw_radar else {k:3.0 for k in ["Care", "Curiosity", "Reflection", "Coherence", "Empathy", "Agency", "Aesthetic"]}

    with st.sidebar:
        rank_name, rank_icon = msc.calculate_rank(radar_dict)
        st.markdown(f"## {rank_icon} {st.session_state.nickname}")
        msc.render_radar_chart(radar_dict)
        
        # 弹窗：画像
        @st.dialog("🧬 画像分析")
        def show_persona():
            if st.button("生成报告"):
                with st.spinner("分析中..."):
                    res = msc.analyze_persona_report(radar_dict)
                    st.write(res)
        if st.button("🧬 详细画像", use_container_width=True): show_persona()
        
        # 弹窗：MSC World
        @st.dialog("🌍 MSC World", width="large")
        def show_world():
            global_nodes = msc.get_global_nodes()
            t1, t2, t3 = st.tabs(["2D Earth", "3D Galaxy", "📡 全球脉动"])
            with t1: msc.render_2d_world_map(global_nodes)
            with t2: msc.render_3d_galaxy(global_nodes)
            with t3:
                # 🌟 新增：全球消息流
                st.caption("实时监听全球用户的思想脉搏...")
                global_stream = msc.get_global_stream()
                for g_msg in global_stream:
                    # 获取该用户的昵称（这里简化处理，直接显示用户名）
                    st.markdown(f"**👤 {g_msg['username']}**: {g_msg['content']}")
                    st.divider()

        if st.button("🌍 MSC World", use_container_width=True, type="primary"): show_world()
            
        # 弹窗：仿真
        @st.dialog("🧪 仿真实验室")
        def show_sim():
            topic = st.text_input("话题")
            if st.button("开始注入"):
                with st.spinner("造物中..."):
                    cnt, msg = msc.simulate_civilization(topic, 3)
                    if cnt > 0: st.success(msg)
                    else: st.error(msg)
        with st.expander("🧪 实验室"):
            if st.button("打开控制台"): show_sim()

        st.divider()
        msc.render_cyberpunk_map(all_nodes_list, height="200px")
        
        @st.dialog("🔭 全屏", width="large")
        def show_full_map():
            msc.render_cyberpunk_map(all_nodes_list, height="600px", is_fullscreen=True)
        if st.button("🔭 全屏", use_container_width=True): show_full_map()
        
        if st.button("退出"): st.session_state.logged_in = False; st.rerun()

    # 主对话逻辑
    st.subheader("💬 意义流")
    
    for msg in chat_history:
        col_chat, col_node = st.columns([0.65, 0.35], gap="small")
        with col_chat:
            c_msg, c_del = st.columns([0.9, 0.1])
            with c_msg:
                with st.chat_message(msg['role']): st.markdown(msg['content'], unsafe_allow_html=True)
            with c_del:
                if msg['role'] == 'user':
                    if st.button("✕", key=f"del_{msg['id']}"):
                        if msc.soft_delete_chat_and_node(msg['id'], msg['content'], st.session_state.username): st.rerun()

        with col_node:
            if msg['role'] == 'user' and msg['content'] in nodes_map:
                node = nodes_map[msg['content']]
                with st.expander(f"✨ {node['care_point']}", expanded=False):
                    st.caption(f"MLS Logic: {node.get('logic_score', 0.5)}")
                    st.markdown(f"**Insight:** {node['insight']}")
                    st.caption(f"Time: {node['created_at'][:16]}")

    if prompt := st.chat_input("输入..."):
        msc.save_chat(st.session_state.username, "user", prompt)
        
        full_history = chat_history + [{'role':'user', 'content':prompt}]
        stream = msc.get_normal_response(full_history)
        reply_text = st.write_stream(stream)
        msc.save_chat(st.session_state.username, "assistant", reply_text)
        
        with st.spinner("⚡ 分析中..."):
            analysis = msc.analyze_meaning_background(prompt)
            if analysis.get("valid", False):
                vec = msc.get_embedding(prompt)
                msc.save_node(st.session_state.username, prompt, analysis, "日常", vec)
                
                if "radar_scores" in analysis: 
                    msc.update_radar_score(st.session_state.username, analysis["radar_scores"])
                
                match = msc.find_resonance(vec, st.session_state.username, analysis)
                if match: 
                    st.toast(f"🔔 发现共鸣！", icon="⚡")
                
                msc.check_group_formation(analysis, vec, st.session_state.username)
                
        st.rerun()
