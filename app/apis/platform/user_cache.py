import gc

from app.log import ExceptionLogger
from app.response import ResponseDict, JSONResponse
from app.models import UserModel, ShipsCacheModel


class UserCache:
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
    async def get_user_cache_data_batch(offset: int, limit: int = 1000) -> ResponseDict:
        try:
            result = await UserModel.get_user_cache_batch(offset, limit)
            return result
        except Exception as e:
            raise e
        finally:
            gc.collect()
    
    @ExceptionLogger.handle_program_exception_async
    async def update_user_cache_data(user_data: dict) -> ResponseDict:
        try:
            account_id = user_data['account_id']
            region_id = user_data['region_id']
            user_cache_result = await UserModel.get_user_cache_data(account_id, region_id)
            if user_cache_result.get('code', None) != 1000:
                return user_cache_result
            ship_id_set = set()
            delete_ship_list = []
            replace_ship_dict = {}
            ship_data = None
            if user_data['hash_value'] and user_data['ships_data']:
                for ship_id, ship_battles in user_data['ships_data'].items():
                    if (
                        int(ship_id) not in user_cache_result['data']['ships_data'] or 
                        ship_battles != user_cache_result['data']['ships_data']
                    ):
                        replace_ship_dict[int(ship_id)] = user_data['details_data'][ship_id]
                        ship_id_set.add(int(ship_id))
                for ship_id, _ in user_cache_result['data']['ships_data'].items():
                    if str(ship_id) not in user_data['ships_data']:
                        delete_ship_list.append(ship_id)
                        ship_id_set.add(int(ship_id))
                data = {
                    'account_id': account_id,
                    'region_id': region_id,
                    'delete_ship_list': delete_ship_list,
                    'replace_ship_dict': replace_ship_dict
                }
                check_ship_id_result = await ShipsCacheModel.check_existing_ship(ship_id_set)
                if check_ship_id_result.get('code', None) != 1000:
                    return check_ship_id_result
                if delete_ship_list != [] or replace_ship_dict != {}:
                    ship_data = data
            del user_data['details_data']
            celery_app.send_task(
                name="update_user_cache",
                args=[user_data, ship_data]
            )
            return JSONResponse.API_1000_Success
        except Exception as e:
            raise e
        finally:
            gc.collect()
