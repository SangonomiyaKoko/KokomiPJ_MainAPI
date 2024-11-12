import uuid
import traceback
from typing import Optional
from aiomysql import MySQLError
from aiomysql.connection import Connection
from aiomysql.cursors import Cursor

from app.db import MysqlConnection
from app.log import write_error_info
from app.response import JSONResponse

class RecentUserModel:
    async def get_recent_user_by_rid(region_id: int):
        conn: Connection = await MysqlConnection.get_connection()
        cur: Cursor = await conn.cursor()
        try:
            data = []
            await cur.execute(
                "SELECT account_id FROM recent WHERE region_id = %s;",
                [region_id]
            )
            users = await cur.fetchall()
            for user in users:
                data.append(user[0])
            return JSONResponse.get_success_response(data)
        except MySQLError as e:
            await conn.rollback()
            error_id = str(uuid.uuid4())
            traceback.print_exc()
            write_error_info(
                error_id = error_id,
                error_type = 'MySQL',
                error_name = f'ERROR_{e.args[0]}',
                error_file = __file__,
                error_info = f'\n{str(e.args[1])}'
            )
            return JSONResponse.get_error_response(3000,'DatabaseError',error_id)
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
            await cur.close()
            await MysqlConnection.release_connection(conn)


    async def add_recent_user(account_id: int, region_id: int, recent_class: int):
        conn: Connection = await MysqlConnection.get_connection()
        cur: Cursor = await conn.cursor()
        try:
            await cur.execute(
                "SELECT recent_class FROM recent WHERE region_id = %s and account_id = %s;", 
                [region_id, account_id]
            )
            user = await cur.fetchone()
            if user is None:
                # 用户不存在，插入新用户
                await cur.execute(
                    "INSERT IGNORE INTO recent (account_id, region_id, recent_class) VALUES (%s, %s, %s);",
                    [account_id, region_id, recent_class]
                )
                await conn.commit()
            else:
                if user[0] <= recent_class:
                    await cur.execute(
                        "UPDATE recent SET recent_class = %s WHERE region_id = %s and account_id = %s;",
                        [recent_class, region_id, account_id]
                    )
                    await conn.commit()
            return JSONResponse.API_1000_Success
        except MySQLError as e:
            await conn.rollback()
            error_id = str(uuid.uuid4())
            traceback.print_exc()
            write_error_info(
                error_id = error_id,
                error_type = 'MySQL',
                error_name = f'ERROR_{e.args[0]}',
                error_file = __file__,
                error_info = f'\n{str(e.args[1])}'
            )
            return JSONResponse.get_error_response(3000,'DatabaseError',error_id)
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
            await cur.close()
            await MysqlConnection.release_connection(conn)

    async def del_recent_user(account_id: int, region_id: int):
        conn: Connection = await MysqlConnection.get_connection()
        cur: Cursor = await conn.cursor()
        try:
            await cur.execute(
                "DELETE FROM recent WHERE region_id = %s and account_id = %s;",
                [region_id, account_id]
            )
            await conn.commit()
            return JSONResponse.API_1000_Success
        except MySQLError as e:
            await conn.rollback()
            error_id = str(uuid.uuid4())
            traceback.print_exc()
            write_error_info(
                error_id = error_id,
                error_type = 'MySQL',
                error_name = f'ERROR_{e.args[0]}',
                error_file = __file__,
                error_info = f'\n{str(e.args[1])}'
            )
            return JSONResponse.get_error_response(3000,'DatabaseError',error_id)
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
            await cur.close()
            await MysqlConnection.release_connection(conn)


    async def update_recent_user(user_recent: dict):
        conn: Connection = await MysqlConnection.get_connection()
        cur: Cursor = await conn.cursor()
        try:
            account_id = user_recent['account_id']
            region_id = user_recent['region_id']
            await cur.execute(
                "SELECT recent_class, last_query_time, last_write_time, last_update_time FROM recent WHERE region_id = %s and account_id = %s;", 
                [region_id, account_id]
            )
            user = await cur.fetchone()
            sql_str = ''
            params = []
            i = 0
            for user_recent_key in ['recent_class', 'last_query_time', 'last_write_time', 'last_update_time']:
                if user_recent.get(user_recent_key) == None:
                    continue
                if user[i] != user_recent.get(user_recent_key):
                    sql_str += f'{user_recent_key} = %s, '
                    params.append(user_recent.get(user_recent_key))
                i += 1
            params = params + [region_id, account_id]
            await cur.execute(
                f"UPDATE recent SET {sql_str},updated_at = CURRENT_TIMESTAMP WHERE region_id = %s and account_id = %s;",
                params
            )
            await conn.commit()
            return JSONResponse.API_1000_Success
        except MySQLError as e:
            await conn.rollback()
            error_id = str(uuid.uuid4())
            traceback.print_exc()
            write_error_info(
                error_id = error_id,
                error_type = 'MySQL',
                error_name = f'ERROR_{e.args[0]}',
                error_file = __file__,
                error_info = f'\n{str(e.args[1])}'
            )
            return JSONResponse.get_error_response(3000,'DatabaseError',error_id)
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
            await cur.close()
            await MysqlConnection.release_connection(conn)

    async def get_user_recent_data(account_id: int, region_id: int):
        '''获取用户recent表的数据'''
        conn: Connection = await MysqlConnection.get_connection()
        cur: Cursor = await conn.cursor()
        try:
            await cur.execute(
                "SELECT recent_class, last_query_time, last_write_time, last_update_time FROM recent "
                "WHERE region_id = %s and account_id = %s;",
                [region_id, account_id]
            )
            user = await cur.fetchone()
            if user:
                data = {
                    'recent_class': user[0],
                    'last_query_time': user[1],
                    'last_write_time': user[2],
                    'last_update_time': user[3]
                }
            else:
                data = None
            return JSONResponse.get_success_response(data)
        except MySQLError as e:
            await conn.rollback()
            error_id = str(uuid.uuid4())
            traceback.print_exc()
            write_error_info(
                error_id = error_id,
                error_type = 'MySQL',
                error_name = f'ERROR_{e.args[0]}',
                error_file = __file__,
                error_info = f'\n{str(e.args[1])}'
            )
            return JSONResponse.get_error_response(3000,'DatabaseError',error_id)
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
            await cur.close()
            await MysqlConnection.release_connection(conn)