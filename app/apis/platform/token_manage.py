import gc

from app.log import ExceptionLogger
from app.middlewares import RedisConnection
from app.response import ResponseDict, JSONResponse
from app.models import UserAccessToken

class GameUser:
    @ExceptionLogger.handle_program_exception_async
    async def get_user_token(region_id: int, account_id: int, token_type: int) -> ResponseDict:
        try:
            token_result = await UserAccessToken.get_ac_value_by_id(account_id, region_id, token_type)
            if token_result['code'] != 1000:
                return token_result
            redis = RedisConnection.get_connection()
            cache_key = f"token_cache_{token_type}:{region_id}:{account_id}"
            token_cache = await redis.get(cache_key)
            if token_cache:
                if token_result['data']['token_value'] != token_result:
                    await redis.set(cache_key, token_result['data']['token_value'])
            else:
                await redis.set(cache_key, token_result['data']['token_value'])
            return token_result
        except Exception as e:
            raise e
        finally:
            gc.collect()

    @ExceptionLogger.handle_program_exception_async
    async def set_user_token(region_id: int, account_id: int, token_value: int, token_type: int) -> ResponseDict:
        try:
            token_result = await UserAccessToken.set_ac_value(account_id, region_id, token_value)
            if token_result['code'] != 1000:
                return token_result
            redis = RedisConnection.get_connection()
            cache_key = f"token_cache_{token_type}:{region_id}:{account_id}"
            token_cache = await redis.get(cache_key)
            if token_cache:
                if token_result['data']['token_value'] != token_result:
                    await redis.set(cache_key, token_result['data']['token_value'])
            else:
                await redis.set(cache_key, token_result['data']['token_value'])
            return token_result
        except Exception as e:
            raise e
        finally:
            gc.collect()

    @ExceptionLogger.handle_program_exception_async
    async def delete_user_token(region_id: int, account_id: int, token_type: int) -> ResponseDict:
        try:
            token_result = await UserAccessToken.delete_ac_value_by_id(account_id, region_id, token_type)
            if token_result['code'] != 1000:
                return token_result
            redis = RedisConnection.get_connection()
            cache_key = f"token_cache_{token_type}:{region_id}:{account_id}"
            await redis.delete(cache_key)
            return token_result
        except Exception as e:
            raise e
        finally:
            gc.collect()