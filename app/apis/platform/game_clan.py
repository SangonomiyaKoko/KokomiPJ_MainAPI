import gc

from app.log import ExceptionLogger
from app.response import ResponseDict, JSONResponse
from app.models import ClanModel, UserModel
from app.middlewares.celery import task_update_clan_users

class GameClan:
    @ExceptionLogger.handle_program_exception_async
    async def get_clan_max_number() -> ResponseDict:
        try:
            result = await ClanModel.get_clan_max_number()
            return result
        except Exception as e:
            raise e
        finally:
            gc.collect()

    @classmethod
    @ExceptionLogger.handle_program_exception_async
    async def update_clan_data(self, clan_data: dict) -> ResponseDict:
        try:
            if clan_data.get('clan_basic', None) and clan_data.get('clan_users', None):
                result = await self.update_clan_basic_data(clan_data['clan_basic'])
                if result.get('code', None) != 1000:
                    return result
            elif clan_data.get('clan_basic', None):
                result = await self.update_clan_basic_data(clan_data['clan_basic'])
                return result
            if clan_data.get('clan_info', None):
                result = await self.update_clan_info_data(clan_data['clan_info'])
                return result
            if clan_data.get('clan_users', None):
                result = await self.update_clan_users_data(clan_data['clan_users'])
                if result.get('code', None) != 1000:
                    return result
            if clan_data.get('clan_season', None):
                result = await self.update_clan_season_data(clan_data['clan_season'])
                if result.get('code', None) != 1000:
                    return result
            return JSONResponse.API_1000_Success
        except Exception as e:
            raise e
        finally:
            gc.collect()

    @ExceptionLogger.handle_program_exception_async
    async def update_clan_basic_data(clan_basic: dict) -> ResponseDict:
        try:
            update_result = await ClanModel.update_clan_basic(clan_basic)
            if update_result.get('code', None) != 1000:
                return update_result
            return JSONResponse.API_1000_Success
        except Exception as e:
            raise e
        finally:
            gc.collect()

    @ExceptionLogger.handle_program_exception_async
    async def update_clan_users_data(clan_users_data: dict) -> ResponseDict:
        try:
            # 首先检查用户是否存在于数据库
            if len(clan_users_data['clan_users']) != 0:
                check_user_exist = await UserModel.check_and_insert_missing_users(clan_users_data['clan_users'])
                if check_user_exist.get('code', None) != 1000:
                    return check_user_exist
            task_update_clan_users.delay(clan_users_data['clan_id'], clan_users_data['hash_value'], clan_users_data['user_list'])
            return JSONResponse.API_1000_Success
        except Exception as e:
            raise e
        finally:
            gc.collect()
    
    @ExceptionLogger.handle_program_exception_async
    async def update_clan_season_data(clan_season: dict) -> ResponseDict:
        try:
            update_result = await ClanModel.update_clan_season(clan_season)
            if update_result.get('code', None) != 1000:
                return update_result
            return JSONResponse.API_1000_Success
        except Exception as e:
            raise e
        finally:
            gc.collect()

    @ExceptionLogger.handle_program_exception_async
    async def update_clan_info_data(clan_data: dict) -> ResponseDict:
        try:
            result = await ClanModel.update_clan_info_batch(clan_data['region_id'], clan_data['season_number'], clan_data['clan_list'])
            if result.get('code', None) != 1000:
                return result
            return JSONResponse.get_success_response(result['data'])
        except Exception as e:
            raise e
        finally:
            gc.collect()