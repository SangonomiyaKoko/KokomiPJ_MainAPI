import gc
import uuid
import traceback

from app.network import BasicAPI
from app.log import write_error_info
from app.response import JSONResponse
from app.utils import ShipName

class Search:
    async def search_user(region_id: int, nickname: str, limit: int = 10, check: bool = False):
        try:
            result = await BasicAPI.get_user_search(region_id, nickname, limit, check)
            return result
        except Exception as e:
            error_id = str(uuid.uuid4())
            write_error_info(
                error_id = error_id,
                error_type = 'Program',
                error_name = str(type(e).__name__),
                error_file = __file__,
                error_info = f'\n{traceback.format_exc()}'
            )
            return JSONResponse.get_error_response(5000,'ProgramError',error_id)
        finally:
            gc.collect()


    async def search_clan(region_id: int, tag: str, limit: int = 10, check: bool = False):
        try:
            result = await BasicAPI.get_clan_search(region_id, tag, limit, check)
            return result
        except Exception as e:
            error_id = str(uuid.uuid4())
            write_error_info(
                error_id = error_id,
                error_type = 'Program',
                error_name = str(type(e).__name__),
                error_file = __file__,
                error_info = f'\n{traceback.format_exc()}'
            )
            return JSONResponse.get_error_response(5000,'ProgramError',error_id)
        finally:
            gc.collect()

    async def search_ship(region_id: int, ship_name: str, language: str):
        try:
            data = ShipName.search_ship(ship_name,region_id,language)
            return JSONResponse.get_success_response(data)
        except Exception as e:
            error_id = str(uuid.uuid4())
            write_error_info(
                error_id = error_id,
                error_type = 'Program',
                error_name = str(type(e).__name__),
                error_file = __file__,
                error_info = f'\n{traceback.format_exc()}'
            )
            return JSONResponse.get_error_response(5000,'ProgramError',error_id)
        finally:
            gc.collect()

    