import streamlit as st

# 页面配置
def set_page_config():
    st.set_page_config(
        page_title="校园失物招领系统",
        page_icon="🎫",
        layout="wide",
        initial_sidebar_state="expanded"
    )

set_page_config()

# 全局样式 —— 已修复滚动动画
st.markdown("""
<style>
    .stApp { background-color: #ffffff; color: #222; }
    .stSidebar { background-color: #f7f7f7; }
    .section {
        background: #fcfcfc; color: #222; border: 1px solid #eee;
        border-radius: 18px; padding: 20px; margin-bottom: 20px;
        max-height: 550px; overflow-y: auto;
    }
    .banner {
        background: linear-gradient(90deg, #e6f0ff, #dceaff);
        border-radius: 16px; padding: 18px 22px; margin-bottom: 28px;
    }

    /* ========== 修复滚动统计栏 ========== */
    .stats-marquee {
        margin-top: 10px;
        width: 100%;
        white-space: nowrap;
        overflow: hidden;
        height: 24px;
        line-height: 24px;
        background: rgba(255,255,255,0.6);
        border-radius: 6px;
        padding: 2px 10px;
    }
    .stats-content {
        display: inline-block;
        animation: stats-scroll 15s linear infinite;
    }
    @keyframes stats-scroll {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }
</style>
""", unsafe_allow_html=True)

# 图标
ITEM_ICONS = {
    "校园卡": "🪪", "钥匙": "🔑", "水杯": "🥤", "钱包": "👛",
    "书籍": "📚", "电子产品": "📱", "眼镜": "👓", "雨伞": "☂️", "其他": "📦"
}
MENU_ICONS = {
    "首页": "🏠", "登录/注册": "🔐", "失物": "📌", "招领": "🙌",
    "发布失物": "➕", "发布招领": "➕", "个人中心": "👤", "管理后台": "⚙️", "公告设置": "📢"
}

# 会话初始化
def init_session():
    defaults = {
        "logged_in": False, "user_id": None, "username": None, "role": "user",
        "page": "首页", "selected_item": None, "page_back": "首页", "apply_item_id": None
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v