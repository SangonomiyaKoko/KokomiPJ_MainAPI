import gc

from app.log import ExceptionLogger
from app.response import ResponseDict, JSONResponse
from app.network import BasicAPI
from app.models import GameModel

class GameBasic:
    @ExceptionLogger.handle_program_exception_async
    async def get_game_version(region_id: int) -> ResponseDict:
        '''获取游戏当前版本
        
        如果网络请求失败则从数据库中读取上次存储的数据
        确保在游戏服务器维护的时候能够获取到数据'''
        try:
            result = await BasicAPI.get_game_version(region_id)
            if result.get('code', None) != 1000:
                return result
            if result['data']:
                data = {
                    'region_id': region_id,
                    'version': result['data']['version']
                }
                celery_app.send_task(
                    name="check_game_version",
                    args=[data]
                )
                return result
            else:
                result = await GameModel.get_game_version(region_id)
                return result
        except Exception as e:
            raise e
        finally:
            gc.collect()
        