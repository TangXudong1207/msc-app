### page_admin.py ###
import streamlit as st
import msc_lib as msc
import msc_db as db
import msc_sim as sim
import pandas as pd
import streamlit_antd_components as sac

def render_admin_dashboard():
    st.markdown("## 👁️ God Mode Dashboard")
    
    # 顶部导航
    admin_menu = sac.tabs([
        sac.TabsItem(label='System Monitor', icon='activity'),
        sac.TabsItem(label='The Matrix (Sim)', icon='robot'),
        sac.TabsItem(label='User Management', icon='people'),
    ], align='center', variant='outline')

    # === Tab 1: 系统监控 ===
    if admin_menu == 'System Monitor':
        c1, c2, c3 = st.columns(3)
        
        # 统计数据
        all_nodes = msc.get_global_nodes()
        all_users = msc.get_all_users("admin")
        active_sims = len([u for u in all_users if u['username'].startswith("sim_")])
        
        with c1: st.metric("Total Population", len(all_users))
        with c2: st.metric("Simulacra (AI)", active_sims)
        with c3: st.metric("Total Meaning Nodes", len(all_nodes))
        
        st.divider()
        st.subheader("📜 System Logs")
        logs = msc.get_system_logs()
        if logs:
            df_logs = pd.DataFrame(logs)
            st.dataframe(df_logs[['created_at', 'level', 'component', 'message', 'user_id']], use_container_width=True)
        else:
            st.info("System operational. No logs.")

    # === Tab 2: 矩阵模拟器 (The Matrix) ===
    elif admin_menu == 'The Matrix (Sim)':
        st.info("💡 Generate virtual citizens to populate the World Layer for testing.")
        
        c_gen, c_act = st.columns([1, 1])
        
        # 左边：创世纪 (造人)
        with c_gen:
            with st.container(border=True):
                st.markdown("### 🧬 Genesis Protocol")
                st.caption("Create archetypal AI agents.")
                
                if st.button("Initialize 5 Virtual Citizens", type="primary", use_container_width=True):
                    with st.spinner("Weaving souls..."):
                        logs = sim.create_virtual_citizens()
                        for l in logs: st.success(l)
        
        # 右边：思想注入 (发帖)
        with c_act:
            with st.container(border=True):
                st.markdown("### 🧠 Synaptic Injection")
                st.caption("Force AI agents to generate meaning nodes.")
                
                # 滑块选择生成数量
                inject_count = st.slider("Thoughts to Generate", 1, 10, 3)
                
                if st.button(f"Inject {inject_count} Thoughts", use_container_width=True):
                    progress_bar = st.progress(0)
                    log_box = st.empty()
                    
                    logs = []
                    # 循环调用，防止超时，并更新进度条
                    for i in range(inject_count):
                        new_logs = sim.inject_thoughts(count=1) # 一次生成一条
                        logs.extend(new_logs)
                        progress_bar.progress((i + 1) / inject_count)
                        # 实时显示最后一条日志
                        if new_logs: log_box.caption(new_logs[-1])
                    
                    st.success("Injection Complete.")
                    with st.expander("View Injection Logs"):
                        st.write(logs)

        st.divider()
        st.markdown("### 🤖 Active Simulacra Status")
        # 显示当前所有虚拟人的状态（雷达图、节点数）
        all_users = msc.get_all_users("admin")
        sim_users = [u for u in all_users if u['username'].startswith("sim_")]
        
        if sim_users:
            sim_data = []
            for u in sim_users:
                # 查节点数
                nodes = db.get_active_nodes_map(u['username'])
                sim_data.append({
                    "Bot Name": u['nickname'],
                    "Username": u['username'],
                    "Nodes": len(nodes),
                    "City": u.get('country', 'Unknown') # 这里借用 country 字段存城市
                })
            st.dataframe(pd.DataFrame(sim_data), use_container_width=True)
        else:
            st.warning("No virtual citizens found. Run Genesis first.")

    # === Tab 3: 用户管理 (核打击) ===
    elif admin_menu == 'User Management':
        st.warning("⚠️ DANGER ZONE")
        
        target_user = st.text_input("Enter Username to Nuke (Delete everything)")
        
        if st.button("☢️ NUKE USER"):
            if target_user:
                if target_user == "admin":
                    st.error("Cannot delete God.")
                else:
                    success, msg = db.nuke_user(target_user)
                    if success: st.success(f"User {target_user} eliminated.")
                    else: st.error(msg)
            else:
                st.warning("Please enter a username.")
