import os


class Config:
    SECRET_KEY = (
        os.environ.get("SECRET_KEY") or "your-secret-key-here-change-in-production"
    )
    # 默认使用SQLite，但可通过环境变量配置MySQL
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = os.environ.get("DB_PORT", "3306")
    DB_NAME = os.environ.get("DB_NAME", "bookmanagement")

    # 如果设置了DATABASE_URL则直接使用，否则根据上面的配置构建MySQL URL
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL")
        or f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,  # 每5分钟回收连接，避免MySQL断开连接
        "pool_pre_ping": True,  # 在使用连接前先ping一下，保证连接有效
    }
