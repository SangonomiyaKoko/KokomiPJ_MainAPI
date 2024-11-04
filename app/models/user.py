import uuid
import traceback
from typing import Optional
from aiomysql import MySQLError
from aiomysql.connection import Connection
from aiomysql.cursors import Cursor

from app.db import MysqlConnection
from app.log import write_error_info
from app.response import JSONResponse

class UserModel:
    async def get_user_basic(
        account_id: int, 
        region_id: int
    ) -> dict:
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
                # 用户不存在，插入新用户
                nickname = f'User_{account_id}'
                await cur.execute(
                    "INSERT INTO user_basic (account_id, region_id, username) VALUES (%s, %s, %s);",
                    [account_id, region_id, nickname]
                )
                await cur.execute(
                    "INSERT INTO user_info (account_id) VALUES (%s);", 
                    [account_id]
                )
                await cur.execute(
                    "INSERT INTO user_cache (account_id) VALUES (%s);", 
                    [account_id]
                )
                await conn.commit()
                data['nickname'] = nickname
            else:
                data['nickname'] = user[0]
            return JSONResponse.get_success_response(data)
        except MySQLError as e:
            await conn.rollback()
            error_id = str(uuid.uuid4())
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


    async def update_user_basic(
        account_id: int, 
        region_id: int,
        nickname: Optional[str] = None,
        need_update: bool = False
    ) -> dict:
        '''更新表中用户名称

        更新user_basic中用户名称（用于后台任务更新）

        注：调用前需先确保数据不为空

        参数：
            account_id: 用户id
            region_id: 服务器id
            nickname: 用户名称
            need_update: 如果为False则说明不需要更新name，只更新time

        返回：
            None
        '''
        conn: Connection = await MysqlConnection.get_connection()
        cur: Cursor = await conn.cursor()
        try:
            if need_update:
                await cur.execute(
                    "UPDATE user_basic SET username = %s WHERE region_id = %s and account_id = %s;", 
                    [nickname, region_id, account_id]
                )
                await conn.commit()
            else:
                await cur.execute(
                    "UPDATE user_basic SET updated_at = CURRENT_TIMESTAMP WHERE region_id = %s and account_id = %s;", 
                    [region_id, account_id]
                )
                await conn.commit()
            return JSONResponse.API_1000_Success
        except MySQLError as e:
            await conn.rollback()
            error_id = str(uuid.uuid4())
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


    async def get_user_clan(
        account_id: int
    ) -> dict:
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
        except MySQLError as e:
            await conn.rollback()
            error_id = str(uuid.uuid4())
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

    async def update_user_clan(
        account_id: int | list,
        clan_id: Optional[int] = None,
        need_update: bool = False
    ) -> dict:
        '''更新用户工会信息

        更新user_clan中用户对应的工会（用于后台任务更新）

        参数：
            account_id: 用户id，可以是某个用户或者用户列表
            clan_id； 工会id
            need_update: 只对于写入单个用户生效

        返回：
            None
        '''
        conn: Connection = await MysqlConnection.get_connection()
        cur: Cursor = await conn.cursor()
        try:
            if isinstance(account_id, list):
                # 如果用户是一个列表
                await cur.executemany(
                    "INSERT INTO user_clan (account_id, clan_id) "
                    "VALUES (%s, %s) AS new_values "
                    "ON DUPLICATE KEY UPDATE "
                    "clan_id = new_values.clan_id, updated_at = CURRENT_TIMESTAMP;",
                    [(aid, clan_id) for aid in account_id]
                )
            else:
                # 单个用户
                if need_update:
                    await cur.execute(
                        "INSERT INTO user_clan (account_id, clan_id) "
                        "VALUES (%s, %s) AS new_values "
                        "ON DUPLICATE KEY UPDATE "
                        "clan_id = new_values.clan_id, updated_at = CURRENT_TIMESTAMP;",
                        [account_id, clan_id]
                    )
                else:
                    await cur.execute(
                        "INSERT INTO user_clan (account_id) "
                        "VALUES (%s) AS new_values "
                        "ON DUPLICATE KEY UPDATE "
                        "updated_at = CURRENT_TIMESTAMP;",
                        [account_id]
                    )
            await conn.commit()
            return JSONResponse.API_1000_Success
        except MySQLError as e:
            await conn.rollback()
            error_id = str(uuid.uuid4())
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

    async def get_user_info(account_id: int) -> dict:
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
                "SELECT is_active, active_level, is_public, total_battles, last_battle_time, UNIX_TIMESTAMP(updated_at) AS update_time FROM user_info WHERE account_id = %s;", 
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
        except MySQLError as e:
            await conn.rollback()
            error_id = str(uuid.uuid4())
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

    async def check_user_info(
        account_id: int,
        user_info: dict
    ):
        '''检查user_info表是否需要更新

        首先从数据库中获取数据，和传入的参数对比，更新发生改变的数据

        注：调用前需先确保数据不为空

        参数：
            account_id: 用户id
            user_info = {
                'is_active': True,
                'active_level': 0,
                'is_public': True,
                'total_battles': 0,
                'last_battle_time': 0
            }
        
        返回：
            Code: 1000/3000/5000
        '''
        conn: Connection = await MysqlConnection.get_connection()
        cur: Cursor = await conn.cursor()
        try:
            await cur.execute(
                "SELECT is_active, active_level, is_public, total_battles, last_battle_time FROM user_info WHERE account_id = %s", 
                [account_id]
            )
            user = await cur.fetchone()
            i = 0
            sql_str = ''
            params = []
            for field in ['is_active', 'active_level', 'is_public', 'total_battles', 'last_battle_time']:
                if user_info[field] != user[i]:
                    sql_str += f'{field} = %s, '
                    params.append(user_info[field])
                i += 1
            params = params + [account_id]
            await cur.execute(
                f"UPDATE user_info SET {sql_str}updated_at = CURRENT_TIMESTAMP WHERE account_id = %s", 
                params
            )
            await conn.commit()
            return JSONResponse.API_1000_Success
        except MySQLError as e:
            await conn.rollback()
            error_id = str(uuid.uuid4())
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