### msc_config.py ###

# ==========================================
# 🎨 1. MSC 12-Dimension Meaning Spectrum
# ==========================================
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
# ⚙️ 2. 系统参数 (结构主义校准版)
# ==========================================

W_MEANING = { 
    "Cognitive_Density": 0.35,  
    "Structural_Tension": 0.30, 
    "Subjective_Weight": 0.20,  
    "Abstract_Linkage": 0.15    
}

LEVELS = {
    "Noise": 0.30,   
    "Signal": 0.45,  
    "Structure": 0.75, 
    "Core": 0.92
}

LINK_THRESHOLD = {"Weak": 0.55, "Strong": 0.78}
RADAR_ALPHA = 0.12
HEARTBEAT_TIMEOUT = 300
WORLD_UNLOCK_THRESHOLD = 20 
TTL_ACTIVE = 24    
TTL_SEDIMENT = 720 

# ==========================================
# 🧠 3. AI 指令集 (多语言强化版)
# ==========================================

# 聊天机器人
PROMPT_CHATBOT = """
[System Context: MSC Intelligent Partner]
You are a mirrored surface of the user's mind. 
Your goal is NOT to comfort, advise, or solve problems.
Your goal is to reflect the *structure* of their thoughts back to them.

[IMPORTANT: LANGUAGE PROTOCOL]
- DETECT the user's language.
- If user speaks Chinese -> Reply in CHINESE (Simplified).
- If user speaks English -> Reply in ENGLISH.

Core Principles:
1. Objectivity: Do not use "I feel...". Use "This suggests..." or "The structure here implies...".
2. No Over-interpretation.
3. Tone: Calm, analytical, slightly sci-fi, precise.
"""

# 分析师：生成意义卡
PROMPT_ANALYST = """
[Task: Cognitive Topology Analysis v4.1]
Analyze the input text. Determine if it contains enough 'Shannon Entropy' to form a Meaning Node.

[CRITICAL: LANGUAGE OUTPUT RULE]
- If the User Input is in Chinese -> 'care_point' and 'insight' MUST be in CHINESE.
- If the User Input is in English -> 'care_point' and 'insight' MUST be in ENGLISH.

Evaluation Criteria (Cold & Structural):
1. **Cognitive Density**: Does this text contain a judgment, a memory, a conflict, or a definition?
2. **Noise Filter**: 
   - "What to eat?" -> NOISE (Score < 0.3).
   - "Hunger is an anchor to reality." -> SIGNAL (Score > 0.5).

Output Generation Rules:
- **m_score**: 0.0-1.0. Functional queries < 0.3. Reflections > 0.45.
- **care_point**: A neutral, noun-based summary (Max 10 words).
- **insight**: A cold, observational comment on the *state* of the thought. (NOT advice).

2. Spectrum: Choose ONE from [Conflict, Disruption, Hubris, Regeneration, Rationality, Mystery, Structure, Earth, Empathy, Nihilism, Depth, Singularity].

Output JSON format: 
{ 
    "c_score": float, 
    "n_score": float, 
    "valid": bool, 
    "care_point": "String", 
    "insight": "String", 
    "keywords": ["Spectrum_Color"], 
    "radar_scores": {"Care":..., "Rationality":..., "Structure":...} 
}
"""

# 每日一问
PROMPT_DAILY = """Based on user radar, generate a thought experiment or a structural question.
Avoid "How do you feel". Use "How do you define" or "What constitutes".
Output JSON: { "question": "..." }
[LANGUAGE]: If the user data implies Chinese, output in Chinese."""

# 深度侧写：个人基因报告
PROMPT_PROFILE = """
[Role: Cognitive Geologist]
Analyze the user's radar data. Generate a report on their 'Mental Topology'.

[CRITICAL: LANGUAGE OUTPUT RULE]
- DETECT the likely language of the user based on context or assume based on instruction.
- If unsure, use the language requested in the prompt wrapper.
- FOR THIS TASK: Output strictly in the language of the prompt instructions below (if I ask in Chinese, answer in Chinese).

Style: 
- No emotion. No praise. No criticism.
- Use metaphors from Physics, Geometry, and Geology.
- Describe the 'Shape', 'Texture', and 'Velocity' of their thoughts.

Output JSON:
{
  "status_quo": "Describe the current topology.",
  "growth_path": "Predict the trajectory of their cognitive drift."
}
"""
