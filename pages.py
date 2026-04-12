from database import DB_PATH
import streamlit as st
import pandas as pd
import os
import time
import random
from datetime import datetime
from config import ITEM_ICONS
from database import *
from utils import rerun
from components import show_item_card

# 首页
def page_home():
    st.title("🎫 校园失物招领平台 🏫 🎓 📚")
    st.caption("寻回遗失物品，传递温暖与善意")
    announce = get_announcement().replace("\n","<br>")
    stats = get_stats()
    stats_text = f"🔴 失物：{stats['lost']}件｜🟢 招领：{stats['found']}件｜⏳ 待审核：{stats['waiting']}件｜🆕 今日发布：{stats['today_publish']}件｜✅ 今日已找回：{stats['today_done']}件"
    st.markdown(f"""<div class='banner'><div>{announce}</div><div class='stats-marquee'><div class='stats-content'>{stats_text}</div></div></div>""",unsafe_allow_html=True)
    col1,col2 = st.columns([6,2])
    with col1: kw = st.text_input("🔍 搜索物品/地点",placeholder="例如：校园卡、图书馆",key="home_search")
    with col2: cat = st.selectbox("📦 分类",["全部"]+list(ITEM_ICONS.keys()),key="home_cat")
    st.divider()
    col_lost,col_found = st.columns(2)
    conn = sqlite3.connect(DB_PATH)
    with col_lost:
        st.markdown(f"""<div class='section'><h3 style='color:#d13434;margin-top:0;'>🔴 失物专区</h3>""",unsafe_allow_html=True)
        q = "SELECT * FROM items WHERE post_type='lost' AND audit_status='passed'"
        params = []
        if kw:
            q += " AND (title LIKE ? OR location LIKE ?)"
            params += [f"%{kw}%",f"%{kw}%"]
        if cat!="全部":
            q += " AND type=?"
            params.append(cat)
        df = pd.read_sql(q,conn,params=params)
        if df.empty:st.info("暂无数据")
        else:
            for _,r in df.iterrows():show_item_card(r,"home_lost")
        st.markdown("</div>",unsafe_allow_html=True)
    with col_found:
        st.markdown(f"""<div class='section'><h3 style='color:#1d8f45;margin-top:0;'>🟢 招领专区</h3>""",unsafe_allow_html=True)
        q = "SELECT * FROM items WHERE post_type='found' AND audit_status='passed'"
        params = []
        if kw:
            q += " AND (title LIKE ? OR location LIKE ?)"
            params += [f"%{kw}%",f"%{kw}%"]
        if cat!="全部":
            q += " AND type=?"
            params.append(cat)
        df = pd.read_sql(q,conn,params=params)
        if df.empty:st.info("暂无数据")
        else:
            for _,r in df.iterrows():show_item_card(r,"home_found")
        st.markdown("</div>",unsafe_allow_html=True)
    conn.close()

# 公告设置
def page_announce_setting():
    st.title("📢 公告设置")
    if st.session_state.role!="admin":st.error("无权限");return
    txt = st.text_area("编辑公告",get_announcement(),height=300)
    if st.button("💾 保存"):save_announcement(txt);st.success("保存成功")

# 失物
def page_lost():
    st.title("📌 失物专区")
    kw = st.text_input("搜索失物",key="lost_search")
    cat = st.selectbox("分类",["全部"]+list(ITEM_ICONS.keys()),key="lost_cat")
    st.divider()
    conn = sqlite3.connect(DB_PATH)
    q = "SELECT * FROM items WHERE post_type='lost' AND audit_status='passed'"
    params = []
    if kw:
        q += " AND (title LIKE ? OR location LIKE ?)"
        params += [f"%{kw}%",f"%{kw}%"]
    if cat!="全部":
        q += " AND type=?"
        params.append(cat)
    df = pd.read_sql(q,conn,params=params)
    for _,r in df.iterrows():show_item_card(r,"lost")
    conn.close()

# 招领
def page_found():
    st.title("🙌 招领专区")
    kw = st.text_input("搜索招领",key="found_search")
    cat = st.selectbox("分类",["全部"]+list(ITEM_ICONS.keys()),key="found_cat")
    st.divider()
    conn = sqlite3.connect(DB_PATH)
    q = "SELECT * FROM items WHERE post_type='found' AND audit_status='passed'"
    params = []
    if kw:
        q += " AND (title LIKE ? OR location LIKE ?)"
        params += [f"%{kw}%",f"%{kw}%"]
    if cat!="全部":
        q += " AND type=?"
        params.append(cat)
    df = pd.read_sql(q,conn,params=params)
    for _,r in df.iterrows():show_item_card(r,"found")
    conn.close()

# 登录注册
def page_login_register():
    st.title("🔐 登录/注册")
    t1,t2 = st.tabs(["登录","注册"])
    with t1:
        sid = st.text_input("学号/管理员")
        pwd = st.text_input("密码",type="password")
        if st.button("登录",use_container_width=True):
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE student_id=? AND password=?",(sid,hash_pw(pwd)))
            u = c.fetchone()
            conn.close()
            if u:
                st.session_state.logged_in = True
                st.session_state.user_id = u["id"]
                st.session_state.username = u["name"]
                st.session_state.role = u["role"]
                st.success("登录成功")
                st.session_state.page = "首页"
                rerun()
            else:st.error("账号或密码错误")
        st.caption("测试账号：admin / 123456，学生账号：2026001 / 123456")
    with t2:
        sid = st.text_input("学号",key="reg_sid")
        name = st.text_input("姓名",key="reg_name")
        pwd = st.text_input("密码",type="password",key="reg_pwd")
        phone = st.text_input("手机号")
        email = st.text_input("邮箱")
        if st.button("注册",use_container_width=True):
            if not (sid and name and pwd):st.error("学号、姓名、密码不能为空");return
            try:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("INSERT INTO users (student_id,password,name,phone,email) VALUES (?,?,?,?,?)",
                          (sid,hash_pw(pwd),name,phone,email))
                conn.commit()
                conn.close()
                st.success("注册成功")
            except:st.error("学号已存在")

# 详情
def page_detail():
    it = st.session_state.get("selected_item")
    if not it:st.session_state.page="首页";rerun()
    icon = ITEM_ICONS.get(it["type"],"📦")
    st.title(f"📄 {icon} {it['title']}")
    c1,c2 = st.columns([1,1.5])
    with c1:
        img_path = it.get("image_path")
        if img_path and os.path.exists(img_path):st.image(img_path,use_column_width=True)
        else:st.info("暂无图片")
    with c2:
        st.markdown(f"**类型：** {icon} {it['type']}")
        st.markdown(f"**类别：** {'🔴 失物' if it['post_type']=='lost' else '🟢 招领'}")
        st.markdown(f"**地点：** 📍 {it['location']}")
        st.markdown(f"**描述：** {it.get('description','无')}")
        st.markdown(f"**审核状态：** {it['audit_status']}")
        st.markdown(f"**物品状态：** {'✅ 已找回' if it['status']=='done' else '🟢 正常'}")
        st.markdown(f"**电话：** {it.get('contact_phone','未填')}")
        st.markdown(f"**微信：** {it.get('contact_wechat','未填')}")
        st.markdown(f"**发布时间：** {it['created_at']}")
    st.divider()

    if st.session_state.logged_in and it['status'] != 'done' and it['post_type'] == 'found':
        if st.button("📝 申请认领", use_container_width=True):
            st.session_state.apply_item_id = it["id"]
            st.session_state.page = "申请招领"
            rerun()

    if st.session_state.logged_in and it['user_id'] == st.session_state.user_id:
        if st.button("✅ 标记已找回",type="primary",use_container_width=True):
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("UPDATE items SET status='done' WHERE id=?",(it['id'],))
            conn.commit()
            conn.close()
            st.success("已标记为已找回")
            time.sleep(0.8)
            rerun()

    if st.button("← 返回",use_container_width=True):
        st.session_state.page = st.session_state.page_back
        rerun()

# 申请招领
def page_apply():
    st.title("📝 申请认领")
    iid = st.session_state.get("apply_item_id")
    if not iid:st.error("无效申请");return

    conn = sqlite3.connect(DB_PATH)
    item = pd.read_sql("SELECT * FROM items WHERE id=?",conn,params=(iid,)).to_dict("records")
    conn.close()

    if not item:st.error("物品不存在");return
    item = item[0]

    if item['post_type'] == 'lost':
        st.error("⚠️ 失物不能申请认领，仅招领物品可认领")
        if st.button("返回详情页"):
            st.session_state.page = "详情"
            rerun()
        return

    st.subheader(f"物品：{item['title']}")
    with st.form("apply"):
        name = st.text_input("姓名")
        sid = st.text_input("学号")
        phone = st.text_input("电话")
        note = st.text_area("补充说明（物品特征/丢失时间）")
        if st.form_submit_button("提交申请",use_container_width=True):
            if name and sid and phone:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("INSERT INTO apply_records (item_id,student_id,name,phone,note,created_at) VALUES (?,?,?,?,?,?)",
                          (iid,sid,name,phone,note,datetime.now()))
                conn.commit()
                conn.close()
                st.success("提交成功，等待管理员审核")
                time.sleep(1)
                st.session_state.page = "详情"
                rerun()
            else:st.error("信息不能为空")

    if st.button("← 返回",use_container_width=True):
        st.session_state.page = "详情"
        rerun()

# 发布失物
def page_post_lost():
    if not st.session_state.logged_in:st.warning("请登录");st.session_state.page="登录注册";rerun()
    st.title("➕ 发布失物")
    with st.form("post_lost"):
        typ = st.selectbox("类型",list(ITEM_ICONS.keys()))
        title = st.text_input("名称")
        desc = st.text_area("描述")
        loc = st.text_input("丢失地点")
        phone = st.text_input("联系电话")
        wechat = st.text_input("微信")
        img = st.file_uploader("图片")
        if st.form_submit_button("提交发布",use_container_width=True):
            if title and loc:
                path = os.path.join("uploads",f"{int(time.time())}_{random.randint(1000,9999)}.png")
                if img:
                    with open(path,"wb") as f:f.write(img.getvalue())
                else:path=""
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute('''INSERT INTO items
                (user_id,type,title,description,location,image_path,post_type,audit_status,contact_phone,contact_wechat,created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
                          (st.session_state.user_id,typ,title,desc,loc,path,"lost","pending",phone,wechat,datetime.now()))
                conn.commit()
                conn.close()
                st.success("提交成功，待管理员审核")
                time.sleep(1)
                st.session_state.page="首页"
                rerun()
            else:st.error("名称和地点不能为空")

# 发布招领
def page_post_found():
    if not st.session_state.logged_in:st.warning("请登录");st.session_state.page="登录注册";rerun()
    st.title("➕ 发布招领")
    with st.form("post_found"):
        typ = st.selectbox("类型",list(ITEM_ICONS.keys()))
        title = st.text_input("名称")
        desc = st.text_area("描述")
        loc = st.text_input("捡到地点")
        phone = st.text_input("电话")
        wechat = st.text_input("微信")
        img = st.file_uploader("图片")
        if st.form_submit_button("提交发布",use_container_width=True):
            if title and loc:
                path = os.path.join("uploads",f"{int(time.time())}_{random.randint(1000,9999)}.png")
                if img:
                    with open(path,"wb") as f:f.write(img.getvalue())
                else:path=""
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute('''INSERT INTO items
                (user_id,type,title,description,location,image_path,post_type,audit_status,contact_phone,contact_wechat,created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
                          (st.session_state.user_id,typ,title,desc,loc,path,"found","pending",phone,wechat,datetime.now()))
                conn.commit()
                conn.close()
                st.success("提交成功，待管理员审核")
                time.sleep(1)
                st.session_state.page="首页"
                rerun()
            else:st.error("名称和地点不能为空")

# 管理后台
def page_admin():
    if st.session_state.role!="admin":st.error("无权限");st.session_state.page="首页";rerun()
    st.title("⚙️ 管理后台")
    t1,t2,t3,t4 = st.tabs(["待审核发布","已通过","认领申请","用户管理"])
    conn = sqlite3.connect(DB_PATH)
    with t1:
        st.subheader("待审核物品")
        df = pd.read_sql("SELECT * FROM items WHERE audit_status='pending'",conn)
        for _,r in df.iterrows():
            with st.container(border=True):
                st.write(f"物品ID：{r['id']}|{r['type']}|{r['title']}|{r['location']}")
                img_p = r['image_path']
                if img_p and os.path.exists(img_p):st.image(img_p,width=200)
                col1,col2 = st.columns(2)
                with col1:
                    if st.button("✅ 通过",key=f"item_pass_{r['id']}"):
                        c = conn.cursor()
                        c.execute("UPDATE items SET audit_status='passed' WHERE id=?",(r['id'],))
                        conn.commit()
                        rerun()
                with col2:
                    if st.button("❌ 拒绝",key=f"item_reject_{r['id']}"):
                        c = conn.cursor()
                        c.execute("UPDATE items SET audit_status='rejected' WHERE id=?",(r['id'],))
                        conn.commit()
                        rerun()
    with t2:
        df = pd.read_sql("SELECT * FROM items WHERE audit_status='passed'",conn)
        st.dataframe(df,use_container_width=True)
    with t3:
        st.subheader("认领申请审核")
        df = pd.read_sql("SELECT * FROM apply_records",conn)
        for _,r in df.iterrows():
            with st.container(border=True):
                st.write(f"申请ID：{r['id']}|物品ID：{r['item_id']}|申请人：{r['name']}({r['student_id']})")
                st.write(f"说明：{r['note']}")
                st.write(f"状态：{r['status']}")
                c1,c2 = st.columns(2)
                with c1:
                    if st.button("✅ 通过",key=f"apply_pass_{r['id']}"):
                        c = conn.cursor()
                        c.execute("UPDATE apply_records SET status='已通过' WHERE id=?",(r['id'],))
                        c.execute("UPDATE items SET status='done' WHERE id=?",(r['item_id'],))
                        conn.commit()
                        rerun()
                with c2:
                    if st.button("❌ 不通过",key=f"apply_reject_{r['id']}"):
                        c = conn.cursor()
                        c.execute("UPDATE apply_records SET status='已拒绝' WHERE id=?",(r['id'],))
                        conn.commit()
                        rerun()
    with t4:
        df = pd.read_sql("SELECT id,student_id,name,phone,role,created_at FROM users",conn)
        st.dataframe(df,use_container_width=True)
    conn.close()

# 个人中心
def page_profile():
    if not st.session_state.logged_in:st.warning("请登录");st.session_state.page="登录注册";rerun()
    st.title("👤 个人中心")
    conn = sqlite3.connect(DB_PATH)
    u = pd.read_sql("SELECT name,student_id,phone,email FROM users WHERE id=?",conn,params=(st.session_state.user_id,)).iloc[0]
    st.write(f"**姓名：** {u['name']}")
    st.write(f"**学号：** {u['student_id']}")
    st.write(f"**电话：** {u['phone'] if pd.notna(u['phone']) else '未填'}")
    st.write(f"**邮箱：** {u['email'] if pd.notna(u['email']) else '未填'}")
    st.subheader("🔐 修改密码")
    new_pw = st.text_input("新密码",type="password")
    if st.button("更新密码"):
        if new_pw:update_password(st.session_state.user_id,new_pw);st.success("密码修改成功")
        else:st.warning("请输入密码")
    st.divider()
    st.subheader("我发布的物品")
    df = pd.read_sql("SELECT * FROM items WHERE user_id=?",conn,params=(st.session_state.user_id,))
    for _,r in df.iterrows():show_item_card(r,"me")
    st.subheader("我的认领记录")
    df_apply = pd.read_sql("SELECT a.*,i.title FROM apply_records a LEFT JOIN items i ON a.item_id=i.id",conn)
    st.dataframe(df_apply,use_container_width=True)
    conn.close()

# 页面映射
page_map = {
    "首页": page_home,
    "登录注册": page_login_register,
    "失物": page_lost,
    "招领": page_found,
    "详情": page_detail,
    "申请招领": page_apply,
    "发布失物": page_post_lost,
    "发布招领": page_post_found,
    "个人中心": page_profile,
    "管理后台": page_admin,
    "公告设置": page_announce_setting
}