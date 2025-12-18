### page_admin.py ###

import streamlit as st
import msc_lib as msc
import msc_viz as viz
import msc_sim as sim
import time
import pandas as pd
import json
import msc_db as db # 必须引入 DB 才能进行删除操作

def render_admin_dashboard():
    st.markdown("## 👁️ Overseer Terminal")
    st.caption("v75.5 Arrival / System Status: ONLINE")
    
    # 获取数据
    all_users = msc.get_all_users("admin")
    global_nodes = msc.get_global_nodes()
    
    # 顶部指标
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Citizens", len(all_users))
    k2.metric("Nodes", len(global_nodes))
    
    avg_care = 0
    if global_nodes:
        total_care = sum([float(n.get('logic_score', 0)) for n in global_nodes])
        avg_care = total_care / len(global_nodes)
    k3.metric("Avg. Meaning", f"{avg_care:.2f}")
    k4.metric("Engine", "Active")
    
    st.divider()
    
    # === 标签页导航 ===
    tabs = st.tabs(["🌍 Global Pulse", "🛠️ Genesis Engine", "👥 Citizen Registry", "🧬 Node Inspector", "⚠️ Logs"])
    
    # Tab 1: 地图
    with tabs[0]:
        c1, c2 = st.columns([0.7, 0.3])
        with c1:
            st.markdown("### 🌌 Real-time Connection Map")
            viz.render_cyberpunk_map(global_nodes, height="500px", is_fullscreen=False)
        with c2:
            st.markdown("### 🎨 Spectrum")
            st.info("Spectrum Analysis Module loading...")

    # Tab 2: 模拟器
    with tabs[1]:
        st.markdown("### ⚡ Genesis Protocol")
        c_gen1, c_gen2 = st.columns(2)
        with c_gen1:
            with st.container(border=True):
                st.markdown("#### 1. Summon Archetypes")
                count_sim = st.slider("Quantity", 1, 5, 2)
                if st.button("👥 Summon Virtual Citizens", use_container_width=True):
                    with st.spinner("Fabricating souls..."):
                        n = sim.create_virtual_citizens(count_sim)
                        st.success(f"Summoned {n} entities.")
                        time.sleep(1)
                        st.rerun()
        with c_gen2:
            with st.container(border=True):
                st.markdown("#### 2. Inject Thoughts")
                count_thought = st.slider("Thought Batch Size", 1, 3, 1)
                if st.button("💉 Inject Semantic Flow", use_container_width=True, type="primary"):
                    with st.status("Simulating neural activity...", expanded=True):
                        logs = sim.inject_thoughts(count_thought)
                        for log in logs: st.text(log)
    
    # Tab 3: 用户管理 (删除功能在这里！)
    with tabs[2]:
        # 分两列：左边看列表，右边删人
        c_list, c_action = st.columns([0.6, 0.4])
        
        with c_list:
            st.markdown("#### 📜 Registered Identities")
            if all_users:
                df = pd.DataFrame(all_users)
                st.dataframe(
                    df[['username', 'nickname', 'last_seen']], 
                    use_container_width=True, 
                    hide_index=True,
                    height=400
                )
            else:
                st.info("No citizens found.")

        with c_action:
            st.markdown("#### 🧨 Termination Protocol")
            # 放在一个红色边框的容器里
            with st.container(border=True):
                st.error("DANGER ZONE: Irreversible Action")
                
                # 1. 选择用户
                user_list = [u['username'] for u in all_users] if all_users else []
                target_user = st.selectbox("Select Target to Wipe", user_list, index=None, placeholder="Select identity...")
                
                # 2. 确认勾选
                confirm_nuke = st.checkbox(f"I confirm: Wipe '{target_user}'")
                
                # 3. 执行按钮
                if st.button("EXECUTE NUKE", type="primary", disabled=not (target_user and confirm_nuke)):
                    if target_user == "admin":
                        st.error("🚫 The Architect cannot be deleted.")
                    else:
                        with st.spinner("Erasing existence..."):
                            success, msg = db.nuke_user(target_user)
                            if success:
                                st.success(f"Target '{target_user}' eliminated.")
                                time.sleep(1.5)
                                st.rerun()
                            else:
                                st.error(f"Failed: {msg}")

    # Tab 4: 节点检查
    with tabs[3]:
        if global_nodes:
            debug_data = []
            for n in global_nodes:
                loc_str = "-"
                try:
                    l = json.loads(n.get('location')) if isinstance(n.get('location'), str) else n.get('location')
                    if l: loc_str = f"{l.get('city','Unknown')}"
                except: pass
                debug_data.append({"User": n['username'], "Content": n['content'], "Score": n.get('logic_score'), "Loc": loc_str})
            st.dataframe(pd.DataFrame(debug_data), use_container_width=True, height=500)
    
    # Tab 5: 日志
    with tabs[4]:
        st.markdown("### ⚠️ System Telemetry")
        if st.button("Refresh Logs"):
            st.rerun()
        
        try:
            logs = msc.get_system_logs(limit=50) # 调用 lib 里的接口
            if logs:
                st.dataframe(pd.DataFrame(logs), use_container_width=True)
            else:
                st.caption("No logs available.")
        except:
            st.caption("Log system not fully initialized.")
