from typing import Optional

import redis.asyncio as redis
from redis.asyncio.client import Redis

from app.core import EnvConfig,api_logger


class RedisConnection:
    '''管理Redis连接'''
    _pool: Optional[Redis] = None

    def __init_connection(self) -> None:
        "初始化Redis连接"
        try:
            config = EnvConfig.get_config()
            self._pool = redis.from_url(
                url=f"redis://:{config.REDIS_PASSWORD}@{config.REDIS_HOST}:{config.REDIS_PORT}",
                encoding="utf-8",
                decode_responses=True
            )
            api_logger.info('Redis connection initialization is complete')
        except Exception as e:
            api_logger.error(f'Failed to initialize the Redis connection')
            api_logger.error(e)

    @classmethod
    async def test_redis(self) -> None:
        "测试Redis连接"
        try:
            if self._pool:
                pass
            else:
                self.__init_connection(self)
            redis_pool = self._pool
            async with redis_pool as redis:
                # ping测试连接
                ping_response = await redis.ping()
                api_logger.info(f"Redis PING Response: {ping_response}")
                # 获取redis版本
                info = await redis.info("server")
                redis_version = info.get("redis_version")
                api_logger.info(f"Redis Version: {redis_version}")
        except Exception as e:
            api_logger.warning(f'Failed to test the Redis connection')
            api_logger.error(e)

    @classmethod
    async def close_redis(self) -> None:
        "关闭Redis连接"
        try:
            if self._pool:
                await self._pool.close()
                api_logger.info('The Redis connection is closed')
            else:
                api_logger.warning('The Redis connection is empty and cannot be closed')
        except Exception as e:
            api_logger.error(f'Failed to close the Redis connection')
            api_logger.error(e)

    @classmethod
    def get_connection(self) -> Redis | None:
        "获取Redis连接"
        if self._pool:
            return self._pool
        else:
            raise Exception('The Redis connection is empty')

    
    
