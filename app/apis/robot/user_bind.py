from app.log import ExceptionLogger
from app.response import JSONResponse
from app.models import BotUserModel

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
            result = await BotUserModel.get_user_bind(platform, user_id)
            if result.get('code',None) != 1000:
                return result
            else:
                data = result['data']
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
            result = await BotUserModel.post_user_bind(user_data)
            if result.get('code',None) != 1000:
                return result
            else:
                data = result['data']
            # 返回结果
            return JSONResponse.get_success_response(data)
        except Exception as e:
            raise e