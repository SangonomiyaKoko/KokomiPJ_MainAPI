from aiomysql.connection import Connection
from aiomysql.cursors import Cursor

from .access_token import UserAccessToken
from app.db import MysqlConnection
from app.log import ExceptionLogger
from app.response import JSONResponse, ResponseDict
from app.utils import UtilityFunctions

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
            conn: Connection = await MysqlConnection.get_connection()  # 获取连接
            await conn.begin()  # 开启事务
            cur: Cursor = await conn.cursor()  # 获取游标

            # 在这里执行sql语句
            await cur.execute()

            await conn.commit()  # 提交事务
            return JSONResponse.API_1000_Success  # 返回数据
        except Exception as e:
            await conn.rollback()  # 执行报错回滚事务
            raise e  # 抛出异常
        finally:
            await cur.close()  # 关闭游标
            await MysqlConnection.release_connection(conn)  # 释放连接

    @ExceptionLogger.handle_database_exception_async
    async def get_user_max_number() -> ResponseDict:
        '''获取数据库中id的最大值

        获取id的最大值，用于数据库遍历更新时确定边界

        参数:
            - None
        
        返回:
            - ResponseDict
        '''
        try:
            conn: Connection = await MysqlConnection.get_connection()
            await conn.begin()
            cur: Cursor = await conn.cursor()

            data = {
                'max_id': 0
            }
            await cur.execute(
                "SELECT MAX(id) AS max_id FROM user_basic;"
            )
            user = await cur.fetchone()
            data['max_id'] = user[0]

            await conn.commit()
            return JSONResponse.get_success_response(data)
        except Exception as e:
            await conn.rollback()
            raise e
        finally:
            await cur.close()
            await MysqlConnection.release_connection(conn)

    @ExceptionLogger.handle_database_exception_async
    async def insert_user(user: list) -> ResponseDict:
        '''写入用户数据
        
        向数据库中写入不存在的用户的数据

        如果参数内没有给出username则会写入一个默认值

        参数:
            user: [aid, rid, name]

        返回:
            ResponseDict
        '''
        try:
            conn: Connection = await MysqlConnection.get_connection()
            await conn.begin()
            cur: Cursor = await conn.cursor()

            # 插入新用户
            if user[2] == None:
                user[2] = UtilityFunctions.get_user_default_name(user[0])
                await cur.execute(
                    "INSERT INTO user_basic (account_id, region_id, username) VALUES (%s, %s, %s);",
                    [user[0], user[1], user[2]]
                )
                await cur.execute(
                    "INSERT INTO user_info (account_id) VALUES (%s);",
                    [user[0]]
                )
                await cur.execute(
                    "INSERT INTO user_ships (account_id) VALUES (%s);",
                    [user[0]]
                )
                await cur.execute(
                    "INSERT INTO user_clan (account_id) VALUES (%s);",
                    [user[0]]
                )
            else:
                # 如果不是默认的名称则更新updated_time
                await cur.execute(
                    "INSERT INTO user_basic (account_id, region_id, username) VALUES (%s, %s, %s);",
                    [user[0], user[1], UtilityFunctions.get_user_default_name(user[0])]
                )
                await cur.execute(
                    "INSERT INTO user_info (account_id) VALUES (%s);",
                    [user[0]]
                )
                await cur.execute(
                    "INSERT INTO user_ships (account_id) VALUES (%s);",
                    [user[0]]
                )
                await cur.execute(
                    "INSERT INTO user_clan (account_id) VALUES (%s);",
                    [user[0]]
                )
                await cur.execute(
                    "UPDATE user_basic SET username = %s WHERE account_id = %s AND region_id = %s",
                    [user[2], user[0], user[1]]
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
    async def insert_missing_users(users) -> ResponseDict:
        '''插入缺少的用户id

        检测用户输入的列表中，是否有数据库缺失的用户

        如果有缺失的用户则写入数据库

        参数:
            users: [ [aid, rid, nickname],[...] ]
        
        返回:
            ResponseDict
        '''
        try:
            conn: Connection = await MysqlConnection.get_connection()
            await conn.begin()
            cur: Cursor = await conn.cursor()

            if users == [] or users == None:
                return JSONResponse.API_1000_Success
            for user in users[1:]:
                sql_str = f"\n    UNION ALL SELECT {user[0]}, {user[1]}"
            await cur.execute(
                "WITH input_ids AS ( "
                f"    SELECT %s AS user_id, %s AS region_id {sql_str} "
                ") "
                "SELECT input_ids.user_id, input_ids.region_id "
                "FROM input_ids "
                "LEFT JOIN user_basic "
                "    ON input_ids.user_id = user_basic.account_id "
                "    AND input_ids.region_id = user_basic.region_id "
                "WHERE user_basic.account_id IS NULL;",
                [user[0][0],user[0][1]]
            )
            missing_users = await cur.fetchall()
            if missing_users == None:
                return JSONResponse.API_1000_Success
            for user in missing_users:
                # 插入新用户
                if user[2] == None:
                    user[2] = UtilityFunctions.get_user_default_name(user[0])
                    await cur.execute(
                        "INSERT INTO user_basic (account_id, region_id, username) VALUES (%s, %s, %s);",
                        [user[0], user[1], user[2]]
                    )
                    await cur.execute(
                        "INSERT INTO user_info (account_id) VALUES (%s);",
                        [user[0]]
                    )
                    await cur.execute(
                        "INSERT INTO user_ships (account_id) VALUES (%s);",
                        [user[0]]
                    )
                    await cur.execute(
                        "INSERT INTO user_clan (account_id) VALUES (%s);",
                        [user[0]]
                    )
                else:
                    # 如果不是默认的名称则更新updated_time
                    await cur.execute(
                        "INSERT INTO user_basic (account_id, region_id, username) VALUES (%s, %s, %s);",
                        [user[0], user[1], UtilityFunctions.get_user_default_name(user[0])]
                    )
                    await cur.execute(
                        "INSERT INTO user_info (account_id) VALUES (%s);",
                        [user[0]]
                    )
                    await cur.execute(
                        "INSERT INTO user_ships (account_id) VALUES (%s);",
                        [user[0]]
                    )
                    await cur.execute(
                        "INSERT INTO user_clan (account_id) VALUES (%s);",
                        [user[0]]
                    )
                    await cur.execute(
                        "UPDATE user_basic SET username = %s WHERE account_id = %s AND region_id = %s",
                        [user[2], user[0], user[1]]
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
    async def batch_insert_users(users: list) -> ResponseDict:
        '''批量写入用户数据
        
        想数据库中批量写入不存在的用户的数据

        如果参数内没有给出username则会写入一个默认值

        参数:
            users: [ [aid, rid, name],[...] ]

        返回:
            ResponseDict
        '''
        try:
            conn: Connection = await MysqlConnection.get_connection()
            await conn.begin()
            cur: Cursor = await conn.cursor()

            for user in users:
                # 插入新用户
                if user[2] == None:
                    user[2] = UtilityFunctions.get_user_default_name(user[0])
                    await cur.execute(
                        "INSERT INTO user_basic (account_id, region_id, username) VALUES (%s, %s, %s);",
                        [user[0], user[1], user[2]]
                    )
                    await cur.execute(
                        "INSERT INTO user_info (account_id) VALUES (%s);",
                        [user[0]]
                    )
                    await cur.execute(
                        "INSERT INTO user_ships (account_id) VALUES (%s);",
                        [user[0]]
                    )
                    await cur.execute(
                        "INSERT INTO user_clan (account_id) VALUES (%s);",
                        [user[0]]
                    )
                else:
                    # 如果不是默认的名称则更新updated_time
                    await cur.execute(
                        "INSERT INTO user_basic (account_id, region_id, username) VALUES (%s, %s, %s);",
                        [user[0], user[1], UtilityFunctions.get_user_default_name(user[0])]
                    )
                    await cur.execute(
                        "INSERT INTO user_info (account_id) VALUES (%s);",
                        [user[0]]
                    )
                    await cur.execute(
                        "INSERT INTO user_ships (account_id) VALUES (%s);",
                        [user[0]]
                    )
                    await cur.execute(
                        "INSERT INTO user_clan (account_id) VALUES (%s);",
                        [user[0]]
                    )
                    await cur.execute(
                        "UPDATE user_basic SET username = %s WHERE account_id = %s AND region_id = %s",
                        [user[2], user[0], user[1]]
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
                "SELECT username, UNIX_TIMESTAMP(updated_at) AS update_time FROM user_basic WHERE region_id = %s and account_id = %s;", 
                [region_id, account_id]
            )
            user = await cur.fetchone()
            if user is None:
                # 用户不存在
                insert_result = await UserModel.insert_user([account_id,region_id,None])
                if insert_result.get('code', None) != 1000:
                    return insert_result
                data['nickname'] = UtilityFunctions.get_user_default_name(account_id)
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
                "SELECT clan_id, UNIX_TIMESTAMP(updated_at) AS update_time FROM user_clan WHERE account_id = %s;", 
                [account_id]
            )
            user = await cur.fetchone()
            if user is None:
                # 用户不存在
                insert_result = await UserModel.insert_user([account_id,region_id,None])
                if insert_result.get('code', None) != 1000:
                    return insert_result
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
                "SELECT is_active, active_level, is_public, total_battles, last_battle_time, UNIX_TIMESTAMP(updated_at) AS update_time "
                "FROM user_info WHERE account_id = %s;", 
                [account_id]
            )
            user = await cur.fetchone()
            data = None
            if user is None:
                # 用户不存在
                insert_result = await UserModel.insert_user([account_id,region_id,None])
                if insert_result.get('code', None) != 1000:
                    return insert_result
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
    async def get_user_cache_batch(offset: int, limit = 1000) -> ResponseDict:
        '''批量获取用户缓存的数据

        获取用户缓存数据，用于缓存的更新

        参数:
            offset: 从哪个id开始读取
            limit: 每次读取多少条数据
        
        返回值:
            ResponseDict
        '''
        try:
            conn: Connection = await MysqlConnection.get_connection()
            await conn.begin()
            cur: Cursor = await conn.cursor()

            data = []
            await cur.execute(
                "SELECT b.region_id, b.account_id, i.is_active, i.active_level, "
                "s.battles_count, s.hash_value, UNIX_TIMESTAMP(s.updated_at) AS update_time "
                "FROM user_basic AS b "
                "LEFT JOIN user_info AS i ON i.account_id = b.account_id "
                "LEFT JOIN user_ships AS s ON s.account_id = b.account_id "
                "ORDER BY b.id LIMIT %s OFFSET %s;", 
                [limit, offset]
            )
            rows = await cur.fetchall()
            for row in rows:
                # 排除已注销账号的数据，避免浪费服务器资源
                if not row[2]:
                    continue
                user = {
                    'user_basic': {
                        'region_id': row[0],
                        'account_id': row[1],
                        'ac_value': UserAccessToken.get_ac_value_by_id(row[1],row[0])
                    },
                    'user_info': {
                        'is_active': row[2],
                        'active_level': row[3]
                    },
                    'user_ships':{
                        'battles_count': row[4],
                        'hash_value': row[5],
                        'update_time': row[6]
                    }
                }
                data.append(user)
            
            await conn.commit()
            return JSONResponse.get_success_response(data)
        except Exception as e:
            await conn.rollback()
            raise e
        finally:
            await cur.close()
            await MysqlConnection.release_connection(conn)