import gc

from app.log import ExceptionLogger
from app.response import ResponseDict, JSONResponse
from app.models import UserModel
from app.middlewares.celery import task_check_user_basic, task_check_user_info

class GameUser:
    @ExceptionLogger.handle_program_exception_async
    async def get_user_max_number() -> ResponseDict:
        try:
            result = await UserModel.get_user_max_number()
            return result
        except Exception as e:
            raise e
        finally:
            gc.collect()

    @ExceptionLogger.handle_program_exception_async
    async def get_user_info_data(account_id: int, region_id: int) -> ResponseDict:
        try:
            result = await UserModel.get_user_info(account_id, region_id)
            return result
        except Exception as e:
            raise e
        finally:
            gc.collect()

    @ExceptionLogger.handle_program_exception_async
    async def check_user_info_data(user_info: dict) -> ResponseDict:
        try:
            task_check_user_info.delay([user_info])
            return JSONResponse.API_1000_Success
        except Exception as e:
            raise e
        finally:
            gc.collect()

    @ExceptionLogger.handle_program_exception_async
    async def check_user_basic_data(user_basic: dict) -> ResponseDict:
        try:
            task_check_user_basic.delay([user_basic])
            return JSONResponse.API_1000_Success
        except Exception as e:
            raise e
        finally:
            gc.collect()

    @ExceptionLogger.handle_database_exception_async
    async def check_user_basic_and_info_data(user_basic:dict, user_info:dict) -> ResponseDict:
        try:
            task_check_user_basic.delay([user_basic])
            task_check_user_info.delay([user_info])
            return JSONResponse.API_1000_Success
        except Exception as e:
            raise e
        finally:
            gc.collect()