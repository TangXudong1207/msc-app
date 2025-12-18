### msc_i18n.py ###
import streamlit as st

# ==========================================
# 🌍 语言包定义 (Translation Dictionary)
# ==========================================
TRANSLATIONS = {
    "en": {
        # --- 通用 ---
        "login_tab": "LOGIN", "signup_tab": "SIGN UP",
        "identity": "IDENTITY", "key": "KEY", "connect": "CONNECT UPLINK",
        "new_id": "NEW ID", "new_pw": "NEW PW", "nick": "NICK", "region": "REGION", "init": "INITIALIZE PROTOCOL",
        "signal_lost": "Signal Lost: Invalid Credentials", "created": "Identity Created. Please Login.",
        "lock_title": "SIGNAL TRANSMITTER LOCKED",
        "lock_msg": "Deep Connection requires Deep Self.<br>You need to cultivate a denser forest before you can invite others in.<br>This is to ensure every connection here is meaningful, not noise.",
        "lock_stat": "Meaning Nodes Generated",
        "chat_signals": "Signals", "chat_no_res": "No resonance detected.", "chat_transmit": "Transmit to", "chat_no_data": "No data exchange yet.", "chat_sel": "Select a frequency channel to begin.",
        "world_lock": "GLOBAL LAYER LOCKED", "world_only": "Only those who cultivate their own garden may view the forest.",
        "world_proto_title": "The Protocol", "world_proto_text": "You are entering the **Collective Mind Layer**. Identities are masked. Only meaning is visible.",
        "world_accept": "Accept Protocol",

        # --- 新版引导 (Arrival Style) ---
        "s0_main": "Welcome.\n\nThis is not a place to rush to conclusions.\n\nMostly, we just slow things down a little.",
        "s0_btn": "Continue",
        
        "s1_main": "You speak.\n\nWe don't rush to answer.\n\nWe observe first what you truly care about.",
        "s1_sub": "Rest assured, there is no scoring here.",
        "s1_btn": "Next",

        "s2_main": "Some words will slowly become important.\nSome will not.\n\nThis is not a filter.\nIt is simply time doing what it does.",
        "s2_sub": "Don't worry about being wrong.\nMost of the time, meaning just hasn't arrived yet.",
        "s2_btn1": "I see", "s2_btn2": "Let me look",

        "s3_main": "I won't think for you.\n\nI simply place an outline aside while you think.",
        "s3_sub": "If these outlines feel inaccurate, just ignore them.\nThey were never conclusions.",
        "s3_btn": "Continue",

        "s4_main": "Some thoughts will become a card.\n\nThey won't judge you.\n\nJust a record:\nYou thought about this here.",
        "s4_sub": "Of course, for most words, nothing happens.",
        "s4_btn1": "Good", "s4_btn2": "A bit cruel",

        "s5_main": "You won't be pushed to socialize.\nNor suddenly matched.\n\nIf someone approaches, it's usually because you cared about similar things.",
        "s5_sub": "Yes, this is more troublesome than 'shared interests'.",
        "s5_btn": "Continue",

        "s6_main": "When you accumulate meaning, you will see a world.\n\nIt's not news, nor events.\n\nMore like—what you care about lighting up somewhere.",
        "s6_sub": "Some places will remain blurry.\nThat is also normal.",
        "s6_btn": "Continue",

        "s7_main": "You can say something now.\nOr say nothing at all.\n\nMSC doesn't mind.",
        "s7_sub": "After all, meaning can never be forced.",
        "s7_btn": "Begin Dialogue"
    },
    "zh": {
        # --- 通用 ---
        "login_tab": "登入", "signup_tab": "注册",
        "identity": "身份ID", "key": "密钥", "connect": "接入链路",
        "new_id": "新账户名", "new_pw": "新密码", "nick": "代号", "region": "区域", "init": "初始化协议",
        "signal_lost": "信号丢失：无效的凭证", "created": "身份已创建，请登入。",
        "lock_title": "信号发射器已锁定",
        "lock_msg": "深度的连接 · 始于深度的自我<br>在邀请他人进入之前，请先耕耘你自己的灵魂森林<br>这是为了确保每一次连接都是信号，而非噪音",
        "lock_stat": "意义节点已生成",
        "chat_signals": "信号源", "chat_no_res": "未侦测到共鸣。", "chat_transmit": "发送至", "chat_no_data": "暂无数据交换。", "chat_sel": "选择一个频率频道以开始。",
        "world_lock": "全球层级已锁定", "world_only": "唯有耕耘过自己花园的人，方可见森林。",
        "world_proto_title": "协议声明", "world_proto_text": "你即将进入 **集体意识层**。身份已被遮蔽，唯有意义可见。",
        "world_accept": "接受协议",

        # --- 新版引导 (文案微调：去掉生硬换行) ---
        "s0_main": "欢迎。\n\n这里不是催促你得出结论的地方。\n\n更多时候，我们只是把事情放慢一点。",
        "s0_btn": "继续",

        "s1_main": "你说话。\n我们不急着回答。\n\n我们先看看，你在乎的是什么。",
        "s1_sub": "放心，不会给你打分。",
        "s1_btn": "下一步",

        "s2_main": "有些话会慢慢变得重要。\n有些不会。\n\n这不是筛选，\n只是时间在做它该做的事。",
        "s2_sub": "你不用担心说错。\n大多数时候，意义只是还没来。",
        "s2_btn1": "我明白了", "s2_btn2": "我再看看",

        "s3_main": "我不会替你思考。\n\n我只是在你思考的时候，\n把轮廓放在一旁。",
        "s3_sub": "如果你觉得这些轮廓并不准确，忽略它们就好。\n它们本来也不是结论。",
        "s3_btn": "继续",

        "s4_main": "有些话会变成一张卡片。\n\n它们不会评判你。\n只是记录：你曾经在这里想过。",
        "s4_sub": "当然，大多数话什么也不会发生。",
        "s4_btn1": "很好", "s4_btn2": "有点残忍",

        "s5_main": "你不会被推着社交，也不会被突然配对。\n\n如果有人靠近你，\n通常是因为你们在乎过相似的东西。",
        "s5_sub": "是的，这比“兴趣相同”麻烦一点。",
        "s5_btn": "继续",

        "s6_main": "当你积累了一些意义卡，你会看到一个世界。\n\n那不是新闻，也不是发生了什么。\n\n更像是——你在乎的东西在这里亮了起来。",
        "s6_sub": "有些地方会一直模糊。那也很正常。",
        "s6_btn": "继续",

        "s7_main": "你可以现在就说点什么。\n也可以什么都不说。\n\nMSC 都不会介意。",
        "s7_sub": "毕竟，意义这件事，从来不是强求来的。",
        "s7_btn": "开始对话"
    }
}

def get_text(key):
    lang = st.session_state.get('language', 'en')
    return TRANSLATIONS[lang].get(key, key)### msc_i18n.py ###

import streamlit as st

# ==========================================
# 🌍 语言包定义 (Translation Dictionary)
# ==========================================
TRANSLATIONS = {
    "en": {
        # --- 通用 ---
        "login_tab": "LOGIN", "signup_tab": "SIGN UP",
        "identity": "IDENTITY", "key": "KEY", "connect": "CONNECT UPLINK",
        "new_id": "NEW ID", "new_pw": "NEW PW", "nick": "NICK", "region": "REGION", "init": "INITIALIZE PROTOCOL",
        "signal_lost": "Signal Lost: Invalid Credentials", "created": "Identity Created. Please Login.",
        "lock_title": "SIGNAL TRANSMITTER LOCKED",
        "lock_msg": "Deep Connection requires Deep Self.<br>You need to cultivate a denser forest before you can invite others in.<br>This is to ensure every connection here is meaningful, not noise.",
        "lock_stat": "Meaning Nodes Generated",
        "chat_signals": "Signals", "chat_no_res": "No resonance detected.", "chat_transmit": "Transmit to", "chat_no_data": "No data exchange yet.", "chat_sel": "Select a frequency channel to begin.",
        "world_lock": "GLOBAL LAYER LOCKED", "world_only": "Only those who cultivate their own garden may view the forest.",
        "world_proto_title": "The Protocol", "world_proto_text": "You are entering the **Collective Mind Layer**. Identities are masked. Only meaning is visible.",
        "world_accept": "Accept Protocol",

        # --- 新版引导 (Arrival Style) ---
        "s0_main": "Welcome.<br><br>This is not a place<br>to rush to conclusions.<br><br>Mostly,<br>we just slow things<br>down a little.",
        "s0_btn": "Continue",
        
        "s1_main": "You speak.<br><br>We don't rush to answer.<br><br>We observe first,<br>what you truly care about.",
        "s1_sub": "Rest assured,<br>there is no scoring here.",
        "s1_btn": "Next",

        "s2_main": "Some words<br>will slowly become important.<br><br>Some will not.<br><br>This is not a filter.<br>It is simply time<br>doing what it does.",
        "s2_sub": "Don't worry about being wrong.<br>Most of the time,<br>meaning just hasn't<br>arrived yet.",
        "s2_btn1": "I see", "s2_btn2": "Let me look",

        "s3_main": "I won't think for you.<br><br>I simply<br>place an outline aside<br>while you think.",
        "s3_sub": "If these outlines<br>feel inaccurate,<br>just ignore them.<br><br>They were never conclusions.",
        "s3_btn": "Continue",

        "s4_main": "Some thoughts<br>will become a card.<br><br>They won't judge you.<br><br>Just a record:<br>You thought about this here.",
        "s4_sub": "Of course,<br>for most words,<br>nothing happens.",
        "s4_btn1": "Good", "s4_btn2": "A bit cruel",

        "s5_main": "You won't be pushed to socialize.<br><br>Nor suddenly matched.<br><br>If someone approaches,<br>it's usually because<br>you cared about<br>similar things.",
        "s5_sub": "Yes,<br>this is more troublesome<br>than 'shared interests'.",
        "s5_btn": "Continue",

        "s6_main": "When you accumulate meaning,<br><br>you will see a world.<br><br>It's not news,<br>nor events.<br><br>More like—<br>what you care about<br>lighting up somewhere.",
        "s6_sub": "Some places<br>will remain blurry.<br><br>That is also normal.",
        "s6_btn": "Continue",

        "s7_main": "You can say something now.<br><br>Or say nothing at all.<br><br>MSC doesn't mind.",
        "s7_sub": "After all,<br>meaning<br>can never be forced.",
        "s7_btn": "Begin Dialogue"
    },
    "zh": {
        # --- 通用 ---
        "login_tab": "登入", "signup_tab": "注册",
        "identity": "身份ID", "key": "密钥", "connect": "接入链路",
        "new_id": "新账户名", "new_pw": "新密码", "nick": "代号", "region": "区域", "init": "初始化协议",
        "signal_lost": "信号丢失：无效的凭证", "created": "身份已创建，请登入。",
        "lock_title": "信号发射器已锁定",
        "lock_msg": "深度的连接 · 始于深度的自我。<br>在邀请他人进入之前，请先耕耘你自己的灵魂森林。<br>这是为了确保每一次连接都是信号，而非噪音。",
        "lock_stat": "意义节点已生成",
        "chat_signals": "信号源", "chat_no_res": "未侦测到共鸣。", "chat_transmit": "发送至", "chat_no_data": "暂无数据交换。", "chat_sel": "选择一个频率频道以开始。",
        "world_lock": "全球层级已锁定", "world_only": "唯有耕耘过自己花园的人，方可见森林。",
        "world_proto_title": "协议声明", "world_proto_text": "你即将进入 **集体意识层**。身份已被遮蔽，唯有意义可见。",
        "world_accept": "接受协议",

        # --- 新版引导 (Arrival Style) ---
        "s0_main": "欢迎。<br><br>这里不是催促你得出结论的地方。<br><br>更多时候，<br>我们只是把事情<br>放慢一点。",
        "s0_btn": "继续",

        "s1_main": "你说话。<br><br>我们不急着回答。<br><br>我们先看看，<br>你在乎的是什么。",
        "s1_sub": "放心，<br>不会给你打分。",
        "s1_btn": "下一步",

        "s2_main": "有些话<br>会慢慢变得重要。<br><br>有些不会。<br><br>这不是筛选。<br>只是时间<br>在做它该做的事。",
        "s2_sub": "你不用担心说错。<br>大多数时候，<br>意义只是<br>还没来。",
        "s2_btn1": "我明白了", "s2_btn2": "我再看看",

        "s3_main": "我不会替你思考。<br><br>我只是<br>在你思考的时候，<br>把轮廓<br>放在一旁。",
        "s3_sub": "如果你觉得这些轮廓<br>并不准确，<br>忽略它们就好。<br><br>它们本来也不是结论。",
        "s3_btn": "继续",

        "s4_main": "有些话<br>会变成一张卡片。<br><br>它们不会评判你。<br><br>只是记录：<br>你曾经在这里想过。",
        "s4_sub": "当然，<br>大多数话<br>什么也不会发生。",
        "s4_btn1": "很好", "s4_btn2": "有点残忍",

        "s5_main": "你不会被推着社交。<br><br>也不会被突然配对。<br><br>如果有人靠近你，<br>通常是因为<br>你们在乎过<br>相似的东西。",
        "s5_sub": "是的，<br>这比“兴趣相同”<br>麻烦一点。",
        "s5_btn": "继续",

        "s6_main": "当你积累了一些意义卡，<br><br>你会看到一个世界。<br><br>那不是新闻，<br>也不是发生了什么。<br><br>更像是——<br>你在乎的东西<br>在这里亮了起来。",
        "s6_sub": "有些地方<br>会一直模糊。<br><br>那也很正常。",
        "s6_btn": "继续",

        "s7_main": "你可以现在就说点什么。<br><br>也可以什么都不说。<br><br>MSC 都不会介意。",
        "s7_sub": "毕竟，<br>意义这件事，<br>从来不是强求来的。",
        "s7_btn": "开始对话"
    }
}

def get_text(key):
    lang = st.session_state.get('language', 'en')
    return TRANSLATIONS[lang].get(key, key)
