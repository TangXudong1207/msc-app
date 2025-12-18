import streamlit as st
import msc_lib as msc
import time
import msc_i18n as i18n

def render_ai_page(username):
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    chat_history = msc.get_active_chats(username)
    nodes_map = msc.get_active_nodes_map(username)
    lang = st.session_state.get('language', 'en')
    
    for msg in chat_history:
        c_msg, c_dot = st.columns([0.92, 0.08])
        with c_msg:
            if msg['role'] == 'user':
                st.markdown(f"<div class='chat-bubble-me'>{msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-bubble-ai'>{msg['content']}</div>", unsafe_allow_html=True)
        with c_dot:
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

    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    placeholder = "Reflect on your thoughts..." if lang == 'en' else "映射此刻的思绪..."
    
    if prompt := st.chat_input(placeholder):
        st.markdown(f"<div class='chat-bubble-me'>{prompt}</div>", unsafe_allow_html=True)
        full_history = chat_history + [{'role':'user', 'content':prompt}]
        
        with st.chat_message("assistant"):
            try:
                response_stream = msc.get_stream_response(full_history)
                full_response = st.write_stream(response_stream)
                msc.save_chat(username, "user", prompt)
                msc.save_chat(username, "assistant", full_response)
            except Exception as e:
                st.error(f"AI Error: {e}")

        analysis = msc.analyze_meaning_background(prompt)
        if analysis.get("valid", False):
            vec = msc.get_embedding(prompt)
            msc.save_node(username, prompt, analysis, "AI对话", vec)
            if "radar_scores" in analysis: msc.update_radar_score(username, analysis["radar_scores"])
            
            toast_msg = "Meaning Captured" if lang == 'en' else "意义已捕获"
            st.toast(toast_msg, icon="🧬")
        
        time.sleep(0.5)
        st.rerun()
