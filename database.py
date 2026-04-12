import sqlite3
import hashlib
import os

# 数据库文件（数据存在这里，重启不丢）
DB_FILE = "lostfound.db"

# 密码加密
def hash_pw(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ===================== 初始化：自动建表 =====================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # 用户表
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT UNIQUE,
        password TEXT,
        name TEXT,
        role TEXT DEFAULT "user"
    )''')

    # 物品表
    c.execute('''CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        type TEXT,
        title TEXT,
        description TEXT,
        location TEXT,
        post_type TEXT,
        audit_status TEXT DEFAULT "pending",
        contact_phone TEXT,
        contact_wechat TEXT
    )''')

    # 设置表（公告）
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')

    # 插入默认账号
    try:
        c.execute("INSERT INTO users (student_id, password, name, role) VALUES (?,?,?,?)",
                  ("admin", hash_pw("123456"), "管理员", "admin"))
        c.execute("INSERT INTO users (student_id, password, name, role) VALUES (?,?,?,?)",
                  ("2026001", hash_pw("123456"), "小明", "user"))
    except:
        pass

    # 插入默认公告
    try:
        c.execute("INSERT INTO settings (key, value) VALUES (?,?)",
                  ("announcement", "欢迎使用校园失物招领平台！文明发布，诚信认领～"))
    except:
        pass

    conn.commit()
    conn.close()

# ===================== 功能函数 =====================

# 获取公告
def get_announcement():
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT value FROM settings WHERE key='announcement'")
        res = c.fetchone()
        conn.close()
        return res[0] if res else "欢迎使用"
    except:
        return "欢迎使用校园失物招领平台"

# 登录
def login(student_id, password):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE student_id=? AND password=?",
                  (student_id, hash_pw(password)))
        res = c.fetchone()
        conn.close()
        return res
    except:
        return None

# 获取物品
def get_items_by_type(post_type):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT * FROM items WHERE post_type=? AND audit_status='passed'", (post_type,))
        data = c.fetchall()
        conn.close()
        return data
    except:
        return []

# 待审核列表
def get_pending_items():
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT * FROM items WHERE audit_status='pending'")
        data = c.fetchall()
        conn.close()
        return data
    except:
        return []

# 统计
def get_stats():
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM items WHERE post_type='lost' AND audit_status='passed'")
        lost = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM items WHERE post_type='found' AND audit_status='passed'")
        found = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM items WHERE audit_status='pending'")
        waiting = c.fetchone()[0]
        conn.close()
        return {"lost": lost, "found": found, "waiting": waiting, "today_publish":0, "today_done":0}
    except:
        return {"lost":0,"found":0,"waiting":0,"today_publish":0,"today_done":0}

# 插入测试数据（首页显示）
def insert_demo_data():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM items")

    demo_items = [
        (1,"校园卡","校园卡丢失","蓝色贴纸","图书馆二楼","lost","passed","13800000001","wx1"),
        (1,"身份证","身份证遗失","姓名小明","校门口","lost","passed","13800000002","wx2"),
        (1,"耳机","白色蓝牙耳机","小米","操场","lost","passed","13800000003","wx3"),
        (1,"钥匙","钥匙一串","蓝色挂件","教学楼A","lost","passed","13800000004","wx4"),
        (1,"钱包","黑色钱包","有现金","食堂","lost","passed","13800000005","wx5"),

        (1,"校园卡","捡到校园卡","蓝色卡面","图书馆一楼","found","passed","13811110001","wx11"),
        (1,"耳机","捡到耳机","白色AirPods","教学楼B","found","passed","13811110002","wx12"),
        (1,"水杯","捡到水杯","粉色","食堂二楼","found","passed","13811110003","wx13"),
        (1,"雨伞","捡到雨伞","黑色全自动","校门口","found","passed","13811110004","wx14"),

        (1,"平板","iPad丢失","银色","图书馆","lost","pending","13800000101","wxp1"),
        (1,"相机","相机遗失","黑色单反","景点","lost","pending","13800000102","wxp2"),
    ]

    c.executemany('''
        INSERT INTO items (user_id, type, title, description, location, post_type, audit_status, contact_phone, contact_wechat)
        VALUES (?,?,?,?,?,?,?,?,?)
    ''', demo_items)

    conn.commit()
    conn.close()

# 启动时初始化
init_db()
insert_demo_data()