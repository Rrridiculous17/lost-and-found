import streamlit as st
import os
from config import ITEM_ICONS, MENU_ICONS
from utils import rerun


# 物品卡片
def show_item_card(item, key_prefix):
    icon = ITEM_ICONS.get(item['type'], "📦")
    date_str = item['created_at'][:10]
    status_label = "✅ 已找回" if item['status'] == "done" else ""
    with st.expander(f"{icon} {item['title']}    🕒 {date_str}    {status_label}", key=f"{key_prefix}_ex_{item['id']}"):
        st.markdown(f"""
        **📍 地点：** {item['location']}  
        **📝 描述：** {item.get('description', '无')}  
        **🔖 类型：** {item['type']}｜ **📌 类别：** {'失物' if item['post_type'] == 'lost' else '招领'}
        """)
        if st.button("查看详情", key=f"btn_{key_prefix}_{item['id']}", use_container_width=True):
            st.session_state.selected_item = dict(item)
            st.session_state.page = "详情"
            rerun()


# 侧边栏菜单
def sidebar():
    with st.sidebar:
        st.markdown("## 🎫 失物招领")
        st.divider()
        if st.session_state.logged_in:
            st.markdown(f"欢迎，{st.session_state.username}")
            if st.button("🚪 退出登录"):
                st.session_state.clear()
                from config import init_session
                init_session()
                rerun()
        else:
            st.markdown("🔒 未登录")
        st.divider()

        # 确保这里的元组第二个元素（page key）没有空格，且与 page_map 一致
        menu = [("首页", "首页"), ("登录/注册", "登录注册"), ("失物", "失物"), ("招领", "招领"),
                ("发布失物", "发布失物"), ("发布招领", "发布招领"), ("个人中心", "个人中心")]

        if st.session_state.role == "admin":
            menu.insert(0, ("公告设置", "公告设置"))
            menu.insert(0, ("管理后台", "管理后台"))

        for name, pg in menu:
            ico = MENU_ICONS.get(name, "📌")
            act = st.session_state.page == pg
            st.button(
                f"{ico} {name}",
                type="primary" if act else "secondary",
                use_container_width=True,
                key=f"m_{pg}",
                on_click=lambda p=pg: st.session_state.update({
                    "page": p,
                    "selected_item": None,
                    "page_back": st.session_state.page
                })
            )