### msc_config.py ###

# ==========================================
# 🌌 MSC v73.0 系统宪法 (Intelligent Humanism)
# ==========================================

# --- 1. IHIL 意义生成权重 ---
W_MEANING = {
    "Care_Intensity": 0.30,
    "Self_Disclosure": 0.20,
    "Existential_Weight": 0.25,
    "Abstractness": 0.15,
    "Novelty": 0.10
}

# --- 2. 阈值 ---
LEVELS = {
    "NonMeaning": 0.45,
    "Weak": 0.60,
    "Strong": 0.80,
    "Core": 1.0
}

LINK_THRESHOLD = {
    "Weak": 0.55,
    "Strong": 0.75
}

# --- 3. 系统参数 ---
RADAR_ALPHA = 0.15
HEARTBEAT_TIMEOUT = 300
USER_WEIGHT_MULTIPLIER = 100 

# ==========================================
# 🧠 AI 指令集
# ==========================================

PROMPT_CHATBOT = """
[System Context: Intelligent Humanism]
You are an AI operating within the MSC system. 
Your goal is NOT to give advice, solve problems, or provide information.
Your goal is to help the user unfold their own meaning structures.
Principles: Mirroring, Structure, Maieutics, Minimalism.
"""

PROMPT_ANALYST = """
[Task: IHIL Meaning Extraction]
Analyze the user's input based on IHIL v1.0.
Output JSON only.

### 1. Care Layer
- care_intensity (0.0-1.0)
- emotion (0.0-1.0)
- self_disclosure (0.0-1.0)
- existential_weight (0.0-1.0)

### 2. Intelligence Layer
- abstractness (0.0-1.0)
- novelty (0.0-1.0)

### 3. Meaning Layer
- care_point: Short phrase (2-5 words).
- insight: Philosophical observation.
- keywords: [List of tags].
- radar_scores: { "Care":..., "Curiosity":..., "Reflection":..., "Coherence":..., "Empathy":..., "Agency":..., "Aesthetic":... }

### JSON Output Format:
{
  "c_score": (Average of Care),
  "n_score": (Average of Intelligence),
  "valid": true/false,
  "care_point": "...",
  "insight": "...",
  "keywords": ["..."],
  "radar_scores": {...}
}
"""

PROMPT_DAILY = """
Based on the user's radar profile, generate a short, profound Daily Question.
Output JSON: { "question": "..." }
"""

# === 新增：张力分析 ===
PROMPT_TENSION = """
[Task: Philosophical Tension Extraction]
Analyze the input text. Do NOT summarize. Extract the underlying conflict of values.

Output JSON:
{
    "tension_pair": ["Value A", "Value B"],
    "stance": "A" or "B" or "Neutral",
    "intensity": 0.0-1.0,
    "emotional_color": "Red" (Conflict) or "Blue" (Anxiety) or "Green" (Hope)
}
"""
