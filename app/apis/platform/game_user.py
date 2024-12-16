import gc

from app.log import ExceptionLogger
from app.response import ResponseDict, JSONResponse
from app.models import UserModel, ClanModel, UserAccessToken
from app.network import BasicAPI
from app.utils import UtilityFunctions
from app.middlewares.celery import celery_app
from .user_cache import UserCache

class GameUser:
    @ExceptionLogger.handle_program_exception_async
    async def get_user_basic(account_id: int, region_id: int) -> ResponseDict:
        '''返回用户基本数据'''
        try:
            # 返回数据的格式
            data = {
                'user': {},
                'clan': {},
                'statistics': {}
            }
            # 请求获取user和clan数据
            ac_value = UserAccessToken.get_ac_value_by_id(account_id,region_id)
            # 返回的user和clan数据格式
            user_basic = {
                'id': account_id,
                'region': region_id,
                'name': UtilityFunctions.get_user_default_name(account_id),
                'karma': 0,
                'crated_at': 0,
                'actived_at': 0,
                'dog_tag': {}
            }
            clan_basic = {
                'id': None,
                'tag': None,
                'league': 5
            }
            # 用于后台更新user_info表的数据
            user_info = {
                'account_id': account_id,
                'region_id': region_id,
                'is_active': True,
                'active_level': 0,
                'is_public': True,
                'total_battles': 0,
                'last_battle_time': 0
            }
            # 获取用户的username
            user_basic_result: dict = await UserModel.get_user_name_by_id(account_id, region_id)
            if user_basic_result.get('code',None) != 1000:
                return user_basic_result
            user_basic['name'] = user_basic_result['data']['nickname']

            # 获取用户所在工会的clan_id
            user_clan_result: dict = await UserModel.get_user_clan_id(account_id,region_id)
            if user_clan_result.get('code',None) != 1000:
                return user_clan_result
            valid_clan = True
            # 判断用户所在工会数据是否有效
            if not UtilityFunctions.check_clan_vaild(user_clan_result['data']['updated_at']):
                valid_clan = False
            # 工会的tag和league
            if valid_clan and user_clan_result['data']['clan_id']:
                # 如果有效则获取工会tag和league
                clan_basic_result = await ClanModel.get_clan_tag_and_league(
                    user_clan_result['data']['clan_id'],
                    region_id
                )
                # 判断工会数据是否有效
                if not UtilityFunctions.check_clan_vaild(clan_basic_result['data']['updated_at']):
                    valid_clan = False
                else:
                    clan_basic['id'] = user_clan_result['data']['clan_id']
                    clan_basic['tag'] = clan_basic_result['data']['tag']
                    clan_basic['league'] = clan_basic_result['data']['league']
            
            # 如果clan数据有效则只请求user数据，否则请求user和clan数据
            if valid_clan:
                basic_data = await BasicAPI.get_user_basic(account_id,region_id,ac_value)
            else:
                basic_data = await BasicAPI.get_user_basic_and_clan(account_id,region_id,ac_value)

            for response in basic_data:
                if response['code'] != 1000 and response['code'] != 1001:
                    return response
            # 用户数据
            if basic_data[0]['code'] == 1001:
                # 用户数据不存在
                user_info['is_active'] = False
                celery_app.send_task(
                    name="check_user_info",
                    args=[user_info]
                )
                return JSONResponse.API_1001_UserNotExist
            if user_basic_result['data']['nickname'] != basic_data[0]['data'][str(account_id)]['name']:
                # 用户名称改变
                user_basic['name'] = basic_data[0]['data'][str(account_id)]['name']
                celery_app.send_task(
                    name="check_user_basic",
                    args=[{
                        'account_id':account_id,
                        'region_id':region_id,
                        'nickname':user_basic['name']
                    }]
                )
            if 'hidden_profile' in basic_data[0]['data'][str(account_id)]:
                # 隐藏战绩
                user_info['is_public'] = False
                user_info['active_level'] = UtilityFunctions.get_active_level(user_info)
                if not valid_clan:
                    #处理工会信息
                    user_clan_data = basic_data[1]['data']
                    if user_clan_data['clan_id'] != None:
                        clan_basic['id'] = user_clan_data['clan_id']
                        clan_basic['tag'] = user_clan_data['clan']['tag']
                        clan_basic['league'] = UtilityFunctions.get_league_by_color(user_clan_data['clan']['color'])
                        celery_app.send_task(
                            name="update_clan_and_user",
                            args=[{
                                'clan_id': clan_basic['id'],
                                'region_id': region_id,
                                'tag': clan_basic['tag'],
                                'league': clan_basic['league']
                            },
                            {
                                'account_id': user_basic['id'],
                                'clan_id': clan_basic['id']
                            }]
                        )
                    else:
                        celery_app.send_task(
                            name="update_user_clan",
                            args=[{
                                'account_id': user_basic['id'],
                                'clan_id': None
                            }]
                        )
                celery_app.send_task(
                    name="check_user_info",
                    args=[user_info]
                )
                if ac_value:
                    return JSONResponse.API_1013_ACisInvalid
                else:
                    return JSONResponse.API_1005_UserHiddenProfite
            user_basic_data = basic_data[0]['data'][str(account_id)]['statistics']
            if (
                user_basic_data == {} or
                user_basic_data['basic'] == {}
            ):
                # 用户没有数据
                user_info['is_active'] = False
                celery_app.send_task(
                    name="check_user_info",
                    args=[user_info]
                )
                return JSONResponse.API_1006_UserDataisNone
            if user_basic_data['basic']['leveling_points'] == 0:
                # 用户没有数据
                user_info['total_battles'] = 0
                user_info['last_battle_time'] = 0
                user_info['active_level'] = 1
                celery_app.send_task(
                    name="check_user_info",
                    args=[user_info]
                )
                return JSONResponse.API_1006_UserDataisNone
            # 获取user_info的数据并更新数据库
            user_info['total_battles'] = user_basic_data['basic']['leveling_points']
            user_info['last_battle_time'] = user_basic_data['basic']['last_battle_time']
            user_info['active_level'] = UtilityFunctions.get_active_level(user_info)
            celery_app.send_task(
                name="check_user_info",
                args=[user_info]
            )
            # 获取user_basic的数据
            user_basic['karma'] = user_basic_data['basic']['karma']
            user_basic['crated_at'] = user_basic_data['basic']['created_at']
            user_basic['actived_at'] = user_basic_data['basic']['last_battle_time']
            user_basic['dog_tag'] = basic_data[0]['data'][str(account_id)]['dog_tag']
            if not valid_clan:
                #处理工会信息
                user_clan_data = basic_data[1]['data']
                if user_clan_data['clan_id'] != None:
                    clan_basic['id'] = user_clan_data['clan_id']
                    clan_basic['tag'] = user_clan_data['clan']['tag']
                    clan_basic['league'] = UtilityFunctions.get_league_by_color(user_clan_data['clan']['color'])
                    celery_app.send_task(
                        name="update_clan_and_user",
                        args=[{
                            'clan_id': clan_basic['id'],
                            'region_id': region_id,
                            'tag': clan_basic['tag'],
                            'league': clan_basic['league']
                        },
                        {
                            'account_id': user_basic['id'],
                            'clan_id': clan_basic['id']
                        }]
                    )
                else:
                    celery_app.send_task(
                        name="update_user_clan",
                        args=[{
                            'account_id': user_basic['id'],
                            'clan_id': None
                        }]
                    )
            # 返回user和clan数据
            data['user'] = user_basic
            data['clan'] = clan_basic

            # 返回结果
            return JSONResponse.get_success_response(data)
        except Exception as e:
            raise e
    
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
