import sqlite3
import hashlib
import os
import pandas as pd
from datetime import datetime, date

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 密码哈希
def hash_pw(p):
    return hashlib.sha256(p.encode()).hexdigest()

# 初始化数据库
def init_db():
    conn = sqlite3.connect("lost_found_final.db")
    c = conn.cursor()

    # 用户表
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, student_id TEXT UNIQUE, password TEXT,
        name TEXT, phone TEXT, email TEXT, role TEXT DEFAULT 'user', created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    # 物品表
    c.execute('''CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, type TEXT, title TEXT,
        description TEXT, location TEXT, image_path TEXT,
        post_type TEXT, audit_status TEXT DEFAULT 'pending', status TEXT DEFAULT 'active',
        contact_phone TEXT, contact_wechat TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    # 认领申请表
    c.execute('''CREATE TABLE IF NOT EXISTS apply_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT, item_id INTEGER, student_id TEXT,
        name TEXT, phone TEXT, note TEXT, status TEXT DEFAULT '待审核', created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    # 系统设置表
    c.execute('''CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)''')
    c.execute("SELECT * FROM settings WHERE key='announcement'")
    if not c.fetchone():
        c.execute("INSERT INTO settings (key,value) VALUES (?,?)", ("announcement", """📢 系统公告：
1. 失物招领审核时间为1-3个工作日，请耐心等待
2. 发布信息务必真实，上传清晰物品图片
3. 冒用信息将被拉黑处理
4. 物品找回后请及时标记"""))

    # 管理员账号
    c.execute("SELECT * FROM users WHERE student_id='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users (student_id,password,name,role) VALUES (?,?,?,?)",
                  ("admin", hash_pw("123456"), "管理员", "admin"))

    # 测试学生账号
    c.execute("SELECT * FROM users WHERE student_id='2026001'")
    if not c.fetchone():
        c.execute("INSERT INTO users (student_id,password,name,role) VALUES (?,?,?,?)",
                  ("2026001", hash_pw("123456"), "测试学生", "user"))

    # 测试物品
    c.execute("SELECT COUNT(*) FROM items")
    if c.fetchone()[0] == 0:
        sample_items = [
            (1, "校园卡", "丢失校园卡一张", "图书馆二楼", "", "lost", "pending", "13800138000", "wx_admin", datetime.now()),
            (1, "钥匙", "一串钥匙，有蓝色挂件", "教学楼A座", "", "lost", "pending", "13800138000", "wx_admin", datetime.now()),
            (1, "水杯", "不锈钢保温杯", "食堂一层", "", "found", "pending", "13800138000", "wx_admin", datetime.now())
        ]
        c.executemany('''
            INSERT INTO items (user_id, type, title, description, location, image_path, post_type, audit_status, contact_phone, contact_wechat, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        ''', sample_items)

    # 视图
    c.execute('''
    CREATE VIEW IF NOT EXISTS view_published_found_items AS
    SELECT items.*, users.name AS publisher_name
    FROM items
    JOIN users ON items.user_id = users.id
    WHERE items.post_type = 'found' AND items.audit_status = 'passed'
    ''')

    # 触发器
    c.execute('''
    CREATE TRIGGER IF NOT EXISTS trigger_apply_update_item_status
    AFTER INSERT ON apply_records
    FOR EACH ROW
    BEGIN
        UPDATE items SET status = 'processing' WHERE id = NEW.item_id;
    END;
    ''')

    c.execute('''
    CREATE TRIGGER IF NOT EXISTS trigger_delete_item_cascade_apply
    BEFORE DELETE ON items
    FOR EACH ROW
    BEGIN
        DELETE FROM apply_records WHERE item_id = OLD.id;
    END;
    ''')

    conn.commit()
    conn.close()

# 获取公告
def get_announcement():
    conn = sqlite3.connect("lost_found_final.db")
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key='announcement'")
    res = c.fetchone()
    conn.close()
    return res[0] if res else ""

# 保存公告
def save_announcement(content):
    conn = sqlite3.connect("lost_found_final.db")
    c = conn.cursor()
    c.execute("UPDATE settings SET value=? WHERE key='announcement'", (content,))
    conn.commit()
    conn.close()

# 修改密码
def update_password(user_id, new_pwd):
    conn = sqlite3.connect("lost_found_final.db")
    c = conn.cursor()
    c.execute("UPDATE users SET password=? WHERE id=?", (hash_pw(new_pwd), user_id))
    conn.commit()
    conn.close()

# 统计数据
def get_stats():
    today = date.today().strftime("%Y-%m-%d")
    conn = sqlite3.connect("lost_found_final.db")
    lost = pd.read_sql("SELECT COUNT(*) FROM items WHERE post_type='lost' AND audit_status='passed'", conn).iloc[0,0]
    found = pd.read_sql("SELECT COUNT(*) FROM items WHERE post_type='found' AND audit_status='passed'", conn).iloc[0,0]
    waiting = pd.read_sql("SELECT COUNT(*) FROM items WHERE audit_status='pending'", conn).iloc[0,0]
    today_publish = pd.read_sql("SELECT COUNT(*) FROM items WHERE DATE(created_at)=?", conn, params=(today,)).iloc[0,0]
    today_done = pd.read_sql("SELECT COUNT(*) FROM items WHERE status='done' AND DATE(created_at)=?", conn, params=(today,)).iloc[0,0]
    conn.close()
    return {"lost":lost,"found":found,"waiting":waiting,"today_publish":today_publish,"today_done":today_done}