import streamlit as st
from pages import page_home, page_admin, page_login

st.set_page_config(page_title="失物招领")

if "login" not in st.session_state:
    st.session_state.login = False
    st.session_state.role = "user"

def main():
    page = st.sidebar.selectbox("页面", ["首页", "登录", "管理后台"])

    page_map = {
        "首页": page_home,
        "登录": page_login,
        "管理后台": page_admin
    }

    page_map[page]()

if __name__ == "__main__":
    main()