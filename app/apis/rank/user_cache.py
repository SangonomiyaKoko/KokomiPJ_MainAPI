import gc

from app.log import ExceptionLogger
from app.middlewares import RedisConnection, celery_app
from app.response import ResponseDict, JSONResponse
from app.network import BasicAPI
from app.models import UserModel, ShipsCacheModel
from app.utils import UtilityFunctions

class UserCache:
    @ExceptionLogger.handle_program_exception_async
    async def update_user_cache(region_id: int, account_id: int) -> ResponseDict:
        try:
            redis = RedisConnection.get_connection()
            user_data = await UserModel.get_user_cache(account_id, region_id)
            if user_data['code'] != 1000:
                return user_data
            token_key = f"token_cache_1:{region_id}:{account_id}"
            token_cache = await redis.get(token_key)
            if token_cache:
                ac_value = token_cache
            else:
                ac_value = None
            update_data = {
                'region_id': region_id,
                'account_id': account_id,
                'basic': None,
                'info': None,
                'clan': None
            }
            user_name = {
                'nickname': None
            }
            user_info = {
                'is_active': True,
                'is_public': True,
                'total_battles': 0,
                'last_battle_time': 0
            }
            user_cache = {
                'account_id': account_id,
                'region_id': region_id,
                'battles_count': 0
            }
            basic_data = await BasicAPI.get_user_basic(account_id, region_id, ac_value)
            if basic_data[0]['code'] != 1000 and basic_data[0]['code'] != 1001:
                return basic_data
            if basic_data[0]['code'] == 1001:
                # 用户数据不存在
                user_info['is_active'] = 0
                update_data['info'] = user_info
                celery_app.send_task(
                    name="update_user_data",
                    args=[update_data],
                    queue='task_queue'
                )
                return JSONResponse.API_1001_UserNotExist
            user_name['nickname'] = basic_data[0]['data'][str(account_id)]['name']
            update_data['basic'] = user_name
            if 'hidden_profile' in basic_data[0]['data'][str(account_id)]:
                # 隐藏战绩
                user_info['is_public'] = False
                update_data['info'] = user_info
                celery_app.send_task(
                    name="update_user_data",
                    args=[update_data],
                    queue='task_queue'
                )
                return JSONResponse.API_1005_UserHiddenProfite
            user_basic_data = basic_data[0]['data'][str(account_id)]['statistics']
            if (
                user_basic_data == {} or
                user_basic_data['basic'] == {}
            ):
                # 用户没有数据
                user_info['is_active'] = False
                update_data['info'] = user_info
                celery_app.send_task(
                    name="update_user_data",
                    args=[update_data],
                    queue='task_queue'
                )
                return JSONResponse.API_1006_UserDataisNone
            if user_basic_data['basic']['leveling_points'] == 0:
                # 用户没有数据
                user_info['total_battles'] = 0
                user_info['last_battle_time'] = 0
                update_data['info'] = user_info
                celery_app.send_task(
                    name="update_user_data",
                    args=[update_data],
                    queue='task_queue'
                )
                return JSONResponse.API_1006_UserDataisNone
            user_info['total_battles'] = user_basic_data['basic']['leveling_points']
            user_info['last_battle_time'] = user_basic_data['basic']['last_battle_time']
            update_data['info'] = user_info
            celery_app.send_task(
                name="update_user_data",
                args=[update_data],
                queue='task_queue'
            )
            ships_data = await BasicAPI.get_user_cache(account_id, region_id, ac_value)
            if ships_data['code'] != 1000 and ships_data['code'] != 1001:
                return ships_data
            new_user_data = ships_data['data']
            sorted_dict = dict(sorted(new_user_data['basic'].items()))
            new_hash_value = UtilityFunctions.get_sha256_value(str(sorted_dict))
            if user_data['data']['hash_value'] == new_hash_value:
                user_cache['battles_count'] = user_info['total_battles']
            else:
                user_cache['battles_count'] = user_info['total_battles']
                user_cache['hash_value'] = new_hash_value
                user_cache['ships_data'] = sorted_dict
                user_cache['details_data'] = new_user_data['details']
            ship_id_set = set()
            replace_ship_dict = {}
            if 'hash_value' in user_cache:
                for ship_id, ship_battles in user_cache['ships_data'].items():
                    if (
                        int(ship_id) not in user_data['data']['ships_data'] or 
                        ship_battles != user_data['data']['ships_data'][int(ship_id)]
                    ):
                        replace_ship_dict[int(ship_id)] = user_cache['details_data'][ship_id]
                        ship_id_set.add(int(ship_id))
                check_ship_id_result = await ShipsCacheModel.check_existing_ship(ship_id_set)
                if check_ship_id_result.get('code', None) != 1000:
                    return check_ship_id_result
                if replace_ship_dict != {}:
                    user_cache['ship_dict'] = replace_ship_dict
                else:
                    user_cache['ship_dict'] = {}
                del user_cache['details_data']
            update_result = await ShipsCacheModel.update_user_ships(user_cache)
            if update_result.get('code', None) != 1000:
                return update_result
            # 设置lock，防止频繁更新
            # lock_key = f"updated_user:{region_id}:{account_id}"
            # lock_result = await redis.set(lock_key, '1', ex=600, nx=True)
            # if not lock_result:
            #     return JSONResponse.API_1021_UserUpdateLockFailed
            data = {
                'updated': len(replace_ship_dict)
            }
            return JSONResponse.get_success_response(data)
        except Exception as e:
            raise e
        finally:
            gc.collect()