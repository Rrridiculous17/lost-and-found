import sqlite3
import hashlib
import os
import pandas as pd
from datetime import datetime, date

# 本地/云端自动适配数据库路径（重启不丢数据）
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
            (1, "校园卡", "校园卡丢失", "卡面有蓝色贴纸，学号2026001", "图书馆二楼", "", "lost", "passed", "13800000001", "wx_abc", datetime.now()),
            (1, "身份证", "身份证遗失", "姓名小明，地址XX小区", "校门口", "", "lost", "passed", "13800000002", "wx_def", datetime.now()),
            (1, "耳机", "白色蓝牙耳机", "牌子是小米，充电仓有划痕", "操场跑道", "", "lost", "passed", "13800000003", "wx_ghi", datetime.now()),
            (1, "钥匙", "钥匙一串", "有蓝色小熊挂件", "教学楼A座门口", "", "lost", "passed", "13800000004", "wx_jkl", datetime.now()),
            (1, "钱包", "黑色钱包", "里面有校园卡和现金", "食堂一楼", "", "lost", "passed", "13800000005", "wx_mno", datetime.now()),
            (1, "手表", "黑色电子表", "表盘有轻微划痕", "篮球场", "", "lost", "passed", "13800000006", "wx_pqr", datetime.now()),
            (1, "U盘", "黑色U盘", "上面有白色条纹", "自习室", "", "lost", "passed", "13800000007", "wx_stu", datetime.now()),
            (1, "眼镜", "黑框眼镜", "镜片无明显划痕", "图书馆三楼", "", "lost", "passed", "13800000008", "wx_vwx", datetime.now()),

            # 招领 found
            (1, "校园卡", "捡到校园卡", "蓝色卡面，学号2025123", "图书馆一楼", "", "found", "passed", "13811110001", "wx_123", datetime.now()),
            (1, "耳机", "捡到耳机", "白色AirPods，左耳有小印记", "教学楼B座", "", "found", "passed", "13811110002", "wx_456", datetime.now()),
            (1, "水杯", "捡到水杯", "粉色保温杯，有卡通图案", "食堂二楼", "", "found", "passed", "13811110003", "wx_789", datetime.now()),
            (1, "雨伞", "捡到雨伞", "黑色全自动雨伞", "校门口", "", "found", "passed", "13811110004", "wx_000", datetime.now()),
            (1, "充电宝", "捡到充电宝", "白色20000毫安", "操场看台", "", "found", "passed", "13811110005", "wx_999", datetime.now()),
            (1, "公交卡", "捡到公交卡", "羊城通，表面有贴纸", "超市门口", "", "found", "passed", "13811110006", "wx_888", datetime.now()),
            (1, "笔记本", "捡到笔记本", "黑色封面，写满笔记", "自习室", "", "found", "passed", "13811110007", "wx_777", datetime.now()),
            (1, "书包", "捡到书包", "蓝色双肩包，有挂件", "体育馆", "", "found", "passed", "13811110008", "wx_666", datetime.now()),

            # ====================== 追加 20 条数据 ======================
            # 失物
            (1, "校园卡", "校园卡遗失", "卡面黄色，带有校徽", "食堂三楼", "", "lost", "passed", "13822220001", "wx_a1", datetime.now()),
            (1, "项链", "银色项链", "吊坠是小爱心", "女生宿舍楼下", "", "lost", "passed", "13822220002", "wx_a2", datetime.now()),
            (1, "计算器", "科学计算器", "卡西欧黑色", "教学楼C座", "", "lost", "passed", "13822220003", "wx_a3", datetime.now()),
            (1, "手套", "黑色手套", "冬季加绒", "操场入口", "", "lost", "passed", "13822220004", "wx_a4", datetime.now()),
            (1, "围巾", "灰色围巾", "针织材质", "图书馆门口", "", "lost", "passed", "13822220005", "wx_a5", datetime.now()),
            (1, "学生证", "学生证丢失", "带有照片和钢印", "行政楼", "", "lost", "passed", "13822220006", "wx_a6", datetime.now()),
            (1, "口红", "品牌口红", "红色系", "女卫生间", "", "lost", "passed", "13822220007", "wx_a7", datetime.now()),
            (1, "护手霜", "护手霜", "圆形铁盒", "超市", "", "lost", "passed", "13822220008", "wx_a8", datetime.now()),
            (1, "书签", "木质书签", "刻有文字", "图书馆四楼", "", "lost", "passed", "13822220009", "wx_a9", datetime.now()),
            (1, "水杯", "玻璃杯", "透明带把手", "篮球场旁", "", "lost", "passed", "13822220010", "wx_a10", datetime.now()),

            # 招领
            (1, "手表", "捡到手表", "白色运动手表", "羽毛球场", "", "found", "passed", "13833330001", "wx_b1", datetime.now()),
            (1, "钥匙", "捡到钥匙", "黑色钥匙扣", "停车场", "", "found", "passed", "13833330002", "wx_b2", datetime.now()),
            (1, "耳机", "捡到耳机", "黑色三星耳机", "图书馆负一楼", "", "found", "passed", "13833330003", "wx_b3", datetime.now()),
            (1, "公交卡", "捡到公交卡", "北京一卡通", "地铁站出口", "", "found", "passed", "13833330004", "wx_b4", datetime.now()),
            (1, "眼镜", "捡到眼镜", "银色半框眼镜", "食堂门口", "", "found", "passed", "13833330005", "wx_b5", datetime.now()),
            (1, "雨伞", "捡到雨伞", "格子图案雨伞", "教学楼D座", "", "found", "passed", "13833330006", "wx_b6", datetime.now()),
            (1, "充电宝", "捡到充电宝", "粉色卡通充电宝", "图书馆大厅", "", "found", "passed", "13833330007", "wx_b7", datetime.now()),
            (1, "钱包", "捡到钱包", "棕色短款钱包", "校门口花坛", "", "found", "passed", "13833330008", "wx_b8", datetime.now()),
            (1, "U盘", "捡到U盘", "银色金属U盘", "自习室座位", "", "found", "passed", "13833330009", "wx_b9", datetime.now()),
            (1, "校园卡", "捡到校园卡", "红色卡面", "体育馆门口", "", "found", "passed", "13833330010", "wx_b10", datetime.now()),
        ]

        c.executemany('''INSERT INTO items
            (user_id,type,title,description,location,image_path,post_type,audit_status,contact_phone,contact_wechat,created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)''', sample_items)

    conn.commit()
    conn.close()

# ===================== 功能函数 =====================
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