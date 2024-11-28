from aiomysql.connection import Connection
from aiomysql.cursors import Cursor

from app.db import MysqlConnection
from app.log import ExceptionLogger
from app.response import JSONResponse, ResponseDict
from app.utils import TimeFormat


class RecentUserModel:
    @ExceptionLogger.handle_database_exception_async
    async def get_recent_user_by_rid(region_id: int) -> ResponseDict:
        try:
            conn: Connection = await MysqlConnection.get_connection()
            await conn.begin()
            cur: Cursor = await conn.cursor()

            data = []
            await cur.execute(
                "SELECT account_id FROM kokomi.recent WHERE region_id = %s;",
                [region_id]
            )
            users = await cur.fetchall()
            for user in users:
                data.append(user[0])
            
            await conn.commit()
            return JSONResponse.get_success_response(data)
        except Exception as e:
            await conn.rollback()
            raise e
        finally:
            await cur.close()
            await MysqlConnection.release_connection(conn)

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
                "SELECT EXISTS(SELECT 1 FROM kokomi.recent WHERE region_id = %s and account_id = %s) AS is_exists_user;",
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
                "SELECT recent_class FROM kokomi.recent WHERE region_id = %s and account_id = %s;", 
                [region_id, account_id]
            )
            user = await cur.fetchone()
            if user is None:
                # 用户不存在，插入新用户
                current_timestamp = TimeFormat.get_current_timestamp()
                await cur.execute(
                    "INSERT INTO kokomi.recent (account_id, region_id, recent_class, last_query_at) VALUES (%s, %s, %s, FROM_UNIXTIME(%s));",
                    [account_id, region_id, recent_class, current_timestamp]
                )
            else:
                if user[0] <= recent_class:
                    await cur.execute(
                        "UPDATE kokomi.recent SET recent_class = %s WHERE region_id = %s and account_id = %s;",
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
                "DELETE FROM kokomi.recent WHERE region_id = %s and account_id = %s;",
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

    @ExceptionLogger.handle_database_exception_async
    async def get_user_recent_data(account_id: int, region_id: int) -> ResponseDict:
        '''获取用户recent表的数据'''
        try:
            conn: Connection = await MysqlConnection.get_connection()
            await conn.begin()
            cur: Cursor = await conn.cursor()

            await cur.execute(
                "SELECT u.is_active, u.active_level, u.is_public, u.total_battles, UNIX_TIMESTAMP(u.last_battle_at) AS last_battle_time, "
                "UNIX_TIMESTAMP(u.updated_at) AS update_time, r.recent_class, "
                "UNIX_TIMESTAMP(r.last_query_at) AS last_query_time, UNIX_TIMESTAMP(r.last_update_at) AS last_update_time "
                "FROM kokomi.recent AS r "
                "LEFT JOIN kokomi.user_info AS u ON u.account_id = r.account_id "
                "WHERE r.region_id = %s and r.account_id = %s;",
                [region_id, account_id]
            )
            user = await cur.fetchone()
            if user:
                data = {
                    'user_recent': {
                        'recent_class': user[6],
                        'last_query_time': user[7],
                        'last_update_time': user[8]
                    },
                    'user_info': {
                        'is_active': user[0],
                        'active_level': user[1],
                        'is_public': user[2],
                        'total_battles': user[3],
                        'last_battle_time': user[4],
                        'update_time': user[5]
                    }
                }
            else:
                await conn.commit()
                return JSONResponse.API_1018_RecentNotEnabled
            
            await conn.commit()
            return JSONResponse.get_success_response(data)
        except Exception as e:
            await conn.rollback()
            raise e
        finally:
            await cur.close()
            await MysqlConnection.release_connection(conn)