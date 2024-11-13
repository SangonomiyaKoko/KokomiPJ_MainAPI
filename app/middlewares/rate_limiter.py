from .redis import RedisConnection
from app.utils import TimeFormat
from app.log import ExceptionLogger

@ExceptionLogger.handle_cache_exception_async
async def rate_limit(host: str, limit: int = 20, window = 10) -> bool:
    '''判断当前ip请求是否到达限速

    使用Redis+固定窗口实现接口请求限流，默认为 20次/10秒

    参数:
        key:请求IP地址.
        limit:窗口内最高请求次数.
        window:窗口大小(s).

    返回:
        bool值，是否到达限速.
    '''
    try:
        redis = RedisConnection.get_connection()
        # 基于当前时间生成固定窗口
        current_time = int(TimeFormat.get_current_timestamp() / window) * window 
        window_key = f"rate_limit:{host}:{current_time}"
        
        # 增加当前窗口的计数
        current_count = await redis.incr(window_key)

        # 设置key的过期时间，加上5s的冗余
        if current_count == 1:
            await redis.expire(window_key, window + 5)

        if current_count > limit:
            return True
        else:
            return False
    except Exception as e:
        raise e