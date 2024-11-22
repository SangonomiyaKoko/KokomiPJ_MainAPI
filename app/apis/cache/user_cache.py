import gc
from app.log import ExceptionLogger
from app.response import ResponseDict
from app.models import UserModel


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
            account_id = user_cache['account_id']
            region_id = user_cache['region_id']
            # 先更新船只缓存再更新用户缓存，确保数据一致性
            result = await UserModel.update_user_cache(account_id,region_id,user_cache['delete_ship_list'],user_cache['replace_ship_dict'])
            if result.get('code', None) != 1000:
                return result
            result = await UserModel.update_user_ships(account_id,user_cache['battles_count'],user_cache['ships_data'])
            return result
        except Exception as e:
            raise e
        finally:
            gc.collect()
