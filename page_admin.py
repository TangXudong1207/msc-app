### page__admin.py ###

import streamlit as st
import msc_lib as msc
import msc_viz as viz
import msc_sim as sim
import time
import pandas as pd
import json
import msc_db as db # 引入 DB 以调用核打击函数

def render_admin_dashboard():
    st.markdown("## 👁️ Overseer Terminal")
    st.caption("v75.5 Arrival / System Status: ONLINE")
    
    all_users = msc.get_all_users("admin")
    global_nodes = msc.get_global_nodes()
    
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
    tabs = st.tabs(["🌍 Global Pulse", "🛠️ Genesis Engine", "👥 Citizen Registry", "🧬 Node Inspector", "⚠️ System Logs"])
    
    with tabs[0]:
        c1, c2 = st.columns([0.7, 0.3])
        with c1:
            st.markdown("### 🌌 Real-time Connection Map")
            viz.render_cyberpunk_map(global_nodes, height="500px", is_fullscreen=False)
        with c2:
            st.markdown("### 🎨 Spectrum")
            st.info("Spectrum Analysis Module loading...")

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
    
    # === 👥 Citizen Registry (含删除功能) ===
    with tabs[2]:
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
            with st.container(border=True):
                st.warning("Warning: This action is irreversible.")
                
                # 下拉选择要删除的用户
                user_list = [u['username'] for u in all_users] if all_users else []
                target_user = st.selectbox("Select Target", user_list, index=None, placeholder="Choose identity...")
                
                # 防误触机制
                confirm_nuke = st.checkbox(f"I confirm I want to wipe '{target_user}'")
                
                if st.button("EXECUTE NUKE", type="primary", disabled=not (target_user and confirm_nuke)):
                    if target_user == "admin":
                        st.error("🚫 You cannot delete The Architect.")
                    else:
                        with st.spinner("Erasing existence..."):
                            success, msg = db.nuke_user(target_user)
                            if success:
                                st.success(f"Target '{target_user}' eliminated.")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(f"Termination Failed: {msg}")

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
    
    with tabs[4]:
        st.markdown("### ⚠️ System Telemetry")
        if st.button("Refresh Logs"):
            st.rerun()
        
        logs = msc.get_system_logs(limit=100)
        if logs:
            df_logs = pd.DataFrame(logs)
            def highlight_err(val):
                color = '#ff4b4b' if val == 'ERROR' else '#ffa421' if val == 'WARN' else 'transparent'
                return f'background-color: {color}'
            
            st.dataframe(
                df_logs[['created_at', 'level', 'component', 'message', 'user_id']], 
                use_container_width=True, 
                height=500
            )
        else:
            st.info("System is quiet. No anomalies detected.")
