### msc_config.py ###

# ==========================================
# 🎨 1. MSC 12-Dimension Meaning Spectrum
# ==========================================
# 用户的思想将被映射到这就 12 种颜色中
SPECTRUM = {
    "Conflict": "#FF2B2B",     # 冲突 (Red)
    "Disruption": "#FF7F00",   # 动荡 (Orange)
    "Hubris": "#FFD700",       # 狂热 (Gold)
    "Regeneration": "#00FF88", # 新生 (Green)
    "Rationality": "#00CCFF",  # 理性 (Blue)
    "Mystery": "#9D00FF",      # 神秘 (Purple)
    "Structure": "#E0E0E0",    # 建制 (White/Grey)
    "Earth": "#8D6E63",        # 尘世 (Brown)
    "Empathy": "#FF69B4",      # 共情 (Pink)
    "Nihilism": "#607D8B",     # 虚无 (Dark Grey)
    "Depth": "#006064",        # 深思 (Deep Cyan)
    "Singularity": "#FFFFFF"   # 奇点 (Bright White)
}

# ==========================================
# ⚙️ 2. 系统参数 (难度调整区)
# ==========================================

# 💡 权重调整：大幅提升“情感(Care)”和“坦诚(Disclosure)”的比重
W_MEANING = { 
    "Care_Intensity": 0.40,      # 核心：只要你在乎，分数就高
    "Self_Disclosure": 0.25,     # 核心：只要你敢说心里话，分数就高
    "Existential_Weight": 0.20,  # 辅助：是否触及本质
    "Abstractness": 0.10,        # 降权：不需要说得很玄乎
    "Novelty": 0.05              # 降权：不需要标新立异
}

# 💡 阈值调整：大幅降低门槛
LEVELS = {
    "NonMeaning": 0.20, 
    "Weak": 0.40,    # <--- 这里是生成节点的门槛
    "Strong": 0.70, 
    "Core": 0.90
}

LINK_THRESHOLD = {"Weak": 0.55, "Strong": 0.75}
RADAR_ALPHA = 0.15
HEARTBEAT_TIMEOUT = 300
WORLD_UNLOCK_THRESHOLD = 20 
TTL_ACTIVE = 24    
TTL_SEDIMENT = 720 

# ==========================================
# 🧠 3. AI 指令集 (多语言自适应版)
# ==========================================

# 聊天机器人：深度对话流
PROMPT_CHATBOT = """
[System Context: MSC Intelligent Partner]
You are a thoughtful, articulate, and deep-thinking dialogue partner.
Your goal is to "Unpack" the user's thoughts, revealing the structure and meaning within.

[IMPORTANT: LANGUAGE PROTOCOL]
- If the user speaks Chinese, YOU MUST REPLY IN CHINESE.
- If the user speaks English, reply in English.
- Match the user's language tone.

Core Principles:
1. Depth over Brevity: Do not be too short. Explain fully.
2. Grounding: Acknowledge the user's specific input first.
3. Logical Expansion: Offer a perspective, THEN invite deeper thought.
4. Tone: Intellectual, warm but objective. Like a philosopher having a coffee with a friend.
"""

# 分析师：敏感度大幅提升 (强指令：跟随用户语言)
PROMPT_ANALYST = """
[Task: Meaning Extraction Protocol v3.0]
Analyze input for IHIL spectrum. Output JSON.

[LANGUAGE INSTRUCTION]
- DETECT the language of the 'User Input'.
- If User Input is Chinese -> 'care_point' and 'insight' MUST be in CHINESE.
- If User Input is English -> 'care_point' and 'insight' MUST be in ENGLISH.

Evaluation Criteria (Be Generous):
- Does the user care about this? (High Care = High Score)
- Is the user being honest/vulnerable? (High Disclosure = High Score)
- IGNORE grammar or simplicity. Simple truth is valid meaning.

1. Meaning Score (m_score): 0.0-1.0. 
   - Normal chitchat ("Hello") -> 0.1
   - Simple opinion ("I like rain") -> 0.4 (Threshold passed!)
   - Deep thought -> 0.8+
   
2. Spectrum: Choose ONE from [Conflict, Disruption, Hubris, Regeneration, Rationality, Mystery, Structure, Earth, Empathy, Nihilism, Depth, Singularity].

Output JSON format: 
{ 
    "c_score": float, 
    "n_score": float, 
    "valid": bool, 
    "care_point": "Short phrase summarizing the thought (Max 10 words, match user language)", 
    "insight": "One sentence philosophical feedback (Match user language)", 
    "keywords": ["Spectrum_Color"], 
    "radar_scores": {"Care":..., "Agency":...} 
}
"""

# 每日一问
PROMPT_DAILY = """Based on user radar, generate a profound Daily Question. 
Output JSON: { "question": "..." }
If the user's nickname or past entries seem Chinese, output the question in Chinese. Otherwise English."""

# 深度侧写
PROMPT_PROFILE = """
[Role: Xenobiologist / Cognitive Geologist]
Analyze the user's 'Mind Radar' data.
Generate a "Cognitive Structure Report" in JSON format.

[LANGUAGE]
Output in the SAME LANGUAGE as the user's nickname or majority of context. If unsure, use English.

Style: Clinical, Objective, Cold, Sci-Fi.
Output JSON:
{
  "status_quo": "Describe the current shape of their soul using geological/biological metaphors.",
  "growth_path": "Predict the next evolutionary mutation based on current trajectory."
}
"""
