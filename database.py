import sqlite3
import hashlib

DB_FILE = "lostfound.db"

# 密码加密
def hash_pw(p):
    return hashlib.sha256(p.encode()).hexdigest()

# ===================== 初始化数据库（自动建表） =====================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # 用户表
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT UNIQUE,
        password TEXT,
        name TEXT,
        role TEXT
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
        audit_status TEXT,
        contact_phone TEXT,
        contact_wechat TEXT
    )''')

    # 设置表
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')

    # 默认账号
    try:
        c.execute("INSERT OR IGNORE INTO users VALUES (1,'admin',?,'管理员','admin')", (hash_pw("123456"),))
        c.execute("INSERT OR IGNORE INTO users VALUES (2,'2026001',?,'小明','user')", (hash_pw("123456"),))
    except:
        pass

    # 默认公告
    try:
        c.execute("INSERT OR IGNORE INTO settings VALUES ('announcement','欢迎使用校园失物招领平台！请诚信发布，文明认领～')")
    except:
        pass

    conn.commit()
    conn.close()

# ===================== 插入完整演示数据（首页显示） =====================
def insert_demo_data():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # 清空旧数据
    c.execute("DELETE FROM items")

    demo_items = [
        # 失物 (lost)
        (1, "校园卡", "校园卡丢失", "蓝色贴纸", "图书馆二楼", "lost", "passed", "13800000001", "wx123"),
        (1, "身份证", "身份证遗失", "姓名小明", "校门口", "lost", "passed", "13800000002", "wx456"),
        (1, "蓝牙耳机", "白色耳机", "小米品牌", "操场", "lost", "passed", "13800000003", "wx789"),
        (1, "钥匙", "钥匙一串", "蓝色挂件", "教学楼A", "lost", "passed", "13800000004", "wx001"),
        (1, "钱包", "黑色钱包", "内含现金", "食堂", "lost", "passed", "13800000005", "wx002"),
        (1, "手表", "电子表", "黑色表带", "篮球场", "lost", "passed", "13800000006", "wx003"),
        (1, "U盘", "黑色U盘", "白色条纹", "自习室", "lost", "passed", "13800000007", "wx004"),
        (1, "眼镜", "黑框眼镜", "无划痕", "图书馆三楼", "lost", "passed", "13800000008", "wx005"),

        # 招领 (found)
        (1, "校园卡", "捡到校园卡", "蓝色卡面", "图书馆一楼", "found", "passed", "13811110001", "wx111"),
        (1, "耳机", "捡到耳机", "白色AirPods", "教学楼B", "found", "passed", "13811110002", "wx222"),
        (1, "水杯", "捡到水杯", "粉色", "食堂二楼", "found", "passed", "13811110003", "wx333"),
        (1, "雨伞", "捡到雨伞", "黑色全自动", "校门口", "found", "passed", "13811110004", "wx444"),
        (1, "充电宝", "捡到充电宝", "白色2万毫安", "操场", "found", "passed", "13811110005", "wx555"),
        (1, "书包", "捡到书包", "蓝色双肩包", "体育馆", "found", "passed", "13811110006", "wx666"),

        # 待审核（管理员后台可见）
        (1, "iPad", "iPad丢失", "银色", "图书馆", "lost", "pending", "13800000101", "wx_p1"),
        (1, "相机", "相机遗失", "黑色单反", "校园景点", "lost", "pending", "13800000102", "wx_p2"),
        (1, "钱包", "捡到钱包", "咖啡色长款", "商场", "found", "pending", "13800000103", "wx_p3"),
    ]

    c.executemany('''
        INSERT INTO items (user_id, type, title, description, location, post_type, audit_status, contact_phone, contact_wechat)
        VALUES (?,?,?,?,?,?,?,?,?)
    ''', demo_items)

    conn.commit()
    conn.close()

# ===================== 功能函数 =====================
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
        return {"lost":0,"found":0,"waiting":0}

# ===================== 启动时自动运行 =====================
init_db()
insert_demo_data()