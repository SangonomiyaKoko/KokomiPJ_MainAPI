import gc

from app.log import ExceptionLogger
from app.response import ResponseDict
from app.models import RootModel


class RootData:
    @ExceptionLogger.handle_program_exception_async
    async def get_innodb_trx() -> ResponseDict:
        try:
            result = await RootModel.get_innodb_trx()
            return result         
        except Exception as e:
            raise e
        finally:
            gc.collect()

    @ExceptionLogger.handle_program_exception_async
    async def get_innodb_processlist() -> ResponseDict:
        try:
            result = await RootModel.get_innodb_processlist()
            return result         
        except Exception as e:
            raise e
        finally:
            gc.collect()

    @ExceptionLogger.handle_program_exception_async
    async def get_basic_user_overview() -> ResponseDict:
        try:
            result = await RootModel.get_basic_user_overview()
            return result         
        except Exception as e:
            raise e
        finally:
            gc.collect()

    @ExceptionLogger.handle_program_exception_async
    async def get_basic_clan_overview() -> ResponseDict:
        try:
            result = await RootModel.get_basic_clan_overview()
            return result         
        except Exception as e:
            raise e
        finally:
            gc.collect()

    @ExceptionLogger.handle_program_exception_async
    async def get_recent_user_overview() -> ResponseDict:
        try:
            result = await RootModel.get_recent_user_overview()
            return result         
        except Exception as e:
            raise e
        finally:
            gc.collect()