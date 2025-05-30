import os
import shutil

from sqlite3 import Connection
from app.db import SQLiteConnection
from app.log import ExceptionLogger
from app.response import ResponseDict, JSONResponse
from app.utils import TimeFormat, UtilityFunctions

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
        # 实际上是将数据转移到待删除文件夹中，防止程序bug导致误删后可以恢复
        user_db_path = SQLiteConnection.get_recent_db_path(account_id,region_id)
        try:
            if os.path.exists(user_db_path):
                # 目标文件夹路径
                destination_folder = SQLiteConnection.get_del_dir_path()
                # 将数据库文件转移到待删除文件夹
                shutil.move(user_db_path, destination_folder)
        except Exception as e:
            raise e

    @ExceptionLogger.handle_database_exception_sync
    def get_user_recent_info(account_id: int, region_id: int) -> ResponseDict:
        user_db_path = SQLiteConnection.get_recent_db_path(account_id,region_id)
        if not os.path.exists(user_db_path):
            return JSONResponse.API_1018_RecentNotEnabled
        try:
            "创建用户recent数据库"
            conn: Connection = SQLiteConnection.get_db_connection(user_db_path)
            cursor = conn.cursor()
            
            sql = f'''
            SELECT date, valid, leveling_points FROM user_info;
            '''
            cursor.execute(sql)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            # 最远从2023年开始统计
            min_date = max(min(t[0] for t in rows), 20221231)
            # 获取日期最小是
            min_timestamp = TimeFormat.db_date2timestamp(min_date, region_id)
            max_timestamp = TimeFormat.db_date2timestamp(TimeFormat.db_timestamp(region_id), region_id)
            # 数据库原始护具
            db_data = {}
            for row in rows:
                db_data[row[0]] = [True if row[1] == 0 else False, row[2]]
            db_result = {}
            exists_years = []
            # 循环逐项计算lp的差值
            current_timestamp = min_timestamp
            while current_timestamp <= max_timestamp - 24*60*60:
                date_1 = TimeFormat.db_timestamp2date(current_timestamp, region_id)
                date_1_data = db_data.get(date_1)
                current_timestamp += 24*60*60
                date_2 = TimeFormat.db_timestamp2date(current_timestamp, region_id)
                year = int(str(date_2)[:4])
                if year not in exists_years:
                    exists_years.append(year)
                date_2_data = db_data.get(date_2)
                if date_1_data and date_2_data:
                    if date_1_data[0] and date_2_data[0]:
                        counts = date_2_data[1] - date_1_data[1]
                        db_result[date_2] = counts
                    else:
                        # Hidden
                        db_result[date_2] = -1
                else:
                    # error
                    db_result[date_2] = -2
            # 最后的数据处理
            result = {
                'size': str(UtilityFunctions.get_file_size_in_mb(user_db_path)) + ' MB',
                'len': len(rows),
                'years': exists_years,
                'data': {}
            }
            for year in exists_years:
                year_data = []
                days = TimeFormat.db_generate_date_list(year)
                for day in days:
                    if day not in db_result:
                        year_data.append(None)
                    else:
                        year_data.append(db_result[day])
                result['data'][year] = year_data
            return JSONResponse.get_success_response(result)
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