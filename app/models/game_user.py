from aiomysql.connection import Connection
from aiomysql.cursors import Cursor

from .access_token import UserAccessToken
from app.db import MysqlConnection
from app.log import ExceptionLogger
from app.response import JSONResponse, ResponseDict
from app.utils import TimeFormat, UtilityFunctions

class UserModel:
    # # 函数统一格式格式
    # @ExceptionLogger.handle_database_exception_async
    # async def func() -> ResponseDict:
    #     '''方法介绍

    #     方法描述

    #     参数:
    #         params
        
    #     返回:
    #         - ResponseDict
    #     '''
    #     conn: Connection = await MysqlConnection.get_connection()
    #     cur: Cursor = await conn.cursor()
    #     try:
    #         raise NotImplementedError
    #     except Exception as e:
    #         await conn.rollback()
    #         raise e
    #     finally:
    #         await cur.close()
    #         await MysqlConnection.release_connection(conn)

    @ExceptionLogger.handle_database_exception_async
    async def get_user_max_number() -> ResponseDict:
        '''获取数据库中id的最大值

        获取id的最大值，用于数据库遍历更新时确定边界

        参数:
            - None
        
        返回:
            - ResponseDict
        '''
        conn: Connection = await MysqlConnection.get_connection()
        cur: Cursor = await conn.cursor()
        try:
            data = {
                'max_id': 0
            }
            await cur.execute(
                "SELECT MAX(id) AS max_id FROM user_basic;"
            )
            user = await cur.fetchone()
            data['max_id'] = user[0]
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
        conn: Connection = await MysqlConnection.get_connection()
        cur: Cursor = await conn.cursor()
        try:
            await conn.begin()
            # 插入新用户
            if user[2] == None:
                user[2] = UtilityFunctions.get_user_default_name(user[0])
                await cur.execute(
                    "INSERT INTO user_basic (account_id, region_id, username) VALUES (%s, %s, %s);"
                    "INSERT INTO user_info (account_id) VALUES (%s);"
                    "INSERT INTO user_ships (account_id) VALUES (%s);"
                    "INSERT INTO clan_user (account_id) VALUES (%s);",
                    [user[0], user[1], user[2], user[0], user[0], user[0]]
                )
            else:
                # 如果不是默认的名称则更新updated_time
                await cur.execute(
                    "INSERT INTO user_basic (account_id, region_id, username) VALUES (%s, %s, %s);"
                    "INSERT INTO user_info (account_id) VALUES (%s);"
                    "INSERT INTO user_ships (account_id) VALUES (%s);"
                    "INSERT INTO clan_user (account_id) VALUES (%s);"
                    "UPDATE user_basic SET updated_at = CURRENT_TIMESTAMP WHERE account_id = %s AND region_id = %s",
                    [user[0], user[1], user[2], user[0], user[0], user[0], user[0], user[1]]
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
        conn: Connection = await MysqlConnection.get_connection()
        cur: Cursor = await conn.cursor()
        try:
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
            await conn.begin()
            for user in missing_users:
                # 插入新用户
                if user[2] == None:
                    user[2] = UtilityFunctions.get_user_default_name(user[0])
                    await cur.execute(
                        "INSERT INTO user_basic (account_id, region_id, username) VALUES (%s, %s, %s);"
                        "INSERT INTO user_info (account_id) VALUES (%s);"
                        "INSERT INTO user_ships (account_id) VALUES (%s);"
                        "INSERT INTO clan_user (account_id) VALUES (%s);",
                        [user[0], user[1], user[2], user[0], user[0], user[0]]
                    )
                else:
                    # 如果不是默认的名称则更新updated_time
                    await cur.execute(
                        "INSERT INTO user_basic (account_id, region_id, username) VALUES (%s, %s, %s);"
                        "INSERT INTO user_info (account_id) VALUES (%s);"
                        "INSERT INTO user_ships (account_id) VALUES (%s);"
                        "INSERT INTO clan_user (account_id) VALUES (%s);"
                        "UPDATE user_basic SET updated_at = CURRENT_TIMESTAMP WHERE account_id = %s AND region_id = %s",
                        [user[0], user[1], user[2], user[0], user[0], user[0], user[0], user[1]]
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
        conn: Connection = await MysqlConnection.get_connection()
        cur: Cursor = await conn.cursor()
        try:
            await conn.begin()
            for user in users:
                # 插入新用户
                if user[2] == None:
                    user[2] = UtilityFunctions.get_user_default_name(user[0])
                    await cur.execute(
                        "INSERT INTO user_basic (account_id, region_id, username) VALUES (%s, %s, %s);"
                        "INSERT INTO user_info (account_id) VALUES (%s);"
                        "INSERT INTO user_ships (account_id) VALUES (%s);"
                        "INSERT INTO clan_user (account_id) VALUES (%s);",
                        [user[0], user[1], user[2], user[0], user[0], user[0]]
                    )
                else:
                    # 如果不是默认的名称则更新updated_time
                    await cur.execute(
                        "INSERT INTO user_basic (account_id, region_id, username) VALUES (%s, %s, %s);"
                        "INSERT INTO user_info (account_id) VALUES (%s);"
                        "INSERT INTO user_ships (account_id) VALUES (%s);"
                        "INSERT INTO clan_user (account_id) VALUES (%s);"
                        "UPDATE user_basic SET updated_at = CURRENT_TIMESTAMP WHERE account_id = %s AND region_id = %s",
                        [user[0], user[1], user[2], user[0], user[0], user[0], user[0], user[1]]
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
        conn: Connection = await MysqlConnection.get_connection()
        cur: Cursor = await conn.cursor()
        try:
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
                data['nickname'] = UtilityFunctions.get_user_default_name(user[0])
                data['update_time'] = None
            else:
                data['nickname'] = user[0]
                data['update_time'] = user[1]
            return JSONResponse.get_success_response(data)
        except Exception as e:
            await conn.rollback()
            raise e
        finally:
            await cur.close()
            await MysqlConnection.release_connection(conn)

    @ExceptionLogger.handle_database_exception_async
    async def update_user_name_if_different(user_basic: dict) -> ResponseDict:
        '''检查更新数据库中用户名称是否为最新

        检查数据库中username是否和最新的数据一致

        !: 传入的user_basic参数必须确保是最新的

        参数:
            user_basic: dict

        返回:
            ResponseDict
        '''
        conn: Connection = await MysqlConnection.get_connection()
        cur: Cursor = await conn.cursor()
        try:
            account_id= user_basic['account_id']
            region_id = user_basic['region_id'] 
            nickname = user_basic['nickname']
            await cur.execute(
                "SELECT username, UNIX_TIMESTAMP(updated_at) "
                "FROM user_basic "
                "WHERE region_id = %s and account_id = %s;", 
                [region_id, account_id]
            )
            user = await cur.fetchone()
            if user is None:
                # 用户不存在
                insert_result = await UserModel.insert_user([account_id,region_id,None])
                if insert_result.get('code', None) != 1000:
                    return insert_result
                return JSONResponse.API_1020_UserNotFoundInDatabase
            else:
                if user[0] != nickname and user[1] == None:
                    # 用户无数据，则直接插入数据
                    await conn.begin()
                    await cur.execute(
                        "UPDATE user_basic SET username = %s WHERE region_id = %s and account_id = %s;", 
                        [nickname, region_id, account_id]
                    )
                    await conn.commit()
                elif user[0] != nickname and user[1] != None:
                    # 用户名称发生改变，更新同时写入记录表
                    await conn.begin()
                    current_time = TimeFormat.get_current_timestamp()
                    await cur.execute(
                        "UPDATE user_basic SET username = %s WHERE region_id = %s and account_id = %s;"
                        "INSERT INTO user_history (account_id, username, start_time, end_time) VALUES (%s, %s, %s, %s);", 
                        [nickname, region_id, account_id, account_id, user[0], user[1], current_time]
                    )
                    await conn.commit()
                else:
                    # 用户名称没有发生变化，不做操作
                    pass
            return JSONResponse.API_1000_Success
        except Exception as e:
            await conn.rollback()
            raise e
        finally:
            await cur.close()
            await MysqlConnection.release_connection(conn)

    @ExceptionLogger.handle_database_exception_async
    async def get_user_clan(account_id: int, region_id: int) -> ResponseDict:
        '''获取用户所在工会数据

        从clan_user中获取用户工会id

        参数：
            account_id: 用户id

        返回：
            ResponseDict
        '''
        conn: Connection = await MysqlConnection.get_connection()
        cur: Cursor = await conn.cursor()
        try:
            data =  {
                'clan_id': None,
                'updated_at': 0
            }
            await cur.execute(
                "SELECT clan_id, UNIX_TIMESTAMP(updated_at) AS update_time FROM clan_user WHERE account_id = %s;", 
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
        conn: Connection = await MysqlConnection.get_connection()
        cur: Cursor = await conn.cursor()
        try:
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
            return JSONResponse.get_success_response(data)
        except Exception as e:
            await conn.rollback()
            raise e
        finally:
            await cur.close()
            await MysqlConnection.release_connection(conn)

    @ExceptionLogger.handle_database_exception_async
    async def update_user_info(user_info: dict) -> ResponseDict:
        '''检查并更新user_info表

        参数:
            user_info: dict
        
        返回:
            ResponseDict
        '''
        conn: Connection = await MysqlConnection.get_connection()
        cur: Cursor = await conn.cursor()
        try:
            account_id = user_info['account_id']
            region_id = user_info['region_id']
            await cur.execute(
                "SELECT is_active, active_level, is_public, total_battles, last_battle_time FROM user_info WHERE account_id = %s;", 
                [account_id]
            )
            user = await cur.fetchone()
            if user is None:
                # 用户不存在
                insert_result = await UserModel.insert_user([account_id,region_id,None])
                if insert_result.get('code', None) != 1000:
                    return insert_result
            sql_str = ''
            params = []
            i = 0
            for field in ['is_active', 'active_level', 'is_public', 'total_battles', 'last_battle_time']:
                if user_info[field] != None and user_info[field] != user[i]:
                    sql_str += f'{field} = %s, '
                    params.append(user_info[field])
                i += 1
            params = params + [account_id]
            await cur.execute(
                f"UPDATE user_info SET {sql_str}updated_at = CURRENT_TIMESTAMP WHERE account_id = %s;", 
                params
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
    async def get_user_cache_batch(offset: int, limit = 1000) -> ResponseDict:
        '''批量获取用户缓存的数据

        获取用户缓存数据，用于缓存的更新

        参数:
            offset: 从哪个id开始读取
            limit: 每次读取多少条数据
        
        返回值:
            ResponseDict
        '''
        conn: Connection = await MysqlConnection.get_connection()
        cur: Cursor = await conn.cursor()
        try:
            data = []
            await cur.execute(
                "SELECT b.region_id, b.account_id, i.is_active, i.active_level, "
                "s.battles_count, s.ships_data, UNIX_TIMESTAMP(s.updated_at) AS update_time "
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
                        'ships_data': row[5],
                        'update_time': row[6]
                    }
                }
                data.append(user)
            return JSONResponse.get_success_response(data)
        except Exception as e:
            await conn.rollback()
            raise e
        finally:
            await cur.close()
            await MysqlConnection.release_connection(conn)

    @ExceptionLogger.handle_database_exception_async
    async def update_user_ships(
        account_id: int, 
        battles_count: int = None, 
        ships_data: bytes = None
    ) -> ResponseDict:
        '''更新用户缓存的数据

        更新用户缓存的更新时间

        参数:
            account_id: 用户id
            battles_count: 战斗总场次
            ships_data: 用户数据
        
        返回值:
            ResponseDict
        '''
        conn: Connection = await MysqlConnection.get_connection()
        cur: Cursor = await conn.cursor()
        try:
            if battles_count:
                await cur.execute(
                    "UPDATE user_ships "
                    "SET battles_count = %s, ships_data = %s "
                    "WHERE account_id = %s;", 
                    [battles_count, ships_data, account_id]
                )
            else:
                await cur.execute(
                    "UPDATE user_ships "
                    "SET updated_at = CURRENT_TIMESTAMP "
                    "WHERE account_id = %s;", 
                    [battles_count, ships_data, account_id]
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
    async def update_user_cache(
        account_id: int, 
        region_id: int, 
        delete_ship_list: list, 
        replace_ship_dict: dict
    ) -> ResponseDict:
        '''更新用户缓存的数据

        更新用户缓存的更新时间

        参数:
            account_id: 用户id
            region_id: 服务器id
            user_cache: 用户需要更新的缓存数据
        
        返回值:
            ResponseDict
        '''
        conn: Connection = await MysqlConnection.get_connection()
        cur: Cursor = await conn.cursor()
        try:
            await conn.begin()
            for del_ship_id in delete_ship_list:
                table_name = f'user_ship_0{del_ship_id % 10}'
                await cur.execute(
                    "DELETE FROM %s "
                    "WHERE ship_id = %s and region_id = %s and account_id = %s;",
                    [table_name, del_ship_id, region_id, account_id]
                )
            for update_ship_id, ship_data in replace_ship_dict.items():
                table_name = f'user_ship_0{update_ship_id % 10}'
                await cur.execute(
                    "UPDATE %s SET battles_count = %s, battle_type_1 = %s, battle_type_2 = %s, battle_type_3 = %s, wins = %s, "
                    "damage_dealt = %s, frags = %s, exp = %s, survived = %s, scouting_damage = %s, art_agro = %s, "
                    "planes_killed = %s, max_exp = %s, max_damage_dealt = %s, max_frags = %s"
                    "WHERE ship_id = %s and region_id = %s and account_id = %s;"
                    "INSERT INTO %s (ship_id, region_id, account_id, battles_count, battle_type_1, battle_type_2, "
                    "battle_type_3, wins, damage_dealt, frags, exp, survived, scouting_damage, art_agro, planes_killed, "
                    "max_exp, max_damage_dealt, max_frags) "
                    "SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s "
                    "WHERE NOT EXISTS (SELECT 1 FROM %s WHERE ship_id = %s and region_id = %s and account_id = %s);",
                    [table_name] + ship_data + [update_ship_id, region_id, account_id] + [table_name] + \
                    [update_ship_id, region_id, account_id] + ship_data + [table_name] + [update_ship_id, region_id, account_id]
                )
            await conn.commit()
            return JSONResponse.API_1000_Success
        except Exception as e:
            await conn.rollback()
            raise e
        finally:
            await cur.close()
            await MysqlConnection.release_connection(conn)
