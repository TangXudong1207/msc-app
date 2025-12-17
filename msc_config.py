### msc_config.py (v75.0 Clean) ###

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

# 🌍 世界门槛：需要多少个节点才能解锁 World
WORLD_UNLOCK_THRESHOLD = 20 

# ⏳ 沉淀周期 (小时)
TTL_ACTIVE = 24    # 活跃 24 小时
TTL_SEDIMENT = 720 # 沉淀 30 天后消失

# ==========================================
# 🧠 3. AI 指令集
# ==========================================
PROMPT_CHATBOT = """
[System Context: Intelligent Humanism]
You are an AI operating within the MSC system. 
Your goal is NOT to give advice, but to help the user unfold their own meaning structures.
Principles: Mirroring, Structure, Maieutics, Minimalism.
"""

# 重点：分析师必须返回 12 维光谱中的一种
PROMPT_ANALYST = """
[Task: IHIL Meaning Extraction]
Analyze input based on IHIL v1.0. Output valid JSON only.

1. Scores (0.0-1.0): Care Intensity, Self Disclosure, Existential Weight, Abstractness.
2. Spectrum Classification: Choose ONE dimension from: 
   Conflict, Disruption, Hubris, Regeneration, Rationality, Mystery, Structure, Earth, Empathy, Nihilism, Depth, Singularity.

Output:
{
  "c_score": 0.0-1.0, 
  "n_score": 0.0-1.0, 
  "valid": bool,
  "care_point": "Short phrase",
  "insight": "Philosophical observation",
  "keywords": ["Spectrum_Dimension_Name", "Other_Tag"], 
  "radar_scores": { ... }
}
"""

PROMPT_DAILY = """Based on user radar, generate a profound Daily Question. Output JSON: { "question": "..." }"""
