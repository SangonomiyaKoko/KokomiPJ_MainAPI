import gc

from app.log import ExceptionLogger
from app.response import ResponseDict, JSONResponse
from app.models import ClanModel


class ClanCache:
    ...
    # @ExceptionLogger.handle_program_exception_async
    # async def get_clan_max_number() -> ResponseDict:
    #     try:
    #         result = await ClanModel.get_clan_max_number()
    #         return result
    #     except Exception as e:
    #         raise e
    #     finally:
    #         gc.collect()

    # @ExceptionLogger.handle_program_exception_async
    # async def get_clan_cache_data_batch(offset: int, limit: int = 1000) -> ResponseDict:
    #     try:
    #         result = await ClanModel.get_clan_cache_batch(offset, limit)
    #         return result
    #     except Exception as e:
    #         raise e
    #     finally:
    #         gc.collect()