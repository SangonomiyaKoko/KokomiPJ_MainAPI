import gc

from app.log import ExceptionLogger
from app.response import ResponseDict, JSONResponse
from app.models import ClanModel

class GameClan:
    @ExceptionLogger.handle_program_exception_async
    async def get_clan(region_id: int) -> ResponseDict:
        try:
            data = {
                'clans': None
            }
            result = await ClanModel.get_clan_by_rid(region_id)
            if result.get('code', None) != 1000:
                return result
            data['clans'] = result['data']
            return JSONResponse.get_success_response(data)
        except Exception as e:
            raise e
        finally:
            gc.collect()