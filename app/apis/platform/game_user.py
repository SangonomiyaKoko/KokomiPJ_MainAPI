import gc
import uuid
import traceback

from app.log import write_error_info
from app.response import JSONResponse
from app.models import UserModel

class GameUser:
    async def get_user_info_data(account_id: int) -> dict:
        try:
            result = await UserModel.get_user_info(account_id)
            return result
        except Exception as e:
            error_id = str(uuid.uuid4())
            write_error_info(
                error_id = error_id,
                error_type = 'Program',
                error_name = str(type(e).__name__),
                error_file = __file__,
                error_info = f'\n{traceback.format_exc()}'
            )
            return JSONResponse.get_error_response(5000,'ProgramError',error_id)
        finally:
            gc.collect()

    async def check_user_info_data(user_info: dict) -> dict:
        try:
            result = UserModel.check_user_info(user_info)
            return result
        except Exception as e:
            error_id = str(uuid.uuid4())
            write_error_info(
                error_id = error_id,
                error_type = 'Program',
                error_name = str(type(e).__name__),
                error_file = __file__,
                error_info = f'\n{traceback.format_exc()}'
            )
            return JSONResponse.get_error_response(5000,'ProgramError',error_id)
        finally:
            gc.collect()

    async def check_user_basic_data(user_basic: dict) -> dict:
        try:
            result = UserModel.check_user_basic(user_basic)
            return result
        except Exception as e:
            error_id = str(uuid.uuid4())
            write_error_info(
                error_id = error_id,
                error_type = 'Program',
                error_name = str(type(e).__name__),
                error_file = __file__,
                error_info = f'\n{traceback.format_exc()}'
            )
            return JSONResponse.get_error_response(5000,'ProgramError',error_id)
        finally:
            gc.collect()