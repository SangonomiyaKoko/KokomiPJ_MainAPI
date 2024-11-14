
from app.db import SQLiteConnection
from app.log import ExceptionLogger

class RecentDatabaseModel:
    @ExceptionLogger.handle_database_exception_sync
    def get_recent_overview(account_id: int, region_id: int):
        user_db_path = SQLiteConnection.get_recent_db_path(account_id,region_id)
        try:
            ...
        except Exception as e:
            raise e
        finally:
            ...