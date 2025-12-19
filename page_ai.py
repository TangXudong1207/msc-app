### page_ai.py ###
import streamlit as st
import msc_lib as msc
import time
import msc_i18n as i18n

# ==========================================
# 🧠 核心逻辑：第一张意义卡提示 (静默版)
# ==========================================
def check_first_meaning_card_silent(username):
    # 这个函数只在后台检查，如果触发了，就悄悄插入数据库
    # 下次刷新时用户就能看到
    nodes = msc.get_active_nodes_map(username)
    if len(nodes) == 1:
        lang = st.session_state.get('language', 'en')
        
        if lang == 'zh':
            msg = """刚刚那句话，被我们留下来了。\n\n在这里，它被称为一张「意义卡」。\n\n意义卡不是观点，也不是结论，而是你真正认真思考过的痕迹。\n\n解锁更多的意义卡，你会看到更多与世界互动的方式。不是被推送，而是从你自己出发。"""
        else:
            msg = """That sentence just now, we kept it.\n\nHere, it is called a "Meaning Card".\n\nA Meaning Card is not an opinion, nor a conclusion, but a trace of your genuine thought.\n\nUnlock more Meaning Cards, and you will see more ways to interact with the world."""
        
        # 悄悄插入，不打断对话
        msc.save_chat(username, "assistant", msg)

# ==========================================
# 🤖 AI 页面渲染 (流畅优化版)
# ==========================================
def render_ai_page(username):
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    # 1. 读取数据
    chat_history = msc.get_active_chats(username)
    nodes_map = msc.get_active_nodes_map(username)
    lang = st.session_state.get('language', 'en')
    
    # 2. 渲染历史消息 (只读操作，很快)
    for msg in chat_history:
        c_msg, c_dot = st.columns([0.92, 0.08])
        with c_msg:
            if msg['role'] == 'user':
                st.markdown(f"<div class='chat-bubble-me'>{msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-bubble-ai'>{msg['content']}</div>", unsafe_allow_html=True)
        with c_dot:
            # 如果这句话生成了节点，显示小圆点
            if msg['role'] == 'user' and msg['content'] in nodes_map:
                node = nodes_map.get(msg['content'])
                if node:
                    st.markdown('<div class="meaning-dot-btn">', unsafe_allow_html=True)
                    with st.popover("●", help="Meaning Extracted"):
                        try: score_val = float(node.get('m_score') or 0.5)
                        except: score_val = 0.5
                        st.caption(f"Score: {score_val:.2f}")
                        st.markdown(f"**{node.get('care_point', 'Unknown')}**")
                        st.info(node.get('insight', 'No insight'))
                    st.markdown('</div>', unsafe_allow_html=True)

    # 3. 输入框 (UI 底部)
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    placeholder = "Reflect on your thoughts..." if lang == 'en' else "映射此刻的思绪..."
    
    if prompt := st.chat_input(placeholder):
        # --- A. 立即响应用户 ---
        # 显示用户消息 (利用 Streamlit 的机制，这里其实已经 rerun 了一次)
        st.markdown(f"<div class='chat-bubble-me'>{prompt}</div>", unsafe_allow_html=True)
        
        full_history = chat_history + [{'role':'user', 'content':prompt}]
        
        # --- B. AI 流式回复 ---
        with st.chat_message("assistant"):
            try:
                response_stream = msc.get_stream_response(full_history)
                full_response = st.write_stream(response_stream)
                
                # 存入数据库
                msc.save_chat(username, "user", prompt)
                msc.save_chat(username, "assistant", full_response)
            except Exception as e:
                st.error(f"AI Error: {e}")

        # --- C. 静默分析 (Silent Analysis) ---
        # 关键优化：不再 rerun 页面，而是让后台悄悄跑
        
        # 1. 告诉用户我们正在工作，但不打断他
        status_msg = "Capturing meaning..." if lang == 'en' else "正在捕获思维深度..."
        st.toast(status_msg, icon="🧬")
        
        # 2. 调用耗时的分析 (这会卡顿 1-2 秒，但页面不会闪烁)
        analysis = msc.analyze_meaning_background(prompt)
        
        if analysis.get("valid", False):
            # 3. 如果有意义，存入数据库
            vec = msc.get_embedding(prompt)
            msc.save_node(username, prompt, analysis, "AI对话", vec)
            
            # 更新雷达
            if "radar_scores" in analysis: 
                msc.update_radar_score(username, analysis["radar_scores"])
            
            # 4. 再次轻提示，告诉用户成功了
            success_msg = "Meaning Node Created" if lang == 'en' else "意义节点已生成"
            st.toast(success_msg, icon="✅")
            
            # 触发彩蛋（静默插入）
            check_first_meaning_card_silent(username)
            
        # --- 重点：这里没有任何 st.rerun() ---
        # 用户此时看到的页面上，刚才那句话旁边没有小红点。
        # 但没关系，当他发下一句话时，页面会自动刷新，小红点就会补显示出来。
        # 这就是“延迟满足”，换来的是“极致流畅”。
