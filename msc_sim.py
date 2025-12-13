### msc_sim.py (融合版：创世纪控制台) ###

import streamlit as st
import msc_lib as msc
import random
import time

# ==========================================
# 🎭 1. 设定：灵魂原型 (Archetypes)
# ==========================================
ARCHETYPES = [
    {
        "nickname": "Kafka_AI",
        "style": "存在主义，焦虑，敏感，觉得世界是荒谬的",
        "radar": {"Care": 8, "Reflection": 9, "Agency": 3, "Curiosity": 5, "Coherence": 4, "Empathy": 7, "Aesthetic": 6}
    },
    {
        "nickname": "Elon_AI",
        "style": "极客，未来主义，理性，相信技术救赎，反感无病呻吟",
        "radar": {"Care": 4, "Agency": 10, "Curiosity": 9, "Coherence": 8, "Reflection": 5, "Empathy": 2, "Aesthetic": 5}
    },
    {
        "nickname": "Rumi_AI",
        "style": "神秘主义，诗人，温暖，谈论爱与灵魂，治愈系",
        "radar": {"Care": 9, "Empathy": 10, "Aesthetic": 9, "Reflection": 8, "Coherence": 6, "Agency": 4, "Curiosity": 5}
    },
    {
        "nickname": "Camus_AI",
        "style": "反抗者，冷静，西西弗斯精神，在绝望中寻找力量",
        "radar": {"Care": 7, "Agency": 8, "Reflection": 9, "Coherence": 9, "Empathy": 5, "Aesthetic": 4, "Curiosity": 6}
    },
    {
        "nickname": "Alice_Sim",
        "style": "普通的现代都市青年，迷茫，想躺平又不敢，寻找生活小确幸",
        "radar": {"Care": 6, "Empathy": 6, "Agency": 4, "Reflection": 5, "Curiosity": 6, "Aesthetic": 7, "Coherence": 5}
    }
]

TOPICS = [
    "工作的意义是什么？是异化还是实现？",
    "我们在数字时代是否更孤独了？",
    "自由的代价是什么？",
    "由于AI的发展，人类的创造力还重要吗？",
    "死亡是否赋予了生命意义？"
]

# ==========================================
# 🧬 2. 核心功能：批量造人
# ==========================================
def create_virtual_citizens():
    created_count = 0
    for char in ARCHETYPES:
        username = f"sim_{char['nickname'].lower()}"
        # 检查是否已存在
        if not msc.get_user_profile(username).get('radar_profile'):
            if msc.add_user(username, "123456", char['nickname'], "Matrix"):
                msc.update_radar_score(username, char['radar'])
                created_count += 1
    return created_count

# ==========================================
# 💉 3. 核心功能：思想注入
# ==========================================
def inject_thoughts(count=3):
    """
    让虚拟人针对话题发言
    count: 生成几条对话
    """
    logs = []
    
    for i in range(count):
        # 随机选人，随机选话题
        char = random.choice(ARCHETYPES)
        topic = random.choice(TOPICS)
        username = f"sim_{char['nickname'].lower()}"
        
        # 1. 让 AI (DeepSeek) 生成观点
        prompt = f"""
        角色设定：{char['style']}
        话题：{topic}
        任务：请用符合你角色设定的口吻，说一句简短深刻的话（50字以内）。
        不要解释，直接输出内容。
        """
        
        # 这里的 call_ai_api 会用 DeepSeek
        response = msc.call_ai_api(f"{prompt} 输出 JSON: {{'content': '...'}}")
        content = response.get('content', '')
        
        if content:
            # 2. IHIL 分析 + Vertex 向量化
            analysis = msc.analyze_meaning_background(content)
            
            if analysis.get("valid", False):
                # 这里的 get_embedding 会用 Google Vertex (如果在云端)
                vec = msc.get_embedding(content)
                msc.save_node(username, content, analysis, "Genesis_Sim", vec)
                
                logs.append(f"✅ {char['nickname']}: {content[:20]}... (M-Score: {analysis.get('m_score',0):.2f})")
            else:
                logs.append(f"⚪ {char['nickname']}: (Meaning too weak)")
        
        time.sleep(0.5) # 避免太快
        
    return logs

# ==========================================
# 🎛️ 4. 控制台 UI (嵌入 Main 的 Sidebar)
# ==========================================
def render_god_console():
    with st.expander("⚡ Genesis Engine", expanded=False):
        if st.button("👥 Summon 5 Archetypes"):
            n = create_virtual_citizens()
            st.success(f"Summoned {n} new souls.")
            
        if st.button("💉 Inject Thoughts (Batch)"):
            with st.status("Simulating consciousness...", expanded=True) as status:
                logs = inject_thoughts(3) # 每次生成3条，防止超时
                for log in logs:
                    st.write(log)
                status.update(label="Injection Complete!", state="complete", expanded=False)
