import streamlit as st

# ==========================================
# 🌍 语言包定义 (Translation Dictionary)
# ==========================================
TRANSLATIONS = {
    "en": {
        "login_tab": "LOGIN", "signup_tab": "SIGN UP",
        "identity": "IDENTITY", "key": "KEY", "connect": "CONNECT UPLINK",
        "new_id": "NEW ID", "new_pw": "NEW PW", "nick": "NICK", "region": "REGION", "init": "INITIALIZE PROTOCOL",
        "signal_lost": "Signal Lost: Invalid Credentials", "created": "Identity Created. Please Login.",
        
        "ob_0_title": "First Contact", "ob_0_sub": "Don't overthink it.",
        "ob_0_text": "We need a sample of your mental frequency to calibrate the system.<br>What's occupying your RAM right now?",
        "ob_0_ph": "e.g. 'Coffee', 'Silence', 'Entropy'...", "ob_0_hint": "No one is judging. Yet. ;)", "ob_btn": "TRANSMIT",
        
        "ob_1_title": "Calibration", "ob_1_sub": "How do you deal with chaos?",
        "ob_1_text": "The system needs to know your bias.<br>When life gives you a difficult problem, you usually:",
        "ob_1_a": "Overthink it", "ob_1_a_hint": "Analyzing every detail until it hurts.",
        "ob_1_b": "Just wing it", "ob_1_b_hint": "Action first, apologies later.",
        
        "ob_2_title": "Online", "ob_2_sub": "Welcome to the Layer.",
        "ob_2_text": "Your frequency has been registered.<br>You are now a node in the network.<br><br>Remember: <b>Quality creates gravity here.</b>",
        "ob_enter": "ENTER MSC",
        
        "lock_title": "SIGNAL TRANSMITTER LOCKED",
        "lock_msg": "Deep Connection requires Deep Self.<br>You need to cultivate a denser forest before you can invite others in.<br>This is to ensure every connection here is meaningful, not noise.",
        "lock_stat": "Meaning Nodes Generated",
        
        "chat_signals": "Signals", "chat_no_res": "No resonance detected.", "chat_transmit": "Transmit to", "chat_no_data": "No data exchange yet.", "chat_sel": "Select a frequency channel to begin.",
        
        "world_lock": "GLOBAL LAYER LOCKED", "world_only": "Only those who cultivate their own garden may view the forest.",
        "world_proto_title": "The Protocol", "world_proto_text": "You are entering the **Collective Mind Layer**. Identities are masked. Only meaning is visible.",
        "world_accept": "Accept Protocol"
    },
    "zh": {
        "login_tab": "登入", "signup_tab": "注册",
        "identity": "身份ID", "key": "密钥", "connect": "接入链路",
        "new_id": "新账户名", "new_pw": "新密码", "nick": "代号", "region": "区域", "init": "初始化协议",
        "signal_lost": "信号丢失：无效的凭证", "created": "身份已创建，请登入。",
        
        "ob_0_title": "初次接触", "ob_0_sub": "别想太复杂。",
        "ob_0_text": "我们需要采集你的精神频率样本以校准系统。<br>此时此刻，什么占据了你的思绪？",
        "ob_0_ph": "例如：'咖啡'，'沉默'，'熵增'...", "ob_0_hint": "暂无评判。至少现在没有。;)", "ob_btn": "发送信号",
        
        "ob_1_title": "系统校准", "ob_1_sub": "你如何面对混乱？",
        "ob_1_text": "系统需要了解你的偏好。<br>当生活给你出一道难题时，你的本能是：",
        "ob_1_a": "过度思考", "ob_1_a_hint": "拆解每个细节，直到感到痛楚。",
        "ob_1_b": "随性而动", "ob_1_b_hint": "先行动，再道歉。",
        
        "ob_2_title": "连接成功", "ob_2_sub": "欢迎来到这一层。",
        "ob_2_text": "你的频率已注册。<br>你现在是网络中的一个节点。<br><br>切记：<b>在这里，质量即引力。</b>",
        "ob_enter": "进入 MSC",
        
        "lock_title": "信号发射器已锁定",
        "lock_msg": "深度的连接 · 始于深度的自我。<br>在邀请他人进入之前，请先耕耘你自己的灵魂森林。<br>这是为了确保每一次连接都是信号，而非噪音。",
        "lock_stat": "意义节点已生成",
        
        "chat_signals": "信号源", "chat_no_res": "未侦测到共鸣。", "chat_transmit": "发送至", "chat_no_data": "暂无数据交换。", "chat_sel": "选择一个频率频道以开始。",
        
        "world_lock": "全球层级已锁定", "world_only": "唯有耕耘过自己花园的人，方可见森林。",
        "world_proto_title": "协议声明", "world_proto_text": "你即将进入 **集体意识层**。身份已被遮蔽，唯有意义可见。",
        "world_accept": "接受协议"
    }
}

def get_text(key):
    lang = st.session_state.get('language', 'en')
    return TRANSLATIONS[lang].get(key, key)
