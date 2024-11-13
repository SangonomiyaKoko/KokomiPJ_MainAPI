from .redis import RedisConnection
from app.utils import TimeFormat
from app.log import ExceptionLogger

# 当前存在key的简单缓存，避免重复查询设置expire
exist_daily_key = []
exist_hourly_key = []

@ExceptionLogger.handle_cache_exception_async
async def record_api_call(status: str = 'ok') -> None:
    '''记录api请求次数和请求结果概括

    记录过去24h和过去30d的请求数据

    参数:
        status: 表示请求结果

    返回:
        None
    '''
    try:
        redis = RedisConnection.get_connection()

        current_hour = TimeFormat.get_form_time(time_format='%Y-%m-%d-%H')
        current_day = TimeFormat.get_form_time(time_format='%Y-%m-%d')
        hourly_key = f'api_calls:hourly:{current_hour}'
        daily_key = f'api_calls:daily:{current_day}'

        await redis.hincrby(hourly_key, "total", 1)
        await redis.hincrby(daily_key, "total", 1)
        if status == "ok":
            await redis.hincrby(daily_key, "ok", 1)
        elif status == "error":
            await redis.hincrby(daily_key, "error", 1)
        if hourly_key not in exist_hourly_key:
            hourly_key_ttl = await redis.ttl(hourly_key)
            if hourly_key_ttl == -1:
                await redis.expire(hourly_key, 25 * 60 * 60)
                exist_hourly_key.append(hourly_key)
        if daily_key not in exist_daily_key:
            daily_key_ttl = await redis.ttl(daily_key)
            if daily_key_ttl == -1:
                await redis.expire(daily_key, 60 * 60 * 24 * 31)
                exist_daily_key.append(daily_key)
        return None
    except Exception as e:
        raise e