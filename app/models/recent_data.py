import os
from sqlite3 import Connection
from app.db import SQLiteConnection
from app.log import ExceptionLogger
from app.response import ResponseDict

class RecentDatabaseModel:
    @classmethod
    @ExceptionLogger.handle_database_exception_sync
    def get_recent_overview(self, account_id: int, region_id: int) -> ResponseDict:
        user_db_path = SQLiteConnection.get_recent_db_path(account_id,region_id)
        try:
            if not os.path.exists(user_db_path):
                self.__create_user_db(user_db_path)

        except Exception as e:
            raise e
        finally:
            ...

    def __create_user_db(db_path: str) -> None:
        "创建数据库"
        conn: Connection = SQLiteConnection.get_db_connection(db_path)
        cursor = conn.cursor()
        table_create_query = f'''
        CREATE TABLE user_info (
            date str PRIMARY KEY,
            valid bool,
            update_time int,
            leveling_points int,
            karma int,
            table_name str
        );
        '''
        cursor.execute(table_create_query)
        conn.commit()
        cursor.close()
        conn.close()