### page__admin.py ###

import streamlit as st
import msc_lib as msc
import msc_viz as viz
import msc_sim as sim
import time
import pandas as pd
import json
import msc_db as db 

def render_admin_dashboard():
    st.markdown("## 👁️ Overseer Terminal")
    st.caption("v75.5 Arrival / System Status: ONLINE")
    
    # 获取数据
    all_users = msc.get_all_users("admin")
    global_nodes = msc.get_global_nodes() # 这里现在获取 500 条
    
    # === 📊 数据预处理：计算用户画像 ===
    user_stats = {}
    if all_users:
        for u in all_users:
            user_stats[u['username']] = {'nodes': 0, 'total_score': 0.0}
            
    if global_nodes:
        for n in global_nodes:
            un = n['username']
            if un in user_stats:
                user_stats[un]['nodes'] += 1
                try: user_stats[un]['total_score'] += float(n.get('logic_score', 0))
                except: pass

    # 生成增强版表格数据
    rich_user_data = []
    if all_users:
        for u in all_users:
            stats = user_stats.get(u['username'], {'nodes':0, 'total_score':0})
            avg = stats['total_score'] / stats['nodes'] if stats['nodes'] > 0 else 0
            rich_user_data.append({
                "User": u['username'],
                "Nick": u['nickname'],
                "Nodes": stats['nodes'],
                "Avg Score": round(avg, 2),
                "Last Seen": u['last_seen'][:16].replace('T', ' ')
            })
    
    # 顶部指标
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Citizens", len(all_users))
    k2.metric("Nodes", len(global_nodes))
    
    avg_sys_care = 0
    if global_nodes:
        total = sum([float(n.get('logic_score', 0)) for n in global_nodes])
        avg_sys_care = total / len(global_nodes)
    k3.metric("Avg. Meaning", f"{avg_sys_care:.2f}")
    k4.metric("Engine", "Active")
    
    st.divider()
    
    tabs = st.tabs(["👥 Registry & Spy", "🌍 Global Pulse", "🛠️ Genesis", "⚠️ Logs"])
    
    # === Tab 1: 用户管理 + 聊天侦探 ===
    with tabs[0]:
        c_list, c_action = st.columns([0.65, 0.35])
        
        with c_list:
            st.markdown("#### 📜 Citizen Stats")
            if rich_user_data:
                # 按照节点数降序排列，方便看到活跃用户
                df = pd.DataFrame(rich_user_data).sort_values(by="Nodes", ascending=False)
                st.dataframe(
                    df, 
                    use_container_width=True, 
                    hide_index=True,
                    height=400,
                    column_config={
                        "Nodes": st.column_config.ProgressColumn("Nodes", min_value=0, max_value=50, format="%d"),
                        "Avg Score": st.column_config.NumberColumn("Avg Score", format="%.2f")
                    }
                )
            else:
                st.info("No citizens found.")

        with c_action:
            # === 删除模块 ===
            st.markdown("#### 🧨 Termination")
            with st.container(border=True):
                user_list = [u['username'] for u in all_users] if all_users else []
                target_user = st.selectbox("Target", user_list, index=None, placeholder="Select to Wipe...")
                confirm_nuke = st.checkbox(f"Confirm Wipe")
                
                if st.button("EXECUTE NUKE", type="primary", disabled=not (target_user and confirm_nuke)):
                    if target_user == "admin":
                        st.error("Cannot delete Architect.")
                    else:
                        with st.spinner("Erasing..."):
                            success, msg = db.nuke_user(target_user)
                            if success:
                                st.success(f"Eliminated.")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(f"Failed: {msg}")
            
            # === 🕵️ 聊天侦探模块 (Chat Spy) ===
            st.markdown("#### 🕵️ Chat Spy")
            with st.container(border=True):
                spy_user = st.selectbox("Inspect User", user_list, index=None, placeholder="View Chats...")
                if spy_user:
                    # 获取该用户的最后 10 条消息
                    chats = msc.get_active_chats(spy_user) 
                    if chats:
                        st.caption(f"Last 10 messages from {spy_user}:")
                        for msg in chats[:10]:
                            role_icon = "👤" if msg['role'] == 'user' else "🤖"
                            st.markdown(f"**{role_icon}**: {msg['content']}")
                            st.divider()
                    else:
                        st.caption("No chat history.")

    # Tab 2: 地图与节点
    with tabs[1]:
        c1, c2 = st.columns([0.7, 0.3])
        with c1:
            viz.render_cyberpunk_map(global_nodes, height="500px", is_fullscreen=False)
        with c2:
            st.markdown("### 🧬 Inspector")
            if global_nodes:
                debug_data = []
                for n in global_nodes:
                    debug_data.append({"User": n['username'], "Content": n['content'], "Score": n.get('logic_score')})
                st.dataframe(pd.DataFrame(debug_data), use_container_width=True, height=450)

    # Tab 3: 模拟器
    with tabs[2]:
        c_gen1, c_gen2 = st.columns(2)
        with c_gen1:
            with st.container(border=True):
                st.markdown("#### Summon Archetypes")
                count_sim = st.slider("Quantity", 1, 5, 2)
                if st.button("👥 Summon", use_container_width=True):
                    with st.spinner("Fabricating..."):
                        sim.create_virtual_citizens(count_sim)
                        st.rerun()
        with c_gen2:
            with st.container(border=True):
                st.markdown("#### Inject Thoughts")
                count_thought = st.slider("Batch Size", 1, 3, 1)
                if st.button("💉 Inject", use_container_width=True, type="primary"):
                    with st.status("Simulating...", expanded=True):
                        logs = sim.inject_thoughts(count_thought)
                        for log in logs: st.text(log)
    
    # Tab 4: 日志
    with tabs[3]:
        if st.button("Refresh Logs"): st.rerun()
        try:
            logs = msc.get_system_logs(limit=50)
            if logs: st.dataframe(pd.DataFrame(logs), use_container_width=True)
            else: st.caption("No logs available.")
        except: st.caption("Log system unavailable.")
