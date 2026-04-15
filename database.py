import sqlite3
import hashlib
import os
import pandas as pd
from datetime import datetime, date

# 本地/云端自动适配数据库路径
if os.name == 'nt':
    DB_PATH = "lost_found_final.db"
else:
    DB_PATH = "/tmp/lost_found_final.db"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def hash_pw(p):
    return hashlib.sha256(p.encode()).hexdigest()


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 用户表 - 修复 em ail -> email
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT UNIQUE,
        password TEXT,
        name TEXT,
        phone TEXT,
        email TEXT,
        role TEXT DEFAULT 'user',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    # 物品表 - 修复 AU TOINCREMENT -> AUTOINCREMENT, pe nding -> pending
    c.execute('''CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        type TEXT,
        title TEXT,
        description TEXT,
        location TEXT,
        image_path TEXT,
        post_type TEXT,
        audit_status TEXT DEFAULT 'pending',
        status TEXT DEFAULT 'active',
        contact_phone TEXT,
        contact_wechat TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    # 认领申请表 - 修复 TABL E -> TABLE, DE FAULT -> DEFAULT
    c.execute('''CREATE TABLE IF NOT EXISTS apply_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER,
        student_id TEXT,
        name TEXT,
        phone TEXT,
        note TEXT,
        status TEXT DEFAULT '待审核',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    # 设置表
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')

    # 公告
    c.execute("SELECT * FROM settings WHERE key='announcement'")
    if not c.fetchone():
        c.execute("INSERT INTO settings (key,value) VALUES (?,?)",
                  ("announcement", "欢迎使用校园失物招领平台！请文明发布、诚信认领，谢谢配合～"))

    # 管理员
    c.execute("SELECT * FROM users WHERE student_id='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users (student_id,password,name,role) VALUES (?,?,?,?)",
                  ("admin", hash_pw("123456"), "管理员", "admin"))

    # 测试学生
    c.execute("SELECT * FROM users WHERE student_id='2026001'")
    if not c.fetchone():
        c.execute("INSERT INTO users (student_id,password,name,role) VALUES (?,?,?,?)",
                  ("2026001", hash_pw("123456"), "小明", "user"))

    # ========================= 大量失物招领数据（默认已通过） =========================
    c.execute("SELECT COUNT(*) FROM items")
    if c.fetchone()[0] == 0:
        sample_items = [
            # 失物 lost
            (1, "校园卡", "校园卡丢失", "卡面有蓝色贴纸，学号2026001", "图书馆二楼", "", "lost", "passed", "13800000001",
             "wx_abc", datetime.now()),
            (1, "身份证", "身份证遗失", "姓名小明，地址XX小区", "校门口", "", "lost", "passed", "13800000002", "wx_def",
             datetime.now()),
            (1, "耳机", "白色蓝牙耳机", "牌子是小米，充电仓有划痕", "操场跑道", "", "lost", "passed", "13800000003",
             "wx_ghi", datetime.now()),
            (1, "钥匙", "钥匙一串", "有蓝色小熊挂件", "教学楼A座门口", "", "lost", "passed", "13800000004", "wx_jkl",
             datetime.now()),
            (1, "钱包", "黑色钱包", "里面有校园卡和现金", "食堂一楼", "", "lost", "passed", "13800000005", "wx_mno",
             datetime.now()),
            (1, "手表", "黑色电子表", "表盘有轻微划痕", "篮球场", "", "lost", "passed", "13800000006", "wx_pqr",
             datetime.now()),
            (1, "U盘", "黑色U盘", "上面有白色条纹", "自习室", "", "lost", "passed", "13800000007", "wx_stu",
             datetime.now()),
            (1, "眼镜", "黑框眼镜", "镜片无明显划痕", "图书馆三楼", "", "lost", "passed", "13800000008", "wx_vwx",
             datetime.now()),

            # 招领 found
            (1, "校园卡", "捡到校园卡", "蓝色卡面，学号2025123", "图书馆一楼", "", "found", "passed", "13811110001",
             "wx_123", datetime.now()),
            (1, "耳机", "捡到耳机", "白色AirPods，左耳有小印记", "教学楼B座", "", "found", "passed", "13811110002",
             "wx_456", datetime.now()),
            (1, "水杯", "捡到水杯", "粉色保温杯，有卡通图案", "食堂二楼", "", "found", "passed", "13811110003", "wx_789",
             datetime.now()),
            (1, "雨伞", "捡到雨伞", "黑色全自动雨伞", "校门口", "", "found", "passed", "13811110004", "wx_000",
             datetime.now()),
            (1, "充电宝", "捡到充电宝", "白色20000毫安", "操场看台", "", "found", "passed", "13811110005", "wx_999",
             datetime.now()),
            (1, "公交卡", "捡到公交卡", "羊城通，表面有贴纸", "超市门口", "", "found", "passed", "13811110006", "wx_888",
             datetime.now()),
            (1, "笔记本", "捡到笔记本", "黑色封面，写满笔记", "自习室", "", "found", "passed", "13811110007", "wx_777",
             datetime.now()),
            (1, "书包", "捡到书包", "蓝色双肩包，有挂件", "体育馆", "", "found", "passed", "13811110008", "wx_666",
             datetime.now()),
        ]

        # 修复 cr eated_at -> created_at
        c.executemany('''INSERT INTO items
            (user_id,type,title,description,location,image_path,post_type,audit_status,contact_phone,contact_wechat,created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)''', sample_items)

    conn.commit()
    conn.close()


def get_announcement():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key='announcement'")
    res = c.fetchone()
    conn.close()
    return res[0] if res else ""


def save_announcement(content):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE settings SET value=? WHERE key='announcement'", (content,))
    conn.commit()
    conn.close()


def update_password(user_id, new_pwd):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET password=? WHERE id=?", (hash_pw(new_pwd), user_id))
    conn.commit()
    conn.close()


def get_stats():
    today = date.today().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_PATH)
    # 修复 COUNT( ) -> COUNT(*)
    lost = pd.read_sql("SELECT COUNT(*) FROM items WHERE post_type='lost' AND audit_status='passed'", conn).iloc[0, 0]
    found = pd.read_sql("SELECT COUNT(*) FROM items WHERE post_type='found' AND audit_status='passed'", conn).iloc[0, 0]
    waiting = pd.read_sql("SELECT COUNT(*) FROM items WHERE audit_status='pending'", conn).iloc[0, 0]
    today_publish = pd.read_sql("SELECT COUNT(*) FROM items WHERE DATE(created_at)=?", conn, params=(today,)).iloc[0, 0]
    today_done = \
    pd.read_sql("SELECT COUNT(*) FROM items WHERE status='done' AND DATE(created_at)=?", conn, params=(today,)).iloc[
        0, 0]
    conn.close()
    return {"lost": lost, "found": found, "waiting": waiting, "today_publish": today_publish, "today_done": today_done}