import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Flask Session 金鑰
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "ChangeThisSecretKey123456"
    )

    # SQLite 資料庫位置
    DATABASE = os.path.join(
        BASE_DIR,
        "instance",
        "database.db"
    )

    # 抽獎扣點
    DRAW_COST = 20