import gc

from app.log import ExceptionLogger
from app.models import RecentUserModel
from app.response import JSONResponse

class RecentData:
    @ExceptionLogger.handle_database_exception_async
    async def get_data_overview(account_id: int, region_id: int):
        try:
            data = None
            result = await RecentUserModel.check_recent_user(account_id,region_id)
            if result.get('code', None) != 1000:
                return result
            data = result['data']
            return JSONResponse.get_success_response(data)    
        except Exception as e:
            raise e
        finally:
            gc.collect()

    async def get_data_by_date():
        ...

    async def get_data_by_date_and_sid():
        ...