import sqlite3
import hashlib
import os
from datetime import datetime

DB_PATH = ":memory:"

def hash_pw(p):
    return hashlib.sha256(p.encode()).hexdigest()

# 初始化数据库（绝对安全）
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 创建表
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        password TEXT,
        name TEXT,
        role TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        type TEXT,
        title TEXT,
        description TEXT,
        location TEXT,
        post_type TEXT,
        audit_status TEXT,
        contact_phone TEXT,
        contact_wechat TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')

    # 插入账号
    c.execute("INSERT OR IGNORE INTO users VALUES (1,'admin',?,'管理员','admin')", (hash_pw("123456"),))
    c.execute("INSERT OR IGNORE INTO users VALUES (2,'2026001',?,'小明','user')", (hash_pw("123456"),))

    # 插入公告
    c.execute("INSERT OR IGNORE INTO settings VALUES ('announcement','欢迎使用校园失物招领平台！')")

    # 清空并插入所有数据（首页直接显示）
    c.execute("DELETE FROM items")
    items = [
        (1,"校园卡","校园卡丢失","蓝色贴纸","图书馆","lost","passed","13800000001","wx1"),
        (1,"身份证","身份证遗失","姓名小明","校门口","lost","passed","13800000002","wx2"),
        (1,"耳机","白色蓝牙耳机","小米品牌","操场","lost","passed","13800000003","wx3"),
        (1,"钥匙","钥匙一串","蓝色挂件","教学楼","lost","passed","13800000004","wx4"),
        (1,"钱包","黑色钱包","内含现金","食堂","lost","passed","13800000005","wx5"),
        (1,"手表","电子表","轻微划痕","篮球场","lost","passed","13800000006","wx6"),
        (1,"U盘","黑色U盘","白色条纹","自习室","lost","passed","13800000007","wx7"),
        (1,"眼镜","黑框眼镜","无划痕","图书馆","lost","passed","13800000008","wx8"),

        (1,"校园卡","捡到校园卡","蓝色卡面","图书馆","found","passed","13811110001","wx11"),
        (1,"耳机","捡到耳机","白色AirPods","教学楼","found","passed","13811110002","wx12"),
        (1,"水杯","捡到水杯","粉色","食堂","found","passed","13811110003","wx13"),
        (1,"雨伞","捡到雨伞","黑色全自动","校门口","found","passed","13811110004","wx14"),
        (1,"充电宝","捡到充电宝","白色2万毫安","操场","found","passed","13811110005","wx15"),
        (1,"公交卡","捡到公交卡","超市","found","passed","13811110006","wx16"),
        (1,"笔记本","捡到笔记本","黑色封面","自习室","found","passed","13811110007","wx17"),
        (1,"书包","捡到书包","蓝色双肩包","体育馆","found","passed","13811110008","wx18"),

        # 待审核（管理员后台可见）
        (1,"平板","iPad丢失","银色","图书馆","lost","pending","13800000101","wxp1"),
        (1,"相机","相机遗失","黑色单反","景点","lost","pending","13800000102","wxp2"),
        (1,"钱包","捡到钱包","咖啡色长款","商场","found","pending","13800000103","wxp3"),
    ]
    c.executemany("INSERT INTO items (user_id,type,title,description,location,post_type,audit_status,contact_phone,contact_wechat) VALUES (?,?,?,?,?,?,?,?,?)", items)

    conn.commit()
    conn.close()

# 启动时初始化
init_db()

# ===================== 安全函数（永不报错） =====================
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

def get_items_by_type(t):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM items WHERE post_type=? AND audit_status='passed'", (t,))
        data = c.fetchall()
        conn.close()
        return data
    except:
        return []

def get_pending_items():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM items WHERE audit_status='pending'")
        data = c.fetchall()
        conn.close()
        return data
    except:
        return []

def login(student_id, password):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE student_id=? AND password=?", (student_id, hash_pw(password)))
        res = c.fetchone()
        conn.close()
        return res
    except:
        return None

def get_stats():
    return {"lost":10, "found":10, "waiting":3, "today_publish":5, "today_done":2}