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
### msc_config.py (v74.0 Global Grid Edition) ###

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
# 🌍 2. 全球扫描网格 (Global Scan Grid)
# ==========================================
# 定义三级扫描策略，含覆盖与去重规则

GLOBAL_GRID = {
    # === Tier 1: The Core (G20 + Hotspots) ===
    # 频率: Daily / 权重: High / 数量: Top 10
    "Tier_1_G20": {
        "frequency": "Daily",
        "limit": 10,
        "weight_multiplier": 2.0, # 引力加倍
        "focus": [
            "USA", "China", "Russia", "Germany", "UK", "France", "Japan", 
            "India", "Brazil", "Saudi Arabia", "Israel", "Iran", "Turkey", 
            "Canada", "Australia", "South Korea", "Indonesia", "Mexico", 
            "South Africa", "Italy", "Argentina"
        ]
    },

    # === Tier 2: The Hubs (Regional Blocks) ===
    # 频率: Weekly / 权重: Medium / 数量: Top 5
    # 必须排除 Tier 1 已扫描的国家
    "Tier_2_Regions": {
        "frequency": "Weekly",
        "limit": 5,
        "weight_multiplier": 1.0,
        "regions": {
            "East_Asia_Periphery": {
                "focus": ["North Korea", "Taiwan Region", "Mongolia"],
                "exclude": ["China", "Japan", "South Korea"]
            },
            "Southeast_Asia": {
                "focus": ["Vietnam", "Thailand", "Philippines", "Malaysia", "Myanmar"],
                "exclude": ["Indonesia"]
            },
            "South_Asia": {
                "focus": ["Pakistan", "Bangladesh", "Sri Lanka"],
                "exclude": ["India"]
            },
            "Central_Asia": {
                "focus": ["Kazakhstan", "Uzbekistan", "Afghanistan"],
                "exclude": []
            },
            "West_Asia_Middle_East": {
                "focus": ["Syria", "Iraq", "Yemen", "UAE", "Qatar"],
                "exclude": ["Israel", "Iran", "Saudi Arabia", "Turkey"]
            },
            "Eastern_Europe": {
                "focus": ["Poland", "Hungary", "Romania", "Belarus"],
                "exclude": ["Russia", "Ukraine"] # Ukraine 虽热，但若未进G20单列，可在此，或手动提级
            },
            "Western_Europe": {
                "focus": ["Netherlands", "Belgium", "Switzerland"],
                "exclude": ["UK", "France", "Germany"]
            },
            "Northern_Europe": {
                "focus": ["Sweden", "Norway", "Finland", "Denmark"],
                "exclude": []
            },
            "Southern_Europe": {
                "focus": ["Spain", "Greece", "Portugal"],
                "exclude": ["Italy"]
            },
            "Balkans": {
                "focus": ["Serbia", "Kosovo", "Bosnia"],
                "exclude": []
            },
            "North_Africa": {
                "focus": ["Egypt", "Libya", "Morocco", "Algeria"],
                "exclude": []
            },
            "West_Africa": {
                "focus": ["Nigeria", "Ghana"],
                "exclude": []
            },
            "East_Africa": {
                "focus": ["Ethiopia", "Kenya", "Sudan"],
                "exclude": []
            },
            "Central_Africa": {
                "focus": ["Congo"],
                "exclude": []
            },
            "Southern_Africa": {
                "focus": ["Zimbabwe"],
                "exclude": ["South Africa"]
            },
            "South_America": {
                "focus": ["Colombia", "Chile", "Venezuela", "Peru"],
                "exclude": ["Brazil", "Argentina"]
            },
            "Central_America": {
                "focus": ["Cuba", "Panama"],
                "exclude": ["Mexico"]
            },
            "Caribbean": {
                "focus": ["Haiti", "Dominican Republic"],
                "exclude": []
            },
            "Oceania": {
                "focus": ["Papua New Guinea", "New Zealand", "Fiji"],
                "exclude": ["Australia"]
            }
        }
    },

    # === Tier 3: The Periphery (Passive Targets) ===
    # 频率: Monthly / 权重: Low / 数量: Top 1-3
    # 这里的意义往往是被指向的
    "Tier_3_Polar": {
        "frequency": "Monthly",
        "limit": 2,
        "weight_multiplier": 0.5,
        "focus": ["Arctic Region", "Antarctica"],
        "role": "Passive_Target"
    }
}

# ==========================================
# ⏳ 3. 时间与温度 (Time & Temperature)
# ==========================================
# TTL (Time To Live) in Hours
# 活跃期过后，节点将沉淀为历史 (Sediment)
TTL_CONFIG = {
    "Hubris": 360,        # 娱乐/泡沫: 15天 (15*24)
    "Conflict": 720,      # 政治/冲突: 30天 (30*24)
    "Structure": 720,
    "Rationality": 2160,  # 经济/技术: 90天 (90*24)
    "Disruption": 2160,
    "Regeneration": 4320, # 艺术/哲学: 180天 (180*24)
    "Depth": 4320,
    "Mystery": 4320,
    "Singularity": 8760   # 奇点: 1年 (365*24)
}

# ==========================================
# ⚙️ 4. 系统基础参数
# ==========================================
LEVELS = {"NonMeaning": 0.45, "Weak": 0.60, "Strong": 0.80, "Core": 1.0}
LINK_THRESHOLD = {"Weak": 0.55, "Strong": 0.75}
RADAR_ALPHA = 0.15
HEARTBEAT_TIMEOUT = 300
USER_WEIGHT_MULTIPLIER = 100 

# ==========================================
# 🧠 5. AI 指令集
# ==========================================

PROMPT_CHATBOT = """
[System Context: Intelligent Humanism]
You are an AI operating within the MSC system. 
Your goal is NOT to give advice, but to help the user unfold their own meaning structures.
Principles: Mirroring, Structure, Maieutics, Minimalism.
"""

PROMPT_ANALYST = """
[Task: IHIL Meaning Extraction]
Analyze input based on IHIL v1.0. Output JSON.
Check for: Care Intensity, Self Disclosure, Existential Weight, Abstractness, Novelty.
Output:
{
  "c_score": 0.0-1.0, "n_score": 0.0-1.0, "valid": bool,
  "care_point": "Short phrase",
  "insight": "Philosophical observation",
  "keywords": ["Tag1", "Tag2"],
  "radar_scores": { "Care":..., "Curiosity":..., "Reflection":..., "Coherence":..., "Empathy":..., "Agency":..., "Aesthetic":... }
}
"""

PROMPT_DAILY = """
Based on the user's radar profile, generate a short, profound Daily Question.
Output JSON: { "question": "..." }
"""

PROMPT_TENSION = """
[Task: Tension Extraction]
Analyze the text. Extract value conflict.
Output JSON: { "tension_pair": ["A", "B"], "emotional_color": "Red/Blue/..." }
"""

# === Oracle 引擎指令 (适配 G20/区域逻辑) ===
# 注意：该 Prompt 会在代码中根据区域动态拼接
PROMPT_ORACLE_TEMPLATE = """
[Task: Global Tension Extraction]
Role: Planetary Observer.
Target Scope: {scope_description}
Action: Identify TOP {limit} significant events. 
Logic: Extract the underlying tension (Fact vs Emotion, or Value A vs Value B).

Assign one Dimension (Color) from MSC Spectrum:
Conflict(Red), Disruption(Orange), Hubris(Gold), Regeneration(Green), 
Rationality(Blue), Mystery(Purple), Structure(Grey), Earth(Brown), 
Empathy(Pink), Nihilism(DarkGrey), Depth(Cyan), Singularity(White).

Output JSON List:
[
  {{
    "title": "Event Title",
    "tension": "Value A vs Value B",
    "dimension": "Conflict",
    "origin": "Country/City Name" (Must be within target scope),
    "impact": "Target Region" (Can be global),
    "intensity": 0.8 (0.0-1.0)
  }}
]
"""
