import sqlite3
import hashlib
import os
import pandas as pd
from datetime import datetime, date

# 强制内存数据库，每次启动全新数据，无缓存
DB_PATH = ":memory:"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def hash_pw(p):
    return hashlib.sha256(p.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 1. 先删除所有表，彻底重置，避免旧表结构冲突
    c.execute("DROP TABLE IF EXISTS users")
    c.execute("DROP TABLE IF EXISTS items")
    c.execute("DROP TABLE IF EXISTS apply_records")
    c.execute("DROP TABLE IF EXISTS settings")

    # 2. 重新创建所有表，结构100%正确
    c.execute('''CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT UNIQUE,
        password TEXT,
        name TEXT,
        phone TEXT,
        email TEXT,
        role TEXT DEFAULT 'user',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE items (
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

    c.execute('''CREATE TABLE apply_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER,
        student_id TEXT,
        name TEXT,
        phone TEXT,
        note TEXT,
        status TEXT DEFAULT '待审核',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')

    # 3. 强制插入公告，100%确保settings表有数据
    c.execute("INSERT INTO settings (key, value) VALUES (?, ?)",
              ("announcement", "欢迎使用校园失物招领平台！\n1. 失物招领审核时间为1-3个工作日，请耐心等待\n2. 发布信息务必真实，上传清晰物品图片\n3. 冒用信息将被拉黑处理\n4. 物品找回后请及时标记"))

    # 4. 插入管理员和测试账号
    c.execute("INSERT INTO users (student_id, password, name, role) VALUES (?, ?, ?, ?)",
              ("admin", hash_pw("123456"), "系统管理员", "admin"))
    c.execute("INSERT INTO users (student_id, password, name, role) VALUES (?, ?, ?, ?)",
              ("2026001", hash_pw("123456"), "测试用户", "user"))

    # 5. 插入首页展示数据（36条，全部passed）
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
        (1, "校园卡", "黄色校园卡", "带校徽", "食堂三楼", "", "lost", "passed", "13822220001", "wx_a1", datetime.now()),
        (1, "项链", "银色项链", "吊坠是小爱心", "女生宿舍楼下", "", "lost", "passed", "13822220002", "wx_a2", datetime.now()),
        (1, "计算器", "科学计算器", "卡西欧黑色", "教学楼C座", "", "lost", "passed", "13822220003", "wx_a3", datetime.now()),
        (1, "手套", "黑色手套", "冬季加绒", "操场入口", "", "lost", "passed", "13822220004", "wx_a4", datetime.now()),
        (1, "围巾", "灰色围巾", "针织材质", "图书馆门口", "", "lost", "passed", "13822220005", "wx_a5", datetime.now()),
        (1, "学生证", "学生证丢失", "带有照片和钢印", "行政楼", "", "lost", "passed", "13822220006", "wx_a6", datetime.now()),
        (1, "口红", "品牌口红", "红色系", "女卫生间", "", "lost", "passed", "13822220007", "wx_a7", datetime.now()),
        (1, "护手霜", "护手霜", "圆形铁盒", "超市", "", "lost", "passed", "13822220008", "wx_a8", datetime.now()),
        (1, "书签", "木质书签", "刻有文字", "图书馆四楼", "", "lost", "passed", "13822220009", "wx_a9", datetime.now()),
        (1, "水杯", "玻璃杯", "透明带把手", "篮球场旁", "", "lost", "passed", "13822220010", "wx_a10", datetime.now()),

        # 招领 found
        (1, "校园卡", "捡到校园卡", "蓝色卡面，学号2025123", "图书馆一楼", "", "found", "passed", "13811110001", "wx_123", datetime.now()),
        (1, "耳机", "捡到耳机", "白色AirPods，左耳有小印记", "教学楼B座", "", "found", "passed", "13811110002", "wx_456", datetime.now()),
        (1, "水杯", "捡到水杯", "粉色保温杯，有卡通图案", "食堂二楼", "", "found", "passed", "13811110003", "wx_789", datetime.now()),
        (1, "雨伞", "捡到雨伞", "黑色全自动雨伞", "校门口", "", "found", "passed", "13811110004", "wx_000", datetime.now()),
        (1, "充电宝", "捡到充电宝", "白色20000毫安", "操场看台", "", "found", "passed", "13811110005", "wx_999", datetime.now()),
        (1, "公交卡", "捡到公交卡", "羊城通，表面有贴纸", "超市门口", "", "found", "passed", "13811110006", "wx_888", datetime.now()),
        (1, "笔记本", "捡到笔记本", "黑色封面，写满笔记", "自习室", "", "found", "passed", "13811110007", "wx_777", datetime.now()),
        (1, "书包", "捡到书包", "蓝色双肩包，有挂件", "体育馆", "", "found", "passed", "13811110008", "wx_666", datetime.now()),
        (1, "手表", "捡到手表", "白色运动手表", "羽毛球场", "", "found", "passed", "13833330001", "wx_b1", datetime.now()),
        (1, "钥匙", "捡到钥匙", "黑色钥匙扣", "停车场", "", "found", "passed", "13833330002", "wx_b2", datetime.now()),
        (1, "耳机", "捡到耳机", "黑色三星耳机", "图书馆负一楼", "", "found", "passed", "13833330003", "wx_b3", datetime.now()),
        (1, "公交卡", "捡到公交卡", "上海一卡通", "地铁站出口", "", "found", "passed", "13833330004", "wx_b4", datetime.now()),
        (1, "眼镜", "捡到眼镜", "银色半框眼镜", "食堂门口", "", "found", "passed", "13833330005", "wx_b5", datetime.now()),
        (1, "雨伞", "捡到雨伞", "格子图案雨伞", "教学楼D座", "", "found", "passed", "13833330006", "wx_b6", datetime.now()),
        (1, "充电宝", "捡到充电宝", "粉色卡通充电宝", "图书馆大厅", "", "found", "passed", "13833330007", "wx_b7", datetime.now()),
        (1, "钱包", "捡到钱包", "棕色短款钱包", "校门口花坛", "", "found", "passed", "13833330008", "wx_b8", datetime.now()),
        (1, "U盘", "捡到U盘", "银色金属U盘", "自习室座位", "", "found", "passed", "13833330009", "wx_b9", datetime.now()),
        (1, "校园卡", "捡到校园卡", "红色卡面", "体育馆门口", "", "found", "passed", "13833330010", "wx_b10", datetime.now()),
    ]

    # 6. 插入待审核数据（5条，管理员后台可见）
    pending_items = [
        (1, "平板", "iPad丢失", "银色平板，11寸", "图书馆自习区", "", "lost", "pending", "13800000101", "wx_p1", datetime.now()),
        (1, "相机", "相机遗失", "黑色单反相机", "校园景点", "", "lost", "pending", "13800000102", "wx_p2", datetime.now()),
        (1, "钱包", "捡到钱包", "咖啡色长款钱包", "商场门口", "", "found", "pending", "13800000103", "wx_p3", datetime.now()),
        (1, "书", "专业课本", "考研数学复习全书", "教室座位", "", "lost", "pending", "13800000104", "wx_p4", datetime.now()),
        (1, "帽子", "黑色帽子", "鸭舌帽，有logo", "操场看台", "", "found", "pending", "13800000105", "wx_p5", datetime.now()),
    ]

    # 7. 合并数据并插入
    all_items = sample_items + pending_items
    c.executemany('''INSERT INTO items
        (user_id, type, title, description, location, image_path, post_type, audit_status, contact_phone, contact_wechat, created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)''', all_items)

    # 8. 插入认领申请（5条，管理员后台可见）
    apply_data = [
        (1, "2026111", "小红", "13899990001", "这是我的校园卡，卡面有蓝色贴纸", "待审核", datetime.now()),
        (3, "2026222", "小刚", "13899990002", "耳机是我的，左耳有小印记", "待审核", datetime.now()),
        (5, "2026333", "小李", "13899990003", "粉色水杯是我的，有卡通图案", "待审核", datetime.now()),
        (7, "2026444", "小张", "13899990004", "我丢了黑色充电宝", "待审核", datetime.now()),
        (9, "2026555", "小王", "13899990005", "棕色短款钱包是我的", "待审核", datetime.now()),
    ]
    c.executemany('''INSERT INTO apply_records
        (item_id, student_id, name, phone, note, status, created_at)
        VALUES (?,?,?,?,?,?,?)''', apply_data)

    conn.commit()
    conn.close()

# ===================== 功能函数（100%无错） =====================
def get_announcement():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key='announcement'")
    res = c.fetchone()
    conn.close()
    return res[0] if res else "欢迎使用校园失物招领平台！"

def save_announcement(content):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("REPLACE INTO settings (key, value) VALUES (?, ?)", ("announcement", content))
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
    return {"lost":lost, "found":found, "waiting":waiting, "today_publish":today_publish, "today_done":today_done}