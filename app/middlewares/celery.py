import pymysql
from dbutils.pooled_db import PooledDB
from celery import Celery, signals
from celery.app.base import logger

from .background_task import check_user_basic, check_clan_tag_and_league, update_user_clan, check_user_info
from app.core import EnvConfig
from app.log import ExceptionLogger
from app.response import JSONResponse


config = EnvConfig.get_config()

# 创建 Celery 应用并配置 Redis 作为消息队列
celery_app = Celery(
    "worker",
    broker=f"redis://:{config.REDIS_PASSWORD}@{config.REDIS_HOST}:{config.REDIS_PORT}/1",  # 消息代理
    backend=f"redis://:{config.REDIS_PASSWORD}@{config.REDIS_HOST}:{config.REDIS_PORT}/2", # 结果存储
    broker_connection_retry_on_startup = True
)

# 创建连接池
pool = None


@signals.worker_init.connect
def init_mysql_pool(**kwargs):
    global pool
    pool = PooledDB(
        creator=pymysql,
        maxconnections=10,  # 最大连接数
        mincached=2,        # 初始化时，连接池中至少创建的空闲的连接
        maxcached=5,        # 最大缓存的连接
        blocking=True,      # 连接池中如果没有可用连接后，是否阻塞
        host=config.MYSQL_HOST,
        user=config.MYSQL_USERNAME,
        password=config.MYSQL_PASSWORD,
        database='kokomi'
    )

@signals.worker_shutdown.connect
def close_mysql_pool(**kwargs):
    pool.close()
    logger.info('MySQL closed')


@celery_app.task
@ExceptionLogger.handle_program_exception_sync
def task_check_user_basic(users: list):
    result = check_user_basic(pool,users)
    return result
    
@celery_app.task
@ExceptionLogger.handle_program_exception_sync
def task_check_clan_basic(clans: list):
    result = check_clan_tag_and_league(pool,clans)
    return result
    
@celery_app.task
@ExceptionLogger.handle_program_exception_sync
def task_update_user_clan(user_clans: list):
    result = update_user_clan(pool,user_clans)
    return result
    
@celery_app.task
@ExceptionLogger.handle_program_exception_sync
def task_check_user_info(users: list):
    result = check_user_info(pool,users)
    return result

