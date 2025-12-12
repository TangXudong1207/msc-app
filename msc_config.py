# ==========================================
# 🎛️ MSC v70.0 系统调音台 (System Constitution)
# ==========================================

# --- 1. 意义生成权重 (Meaning Weights) ---
W_MEANING = {
    "C_emotion": 0.35,        # 情绪强度
    "C_self": 0.25,           # 自我暴露度
    "N_abstract": 0.20,       # 抽象/理论度
    "N_relative": 0.20        # 相对新颖度 (与历史对比)
}

# --- 2. 意义层级阈值 (Meaning Levels) ---
# M_score = Sum(Weights * Scores)
LEVELS = {
    "NonMeaning": 0.40,    # < 0.40: 废话，不生成节点
    "Weak": 0.60,          # 0.40 - 0.60: 弱意义 (浅灰色点)
    "Strong": 0.80,        # 0.60 - 0.80: 强意义 (亮色点)
    "Core": 1.0            # > 0.80: 核心意义 (恒星级)
}

# --- 3. 共鸣权重 (Linkage Weights) ---
W_MLS = {
    "TagOverlap": 0.30,       # 标签重叠
    "SemanticSim": 0.25,      # 语义向量相似
    "ValueAlign": 0.20,       # 价值观(雷达)一致性
    "Existential": 0.15,      # 存在性问题匹配
    "Temporal": 0.10          # 时间一致性 (暂用1.0模拟)
}

# 链接阈值
LINK_THRESHOLD = {
    "Weak": 0.55,   # 暗线
    "Strong": 0.75  # 亮线/融合
}

# --- 4. 雷达生长参数 ---
RADAR_DECAY = 0.999      # 每日衰减率
RADAR_ALPHA = 0.15       # 学习率 (单次对话的影响力)

# --- 5. 系统参数 ---
HEARTBEAT_TIMEOUT = 300
CHAT_HISTORY_LIMIT = 50

# --- 6. AI 指令 (System Prompts) ---

PROMPT_CHATBOT = """
你是一个智慧、温暖的对话伙伴。像老朋友一样交谈，不要说教。
"""

# v70.0 升级版分析师：要求返回细分维度
PROMPT_ANALYST = """
任务：对用户输入进行【高精度意义审计】。

请对以下维度打分 (0.0 - 1.0)：
1. Emotion (情绪强度): 愤怒/悲伤/喜悦/激情的烈度。
2. SelfDisclosure (自我暴露): 是否谈及隐私、脆弱、真实感受。
3. Abstraction (抽象度): 是描述具体琐事(0)还是抽象规律/哲学(1)。
4. Existential (存在性): 是否涉及"我是谁/死亡/自由/意义"等终极问题 (True/False)。

同时提取：
- Care Point (核心关切)
- Meaning Layer (结构分析)
- Insight (洞察)
- Keywords (3个核心标签)
- Radar Scores (7维度评分 0-10)
"""

PROMPT_DAILY = "生成一个每日灵魂追问。短小精悍。"
PROMPT_PERSONA = "生成深度人物画像：静态底色 + 动态进化。"
PROMPT_OBSERVER = "用一句话幽默深刻地评论这段对话。"
