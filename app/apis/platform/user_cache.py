import gc
from app.log import ExceptionLogger
from app.response import ResponseDict, JSONResponse
from app.models import UserModel
from app.middlewares.celery import task_check_user_cache


class UserCache:
    @ExceptionLogger.handle_program_exception_async
    async def get_user_cache_data_batch(offset: int, limit: int = 1000) -> ResponseDict:
        try:
            result = await UserModel.get_user_cache_batch(offset, limit)
            return result
        except Exception as e:
            raise e
        finally:
            gc.collect()
    
    @ExceptionLogger.handle_program_exception_async
    async def update_user_cache_data(user_cache: dict) -> ResponseDict:
        try:
            print(user_cache)
            # task_check_user_cache.delay(user_cache)
            return JSONResponse.API_1000_Success
        except Exception as e:
            raise e
        finally:
            gc.collect()
