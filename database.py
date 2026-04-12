import sqlite3
import hashlib
import os
import pandas as pd
from datetime import datetime, date

# 强制云端每次重建数据库
DB_PATH = ":memory:"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def hash_pw(p):
    return hashlib.sha256(p.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 用户表
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

    # 物品表
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

    # 认领申请表
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
    c.execute("INSERT OR IGNORE INTO settings (key,value) VALUES ('announcement','欢迎使用校园失物招领平台！')")

    # 账号
    c.execute("INSERT OR IGNORE INTO users (student_id,password,name,role) VALUES ('admin','"+hash_pw("123456")+"','管理员','admin')")
    c.execute("INSERT OR IGNORE INTO users (student_id,password,name,role) VALUES ('2026001','"+hash_pw("123456")+"','小明','user')")

    # 每次启动都强制插入 36 条数据
    c.execute("DELETE FROM items")

    sample_items = [
        (1, "校园卡", "校园卡丢失", "蓝色贴纸", "图书馆二楼", "", "lost", "passed", "13800000001", "wx1", datetime.now()),
        (1, "身份证", "身份证遗失", "姓名小明", "校门口", "", "lost", "passed", "13800000002", "wx2", datetime.now()),
        (1, "耳机", "白色蓝牙耳机", "小米", "操场", "", "lost", "passed", "13800000003", "wx3", datetime.now()),
        (1, "钥匙", "钥匙一串", "蓝色挂件", "教学楼A", "", "lost", "passed", "13800000004", "wx4", datetime.now()),
        (1, "钱包", "黑色钱包", "有现金", "食堂", "", "lost", "passed", "13800000005", "wx5", datetime.now()),
        (1, "手表", "黑色电子表", "轻微划痕", "篮球场", "", "lost", "passed", "13800000006", "wx6", datetime.now()),
        (1, "U盘", "黑色U盘", "白色条纹", "自习室", "", "lost", "passed", "13800000007", "wx7", datetime.now()),
        (1, "眼镜", "黑框眼镜", "无划痕", "图书馆三楼", "", "lost", "passed", "13800000008", "wx8", datetime.now()),
        (1, "校园卡", "黄色校园卡", "带校徽", "食堂三楼", "", "lost", "passed", "13822220001", "wx9", datetime.now()),
        (1, "项链", "银色项链", "爱心吊坠", "宿舍楼下", "", "lost", "passed", "13822220002", "wx10", datetime.now()),

        (1, "校园卡", "捡到校园卡", "蓝色卡面", "图书馆一楼", "", "found", "passed", "13811110001", "wx11", datetime.now()),
        (1, "耳机", "捡到耳机", "白色AirPods", "教学楼B", "", "found", "passed", "13811110002", "wx12", datetime.now()),
        (1, "水杯", "捡到水杯", "粉色", "食堂二楼", "", "found", "passed", "13811110003", "wx13", datetime.now()),
        (1, "雨伞", "捡到雨伞", "黑色全自动", "校门口", "", "found", "passed", "13811110004", "wx14", datetime.now()),
        (1, "充电宝", "捡到充电宝", "白色2万毫安", "操场", "", "found", "passed", "13811110005", "wx15", datetime.now()),
        (1, "公交卡", "捡到公交卡", "羊城通", "超市", "", "found", "passed", "13811110006", "wx16", datetime.now()),
        (1, "笔记本", "捡到笔记本", "黑色封面", "自习室", "", "found", "passed", "13811110007", "wx17", datetime.now()),
        (1, "书包", "捡到书包", "蓝色双肩包", "体育馆", "", "found", "passed", "13811110008", "wx18", datetime.now()),

        (1, "计算器", "计算器丢失", "卡西欧", "教学楼C", "", "lost", "passed", "13822220003", "wx19", datetime.now()),
        (1, "手套", "黑色手套", "加绒", "操场", "", "lost", "passed", "13822220004", "wx20", datetime.now()),
        (1, "围巾", "灰色围巾", "针织", "图书馆", "", "lost", "passed", "13822220005", "wx21", datetime.now()),
        (1, "学生证", "学生证丢失", "带钢印", "行政楼", "", "lost", "passed", "13822220006", "wx22", datetime.now()),
        (1, "口红", "口红丢失", "红色", "卫生间", "", "lost", "passed", "13822220007", "wx23", datetime.now()),
        (1, "护手霜", "护手霜丢失", "铁盒", "超市", "", "lost", "passed", "13822220008", "wx24", datetime.now()),
        (1, "书签", "书签丢失", "木质", "图书馆四楼", "", "lost", "passed", "13822220009", "wx25", datetime.now()),
        (1, "水杯", "玻璃杯丢失", "透明把手", "篮球场", "", "lost", "passed", "13822220010", "wx26", datetime.now()),

        (1, "手表", "捡到手表", "白色运动", "羽毛球场", "", "found", "passed", "13833330001", "wx27", datetime.now()),
        (1, "钥匙", "捡到钥匙", "黑色扣", "停车场", "", "found", "passed", "13833330002", "wx28", datetime.now()),
        (1, "耳机", "捡到耳机", "黑色三星", "图书馆负一", "", "found", "passed", "13833330003", "wx29", datetime.now()),
        (1, "公交卡", "捡到公交卡", "北京一卡通", "地铁口", "", "found", "passed", "13833330004", "wx30", datetime.now()),
        (1, "眼镜", "捡到眼镜", "银色半框", "食堂门口", "", "found", "passed", "13833330005", "wx31", datetime.now()),
        (1, "雨伞", "捡到雨伞", "格子", "教学楼D", "", "found", "passed", "13833330006", "wx32", datetime.now()),
        (1, "充电宝", "捡到充电宝", "粉色卡通", "图书馆大厅", "", "found", "passed", "13833330007", "wx33", datetime.now()),
        (1, "钱包", "捡到钱包", "棕色短款", "校门口", "", "found", "passed", "13833330008", "wx34", datetime.now()),
        (1, "U盘", "捡到U盘", "银色金属", "自习室", "", "found", "passed", "13833330009", "wx35", datetime.now()),
        (1, "校园卡", "捡到校园卡", "红色", "体育馆", "", "found", "passed", "13833330010", "wx36", datetime.now()),
    ]

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
    lost = pd.read_sql("SELECT COUNT(*) FROM items WHERE post_type='lost' AND audit_status='passed'", conn).iloc[0,0]
    found = pd.read_sql("SELECT COUNT(*) FROM items WHERE post_type='found' AND audit_status='passed'", conn).iloc[0,0]
    waiting = pd.read_sql("SELECT COUNT(*) FROM items WHERE audit_status='pending'", conn).iloc[0,0]
    today_publish = pd.read_sql("SELECT COUNT(*) FROM items WHERE DATE(created_at)=?", conn, params=(today,)).iloc[0,0]
    today_done = pd.read_sql("SELECT COUNT(*) FROM items WHERE status='done' AND DATE(created_at)=?", conn, params=(today,)).iloc[0,0]
    conn.close()
    return {"lost":lost,"found":found,"waiting":waiting,"today_publish":today_publish,"today_done":today_done}