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

    # @ExceptionLogger.handle_database_exception_async
    # async def get_user_max_number() -> ResponseDict:
    #     '''获取数据库中id的最大值

    #     获取id的最大值，用于数据库遍历更新时确定边界

    #     参数:
    #         - None
        
    #     返回:
    #         - ResponseDict
    #     '''
    #     try:
    #         conn: Connection = await MysqlConnection.get_connection()
    #         await conn.begin()
    #         cur: Cursor = await conn.cursor()

    #         data = {
    #             'max_id': 0
    #         }
    #         await cur.execute(
    #             f"SELECT MAX(id) AS max_id FROM {MAIN_DB}.user_basic;"
    #         )
    #         user = await cur.fetchone()
    #         data['max_id'] = user[0]

    #         await conn.commit()
    #         return JSONResponse.get_success_response(data)
    #     except Exception as e:
    #         await conn.rollback()
    #         raise e
    #     finally:
    #         await cur.close()
    #         await MysqlConnection.release_connection(conn)

    # @ExceptionLogger.handle_database_exception_async
    # async def check_and_insert_missing_users(users: list) -> ResponseDict:
    #     '''检查并插入缺失的用户id

    #     只支持同一服务器下的用户
        
    #     参数:
    #         user: [{...}]

    #     返回:
    #         ResponseDict    
    #     '''
    #     try:
    #         conn: Connection = await MysqlConnection.get_connection()
    #         await conn.begin()
    #         cur: Cursor = await conn.cursor()

    #         sql_str = ''
    #         params = [users[0]['region_id'],users[0]['account_id']]
    #         for user in users[1:]:
    #             sql_str += ', %s'
    #             params.append(user['account_id'])
    #         await cur.execute(
    #             "SELECT account_id, username, UNIX_TIMESTAMP(updated_at) AS update_time "
    #             f"FROM {MAIN_DB}.user_basic WHERE region_id = %s AND account_id in ( %s{sql_str} );",
    #             params
    #         )
    #         exists_users = {}
    #         rows = await cur.fetchall()
    #         for row in rows:
    #             exists_users[row[0]] = [row[1],row[2]]
    #         for user in users:
    #             account_id = user['account_id']
    #             region_id = user['region_id']
    #             nickname = user['nickname']
    #             if account_id not in exists_users:
    #                 await cur.execute(
    #                     f"INSERT INTO {MAIN_DB}.user_basic (account_id, region_id, username) VALUES (%s, %s, %s);",
    #                     [account_id, region_id, UtilityFunctions.get_user_default_name(account_id)]
    #                 )
    #                 await cur.execute(
    #                     f"INSERT INTO {MAIN_DB}.user_info (account_id) VALUES (%s);",
    #                     [account_id]
    #                 )
    #                 await cur.execute(
    #                     f"INSERT INTO {MAIN_DB}.user_ships (account_id) VALUES (%s);",
    #                     [account_id]
    #                 )
    #                 await cur.execute(
    #                     f"INSERT INTO {MAIN_DB}.user_clan (account_id) VALUES (%s);",
    #                     [account_id]
    #                 )
    #                 await cur.execute(
    #                     f"UPDATE {MAIN_DB}.user_basic SET username = %s WHERE region_id = %s AND account_id = %s",
    #                     [nickname, region_id, account_id]
    #                 )
    #             else:
    #                 if exists_users[account_id][1] == None:
    #                     await cur.execute(
    #                         f"UPDATE {MAIN_DB}.user_basic SET username = %s WHERE region_id = %s AND account_id = %s",
    #                         [nickname, region_id, account_id]
    #                     )
    #                 elif nickname != exists_users[account_id][0]:
    #                     await cur.execute(
    #                         f"UPDATE {MAIN_DB}.user_basic SET username = %s WHERE region_id = %s and account_id = %s;", 
    #                         [nickname, region_id, account_id]
    #                     ) 
    #                     await cur.execute(
    #                         f"INSERT INTO {MAIN_DB}.user_history (account_id, username, start_time, end_time) "
    #                         "VALUES (%s, %s, FROM_UNIXTIME(%s), FROM_UNIXTIME(%s));", 
    #                         [account_id, exists_users[account_id][0], exists_users[account_id][1], TimeFormat.get_current_timestamp()]
    #                     )
            
    #         await conn.commit()
    #         return JSONResponse.API_1000_Success
    #     except Exception as e:
    #         await conn.rollback()
    #         raise e
    #     finally:
    #         await cur.close()
    #         await MysqlConnection.release_connection(conn)

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
    async def get_user_info(account_id: int, region_id: int) -> ResponseDict:
        '''获取用户详细数据

        从user_info中获取用户详细数据

        注：调用前需先确保数据不为空

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
                "SELECT is_active, active_level, is_public, total_battles, "
                "UNIX_TIMESTAMP(last_battle_at) AS last_battle_time, UNIX_TIMESTAMP(updated_at) AS update_time "
                f"FROM {MAIN_DB}.user_info WHERE account_id = %s;", 
                [account_id]
            )
            user = await cur.fetchone()
            data = None
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
                data = {
                    'is_active': 0,
                    'active_level': 0,
                    'is_public': 0,
                    'total_battles': 0,
                    'last_battle_time': 0,
                    'update_time': None
                }
            else:
                data = {
                    'is_active': user[0],
                    'active_level': user[1],
                    'is_public': user[2],
                    'total_battles': user[3],
                    'last_battle_time': user[4],
                    'update_time': user[5]
                }
            
            await conn.commit()
            return JSONResponse.get_success_response(data)
        except Exception as e:
            await conn.rollback()
            raise e
        finally:
            await cur.close()
            await MysqlConnection.release_connection(conn)

    @ExceptionLogger.handle_database_exception_async
    async def get_user_ships(account_id: int, region_id: int) -> ResponseDict:
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

            row = await cur.execute(
                "SELECT b.region_id, b.account_id, s.battles_count, s.hash_value, UNIX_TIMESTAMP(s.updated_at) AS update_time "
                f"FROM {MAIN_DB}.user_basic AS b LEFT JOIN {MAIN_DB}.user_ships AS s ON s.account_id = b.account_id "
                "WHERE b.region_id = %s AND b.account_id = %s;", 
                [region_id, account_id]
            )
            data = None
            if row:
                data = {
                    'battles_count': row[2],
                    'hash_value': row[3],
                    'update_time': row[4]
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

            row = await cur.execute(
                "SELECT battles_count, hash_value, ships_data, UNIX_TIMESTAMP(updated_at) AS update_time "
                f"FROM {MAIN_DB}.user_ships WHERE account_id = %s;", 
                [account_id]
            )
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

            await conn.commit()
            return JSONResponse.get_success_response(data)
        except Exception as e:
            await conn.rollback()
            raise e
        finally:
            await cur.close()
            await MysqlConnection.release_connection(conn)

    # @ExceptionLogger.handle_database_exception_async
    # async def get_user_cache_data(account_id: int, region_id: int) -> ResponseDict:
    #     '''获取用户的缓存数据'''
    #     try:
    #         conn: Connection = await MysqlConnection.get_connection()
    #         await conn.begin()
    #         cur: Cursor = await conn.cursor()
            
    #         await cur.execute(
    #             "SELECT battles_count, hash_value, ships_data, UNIX_TIMESTAMP(updated_at) AS update_time "
    #             f"FROM {MAIN_DB}.user_ships WHERE account_id = %s;", 
    #             [account_id]
    #         )
    #         user = await cur.fetchone()
    #         if user is None:
    #             # 用户不存在
    #             name = UtilityFunctions.get_user_default_name(account_id)
    #             await cur.execute(
    #                 f"INSERT INTO {MAIN_DB}.user_basic (account_id, region_id, username) VALUES (%s, %s, %s);",
    #                 [account_id, region_id, name]
    #             )
    #             await cur.execute(
    #                 f"INSERT INTO {MAIN_DB}.user_info (account_id) VALUES (%s);",
    #                 [account_id]
    #             )
    #             await cur.execute(
    #                 f"INSERT INTO {MAIN_DB}.user_ships (account_id) VALUES (%s);",
    #                 [account_id]
    #             )
    #             await cur.execute(
    #                 f"INSERT INTO {MAIN_DB}.user_clan (account_id) VALUES (%s);",
    #                 [account_id]
    #             )
    #             data = {
    #                 'battles_count': None,
    #                 'hash_value': None,
    #                 'ships_data': None,
    #                 'update_time': None
    #             }
    #         else:
    #             data = {
    #                 'battles_count': user[0],
    #                 'hash_value': user[1],
    #                 'ships_data': BinaryParserUtils.from_user_binary_data_to_dict(user[2]),
    #                 'update_time': user[3]
    #             }
            
    #         await conn.commit()
    #         return JSONResponse.get_success_response(data)
    #     except Exception as e:
    #         await conn.rollback()
    #         raise e
    #     finally:
    #         await cur.close()
    #         await MysqlConnection.release_connection(conn)

    # @ExceptionLogger.handle_database_exception_async
    # async def get_user_cache_batch(offset: int, limit = 1000) -> ResponseDict:
    #     '''批量获取用户缓存的数据

    #     获取用户缓存数据，用于缓存的更新

    #     参数:
    #         offset: 从哪个id开始读取
    #         limit: 每次读取多少条数据
        
    #     返回值:
    #         ResponseDict
    #     '''
    #     try:
    #         conn: Connection = await MysqlConnection.get_connection()
    #         await conn.begin()
    #         cur: Cursor = await conn.cursor()

    #         data = []
    #         await cur.execute(
    #             "SELECT b.region_id, b.account_id, i.is_active, i.active_level, UNIX_TIMESTAMP(i.updated_at) AS info_update_time, "
    #             "s.battles_count, s.hash_value, UNIX_TIMESTAMP(s.updated_at) AS update_time "
    #             f"FROM {MAIN_DB}.user_basic AS b "
    #             f"LEFT JOIN {MAIN_DB}.user_info AS i ON i.account_id = b.account_id "
    #             f"LEFT JOIN {MAIN_DB}.user_ships AS s ON s.account_id = b.account_id "
    #             "WHERE b.id BETWEEN %s AND %s;", 
    #             [offset+1, offset+limit]
    #         )
    #         rows = await cur.fetchall()
    #         for row in rows:
    #             # 排除已注销账号的数据，避免浪费服务器资源
    #             if row[4] and not row[2]:
    #                 continue
    #             user = {
    #                 'user_basic': {
    #                     'region_id': row[0],
    #                     'account_id': row[1],
    #                     'ac_value': UserAccessToken.get_ac_value_by_id(row[1],row[0])
    #                 },
    #                 'user_info': {
    #                     'is_active': row[2],
    #                     'active_level': row[3]
    #                 },
    #                 'user_ships':{
    #                     'battles_count': row[5],
    #                     'hash_value': row[6],
    #                     'update_time': row[7]
    #                 }
    #             }
    #             data.append(user)
            
    #         await conn.commit()
    #         return JSONResponse.get_success_response(data)
    #     except Exception as e:
    #         await conn.rollback()
    #         raise e
    #     finally:
    #         await cur.close()
    #         await MysqlConnection.release_connection(conn)