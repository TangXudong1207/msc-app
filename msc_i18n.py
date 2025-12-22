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

        # --- 新手引导 (v2.0 Poetic) ---
        "s1_main": "Here is:<br><br>A corner of the library<br>lit late into the night.<br><br>A bar, not noisy,<br>but with quiet whispers.<br><br>A space where one<br>can simply speak.",
        "s1_btn": "Enter",

        "s2_main": "People here:<br><br>Unfinished thoughts are common.<br>Perfect expressions are rare.<br>Unresolved questions are everywhere.<br><br>You don't need to rush to be the former,<br>nor fear being the latter.",
        "s2_btn": "Understood",

        "s3_main": "Here you will:<br><br>Slowly see the world.<br><br>Slowly find sincere friends in thought,<br>or lifelong rivals.",
        "s3_btn": "Begin Journey"
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

        # --- 新手引导 (v2.0 Poetic) ---
        "s1_main": "这里是：<br><br>深夜还亮着灯的<br>图书馆一角。<br><br>不吵闹、<br>但有人低声交谈的酒吧。<br><br>一个人可以说话的空间。",
        "s1_btn": "进入",

        "s2_main": "这里的人：<br><br>不成熟的思想司空见惯，<br>对的表达凤毛麟角，<br>没想清楚的问题比比皆是。<br><br>你不用急着成为前者，<br>也不用害怕自己属于后者。",
        "s2_btn": "明白了",

        "s3_main": "这里你会：<br><br>慢慢看到世界，<br><br>慢慢拥有思想上的<br>真挚朋友<br>或一生宿敌。",
        "s3_btn": "开始旅程"
    }
}

def get_text(key):
    lang = st.session_state.get('language', 'en')
    return TRANSLATIONS[lang].get(key, key)
