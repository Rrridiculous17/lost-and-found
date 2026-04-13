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

# 最简样式
st.markdown("""
<style>
    .stApp { 
        background-color: #ffffff !important; 
    }
    .stSidebar { 
        background-color: #f7f7f7 !important; 
    }
</style>
""", unsafe_allow_html=True)

# 图标配置
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
        "logged_in": False,
        "user_id": None,
        "username": None,
        "role": "user",
        "page": "首页",
        "selected_item": None,
        "page_back": "首页",
        "apply_item_id": None
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v