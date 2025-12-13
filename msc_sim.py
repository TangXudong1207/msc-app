### msc_sim.py (创世纪引擎：合成数据生成器) ###

import msc_lib as msc
import msc_db as db
import json
import random
import time
import streamlit as st

# ==========================================
# 🎭 1. 设定：创世纪原本 (Archetypes)
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
# 🧬 2. 核心逻辑：造人与对话
# ==========================================
def simulate_genesis(n_rounds=3):
    """
    运行创世纪模拟。
    n_rounds: 每个角色针对每个话题发言的轮数
    """
    print(f"🚀 创世纪引擎启动... 准备生成 {len(ARCHETYPES)} 个数字生命。")
    
    # 1. 注册用户 (如果没有的话)
    for char in ARCHETYPES:
        username = f"sim_{char['nickname'].lower()}"
        # 尝试注册，密码默认 123456
        if db.get_user_profile(username)['radar_profile'] is None:
            print(f"   ➕ 创建新生命: {char['nickname']}")
            msc.add_user(username, "123456", char['nickname'], "Matrix")
            # 初始化雷达
            msc.update_radar_score(username, char['radar'])
        else:
            print(f"   ✅ 生命已存在: {char['nickname']}")

    # 2. 开始思想碰撞
    total_nodes = 0
    
    for topic in TOPICS:
        print(f"\n📢 议题开启: {topic}")
        selected_chars = random.sample(ARCHETYPES, 3) # 每轮选3个人聊
        
        for char in selected_chars:
            username = f"sim_{char['nickname'].lower()}"
            
            # 让 AI 生成观点
            prompt = f"""
            角色设定：{char['style']}
            话题：{topic}
            任务：请用符合你角色设定的口吻，说一句简短深刻的话（50字以内）。
            不要解释，直接输出内容。
            """
            
            print(f"   Thinking ({char['nickname']})...")
            # 这里调用 msc_lib 的 AI 接口
            response = msc.call_ai_api(f"{prompt} 输出 JSON: {{'content': '...'}}")
            
            content = response.get('content', '')
            if content:
                print(f"   💬 {char['nickname']}: {content}")
                
                # 3. IHIL 介入：生成 MSC 节点
                # 模拟用户输入，走一遍完整的分析流程
                analysis = msc.analyze_meaning_background(content)
                
                if analysis.get("valid", False):
                    # 生成向量 (本地模型)
                    vec = msc.get_embedding(content)
                    # 存入数据库
                    msc.save_node(username, content, analysis, "Genesis_Sim", vec)
                    # 更新雷达
                    if "radar_scores" in analysis:
                        msc.update_radar_score(username, analysis["radar_scores"])
                    
                    total_nodes += 1
                    print(f"      ✨ 节点已结晶 (M-Score: {analysis['m_score']:.2f})")
                else:
                    print("      💨 意义太弱，未结晶")
            
            time.sleep(1) # 防止 API 限流

    print(f"\n🎉 创世纪完成！共生成 {total_nodes} 个意义节点。请前往 World 页面查看。")

# ==========================================
# ▶️ 运行入口
# ==========================================
if __name__ == "__main__":
    # 这是一个独立脚本，直接运行即可
    simulate_genesis()
