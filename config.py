import os

class Config:
    # Flask配置
    SECRET_KEY = os.urandom(24)

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'  # 使用SQLite作为例子
    SQLALCHEMY_TRACK_MODIFICATIONS = False
