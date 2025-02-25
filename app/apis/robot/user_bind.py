import json

from app.log import ExceptionLogger
from app.response import JSONResponse
from app.models import BotUserModel, UserAccessToken, UserAccessToken2
from app.middlewares import RedisConnection

class BotUser:
    @ExceptionLogger.handle_program_exception_async
    async def get_user_bind(
        platform: str,
        user_id: str
    ):
        '''用于获取用户绑定数据

        返回用户绑定数据，没有绑定数据则返回None
        
        参数:
            platform, user_id

        返回:
            ResponseDict
        '''
        try:
            # 返回数据的格式
            data = None
            redis = RedisConnection.get_connection()
            key = f"app_bot:bind_cache:{platform}:{user_id}"
            result = await BotUserModel.get_user_bind(platform, user_id)
            if result.get('code',None) != 1000:
                return result
            else:
                data = result['data']
                if data:
                    await redis.set(name=key, value=json.dumps(result['data']),ex=24*60*60)
            # 返回结果
            return JSONResponse.get_success_response(data)
        except Exception as e:
            raise e
        
        
    @ExceptionLogger.handle_program_exception_async
    async def post_user_bind(
        user_data: dict
    ):
        '''用于更新用户绑定数据

        通过用户绑定数据，写入或者更新数据库数据
        
        参数:
            user_data

        返回:
            ResponseDict
        '''
        try:
            # 返回数据的格式
            data = None
            redis = RedisConnection.get_connection()
            key = f"app_bot:bind_cache:{user_data['platform']}:{user_data['user_id']}"
            await redis.delete(key)
            result = await BotUserModel.post_user_bind(user_data)
            if result.get('code',None) != 1000:
                return result
            else:
                data = result['data']
                await redis.set(
                    name=key, 
                    value=json.dumps({'account_id': user_data['account_id'], 'region_id': user_data['region_id']}), 
                    ex=24*60*60
                )
            # 返回结果
            return JSONResponse.get_success_response(data)
        except Exception as e:
            raise e
            
    @ExceptionLogger.handle_program_exception_async
    async def get_user_basic(account_id: int, region_id: int):
        try:
            # 返回数据的格式
            data = {
                'region_id': region_id,
                'user': {},
                'clan': {},
                'token': {}
            }
            # 获取用户相关的access token
            ac_value = await UserAccessToken.get_ac_value_by_id(account_id, region_id)
            ac2_value = UserAccessToken2.get_ac_value_by_id(account_id, region_id)
            data['token'] = {
                'ac': ac_value,
                'ac2': ac2_value
            }
            # 获取用户的名称和工会数据，读取数据库数据并更新redis数据
            redis = RedisConnection.get_connection()
            user_data = await BotUserModel.get_user_data(account_id, region_id)
            if user_data.get('code') != 1000:
                return user_data
            user_data = user_data['data']
            data['user'] = user_data['user']
            if user_data['expired']:
                data['clan'] = None
            else:
                data['clan'] = user_data['clan']
            return JSONResponse.get_success_response(data)
        except Exception as e:
            raise e
            
    @ExceptionLogger.handle_program_exception_async
    async def get_clan_basic(clan_id: int, region_id: int):
        try:
            # 返回数据的格式
            clan_data = await BotUserModel.get_clan_data(clan_id, region_id)
            if clan_data.get('code') != 1000:
                    return clan_data
            return JSONResponse.get_success_response(clan_data['data'])
        except Exception as e:
            raise e