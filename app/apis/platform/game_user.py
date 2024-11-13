import gc
from app.log import ExceptionLogger
from app.response import JSONResponse
from app.models import UserModel

class GameUser:
    @ExceptionLogger.handle_program_exception_async
    async def get_user_info_data(account_id: int) -> dict:
        try:
            result = await UserModel.get_user_info(account_id)
            return result
        except Exception as e:
            raise e
        finally:
            gc.collect()

    @ExceptionLogger.handle_program_exception_async
    async def check_user_info_data(user_info: dict) -> dict:
        try:
            result = await UserModel.check_user_info(user_info)
            return result
        except Exception as e:
            raise e
        finally:
            gc.collect()

    @ExceptionLogger.handle_program_exception_async
    async def check_user_basic_data(user_basic: dict) -> dict:
        try:
            result = await UserModel.check_user_basic(user_basic)
            return result
        except Exception as e:
            raise e
        finally:
            gc.collect()