import gc

from app.network import BasicAPI
from app.log import ExceptionLogger
from app.response import JSONResponse,  ResponseDict
from app.utils import ShipName

class Search:
    @ExceptionLogger.handle_program_exception_async
    async def search_user(
        region_id: int, 
        nickname: str, 
        limit: int = 10, 
        check: bool = False
    ) -> ResponseDict:
        try:
            result = await BasicAPI.get_user_search(region_id, nickname, limit, check)
            return result
        except Exception as e:
            raise e
        finally:
            gc.collect()

    @ExceptionLogger.handle_program_exception_async
    async def search_clan(
        region_id: int, 
        tag: str, 
        limit: int = 10, 
        check: bool = False
    ) -> ResponseDict:
        try:
            result = await BasicAPI.get_clan_search(region_id, tag, limit, check)
            return result
        except Exception as e:
            raise e
        finally:
            gc.collect()

    @ExceptionLogger.handle_program_exception_async
    async def search_ship(region_id: int, ship_name: str, language: str) -> ResponseDict:
        try:
            data = ShipName.search_ship(ship_name,region_id,language)
            return JSONResponse.get_success_response(data)
        except Exception as e:
            raise e
        finally:
            gc.collect()

    