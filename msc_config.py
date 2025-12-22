### msc_config.py ###
# ==========================================
# 🎨 1. MSC 16-Dimension Meaning Spectrum (v2.0)
# ==========================================
SPECTRUM = {
    "Conflict": "#FF2B2B",     "Hubris": "#FFD700",       "Vitality": "#FF7F00",
    "Rationality": "#00CCFF",  "Structure": "#E0E0E0",    "Truth": "#FFFFFF",
    "Curiosity": "#00E676",    "Mystery": "#9D00FF",
    "Nihilism": "#607D8B",     "Mortality": "#212121",    "Consciousness": "#69F0AE",
    "Empathy": "#FF4081",      "Heritage": "#795548",     "Melancholy": "#536DFE",
    "Aesthetic": "#AB47BC",    "Entropy": "#546E7A"
}

RADAR_AXES = ["Care", "Curiosity", "Reflection", "Coherence", "Agency", "Aesthetic", "Transcendence"]

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
# ⚙️ 系统参数
# ==========================================
W_MEANING = { "Cognitive_Density": 0.35, "Structural_Tension": 0.30, "Subjective_Weight": 0.20, "Abstract_Linkage": 0.15 }
LEVELS = { "Noise": 0.25, "Signal": 0.40, "Structure": 0.75, "Core": 0.92 }
LINK_THRESHOLD = {"Weak": 0.55, "Strong": 0.78}
RADAR_ALPHA = 0.12
HEARTBEAT_TIMEOUT = 300
WORLD_UNLOCK_THRESHOLD = 20 
TTL_ACTIVE = 24    
TTL_SEDIMENT = 720 

# ==========================================
# 🧠 AI 指令集 (中文强化版)
# ==========================================

PROMPT_CHATBOT = """
[System Context: MSC Intelligent Partner]
You are a mirrored surface of the user's mind. 
Goal: Reflect the *structure* of their thoughts. Do NOT advise or solve problems.

[LANGUAGE PROTOCOL]
- IF User speaks CHINESE -> YOU MUST REPLY IN CHINESE (Simplified).
- IF User speaks ENGLISH -> Reply in ENGLISH.

Tone: Calm, analytical, slightly sci-fi, precise.
"""

PROMPT_ANALYST = """
[Task: Cognitive Topology Analysis]
Analyze the input text. Extract Meaning Structure.

[CRITICAL: LANGUAGE OUTPUT RULE]
1. DETECT user language.
2. If User Input is CHINESE -> 'care_point' and 'insight' MUST be in SIMPLIFIED CHINESE.
3. If User Input is ENGLISH -> Output in ENGLISH.

[CRITICAL: SPECTRUM SELECTION]
Classify thought into ONE of the 16 dimensions (e.g. Conflict, Truth, Void, Empathy...).
Do NOT reject as Noise unless it's pure gibberish.

Output JSON: 
{ 
    "c_score": float (0.0-1.0), 
    "n_score": float (0.0-1.0), 
    "valid": bool, 
    "care_point": "String (Max 10 chars, Noun-based, IN USER LANGUAGE)", 
    "insight": "String (Deep observation, IN USER LANGUAGE)", 
    "keywords": ["Selected_Spectrum_Word"], 
    "radar_scores": {"Target_Radar_Axis": 1.0} 
}
"""

PROMPT_DAILY = """Based on user radar, generate a structural question.
Avoid "How do you feel". Use "How do you define".
Output JSON: { "question": "..." }
[LANGUAGE]: If user data implies Chinese, output in Chinese."""

PROMPT_PROFILE = """
[Role: Cognitive Geologist]
Analyze the user's radar data.
Generate a report on their 'Mental Topology'.
[LANGUAGE]: Strictly follow the requested language (Chinese or English).
Output JSON:
{
  "status_quo": "Describe the current topology.",
  "growth_path": "Predict the trajectory of their cognitive drift."
}
"""

# 🟢 新增：关系隐喻生成器 Prompt
PROMPT_METAPHOR = """
[Task: Generate Relationship Metaphor]
Analyze the Radar Data of User A and User B.
Generate a poetic, abstract metaphor describing their connection.

[Rules]
1. NO technical terms (e.g., "High Agency", "Low Care").
2. Use Metaphors: Light/Shadow, Sea/Island, Anchor/Wind, Mirror/Door.
3. If Match Type is 'Resonance' -> Emphasize similarity, shared silence, parallel paths.
4. If Match Type is 'Tension' -> Emphasize contrast, necessary conflict, balance.
5. Length: Max 25 words.

[Language]
- If request is ZH -> Simplified Chinese.
- If request is EN -> English.

Output JSON: { "metaphor": "..." }
"""
