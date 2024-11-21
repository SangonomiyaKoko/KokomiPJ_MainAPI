from aiomysql.connection import Connection
from aiomysql.cursors import Cursor

from .ac import UserAccessToken
from app.db import MysqlConnection
from app.log import ExceptionLogger
from app.response import JSONResponse, ResponseDict

class UserModel:
    @ExceptionLogger.handle_database_exception_async
    async def get_user_max_number() -> ResponseDict:
        '''获取数据库中id的最大值

        获取id的最大值，用于数据库遍历更新

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
            # 数据库回滚
            await conn.rollback()
            raise e
        finally:
            # 释放资源
            await cur.close()
            await MysqlConnection.release_connection(conn)


    @ExceptionLogger.handle_database_exception_async
    async def get_user_basic(account_id: int, region_id: int) -> ResponseDict:
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
                await conn.begin() # 开始事务
                # 用户不存在，插入新用户
                nickname = f'User_{account_id}'
                await cur.execute(
                    "INSERT INTO user_basic (account_id, region_id, username) VALUES (%s, %s, %s);"
                    "INSERT INTO user_info (account_id) VALUES (%s);"
                    "INSERT INTO user_ships (account_id) VALUES (%s);"
                    "INSERT INTO user_clan (account_id) VALUES (%s);"
                    "INSERT INTO user_pr (account_id) VALUES (%s);",
                    [account_id, region_id, nickname, account_id, account_id, account_id, account_id]
                )
                await conn.commit() # 提交事务
                data['nickname'] = nickname
                data['update_time'] = 0
            else:
                data['nickname'] = user[0]
                data['update_time'] = user[1]
            return JSONResponse.get_success_response(data)
        except Exception as e:
            # 数据库回滚
            await conn.rollback()
            raise e
        finally:
            # 释放资源
            await cur.close()
            await MysqlConnection.release_connection(conn)

    @ExceptionLogger.handle_database_exception_async
    async def check_user_basic(user_basic: dict) -> ResponseDict:
        conn: Connection = await MysqlConnection.get_connection()
        cur: Cursor = await conn.cursor()
        try:
            account_id= user_basic['account_id']
            region_id = user_basic['region_id'] 
            nickname = user_basic['nickname']
            await cur.execute(
                "SELECT username FROM user_basic WHERE region_id = %s and account_id = %s;", 
                [region_id, account_id]
            )
            user = await cur.fetchone()
            await conn.begin()
            if user is None:
                # 用户不存在，插入新用户
                nickname = f'User_{account_id}'
                await cur.execute(
                    "INSERT INTO user_basic (account_id, region_id, username) VALUES (%s, %s, %s);"
                    "INSERT INTO user_info (account_id) VALUES (%s);"
                    "INSERT INTO user_ships (account_id) VALUES (%s);"
                    "INSERT INTO user_clan (account_id) VALUES (%s);"
                    "INSERT INTO user_pr (account_id) VALUES (%s);",
                    [account_id, region_id, nickname, account_id, account_id, account_id, account_id]
                )
            else:
                if user[0] != nickname:
                    await cur.execute(
                        "UPDATE user_basic SET username = %s, updated_at = CURRENT_TIMESTAMP WHERE region_id = %s and account_id = %s;", 
                        [nickname, region_id, account_id]
                    )
                else:
                    await cur.execute(
                        "UPDATE user_basic SET updated_at = CURRENT_TIMESTAMP WHERE region_id = %s and account_id = %s;", 
                        [region_id, account_id]
                    )
            await conn.commit()
            return JSONResponse.API_1000_Success
        except Exception as e:
            # 数据库回滚
            await conn.rollback()
            raise e
        finally:
            # 释放资源
            await cur.close()
            await MysqlConnection.release_connection(conn)

    @ExceptionLogger.handle_database_exception_async
    async def get_user_clan(account_id: int) -> ResponseDict:
        '''获取用户所在工会数据

        从user_clan中获取用户工会数据

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
                "SELECT clan_id, UNIX_TIMESTAMP(updated_at) AS update_time FROM user_clan WHERE account_id = %s;", 
                [account_id]
            )
            user = await cur.fetchone()
            if user is None:
                return JSONResponse.get_success_response(data)
            else:
                data['clan_id'] = user[0]
                data['updated_at'] = user[1]
                return JSONResponse.get_success_response(data)
        except Exception as e:
            # 数据库回滚
            await conn.rollback()
            raise e
        finally:
            # 释放资源
            await cur.close()
            await MysqlConnection.release_connection(conn)

    @ExceptionLogger.handle_database_exception_async
    async def get_user_info(account_id: int) -> ResponseDict:
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
            if user:
                data = {
                    'is_active': user[0],
                    'active_level': user[1],
                    'is_public': user[2],
                    'total_battles': user[3],
                    'last_battle_time': user[4],
                    'update_time': user[5]
                }
            else:
                data = None
            return JSONResponse.get_success_response(data)
        except Exception as e:
            # 数据库回滚
            await conn.rollback()
            raise e
        finally:
            # 释放资源
            await cur.close()
            await MysqlConnection.release_connection(conn)

    @ExceptionLogger.handle_database_exception_async
    async def check_user_info(user_info: dict) -> ResponseDict:
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
            await cur.execute(
                "SELECT is_active, active_level, is_public, total_battles, last_battle_time FROM user_info WHERE account_id = %s;", 
                [account_id]
            )
            user = await cur.fetchone()
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
            # 数据库回滚
            await conn.rollback()
            raise e
        finally:
            # 释放资源
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
                        'ac_value': UserAccessToken.get_ac_value_by_aid(row[1],row[0])
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
            # 数据库回滚
            await conn.rollback()
            raise e
        finally:
            # 释放资源
            await cur.close()
            await MysqlConnection.release_connection(conn)

    @ExceptionLogger.handle_database_exception_async
    async def update_user_ships_data(
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
            # 数据库回滚
            await conn.rollback()
            raise e
        finally:
            # 释放资源
            await cur.close()
            await MysqlConnection.release_connection(conn)

    @ExceptionLogger.handle_database_exception_async
    async def update_user_cache_data(
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
            # 数据库回滚
            await conn.rollback()
            raise e
        finally:
            # 释放资源
            await cur.close()
            await MysqlConnection.release_connection(conn)
