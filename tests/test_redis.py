import sys
sys.path.append('F:\Kokomi_PJ_Api')

import asyncio

from app.core import ProjectConfig
from app.core import RedisConnection

async def test_redis():
    ...
    # ProjectConfig().init_config()
    # await RedisConnectionPool().test_redis()
    # await RedisConnectionPool().close_pool()
    # redis_pool = RedisConnectionPool().get_pool()
    # await redis_pool.set("test_key", "test_value", 60)
    # value = await redis_pool.get("test_key")
    # print(value)
    # await redispool.close_pool()

if __name__ == '__main__':
    asyncio.run(test_redis())