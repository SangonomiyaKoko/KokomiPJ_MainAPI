import gc
from app.log import ExceptionLogger
from app.response import ResponseDict, JSONResponse
from app.models import UserModel
from app.middlewares.celery import task_update_user_ship, task_update_user_ships


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
    async def update_user_cache_data(user_data: dict) -> ResponseDict:
        try:
            account_id = user_data['account_id']
            region_id = user_data['region_id']
            user_cache_result = await UserModel.get_user_cache_data(account_id, region_id)
            if user_cache_result.get('code', None) != 1000:
                return user_cache_result
            delete_ship_list = {0:[],2:[],4:[],6:[],8:[]}
            replace_ship_dict = {0:{},2:{},4:{},6:{},8:{}}
            if user_data['ships_data']:
                for ship_id, ship_battles in user_data['ships_data'].items():
                    if (
                        int(ship_id) not in user_cache_result['data']['ships_data'] or 
                        ship_battles != user_cache_result['data']['ships_data']
                    ):
                        replace_ship_dict[int(ship_id) % 10][int(ship_id)] = user_data['details_data'][ship_id]
                for ship_id, _ in user_cache_result['data']['ships_data'].items():
                    if str(ship_id) not in user_data['ships_data']:
                        delete_ship_list[ship_id % 10].append(ship_id)
                for table_name in [0, 2, 4, 6, 8]:
                    data = {
                        'account_id': account_id,
                        'region_id': region_id,
                        'table_name': table_name,
                        'delete_ship_list': delete_ship_list[table_name],
                        'replace_ship_dict': replace_ship_dict[table_name]
                    }
                    if delete_ship_list[table_name] != [] or replace_ship_dict[table_name] != {}:
                        task_update_user_ship.delay(data)
            del user_data['details_data']
            task_update_user_ships.delay(user_data)
            return JSONResponse.API_1000_Success
        except Exception as e:
            raise e
        finally:
            gc.collect()
