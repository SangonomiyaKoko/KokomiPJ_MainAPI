import pymysql
from dbutils.pooled_db import PooledDB

from config import settings
from log import log as logger

class DatabaseConnection:
    _pool = None

    @classmethod
    def init_pool(cls):
        try:
            cls._pool = PooledDB(
                creator=pymysql,
                maxconnections=2,  # 最大连接数
                mincached=1,        # 初始化时，连接池中至少创建的空闲的连接
                maxcached=2,        # 最大缓存的连接
                blocking=True,      # 连接池中如果没有可用连接后，是否阻塞
                host=settings.MYSQL_HOST,
                user=settings.MYSQL_USERNAME,
                password=settings.MYSQL_PASSWORD,
                charset='utf8mb4',
                connect_timeout=10
            )
            logger.info(f'数据库连接成功')
        except Exception as e:
            logger.error(f'数据库连接失败')
            print(e)

    @classmethod
    def close_pool(cls):
        if cls._pool:
            cls._pool.close()
            logger.info(f'数据库连接关闭')
    
    @classmethod
    def get_pool(cls):
        if cls._pool:
            return cls._pool
        else:
            logger.info(f'数据库重新连接中')
            cls.init_pool()
            return cls._pool


