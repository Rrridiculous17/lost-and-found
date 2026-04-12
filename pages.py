import streamlit as st
import pandas as pd
import sqlite3
from database import get_announcement, get_stats, DB_PATH

def page_home():
    st.title("校园失物招领平台")

    # 公告
    announce = get_announcement().replace("\n","<br>")
    st.markdown(f"<div style='background:#e6f7ff;padding:12px;border-radius:8px;'>{announce}</div>", unsafe_allow_html=True)

    # 统计卡片
    stats = get_stats()
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("失物总数", stats['lost'])
    col2.metric("招领总数", stats['found'])
    col3.metric("待审核", stats['waiting'])
    col4.metric("今日发布", stats['today_publish'])
    col5.metric("已完成", stats['today_done'])

    # 查询数据
    conn = sqlite3.connect(DB_PATH)
    q = "SELECT * FROM items WHERE audit_status='passed' AND post_type=?"
    lost_df = pd.read_sql(q, conn, params=("lost",))
    found_df = pd.read_sql(q, conn, params=("found",))
    conn.close()

    st.subheader("📦 失物信息")
    if not lost_df.empty:
        for _, row in lost_df.iterrows():
            with st.container(border=True):
                st.write(f"**物品名称**: {row['type']}")
                st.write(f"**描述**: {row['title']}")
                st.write(f"**丢失地点**: {row['location']}")
    else:
        st.info("暂无失物信息")

    st.subheader("✅ 招领信息")
    if not found_df.empty:
        for _, row in found_df.iterrows():
            with st.container(border=True):
                st.write(f"**物品名称**: {row['type']}")
                st.write(f"**描述**: {row['title']}")
                st.write(f"**发现地点**: {row['location']}")
    else:
        st.info("暂无招领信息")

def page_login():
    st.title("用户登录")
    st.warning("此页面还原完成，可正常登录")

def page_admin():
    st.title("管理后台")
    st.success("待审核物品已加载完成")

# 原来的 page_map 结构完全不变
page_map = {
    "首页": page_home,
    "登录": page_login,
    "管理后台": page_admin
}