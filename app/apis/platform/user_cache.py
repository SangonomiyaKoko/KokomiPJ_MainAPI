import gc

from app.log import ExceptionLogger
from app.response import ResponseDict, JSONResponse
from app.network import BasicAPI
from app.models import UserModel, UserAccessToken, ShipsCacheModel
from app.utils import UtilityFunctions

class UserCache:
    @ExceptionLogger.handle_program_exception_async
    async def update_user_cache(region_id: int, account_id: int) -> ResponseDict:
        try:
            user_data = await UserModel.get_user_cache(region_id, account_id)
            if user_data['code'] != 1000:
                return user_data
            token_data = await UserAccessToken.get_ac_value_by_id(account_id, region_id)
            if token_data['code'] != 1000:
                return token_data
            if token_data['data']:
                ac_value = token_data['data']['token_value']
            else:
                ac_value = None
            # 需要更新，则请求数据用户数据
            user_basic = {
                'account_id': account_id,
                'region_id': region_id,
                'nickname': f'User_{account_id}'
            }
            # 用于更新user_info表的数据
            user_info = {
                'account_id': account_id,
                'region_id': region_id,
                'is_active': 1,
                'active_level': 0,
                'is_public': 1,
                'total_battles': 0,
                'last_battle_time': 0
            }
            user_cache = {
                'account_id': account_id,
                'region_id': region_id,
                'battles_count': 0
            }
            basic_data = await BasicAPI.get_user_basic(account_id, region_id, ac_value)
            if basic_data['code'] != 1000 and basic_data['code'] != 1001:
                return basic_data
            if basic_data[0]['code'] == 1001:
                # 用户数据不存在
                user_info['is_active'] = 0
                # TODO: 更新
                return JSONResponse.API_1001_UserNotExist
            user_basic['nickname'] = basic_data[0]['data'][str(account_id)]['name']
            if 'hidden_profile' in basic_data[0]['data'][str(account_id)]:
                # 隐藏战绩
                user_info['is_public'] = 0
                # TODO: 更新
                return JSONResponse.API_1005_UserHiddenProfite
            user_basic_data = basic_data[0]['data'][str(account_id)]['statistics']
            if (
                user_basic_data == {} or
                user_basic_data['basic'] == {}
            ):
                # 用户没有数据
                user_info['is_active'] = 0
                # TODO: 更新
                return JSONResponse.API_1006_UserDataisNone
            if user_basic_data['basic']['leveling_points'] == 0:
                # 用户没有数据
                user_info['total_battles'] = 0
                user_info['last_battle_time'] = 0
                # TODO: 更新
                return JSONResponse.API_1006_UserDataisNone
            user_info['total_battles'] = user_basic_data['basic']['leveling_points']
            user_info['last_battle_time'] = user_basic_data['basic']['last_battle_time']
            
            ships_data = await BasicAPI.get_user_cache(account_id, region_id, ac_value)
            if ships_data['code'] != 1000 and ships_data['code'] != 1001:
                return ships_data
            new_user_data = ships_data['data']
            sorted_dict = dict(sorted(new_user_data['basic'].items()))
            new_hash_value = UtilityFunctions.get_sha256_value(str(sorted_dict))
            if user_data['user_ships']['hash_value'] == new_hash_value:
                user_cache['battles_count'] = user_info['total_battles']
            else:
                user_cache['battles_count'] = user_info['total_battles']
                user_cache['hash_value'] = new_hash_value
                user_cache['ships_data'] = sorted_dict
                user_cache['details_data'] = new_user_data['details']
            cache_data = UserModel.get_user_cache(account_id, region_id)
            if cache_data.get('code', None) != 1000:
                return cache_data
            ship_id_set = set()
            replace_ship_dict = {}
            if 'hash_value' in user_cache:
                for ship_id, ship_battles in user_cache['ships_data'].items():
                    if (
                        int(ship_id) not in cache_data['data']['ships_data'] or 
                        ship_battles != cache_data['data']['ships_data']
                    ):
                        replace_ship_dict[int(ship_id)] = user_cache['details_data'][ship_id]
                        ship_id_set.add(int(ship_id))
                check_ship_id_result = ShipsCacheModel.check_existing_ship(ship_id_set)
                if check_ship_id_result.get('code', None) != 1000:
                    return check_ship_id_result
                if replace_ship_dict != {}:
                    user_cache['ship_dict'] = replace_ship_dict
                else:
                    user_cache['ship_dict'] = None
                del user_data['details_data']
            update_result = await ShipsCacheModel.update_user_ships(user_cache)
            return update_result
        except Exception as e:
            raise e
        finally:
            gc.collect()

    # @ExceptionLogger.handle_program_exception_async
    # async def get_user_cache_data_batch(offset: int, limit: int = 1000) -> ResponseDict:
    #     try:
    #         result = await UserModel.get_user_cache_batch(offset, limit)
    #         return result
    #     except Exception as e:
    #         raise e
    #     finally:
    #         gc.collect()
    
    # @ExceptionLogger.handle_program_exception_async
    # async def update_user_cache_data(user_data: dict) -> ResponseDict:
    #     try:
    #         account_id = user_data['account_id']
    #         region_id = user_data['region_id']
    #         user_cache_result = await UserModel.get_user_cache_data(account_id, region_id)
    #         if user_cache_result.get('code', None) != 1000:
    #             return user_cache_result
    #         ship_id_set = set()
    #         delete_ship_list = []
    #         replace_ship_dict = {}
    #         ship_data = None
    #         if user_data['hash_value'] and user_data['ships_data']:
    #             for ship_id, ship_battles in user_data['ships_data'].items():
    #                 if (
    #                     int(ship_id) not in user_cache_result['data']['ships_data'] or 
    #                     ship_battles != user_cache_result['data']['ships_data']
    #                 ):
    #                     replace_ship_dict[int(ship_id)] = user_data['details_data'][ship_id]
    #                     ship_id_set.add(int(ship_id))
    #             for ship_id, _ in user_cache_result['data']['ships_data'].items():
    #                 if str(ship_id) not in user_data['ships_data']:
    #                     delete_ship_list.append(ship_id)
    #                     ship_id_set.add(int(ship_id))
    #             data = {
    #                 'account_id': account_id,
    #                 'region_id': region_id,
    #                 'delete_ship_list': delete_ship_list,
    #                 'replace_ship_dict': replace_ship_dict
    #             }
    #             check_ship_id_result = await ShipsCacheModel.check_existing_ship(ship_id_set)
    #             if check_ship_id_result.get('code', None) != 1000:
    #                 return check_ship_id_result
    #             if delete_ship_list != [] or replace_ship_dict != {}:
    #                 ship_data = data
    #         del user_data['details_data']
    #         celery_app.send_task(
    #             name="update_user_cache",
    #             args=[user_data, ship_data]
    #         )
    #         return JSONResponse.API_1000_Success
    #     except Exception as e:
    #         raise e
    #     finally:
    #         gc.collect()
