from aiomysql.connection import Connection
from aiomysql.cursors import Cursor

from app.db import MysqlConnection
from app.log import ExceptionLogger
from app.response import JSONResponse, ResponseDict
from app.utils import TimeFormat

from .db_name import MAIN_DB


class RecentUserModel:
    @ExceptionLogger.handle_database_exception_async
    async def check_recent_user(account_id: int, region_id: int) -> ResponseDict:
        try:
            conn: Connection = await MysqlConnection.get_connection()
            await conn.begin()
            cur: Cursor = await conn.cursor()

            data = {
                'enabled': False
            }
            await cur.execute(
                f"SELECT EXISTS(SELECT 1 FROM {MAIN_DB}.recent WHERE region_id = %s and account_id = %s) AS is_exists_user;",
                [region_id, account_id]
            )
            user = await cur.fetchone()
            if user[0]:
                data['enabled'] = True
            
            await conn.commit()
            return JSONResponse.get_success_response(data)
        except Exception as e:
            await conn.rollback()
            raise e
        finally:
            await cur.close()
            await MysqlConnection.release_connection(conn)

    @ExceptionLogger.handle_database_exception_async
    async def add_recent_user(account_id: int, region_id: int, recent_class: int) -> ResponseDict:
        try:
            conn: Connection = await MysqlConnection.get_connection()
            await conn.begin()
            cur: Cursor = await conn.cursor()

            await cur.execute(
                f"SELECT recent_class FROM {MAIN_DB}.recent WHERE region_id = %s and account_id = %s;", 
                [region_id, account_id]
            )
            user = await cur.fetchone()
            if user is None:
                # 用户不存在，插入新用户
                current_timestamp = TimeFormat.get_current_timestamp()
                await cur.execute(
                    f"INSERT INTO {MAIN_DB}.recent (account_id, region_id, recent_class, last_query_at) "
                    "VALUES (%s, %s, %s, FROM_UNIXTIME(%s));",
                    [account_id, region_id, recent_class, current_timestamp]
                )
            else:
                if user[0] <= recent_class:
                    await cur.execute(
                        f"UPDATE {MAIN_DB}.recent SET recent_class = %s WHERE region_id = %s and account_id = %s;",
                        [recent_class, region_id, account_id]
                    )
            
            await conn.commit()
            return JSONResponse.API_1000_Success
        except Exception as e:
            await conn.rollback()
            raise e
        finally:
            await cur.close()
            await MysqlConnection.release_connection(conn)

    @ExceptionLogger.handle_database_exception_async
    async def del_recent_user(account_id: int, region_id: int) -> ResponseDict:
        try:
            conn: Connection = await MysqlConnection.get_connection()
            await conn.begin()
            cur: Cursor = await conn.cursor()

            await cur.execute(
                f"DELETE FROM {MAIN_DB}.recent WHERE region_id = %s and account_id = %s;",
                [region_id, account_id]
            )

            await conn.commit()
            return JSONResponse.API_1000_Success
        except Exception as e:
            await conn.rollback()
            raise e
        finally:
            await cur.close()
            await MysqlConnection.release_connection(conn)
