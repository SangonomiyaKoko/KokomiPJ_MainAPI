from typing import Optional
import redis.asyncio as redis
from redis.asyncio.client import Redis
from app.core import EnvConfig, api_logger


class RedisConnection:
    '''管理Redis连接'''
    _pools: dict[int, Redis] = {}

    @classmethod
    def _init_connection(cls, db: int = 0) -> Redis:
        """初始化Redis连接"""
        try:
            if db not in cls._pools:
                config = EnvConfig.get_config()
                cls._pools[db] = redis.from_url(
                    url=f"redis://:{config.REDIS_PASSWORD}@{config.REDIS_HOST}:{config.REDIS_PORT}/{db}",
                    encoding="utf-8",
                    decode_responses=True
                )
                api_logger.info(f'Redis connection to DB {db} initialized')
            return cls._pools[db]
        except Exception as e:
            api_logger.error(f'Failed to initialize Redis connection for DB {db}')
            api_logger.error(e)
            raise

    @classmethod
    async def test_redis(cls, db: int = 0) -> None:
        """测试Redis连接"""
        try:
            redis_pool = cls._init_connection(db)
            async with redis_pool as redis_instance:
                # ping测试连接
                ping_response = await redis_instance.ping()
                api_logger.info(f"Redis PING Response: {ping_response}")
                # 获取redis版本
                info = await redis_instance.info("server")
                redis_version = info.get("redis_version")
                api_logger.info(f"Redis Version: {redis_version}")
        except Exception as e:
            api_logger.warning(f'Failed to test Redis connection for DB {db}')
            api_logger.error(e)

    @classmethod
    async def close_redis(cls, db: Optional[int] = None) -> None:
        """关闭Redis连接"""
        try:
            if db is not None:
                # 关闭指定数据库的连接
                pool = cls._pools.pop(db, None)
                if pool:
                    await pool.close()
                    api_logger.info(f'Redis connection to DB {db} is closed')
                else:
                    api_logger.warning(f'Redis connection to DB {db} is empty and cannot be closed')
            else:
                # 关闭所有连接
                for db, pool in cls._pools.items():
                    await pool.close()
                    api_logger.info(f'Redis connection to DB {db} is closed')
                cls._pools.clear()
        except Exception as e:
            api_logger.error(f'Failed to close Redis connections')
            api_logger.error(e)

    @classmethod
    def get_connection(cls, db: int = 0) -> Redis:
        """获取Redis连接"""
        try:
            return cls._init_connection(db)
        except Exception as e:
            api_logger.error(f'Failed to get Redis connection for DB {db}')
            api_logger.error(e)
            return None
