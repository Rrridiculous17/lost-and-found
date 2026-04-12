import streamlit as st
from database import *

def page_home():
    st.title("校园失物招领平台")
    announce = get_announcement()
    st.info(announce)

    s = get_stats()
    col1, col2, col3 = st.columns(3)
    col1.metric("失物", s["lost"])
    col2.metric("招领", s["found"])
    col3.metric("待审核", s["waiting"])

    st.subheader("失物信息")
    for item in get_items_by_type("lost"):
        with st.container(border=True):
            st.write(f"物品：{item[2]}")
            st.write(f"描述：{item[3]}")
            st.write(f"地点：{item[5]}")

    st.subheader("招领信息")
    for item in get_items_by_type("found"):
        with st.container(border=True):
            st.write(f"物品：{item[2]}")
            st.write(f"描述：{item[3]}")
            st.write(f"地点：{item[5]}")

def page_admin():
    st.title("管理后台")
    for item in get_pending_items():
        with st.container(border=True):
            st.write(f"物品：{item[2]}")
            st.write("待审核")

def page_login():
    st.title("登录")
    user = st.text_input("学号")
    pwd = st.text_input("密码", type="password")
    if st.button("登录"):
        res = login(user, pwd)
        if res:
            st.success("登录成功")
        else:
            st.error("账号或密码错误")