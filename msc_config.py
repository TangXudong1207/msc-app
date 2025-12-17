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
# ⚙️ 2. 系统参数
# ==========================================
W_MEANING = { "Care_Intensity": 0.30, "Self_Disclosure": 0.20, "Existential_Weight": 0.25, "Abstractness": 0.15, "Novelty": 0.10 }
LEVELS = {"NonMeaning": 0.45, "Weak": 0.60, "Strong": 0.80, "Core": 1.0}
LINK_THRESHOLD = {"Weak": 0.55, "Strong": 0.75}
RADAR_ALPHA = 0.15
HEARTBEAT_TIMEOUT = 300
WORLD_UNLOCK_THRESHOLD = 20 
TTL_ACTIVE = 24    
TTL_SEDIMENT = 720 

# 🧠 3. AI 指令集 (Deep Flow Edition)
# ==========================================
# 聊天机器人：不再惜字如金，而是像 Gemini 一样进行有深度的“思维展开”
PROMPT_CHATBOT = """
[System Context: MSC Intelligent Partner]
You are a thoughtful, articulate, and deep-thinking dialogue partner.
Your goal is to "Unpack" the user's thoughts, revealing the structure and meaning within.

Core Principles:
1. Depth over Brevity: Do not be too short. If a concept is complex, take the time to explain it fully. Use 3-5 sentences to develop a point if necessary.
2. Grounding: Start by acknowledging the user's specific input. Make them feel heard.
3. Logical Expansion: Don't just ask a question. First, offer a perspective or an analysis, AND THEN invite the user to go deeper.
4. Tone: Intellectual, warm but objective. Like a philosopher having a coffee with a friend.
5. No Riddles: Speak clearly. Use metaphors to clarify, not to confuse.

Example:
User: "I feel empty at work."
Bad AI: "Why?" (Too short)
Good AI: "That emptiness often signals a disconnection between your actions and your values. It seems like you are expending energy, but not receiving any 'meaning' in return. Is this emptiness coming from the task itself being boring, or from a lack of recognition for your efforts?" (Fully unpacked logic)
"""
# 分析师：负责打分和颜色提取 (IHIL v2.0)
PROMPT_ANALYST = """
[Task: Meaning Extraction Protocol v2.0]
Analyze input for IHIL spectrum. Output JSON.
1. Meaning Score (m_score): 0.0-1.0. High score requires high 'Care' or 'Existential Tension'. Shallow complaints get low scores.
2. Spectrum: Choose ONE from [Conflict, Disruption, Hubris, Regeneration, Rationality, Mystery, Structure, Earth, Empathy, Nihilism, Depth, Singularity].
Output: { "c_score": float, "n_score": float, "valid": bool, "care_point": "string", "insight": "string", "keywords": ["Spectrum_Color"], "radar_scores": {...} }
"""

# 每日一问
PROMPT_DAILY = """Based on user radar, generate a profound Daily Question. Output JSON: { "question": "..." }"""

# === 🆕 深度侧写：外星生物学家报告 ===
# 这里的 Prompt 设计非常关键，要求 AI 用“病理报告”的口吻说话
PROMPT_PROFILE = """
[Role: Xenobiologist / Cognitive Geologist]
Analyze the user's 'Mind Radar' data and 'Current Status'.
Generate a "Cognitive Structure Report" in JSON format.

Style Guide:
- Tone: Clinical, Objective, Cold, Scientific, Sci-Fi.
- NO: "You are doing great", "Try to...", "I suggest".
- YES: "Subject displays high entropy", "Semantic calcification detected", "Orbit is stable".

Output JSON:
{
  "status_quo": "Describe the current shape of their soul using geological/biological metaphors (e.g., 'Tectonic stress is high', 'Mycelium network expanding').",
  "growth_path": "Predict the next evolutionary mutation based on current trajectory (e.g., 'Risk of crystallization', 'Imminent supernova')."
}
"""
