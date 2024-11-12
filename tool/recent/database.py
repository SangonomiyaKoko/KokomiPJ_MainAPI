import os
import time
import pymysql
import sqlite3
from sqlite3 import Connection
from dbutils.pooled_db import PooledDB
from datetime import datetime, timezone, timedelta

import brotli

from .config import MASTER_DB_PATH, REGION_UTC_LIST
from .network import Recent_Network


class Recent_DB:
    def get_recent_db_path(account_id: int,region_id: int) -> str:
        "获取db文件path"
        return os.path.join(MASTER_DB_PATH, f'{region_id}', f'{account_id}.db')

    def get_db_connection(db_path: str) -> Connection:
        "获取数据库连接"
        connection = sqlite3.connect(db_path)
        return connection

    def create_user_db(self,db_path: str):
        "创建数据库"
        conn: Connection = self.get_recent_db_path(db_path)
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

    @classmethod
    def get_user_info(self,db_path: str):
        "获取user_info表中的数据"
        conn: Connection = self.get_db_connection(db_path)
        cursor = conn.cursor()
        query = f"SELECT date, table_name FROM user_info"
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data

    @classmethod
    def get_user_info_by_date(self, db_path: str, date: str):
        "获取user_info表中的数据"
        conn: Connection = self.get_db_connection(db_path)
        cursor = conn.cursor()
        query = f"SELECT * FROM user_info WHERE date = '{date}'"
        cursor.execute(query)
        data = cursor.fetchone()
        cursor.close()
        conn.close()
        return data
    
    @classmethod
    def delete_date_and_table(
        self,
        db_path: str,
        del_date_list: list = None,
        del_table_list: list = None
    ):
        "删除数据"
        conn: Connection = self.get_db_connection(db_path)
        cursor = conn.cursor()
        del_num = 0
        for del_date in del_date_list:
            query = f"DELETE FROM user_info WHERE date = '{del_date}'"
            cursor.execute(query)
            del_num += 1
        for del_table in del_table_list:
            query = f"DELETE FROM {del_table}"
            cursor.execute(query)
        conn.commit()
        cursor.close()
        conn.close()
        return del_num
    
    @classmethod
    def copy_user_info(self, db_path: str, date_1: str, date_2: str):
        conn: Connection = self.get_db_connection(db_path)
        cursor = conn.cursor()
        query = f"SELECT * FROM user_info WHERE date = '{date_2}'"
        cursor.execute(query)
        data = cursor.fetchone()
        cursor.close()
        conn.close()
        if data is None:
            return False
        else:
            self.insert_database(
                db_path=db_path,
                date=date_1,
                valid=data[1],
                update_time=data[2],
                level_point=data[3],
                karma=data[4],
                battles_count=None,
                table_name=data[5],
                ship_info_data=None
            )
            return True
        

    def get_user_start_date(self,account_id: int,region_id: int):
        db_path = self.get_recent_db_path(account_id,region_id)
        if os.path.exists(db_path) == False:
            return (0,'-')
        rows = self.get_user_info(db_path)
        if rows == []:
            return (0,'-')
        min_date = 0
        date_num = 0
        for row in rows:
            if min_date == 0:
                min_date = row[0]
            else:
                if min_date < row[0]:
                    pass
                else:
                    min_date = row[0]
            date_num += 1
        return (date_num,str(min_date))

    def check_database_exists(self,db_path:str,date_1:str,date_2:str):
        date_1_data = None
        data = None
        if os.path.exists(db_path) is False:
            return None
        conn: Connection = self.get_recent_db_path(db_path)
        cursor = conn.cursor()
        query = f"SELECT * FROM user_info"
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        if data is None:
            return None
        for index in data:
            if str(index[0]) == date_1:
                date_1_data = index
            if str(index[0]) == date_2:
                data = index
        return [date_1_data,data]

    def insert_database(
        self,
        db_path: str,
        date: str,
        valid: bool,
        update_time: int,
        level_point: int,
        karma: int,
        table_name: str,
        battles_count: dict,
        ship_info_data: dict
    ):
        conn: Connection = self.get_db_connection(db_path)
        cursor = conn.cursor()
        insert_data = (date,valid,update_time,level_point,karma,table_name)
        insert_or_replace_query = f'''
        INSERT OR REPLACE INTO user_info (
            date,
            valid,
            update_time,
            leveling_points,
            karma,
            table_name
        ) VALUES (
            ?, ?, ?, ?, ?, ?
        )'''
        cursor.execute(insert_or_replace_query, insert_data)
        if ship_info_data != None:
            table_create_query = f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                ship_id str PRIMARY KEY,
                battles_count int,
                ship_data bytes
            );
            '''
            cursor.execute(table_create_query)
            conn.commit()
            table_delete_query = f'''
            DELETE FROM {table_name}
            '''
            cursor.execute(table_delete_query)
            conn.commit()
            for ship_id,ship_data in ship_info_data.items():
                insert_data = (
                    ship_id,
                    battles_count[ship_id],
                    brotli.compress(bytes(str(ship_data), encoding='utf-8')) if ship_data != {} else None
                )
                insert_or_replace_query = f'''
                INSERT OR REPLACE INTO day_{date} (
                    ship_id,
                    battles_count,
                    ship_data
                ) VALUES (
                    ?, ?, ?
                )'''
                cursor.execute(insert_or_replace_query, insert_data)
            conn.commit()
        cursor.close()
        conn.close()

    def convert_timestamp_to_local_time(timestamp: int, utc_offset: int) -> str:
        utc_time = datetime.fromtimestamp(timestamp, timezone.utc)
        target_time = utc_time + timedelta(hours=utc_offset)
        return target_time.strftime('%Y%m%d')

    async def update(
        self,
        account_id: int,
        region_id: int,
        new: bool,
        valid: bool,
        leveling_points: int,
        karma: int,
        ac_value: str = None
    ):
        timestamp = int(time.time())
        # 今天的日期
        date_1 = self.convert_timestamp_to_local_time(timestamp,REGION_UTC_LIST.get(region_id))
        # 昨天的日期
        date_2 = self.convert_timestamp_to_local_time(timestamp-24*60*60,REGION_UTC_LIST.get(region_id))
        db_path = self.get_recent_db_path(account_id,region_id)
        responses = await Recent_Network.get_recent_data(account_id,region_id,ac_value)
        for response in responses:
            if response['code'] != 1000:
                return response
        result = Recent_Network.data_processing(account_id,responses)
        if new is True:
            Recent_DB.insert_database(
                db_path=db_path,
                date=date_2,
                valid=valid,
                update_time=timestamp,
                level_point=leveling_points,
                karma=karma,
                battles_count=result['battles_count'],
                table_name=f'day_{date_2}',
                ship_info_data=result['ships']
            )
            Recent_DB.insert_database(
                db_path=db_path,
                date=date_1,
                valid=valid,
                update_time=timestamp,
                level_point=leveling_points,
                karma=karma,
                battles_count=result['battles_count'],
                table_name=f'day_{date_2}',
                ship_info_data=None
            )
        else:
            Recent_DB.insert_database(
                db_path=db_path,
                date=date_1,
                valid=valid,
                update_time=timestamp,
                level_point=leveling_points,
                karma=karma,
                battles_count=result['battles_count'],
                table_name=f'day_{date_1}',
                ship_info_data=result['ships']
            )
        return {'status':'ok','message':'SUCCESS'}
