import streamlit as st
import sqlite3
from database import *

def page_home():
    st.title("校园失物招领平台")

    # 公告
    announce = get_announcement()
    st.info(announce)

    # 统计
    stats = get_stats()
    col1, col2, col3 = st.columns(3)
    col1.metric("失物", stats["lost"])
    col2.metric("招领", stats["found"])
    col3.metric("待审核", stats["waiting"])

    # 失物列表
    st.subheader("失物信息")
    lost_items = get_items_by_type("lost")
    for item in lost_items:
        with st.container(border=True):
            st.write(f"📌 {item[2]}")
            st.write(f"📝 {item[3]}")
            st.write(f"📍 {item[5]}")

    # 招领列表
    st.subheader("招领信息")
    found_items = get_items_by_type("found")
    for item in found_items:
        with st.container(border=True):
            st.write(f"📌 {item[2]}")
            st.write(f"📝 {item[3]}")
            st.write(f"📍 {item[5]}")

def page_admin():
    st.title("管理员后台")
    pending = get_pending_items()
    for item in pending:
        with st.container(border=True):
            st.write(f"物品：{item[2]}")
            st.write(f"描述：{item[3]}")
            st.button("通过", key=f"pass{item[0]}")

def page_login():
    st.title("登录")
    user = st.text_input("学号")
    pwd = st.text_input("密码", type="password")
    if st.button("登录"):
        res = login(user, pwd)
        if res:
            st.session_state["login"] = True
            st.session_state["role"] = res[3]
            st.success("登录成功")
        else:
            st.error("账号或密码错误")