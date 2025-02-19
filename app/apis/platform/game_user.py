import gc

from app.log import ExceptionLogger
from app.response import ResponseDict, JSONResponse
from app.models import UserModel, ClanModel, UserAccessToken
from app.network import BasicAPI
from app.utils import UtilityFunctions
from .user_cache import UserCache

class GameUser:
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
    async def update_user_data(user_data: dict) -> ResponseDict:
        try:
            if user_data.get('user_recent', None):
                celery_app.send_task(
                    name="check_user_recent",
                    args=[user_data['user_recent']]
                )
            if user_data.get('user_basic', None):
                celery_app.send_task(
                    name="check_user_basic",
                    args=[user_data['user_basic']]
                )
            if user_data.get('user_info', None):
                celery_app.send_task(
                    name="check_user_info",
                    args=[user_data['user_info']]
                )
            if user_data.get('user_cache', None):
                await UserCache.update_user_cache_data(user_data['user_cache'])
            return JSONResponse.API_1000_Success
        except Exception as e:
            raise e
        finally:
            gc.collect()
