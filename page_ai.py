### page_ai.py ###
import streamlit as st
import msc_lib as msc
import time
import msc_i18n as i18n

# ==========================================
# 🧠 核心逻辑：第一张意义卡提示
# ==========================================
def check_first_meaning_card(username):
    # 获取当前所有节点
    nodes = msc.get_active_nodes_map(username)
    # 如果节点数量正好为 1，说明刚刚生成了第一张
    if len(nodes) == 1:
        lang = st.session_state.get('language', 'en')
        
        if lang == 'zh':
            msg = """刚刚那句话，
被我们留下来了。

在这里，
它被称为一张「意义卡」。

意义卡不是观点，
也不是结论，
而是你真正认真思考过的痕迹。

它们会慢慢堆积，
形成你自己的分布、形状和偏向。

解锁更多的意义卡，
你会看到更多与世界互动的方式。
不是被推送，
而是从你自己出发。"""
        else:
            msg = """That sentence just now,
we kept it.

Here,
it is called a "Meaning Card".

A Meaning Card is not an opinion,
nor a conclusion,
but a trace of your genuine thought.

They will slowly accumulate,
forming your own distribution, shape, and bias.

Unlock more Meaning Cards,
and you will see more ways to interact with the world.
Not by being pushed,
but by starting from yourself."""
        
        # 插入这条解释性消息
        msc.save_chat(username, "assistant", msg)

# ==========================================
# 🤖 AI 页面渲染
# ==========================================
def render_ai_page(username):
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    chat_history = msc.get_active_chats(username)
    nodes_map = msc.get_active_nodes_map(username)
    lang = st.session_state.get('language', 'en')
    
    # 渲染历史消息
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

    # 输入框
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    placeholder = "Reflect on your thoughts..." if lang == 'en' else "映射此刻的思绪..."
    
    if prompt := st.chat_input(placeholder):
        # 1. 立即上屏用户输入
        st.markdown(f"<div class='chat-bubble-me'>{prompt}</div>", unsafe_allow_html=True)
        
        full_history = chat_history + [{'role':'user', 'content':prompt}]
        
        # 2. AI 流式回复
        with st.chat_message("assistant"):
            try:
                response_stream = msc.get_stream_response(full_history)
                full_response = st.write_stream(response_stream)
                
                # 3. 存储对话
                msc.save_chat(username, "user", prompt)
                msc.save_chat(username, "assistant", full_response)
            except Exception as e:
                st.error(f"AI Error: {e}")

        # 4. 后台分析意义 (Meaning Analysis)
        # 这一步通常比较快，但在 Vertex AI 上可能需要 1-2 秒
        # 我们用 spinner 让用户知道系统在思考
        analysis = msc.analyze_meaning_background(prompt)
        
        if analysis.get("valid", False):
            # 5. 如果有意义，生成节点
            vec = msc.get_embedding(prompt)
            msc.save_node(username, prompt, analysis, "AI对话", vec)
            
            # 更新雷达
            if "radar_scores" in analysis: 
                msc.update_radar_score(username, analysis["radar_scores"])
            
            # 提示用户
            toast_msg = "Meaning Captured" if lang == 'en' else "意义已捕获"
            st.toast(toast_msg, icon="🧬")
            
            # === 🆕 触发第一张卡的解释逻辑 ===
            check_first_meaning_card(username)
            
            # 刷新页面以显示新节点和可能的新消息
            time.sleep(1.0) # 稍微停顿让用户看清 AI 回复
            st.rerun()
