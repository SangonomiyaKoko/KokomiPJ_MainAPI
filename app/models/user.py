from aiomysql.connection import Connection
from aiomysql.cursors import Cursor

from app.db import MysqlConnection
from app.log import ExceptionLogger
from app.response import JSONResponse, ResponseDict

class UserModel:
    @ExceptionLogger.handle_database_exception_async
    async def get_user_basic(account_id: int, region_id: int) -> ResponseDict:
        '''获取用户名称

        从user_basic中获取用户名称数据
        
        如果用户不存在会插入并返回一个默认值

        参数：
            account_id: 用户id
            region_id: 服务器id

        返回：
            nickname: 用户昵称
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
                    "INSERT IGNORE INTO user_basic (account_id, region_id, username) VALUES (%s, %s, %s);",
                    [account_id, region_id, nickname]
                )
                await cur.execute(
                    "INSERT IGNORE INTO user_info (account_id) VALUES (%s);", 
                    [account_id]
                )
                await cur.execute(
                    "INSERT IGNORE INTO user_ships (account_id) VALUES (%s);", 
                    [account_id]
                )
                await cur.execute(
                    "INSERT IGNORE INTO user_pr (account_id) VALUES (%s);", 
                    [account_id]
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
                    "INSERT IGNORE INTO user_basic (account_id, region_id, username) VALUES (%s, %s, %s);",
                    [account_id, region_id, nickname]
                )
                await cur.execute(
                    "INSERT IGNORE INTO user_info (account_id) VALUES (%s);", 
                    [account_id]
                )
                await cur.execute(
                    "INSERT IGNORE INTO user_ships (account_id) VALUES (%s);", 
                    [account_id]
                )
                await cur.execute(
                    "INSERT IGNORE INTO user_pr (account_id) VALUES (%s);", 
                    [account_id]
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
            nickname: 用户昵称
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
            dict
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
                if user_info[field] != user[i]:
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