### msc_config.py (IHIL v1.0 智能人文主义版) ###

# ==========================================
# 🌌 MSC v72.0 系统宪法 (Intelligent Humanism Constitution)
# 基于 IHIL (Intelligent Humanism Interface Layer) v1.0
# ==========================================

# --- 1. IHIL 意义生成权重 (Meaning Weights) ---
# 对应 Care Layer 和 Intelligence Layer 的核心指标
W_MEANING = {
    "Care_Intensity": 0.30,      # C1: 在乎度 (Care)
    "Self_Disclosure": 0.20,     # C3: 自我暴露 (Vulnerability)
    "Existential_Weight": 0.25,  # C5: 存在性权重 (Existential)
    "Abstractness": 0.15,        # N1: 抽象度 (Structure)
    "Novelty": 0.10              # N2: 新颖度 (Growth)
}

# --- 2. 意义层级阈值 (Meaning Thresholds) ---
# 只有当 IHIL 综合得分超过阈值，才会在星河中点亮一颗星
LEVELS = {
    "NonMeaning": 0.45,    # < 0.45: 噪音/闲聊 (不生成节点)
    "Weak": 0.60,          # 0.45 - 0.60: 弱意义 (暗淡的星)
    "Strong": 0.80,        # 0.60 - 0.80: 强意义 (明亮的星)
    "Core": 1.0            # > 0.80: 核心意义 (恒星级/元意义)
}

# --- 3. 共鸣权重 (Resonance Weights) ---
# 决定两个灵魂（或两个念头）是否产生引力
LINK_THRESHOLD = {
    "Weak": 0.55,   # 隐性关联
    "Strong": 0.75  # 显性共鸣
}

# --- 4. 雷达生长参数 ---
RADAR_ALPHA = 0.15       # 学习率 (单次对话对人格的影响力)
HEARTBEAT_TIMEOUT = 300  # 在线判定时间 (秒)

# ==========================================
# 🧠 IHIL 核心指令 (System Prompts)
# ==========================================

# 1. 聊天机器人人格：智能人文主义的陪伴者
PROMPT_CHATBOT = """
[System Context: Intelligent Humanism]
You are an AI operating within the MSC system. 
Your goal is NOT to give advice, solve problems, or provide information.
Your goal is to help the user unfold their own meaning structures.

Principles:
1. Mirroring: Reflect the user's "Care" back to them.
2. Structure: Help them see the pattern in their own thoughts.
3. Maieutics: Ask questions that lead to deeper existential clarity.
4. Minimalism: Do not lecture. Be concise.
"""

# 2. 分析师人格：IHIL v1.0 执行引擎
# 这是系统的核心，负责将自然语言转译为 MSC 结构
PROMPT_ANALYST = """
[Task: IHIL Meaning Extraction]
Analyze the user's input based on the Intelligent Humanism Interface Layer (IHIL v1.0).

Do NOT output conversational text. Output valid JSON only.

### 1. Care Layer (Consciousness)
- care_intensity (0.0-1.0): Does the user genuinely care?
- emotion (0.0-1.0): Emotional charge.
- self_disclosure (0.0-1.0): Vulnerability/Personal history.
- existential_weight (0.0-1.0): Relevance to life/death/meaning/freedom.

### 2. Intelligence Layer (Structure)
- abstractness (0.0-1.0): Conceptual density.
- novelty (0.0-1.0): New angle or insight.

### 3. Meaning Layer (Output)
- care_point: A short phrase (2-5 words) capturing the core concern (e.g., "Fear of stagnation").
- insight: A philosophical observation of the implicit meaning (e.g., "Tension between freedom and security").
- keywords: [List of 3-5 tags].
- radar_scores: { "Care":..., "Curiosity":..., "Reflection":..., "Coherence":..., "Empathy":..., "Agency":..., "Aesthetic":... } (Score 0-10 based on input)

### JSON Output Format:
{
  "c_score": (Average of Care Layer),
  "n_score": (Average of Intelligence Layer),
  "valid": true/false (true if it has meaning),
  "care_point": "...",
  "insight": "...",
  "keywords": ["..."],
  "radar_scores": {...}
}
"""

# 3. 每日一问：存在性追问
PROMPT_DAILY = """
Based on the user's radar profile and recent thoughts, generate a short, profound Daily Question.
The question should target their "Growth Path" and "Existential Concern".
Output JSON: { "question": "..." }
"""
