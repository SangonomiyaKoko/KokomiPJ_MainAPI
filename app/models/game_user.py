from aiomysql.connection import Connection
from aiomysql.cursors import Cursor

from .access_token import UserAccessToken
from app.db import MysqlConnection
from app.log import ExceptionLogger
from app.response import JSONResponse, ResponseDict
from app.utils import UtilityFunctions, TimeFormat, BinaryParserUtils

from .db_name import MAIN_DB


class UserModel:
    # # 函数统一格式格式
    @ExceptionLogger.handle_database_exception_async
    async def func() -> ResponseDict:
        '''方法介绍

        方法描述

        参数:
            params
        
        返回:
            ResponseDict
        '''
        try:
            connection: Connection = await MysqlConnection.get_connection()  # 获取连接
            await connection.begin()  # 开启事务
            cursor: Cursor = await connection.cursor()  # 获取游标

            # 在这里执行sql语句
            await cursor.execute()

            await connection.commit()  # 提交事务
            return JSONResponse.API_1000_Success  # 返回数据
        except Exception as e:
            await connection.rollback()  # 执行报错回滚事务
            raise e  # 抛出异常
        finally:
            await cursor.close()  # 关闭游标
            await MysqlConnection.release_connection(connection)  # 释放连接

    @ExceptionLogger.handle_database_exception_async
    async def get_user_name_by_id(account_id: int, region_id: int) -> ResponseDict:
        '''获取用户名称

        从user_basic中获取用户名称数据

        如果用户不存在会插入并返回一个默认值

        参数：
            account_id: 用户id
            region_id: 服务器id

        返回：
            ResponseDict
        '''
        try:
            conn: Connection = await MysqlConnection.get_connection()
            await conn.begin()
            cur: Cursor = await conn.cursor()

            data = {
                'nickname': None,
                'update_time': None
            }
            await cur.execute(
                "SELECT username, UNIX_TIMESTAMP(updated_at) AS update_time "
                f"FROM {MAIN_DB}.user_basic WHERE region_id = %s and account_id = %s;", 
                [region_id, account_id]
            )
            user = await cur.fetchone()
            if user is None:
                # 用户不存在
                name = UtilityFunctions.get_user_default_name(account_id)
                await cur.execute(
                    f"INSERT INTO {MAIN_DB}.user_basic (account_id, region_id, username) VALUES (%s, %s, %s);",
                    [account_id, region_id, name]
                )
                await cur.execute(
                    f"INSERT INTO {MAIN_DB}.user_info (account_id) VALUES (%s);",
                    [account_id]
                )
                await cur.execute(
                    f"INSERT INTO {MAIN_DB}.user_ships (account_id) VALUES (%s);",
                    [account_id]
                )
                await cur.execute(
                    f"INSERT INTO {MAIN_DB}.user_clan (account_id) VALUES (%s);",
                    [account_id]
                )
                data['nickname'] = name
                data['update_time'] = None
            else:
                data['nickname'] = user[0]
                data['update_time'] = user[1]
            
            await conn.commit()
            return JSONResponse.get_success_response(data)
        except Exception as e:
            await conn.rollback()
            raise e
        finally:
            await cur.close()
            await MysqlConnection.release_connection(conn)

    @ExceptionLogger.handle_database_exception_async
    async def get_user_clan_id(account_id: int, region_id: int) -> ResponseDict:
        '''获取用户所在工会数据

        从clan_user中获取用户工会id

        参数：
            account_id: 用户id

        返回：
            ResponseDict
        '''
        try:
            conn: Connection = await MysqlConnection.get_connection()
            await conn.begin()
            cur: Cursor = await conn.cursor()

            data =  {
                'clan_id': None,
                'updated_at': 0
            }
            await cur.execute(
                "SELECT clan_id, UNIX_TIMESTAMP(updated_at) AS update_time "
                f"FROM {MAIN_DB}.user_clan WHERE account_id = %s;", 
                [account_id]
            )
            user = await cur.fetchone()
            if user is None:
                # 用户不存在
                name = UtilityFunctions.get_user_default_name(account_id)
                await cur.execute(
                    f"INSERT INTO {MAIN_DB}.user_basic (account_id, region_id, username) VALUES (%s, %s, %s);",
                    [account_id, region_id, name]
                )
                await cur.execute(
                    f"INSERT INTO {MAIN_DB}.user_info (account_id) VALUES (%s);",
                    [account_id]
                )
                await cur.execute(
                    f"INSERT INTO {MAIN_DB}.user_ships (account_id) VALUES (%s);",
                    [account_id]
                )
                await cur.execute(
                    f"INSERT INTO {MAIN_DB}.user_clan (account_id) VALUES (%s);",
                    [account_id]
                )
                data['clan_id'] = None
                data['updated_at'] = None
            else:
                data['clan_id'] = user[0]
                data['updated_at'] = user[1]
            
            await conn.commit()
            return JSONResponse.get_success_response(data)
        except Exception as e:
            await conn.rollback()
            raise e
        finally:
            await cur.close()
            await MysqlConnection.release_connection(conn)

    @ExceptionLogger.handle_database_exception_async
    async def get_user_cache(account_id: int, region_id: int) -> ResponseDict:
        '''获取用户详细数据

        参数：
            account_id: 用户id

        返回：
            ResponseDict
        '''
        try:
            conn: Connection = await MysqlConnection.get_connection()
            await conn.begin()
            cur: Cursor = await conn.cursor()

            await cur.execute(
                "SELECT battles_count, hash_value, ships_data, UNIX_TIMESTAMP(updated_at) AS update_time "
                f"FROM {MAIN_DB}.user_ships WHERE account_id = %s;", 
                [account_id]
            )
            row = await cur.fetchone()
            data = None
            if row:
                data = {
                    'battles_count': row[0],
                    'hash_value': row[1],
                    'ships_data': BinaryParserUtils.from_user_binary_data_to_dict(row[2]),
                    'update_time': row[3]
                }
            else:
                # 用户不存在
                name = UtilityFunctions.get_user_default_name(account_id)
                await cur.execute(
                    f"INSERT INTO {MAIN_DB}.user_basic (account_id, region_id, username) VALUES (%s, %s, %s);",
                    [account_id, region_id, name]
                )
                await cur.execute(
                    f"INSERT INTO {MAIN_DB}.user_info (account_id) VALUES (%s);",
                    [account_id]
                )
                await cur.execute(
                    f"INSERT INTO {MAIN_DB}.user_ships (account_id) VALUES (%s);",
                    [account_id]
                )
                await cur.execute(
                    f"INSERT INTO {MAIN_DB}.user_clan (account_id) VALUES (%s);",
                    [account_id]
                )
                data = {
                    'battles_count': 0,
                    'hash_value': None,
                    'ships_data': [],
                    'update_time': None
                }

            await conn.commit()
            return JSONResponse.get_success_response(data)
        except Exception as e:
            await conn.rollback()
            raise e
        finally:
            await cur.close()
            await MysqlConnection.release_connection(conn)
