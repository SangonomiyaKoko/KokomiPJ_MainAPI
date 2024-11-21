import os
import shutil

from sqlite3 import Connection
from app.db import SQLiteConnection
from app.log import ExceptionLogger
from app.response import ResponseDict

class RecentDatabaseModel:
    @classmethod
    @ExceptionLogger.handle_database_exception_sync
    def get_recent_overview(self, account_id: int, region_id: int) -> ResponseDict:
        "获取用户数据库是否存在，不存在则创建数据库"
        user_db_path = SQLiteConnection.get_recent_db_path(account_id,region_id)
        try:
            if not os.path.exists(user_db_path):
                self.__create_user_db(user_db_path)
        except Exception as e:
            raise e

    @ExceptionLogger.handle_database_exception_sync
    def del_user_recent(account_id: int, region_id: int) -> ResponseDict:
        "删除用户的recent数据"
        # 实际上是将数据转移到待删除文件夹中，防止程序bug导致误删
        user_db_path = SQLiteConnection.get_recent_db_path(account_id,region_id)
        try:
            if os.path.exists(user_db_path):
                # 目标文件夹路径
                destination_folder = SQLiteConnection.get_del_dir_path()
                # 将数据库文件转移到待删除文件夹
                shutil.move(user_db_path, destination_folder)
        except Exception as e:
            raise e


    def __create_user_db(db_path: str) -> None:
        "创建用户recent数据库"
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