### msc_config.py ###
# ==========================================
# 🎨 1. MSC 16-Dimension Meaning Spectrum (v2.0)
# ==========================================
SPECTRUM = {
    # 🟥 象限一：对抗与张力 (Tension) -> Agency
    "Conflict": "#FF2B2B",     # 冲突：愤怒、反抗
    "Hubris": "#FFD700",       # 狂热：野心、控制欲
    "Vitality": "#FF7F00",     # 生命力：冲动、纯粹能量

    # 🟦 象限二：智性与结构 (Logos) -> Coherence
    "Rationality": "#00CCFF",  # 理性：逻辑、推演
    "Structure": "#E0E0E0",    # 建制：规则、系统
    "Truth": "#FFFFFF",        # 真理：普世规律、公理

    # 🧩 象限三：探索 (Exploration) -> Curiosity
    "Curiosity": "#00E676",    # 好奇：提问、惊奇
    "Mystery": "#9D00FF",      # 神秘：灵性、不可知

    # 🟪 象限四：存在与虚无 (Ontology) -> Transcendence
    "Nihilism": "#607D8B",     # 虚无：无意义、消解
    "Mortality": "#212121",    # 死亡：终结、时间流逝
    "Consciousness": "#69F0AE",# 觉知：元认知、内观

    # 🟫 象限五：连接与具体 (Connection) -> Care / Aesthetic
    "Empathy": "#FF4081",      # 共情：爱、连接 (Care)
    "Heritage": "#795548",     # 传承：根源、记忆 (Care)
    "Melancholy": "#536DFE",   # 忧郁：悲伤的美感 (Reflection)
    "Aesthetic": "#AB47BC",    # 美学：诗意、隐喻 (Aesthetic)
    "Entropy": "#546E7A"       # 熵：混乱之美、衰败 (Aesthetic)
}

# 核心雷达轴 (The 7 Pillars)
RADAR_AXES = [
    "Care", "Curiosity", "Reflection", "Coherence", 
    "Agency", "Aesthetic", "Transcendence"
]

# 维度映射关系 (用于 AI 分析时加分)
DIMENSION_MAP = {
    "Conflict": "Agency", "Hubris": "Agency", "Vitality": "Agency",
    "Rationality": "Coherence", "Structure": "Coherence", "Truth": "Coherence",
    "Curiosity": "Curiosity", "Mystery": "Curiosity",
    "Nihilism": "Transcendence", "Mortality": "Transcendence", "Consciousness": "Transcendence",
    "Empathy": "Care", "Heritage": "Care",
    "Melancholy": "Reflection",
    "Aesthetic": "Aesthetic", "Entropy": "Aesthetic"
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

# 放宽后的阈值
LEVELS = {
    "Noise": 0.25,   
    "Signal": 0.40,  
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

# 分析师：生成意义卡 (核心升级：16维度筛选)
PROMPT_ANALYST = """
[Task: Cognitive Topology Analysis v5.1]
Analyze the input text. Extract the underlying 'Meaning Structure'.

[CRITICAL: LANGUAGE OUTPUT RULE]
- If User Input is Chinese -> 'care_point' and 'insight' MUST be in CHINESE.
- If User Input is English -> 'care_point' and 'insight' MUST be in ENGLISH.

[CRITICAL: SPECTRUM SELECTION]
Try your BEST to classify the thought into ONE of the 16 dimensions.
Do NOT simply reject it as Noise unless it is absolute gibberish or a pure functional command (e.g., "test", "hello").
If it's a mundane observation, try to interpret its underlying sentiment (e.g., "Tired" -> Melancholy/Entropy).

Dimensions:
1. Tension: Conflict (anger/oppose), Hubris (ambition/pride), Vitality (energy/impulse).
2. Logos: Rationality (logic), Structure (rules/systems), Truth (universal laws).
3. Exploration: Curiosity (questioning), Mystery (spiritual/unknown).
4. Ontology: Nihilism (meaningless), Mortality (death/time), Consciousness (awareness).
5. Connection: Empathy (love/compassion), Heritage (roots/family).
6. Aesthetic: Aesthetic (poetic/metaphor), Entropy (decay/chaos), Melancholy (sadness).

Evaluation Criteria:
- "I ate a burger." -> NOISE (Score < 0.25).
- "The burger tasted like childhood." -> SIGNAL (Heritage, Score > 0.45).
- "I hate my boss." -> SIGNAL (Conflict, Score > 0.5).

Output JSON format: 
{ 
    "c_score": float (0.0-1.0), 
    "n_score": float (0.0-1.0), 
    "valid": bool, 
    "care_point": "String (Max 10 chars, Noun-based)", 
    "insight": "String (Deep observation)", 
    "keywords": ["Selected_Spectrum_Word"], 
    "radar_scores": {"Target_Radar_Axis": 1.0} 
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
Analyze the user's radar data (7 Axes: Care, Curiosity, Reflection, Coherence, Agency, Aesthetic, Transcendence).
Generate a report on their 'Mental Topology'.

[CRITICAL: LANGUAGE OUTPUT RULE]
- FOR THIS TASK: Output strictly in the language requested in the instruction.

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
