### msc_config.py (v74.0 Complete) ###

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
GLOBAL_GRID = {
    # === Tier 1: The Core (G20 + Hotspots) ===
    # 频率: Daily / 权重: High / 数量: Top 10
    "Tier_1_G20": {
        "frequency": "Daily",
        "limit": 10,
        "weight_multiplier": 2.0,
        "countries": [
            "USA", "China", "Russia", "Germany", "UK", "France", "Japan", 
            "India", "Brazil", "Saudi Arabia", "Israel", "Iran", "Turkey", 
            "Canada", "Australia", "South Korea", "Indonesia", "Mexico", 
            "South Africa", "Italy", "Argentina"
        ]
    },

    # === Tier 2: The Hubs (Regional Blocks) ===
    # 频率: Weekly / 权重: Medium / 数量: Top 5
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
                "exclude": ["Russia", "Ukraine"]
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
    # 频率: Monthly / 权重: Low / 数量: Top 2
    "Tier_3_Polar": {
        "frequency": "Monthly",
        "limit": 2,
        "weight_multiplier": 0.5,
        "focus": ["Arctic Region", "Antarctica"],
        "role": "Passive_Target"
    }
}

# ==========================================
# ⏳ 3. 时间与温度 (TTL in Hours)
# ==========================================
TTL_CONFIG = {
    "Hubris": 360,        # 15 Days
    "Conflict": 720,      # 30 Days
    "Structure": 720,
    "Rationality": 2160,  # 90 Days
    "Disruption": 2160,
    "Regeneration": 4320, # 180 Days
    "Depth": 4320,
    "Mystery": 4320,
    "Earth": 4320,
    "Empathy": 2160,
    "Nihilism": 2160,
    "Singularity": 8760   # 1 Year
}

# ==========================================
# ⚙️ 4. 系统基础参数
# ==========================================
W_MEANING = {
    "Care_Intensity": 0.30,
    "Self_Disclosure": 0.20,
    "Existential_Weight": 0.25,
    "Abstractness": 0.15,
    "Novelty": 0.10
}

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
Analyze input based on IHIL v1.0. Output valid JSON only.
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

# === Oracle 引擎核心模板 ===
# 注意：{scope_description} 和 {limit} 会在运行时被替换
PROMPT_ORACLE_TEMPLATE = """
[Task: Global Tension Extraction]
Role: Planetary Observer.
Target Scope: {scope_description}
Action: Identify TOP {limit} significant events currently happening or trending.
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
