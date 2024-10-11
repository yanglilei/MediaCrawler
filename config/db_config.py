import os


class DBConfig:
    # mysql config
    RELATION_DB_PWD = os.getenv("RELATION_DB_PWD", "ying*#1234")
    RELATION_DB_USER = os.getenv("RELATION_DB_USER", "root")
    RELATION_DB_HOST = os.getenv("RELATION_DB_HOST", "localhost")
    RELATION_DB_PORT = os.getenv("RELATION_DB_PORT", "3306")
    RELATION_DB_NAME = os.getenv("RELATION_DB_NAME", "media_crawler")

    # RELATION_DB_URL = f"mysql://{RELATION_DB_USER}:{RELATION_DB_PWD}@{RELATION_DB_HOST}:{RELATION_DB_PORT}/{RELATION_DB_NAME}"

    # redis config
    REDIS_DB_HOST = "127.0.0.1"  # your redis host
    REDIS_DB_PWD = os.getenv("REDIS_DB_PWD", "ying*#1234")  # your redis password
    REDIS_DB_PORT = os.getenv("REDIS_DB_PORT", 6379)  # your redis port
    REDIS_DB_NUM = os.getenv("REDIS_DB_NUM", 4)  # your redis db num

    # 缓存类型
    # 目前redis暂时无用到
    CACHE_TYPE_REDIS = "redis"
    # 目前都是存储到内存
    CACHE_TYPE_MEMORY = "memory"
