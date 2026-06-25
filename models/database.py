import sqlite3
from config import Config


def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            score INTEGER DEFAULT 0
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL DEFAULT '1234',
            team_name TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            weight REAL DEFAULT 1.0,
            description TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS purchase_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item_id INTEGER,
            purchase_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(item_id) REFERENCES items(id)
        )
    """)

    # 第一次建立資料庫時加入預設獎品
    if not conn.execute("SELECT * FROM items").fetchall():

        rewards = [
            ('造型文具', 1.0, '可以兌換精美造型文具一個。'),
            ('限量商品', 1.0, '搶手限量小禮物，換完為止！'),
            ('功課減量', 1.0, '今天的功課可以少寫一部分。'),
            ('使用電腦', 3.0, '獲得特定時間使用課堂電腦的權利。'),
            ('值日生跳過', 1.0, '今天當值日生的工作由下一組頂替。'),
            ('免睡卡', 2.0, '午休時間可以不用睡覺（需安靜）。'),
            ('點數加倍', 0.5, '下一輪活動獲得的分數直接翻倍！'),
            ('免罰金牌', 1.0, '抵消一次小違規 or 小處罰。'),
            ('V I P', 0.5, '尊榮班級最高權限，解鎖特殊福利。'),
            ('珍珠奶茶', 2.0, '哇！犒賞一杯冰涼好喝的珍珠奶茶！'),
            ('我想跟他坐', 1.0, '班級座位調整時，可以指定跟好朋友坐在一起。'),
            ('銘謝惠顧', 2.0, '可惜差了一點點，下次手氣一定會更好！'),
            ('禮物卡', 1.0, '獲得一張神秘好禮兌換卡。')
        ]

        for name, weight, desc in rewards:
            conn.execute(
                "INSERT INTO items (name, weight, description) VALUES (?, ?, ?)",
                (name, weight, desc)
            )

    conn.commit()
    conn.close()