import gc
from app.log import ExceptionLogger
from app.response import ResponseDict, JSONResponse
from app.models import UserModel

class GameUser:
    @ExceptionLogger.handle_program_exception_async
    async def get_user_info_data(account_id: int) -> ResponseDict:
        try:
            result = await UserModel.get_user_info(account_id)
            return result
        except Exception as e:
            raise e
        finally:
            gc.collect()

    @ExceptionLogger.handle_program_exception_async
    async def check_user_info_data(user_info: dict) -> ResponseDict:
        try:
            result = await UserModel.check_user_info(user_info)
            return result
        except Exception as e:
            raise e
        finally:
            gc.collect()

    @ExceptionLogger.handle_program_exception_async
    async def check_user_basic_data(user_basic: dict) -> ResponseDict:
        try:
            result = await UserModel.check_user_basic(user_basic)
            return result
        except Exception as e:
            raise e
        finally:
            gc.collect()

    @ExceptionLogger.handle_database_exception_async
    async def check_user_basic_and_info_data(user_basic:dict, user_info:dict) -> ResponseDict:
        try:
            if user_basic:
                result = await UserModel.check_user_basic(user_basic)
                if result.get('code', None) != 1000: return result
            if user_info:
                result = await UserModel.check_user_info(user_info)
                if result.get('code', None) != 1000: return result
            return JSONResponse.API_1000_Success
        except Exception as e:
            raise e
        finally:
            gc.collect()