import gc

from app.network import BasicAPI
from app.log import ExceptionLogger
from app.response import JSONResponse, ResponseDict
from app.models import RecentUserModel, RecentDatabaseModel, UserModel, UserAccessToken
from app.utils import UtilityFunctions, TimeFormat
from app.middlewares.celery import task_check_user_basic, task_check_user_info, task_check_user_recent


class RecentBasic:
    @ExceptionLogger.handle_program_exception_async
    async def get_recent(region_id: int) -> ResponseDict:
        try:
            data = {
                'users': None,
                'access': None
            }
            result = await RecentUserModel.get_recent_user_by_rid(region_id)
            if result.get('code', None) != 1000:
                return result
            ac_value = UserAccessToken.get_ac_value_by_rid(region_id)
            data['users'] = result['data']
            data['access'] = ac_value
            return JSONResponse.get_success_response(data)            
        except Exception as e:
            raise e
        finally:
            gc.collect()

    @classmethod
    @ExceptionLogger.handle_program_exception_async
    async def add_recent(self, account_id: int,region_id: int, recent_class: int) -> ResponseDict:
        try:
            check_result = await self.__check_user_status(account_id,region_id)
            if check_result.get('code',None) != 1000:
                return check_result
            result = await RecentUserModel.add_recent_user(account_id,region_id,recent_class)
            return result
        except Exception as e:
            raise e
        finally:
            gc.collect()

    @classmethod
    @ExceptionLogger.handle_program_exception_async
    async def update_recent(self, user_data: dict) -> ResponseDict:
        try:
            if user_data['user_recent']:
                task_check_user_recent.delay(user_data['user_recent'])
            if user_data['user_basic']:
                task_check_user_basic.delay(user_data['user_basic'])
            if user_data['user_info']:
                task_check_user_info.delay(user_data['user_info'])
            return JSONResponse.API_1000_Success
        except Exception as e:
            raise e
        finally:
            gc.collect()

    @ExceptionLogger.handle_program_exception_async
    async def del_recent(account_id: int,region_id: int) -> ResponseDict:
        try:
            # 先删recent数据库再删user_recent数据库，防止出现垃圾数据
            RecentDatabaseModel.del_user_recent(account_id,region_id)
            result = await RecentUserModel.del_recent_user(account_id,region_id)
            return result
        except Exception as e:
            raise e
        finally:
            gc.collect()

    @ExceptionLogger.handle_program_exception_async
    async def get_user_recent(account_id: int, region_id: int) -> ResponseDict:
        try:
            result = await RecentUserModel.get_user_recent_data(account_id,region_id)
            return result
        except Exception as e:
            raise e
        finally:
            gc.collect()

    async def __check_user_status(account_id: int,region_id: int) -> ResponseDict:
        '''检查用户数据是否符合开启recent的条件

        1. 账号有数据
        2. 最近6个月活跃

        只有符合条件的账号才会启用
        '''
        # 用于后台更新user_info表的数据
        user_basic = {
            'account_id': account_id,
            'region_id': region_id,
            'nickname': None
        }
        user_info = {
            'account_id': account_id,
            'region_id': region_id,
            'is_active': True,
            'active_level': 0,
            'is_public': True,
            'total_battles': 0,
            'last_battle_time': 0
        }
        # 确保user在数据库中
        user_basic_result: dict = await UserModel.get_user_name_by_id(account_id, region_id)
        if user_basic_result.get('code',None) != 1000:
            return user_basic_result
        # 请求获取数据
        basic_data = await BasicAPI.get_user_basic(account_id,region_id)
        for response in basic_data:
            if response['code'] != 1000 and response['code'] != 1001:
                return response
        # 用户数据
        if basic_data[0]['code'] == 1001:
            # 用户数据不存在
            user_info['is_active'] = False
            task_check_user_info.delay(user_info)
            return JSONResponse.API_1001_UserNotExist
        if user_basic['nickname'] != user_basic_result['data']['nickname']:
            # 用户名称改变
            user_basic['nickname'] = basic_data[0]['data'][str(account_id)]['name']
            task_check_user_basic.delay(user_basic)
        if 'hidden_profile' in basic_data[0]['data'][str(account_id)]:
            # 隐藏战绩
            user_info['is_public'] = False
            user_info['active_level'] = UtilityFunctions.get_active_level(user_info)
            task_check_user_info.delay(user_info)
            return JSONResponse.API_1005_UserHiddenProfite
        user_basic_data = basic_data[0]['data'][str(account_id)]['statistics']
        if (
            user_basic_data == {} or
            user_basic_data['basic'] == {} or
            user_basic_data['basic']['leveling_points'] == 0
        ):
            # 用户没有数据
            user_info['total_battles'] = 0
            user_info['last_battle_time'] = 0
            user_info['active_level'] = UtilityFunctions.get_active_level(user_info)
            task_check_user_info.delay(user_info)
            return JSONResponse.API_1006_UserDataisNone
        # 获取user_info的数据并更新数据库
        user_info['total_battles'] = user_basic_data['basic']['leveling_points']
        user_info['last_battle_time'] = user_basic_data['basic']['last_battle_time']
        user_info['active_level'] = UtilityFunctions.get_active_level(user_info)
        task_check_user_info.delay(user_info)
        # 检查用户是否活跃
        current_timestamp = TimeFormat.get_current_timestamp()
        if current_timestamp - user_basic_data['basic']['last_battle_time'] >= 180*24*60*60:
            return JSONResponse.API_1014_EnableRecentFailed
        return JSONResponse.API_1000_Success