import sqlite3
import hashlib
import pandas as pd
from datetime import date

DB_PATH = "lostfound.db"

# 密码加密
def hash_pw(p):
    return hashlib.sha256(p.encode()).hexdigest()

# 初始化建表 + 自动插入数据
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT UNIQUE,
        password TEXT,
        name TEXT,
        phone TEXT,
        email TEXT,
        role TEXT DEFAULT 'user',
        created_at DATE DEFAULT (date('now'))
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        type TEXT,
        title TEXT,
        description TEXT,
        location TEXT,
        post_type TEXT,
        audit_status TEXT DEFAULT 'pending',
        contact_phone TEXT,
        contact_wechat TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')

    # 默认管理员
    try:
        c.execute("INSERT INTO users (student_id,password,name,role) VALUES (?,?,?,?)",
                  ("admin", hash_pw("123456"), "管理员", "admin"))
    except:
        pass

    # 默认公告
    try:
        c.execute("INSERT INTO settings (key,value) VALUES (?,?)",
                  ("announcement", "欢迎使用校园失物招领平台！\n请诚信发布、文明认领。"))
    except:
        pass

    # 插入演示数据
    try:
        items = [
            (1, "校园卡", "丢失校园卡", "蓝色卡贴", "图书馆二楼", "lost", "passed", "13800000001", "wx1"),
            (1, "身份证", "丢失身份证", "姓名小明", "校门口", "lost", "passed", "13800000002", "wx2"),
            (1, "耳机", "丢失蓝牙耳机", "白色小米", "操场", "lost", "passed", "13800000003", "wx3"),
            (1, "钥匙", "丢失钥匙串", "蓝色挂件", "教学楼", "lost", "passed", "13800000004", "wx4"),

            (1, "校园卡", "捡到校园卡", "蓝色卡面", "图书馆一楼", "found", "passed", "13811110001", "wx11"),
            (1, "耳机", "捡到耳机", "白色AirPods", "教学楼B", "found", "passed", "13811110002", "wx12"),
            (1, "水杯", "捡到水杯", "粉色", "食堂", "found", "passed", "13811110003", "wx13"),

            (1, "iPad", "丢失iPad", "银色平板", "图书馆", "lost", "pending", "13800000101", "wx_p1"),
            (1, "相机", "丢失相机", "黑色单反", "校园景点", "lost", "pending", "13800000102", "wx_p2"),
        ]
        c.executemany('''INSERT INTO items
            (user_id,type,title,description,location,post_type,audit_status,contact_phone,contact_wechat)
            VALUES (?,?,?,?,?,?,?,?,?)''', items)
    except:
        pass

    conn.commit()
    conn.close()

# 初始化数据库
init_db()

# ===================== 原有函数完全不变 =====================
def get_announcement():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT value FROM settings WHERE key='announcement'")
        res = c.fetchone()
        conn.close()
        return res[0] if res else "欢迎使用"
    except:
        return "欢迎使用校园失物招领平台"

def get_stats():
    try:
        conn = sqlite3.connect(DB_PATH)
        lost = pd.read_sql("SELECT COUNT(*) FROM items WHERE post_type='lost' AND audit_status='passed'", conn).iloc[0,0]
        found = pd.read_sql("SELECT COUNT(*) FROM items WHERE post_type='found' AND audit_status='passed'", conn).iloc[0,0]
        waiting = pd.read_sql("SELECT COUNT(*) FROM items WHERE audit_status='pending'", conn).iloc[0,0]
        today_pub = pd.read_sql("SELECT COUNT(*) FROM items WHERE created_at=date('now')", conn).iloc[0,0]
        conn.close()
        return {
            "lost": lost,
            "found": found,
            "waiting": waiting,
            "today_publish": today_pub,
            "today_done": 3
        }
    except:
        return {"lost":0,"found":0,"waiting":0,"today_publish":0,"today_done":0}

def login(student_id, password):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE student_id=? AND password=?",
                  (student_id, hash_pw(password)))
        res = c.fetchone()
        conn.close()
        return res
    except:
        return None

def save_announcement(content):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("REPLACE INTO settings (key,value) VALUES (?,?)", ("announcement", content))
        conn.commit()
        conn.close()
    except:
        pass

def update_password(user_id, new_pwd):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE users SET password=? WHERE id=?", (hash_pw(new_pwd), user_id))
        conn.commit()
        conn.close()
    except:
        pass