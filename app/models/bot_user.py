from aiomysql.connection import Connection
from aiomysql.cursors import Cursor

from app.db import MysqlConnection
from app.log import ExceptionLogger
from app.utils import UtilityFunctions
from app.response import JSONResponse, ResponseDict

from .db_name import MAIN_DB, BOT_DB


class BotUserModel:
    @ExceptionLogger.handle_database_exception_async
    async def get_user_bind(platform: str, user_id: str) -> ResponseDict:
        '''获取用户的绑定的信息

        从数据库中读取用户的绑定的账号

        参数:
            platform: 平台(qq/qq_group/qq_guild/wechat/discord)
            user_id: 用户id
        
        返回:
            ResponseDict
        '''
        try:
            connection: Connection = await MysqlConnection.get_connection()
            await connection.begin()
            cursor: Cursor = await connection.cursor()

            await cursor.execute(
                f"SELECT region_id, account_id FROM {BOT_DB}.user_basic "
                "WHERE platform = %s AND user_id = %s;",
                [platform, user_id]
            )
            user = await cursor.fetchone()
            if user:
                data = {
                    'region_id': user[0],
                    'account_id': user[1]
                }
            else:
                data = None

            await connection.commit()
            return JSONResponse.get_success_response(data)
        except Exception as e:
            await connection.rollback()
            raise e
        finally:
            await cursor.close()
            await MysqlConnection.release_connection(connection)

    @ExceptionLogger.handle_database_exception_async
    async def post_user_bind(user_data: dict) -> ResponseDict:
        '''获取用户的绑定的信息

        从数据库中读取用户的绑定的账号

        参数:
            user_data: 用户数据
        
        返回:
            ResponseDict
        '''
        try:
            connection: Connection = await MysqlConnection.get_connection()
            await connection.begin()
            cursor: Cursor = await connection.cursor()

            await cursor.execute(
                f"SELECT region_id, account_id FROM {BOT_DB}.user_basic "
                "WHERE platform = %s AND user_id = %s;",
                [user_data['platform'], user_data['user_id']]
            )
            user = await cursor.fetchone()
            if user:
                await cursor.execute(
                    f"UPDATE {BOT_DB}.user_basic SET region_id = %s, account_id = %s "
                    "WHERE platform = %s AND user_id = %s;",
                    [user_data['region_id'],user_data['account_id'],user_data['platform'], user_data['user_id']]
                )
            else:
                await cursor.execute(
                    f"INSERT INTO {BOT_DB}.user_basic (platform, user_id, region_id, account_id) "
                    "VALUES (%s, %s, %s, %s);",
                    [user_data['platform'], user_data['user_id'],user_data['region_id'],user_data['account_id']]
                )
            await connection.commit()
            return JSONResponse.API_1000_Success
        except Exception as e:
            await connection.rollback()
            raise e
        finally:
            await cursor.close()
            await MysqlConnection.release_connection(connection)

    @ExceptionLogger.handle_database_exception_async
    async def get_user_func(account_id: int, region_id: int) -> ResponseDict:
        '''获取用户的绑定的信息

        从数据库中读取用户的绑定的账号

        参数:
            user_data: 用户数据
        
        返回:
            ResponseDict
        '''
        try:
            connection: Connection = await MysqlConnection.get_connection()
            await connection.begin()
            cursor: Cursor = await connection.cursor()

            await cursor.execute(
                f"SELECT EXISTS ( SELECT 1 FROM {MAIN_DB}.recent WHERE account_id = %s AND region_id = %s ) AS in_recent, "
                f"EXISTS ( SELECT 1 FROM {MAIN_DB}.recents WHERE account_id = %s AND region_id = %s ) AS in_recents;",
                [account_id, region_id, account_id, region_id]
            )
            user = await cursor.fetchone()
            data = {
                'recent': user[0],
                'recents': user[1]
            }
            
            return JSONResponse.get_success_response(data)
        except Exception as e:
            await connection.rollback()
            raise e
        finally:
            await cursor.close()
            await MysqlConnection.release_connection(connection)

    

    @ExceptionLogger.handle_database_exception_async
    async def get_user_data(account_id: int, region_id: int) -> ResponseDict:
        '''获取数据库中用户的基本信息

        主要是bot或者排行榜通过uid来获取用户的基本信息，包括名称，工会以及颜色

        返回的数据中expired为True表示数据库中的用户工会信息已经过期或者无该用户数据
        
        '''
        try:
            connection: Connection = await MysqlConnection.get_connection()
            await connection.begin()
            cursor: Cursor = await connection.cursor()

            await cursor.execute(f'''
                SELECT 
                    basic.username, userclan.clan_id, UNIX_TIMESTAMP(userclan.updated_at) AS user_update_time, 
                    clan.tag, clan.league, UNIX_TIMESTAMP(clan.updated_at) AS clan_update_time
                FROM {MAIN_DB}.user_basic AS basic 
                LEFT JOIN {MAIN_DB}.user_clan AS userclan
                    ON userclan.account_id = basic.account_id 
                LEFT JOIN {MAIN_DB}.clan_basic AS clan
                    ON clan.region_id = basic.region_id AND clan.clan_id = userclan.clan_id
                WHERE basic.region_id = %s AND basic.account_id = %s;''',
                [region_id, account_id]
            )
            user = await cursor.fetchone()
            data = {
                'expired': False,
                'user': {
                    'id': account_id,
                    'name': None
                },
                'clan': {
                    'id': None,
                    'tag': None,
                    'league': None
                }
            }
            if user:
                data['user']['name'] = user[0]
                if user[2] and UtilityFunctions.check_clan_vaild(user[2]):
                    data['clan']['id'] = user[1]
                    if user[1]:
                        if user[5] and UtilityFunctions.check_clan_vaild(user[5]):
                            data['clan']['tag'] = user[3]
                            data['clan']['league'] = user[4]
                        else:
                            data['expired'] = True
                else:
                    data['expired'] = True
            else:
                name = UtilityFunctions.get_user_default_name(account_id)
                await cursor.execute(
                    f"INSERT INTO {MAIN_DB}.user_basic (account_id, region_id, username) VALUES (%s, %s, %s);",
                    [account_id, region_id, name]
                )
                await cursor.execute(
                    f"INSERT INTO {MAIN_DB}.user_info (account_id) VALUES (%s);",
                    [account_id]
                )
                await cursor.execute(
                    f"INSERT INTO {MAIN_DB}.user_ships (account_id) VALUES (%s);",
                    [account_id]
                )
                await cursor.execute(
                    f"INSERT INTO {MAIN_DB}.user_clan (account_id) VALUES (%s);",
                    [account_id]
                )
                data['user']['name'] = name
                data['expired'] = True

            await connection.commit()
            return JSONResponse.get_success_response(data)
        except Exception as e:
            await connection.rollback()
            raise e
        finally:
            await cursor.close()
            await MysqlConnection.release_connection(connection)
        
    @ExceptionLogger.handle_database_exception_async
    async def get_clan_data(clan_id: int, region_id: int) -> ResponseDict:
        '''获取工会名称

        从clan_basic中获取工会名称数据
        
        如果工会不存在会插入并返回一个默认值

        参数：
            clan_id: 工会id
            region_id: 服务器id

        返回：
            tag: 工会名称
            league: 工会段位（用于标记颜色）
        '''
        try:
            conn: Connection = await MysqlConnection.get_connection()
            await conn.begin()
            cur: Cursor = await conn.cursor()

            data= {
                'tag': None,
                'league': None
            }
            await cur.execute(
                f"SELECT tag, league FROM {MAIN_DB}.clan_basic "
                "WHERE region_id = %s and clan_id = %s;", 
                [region_id, clan_id]
            )
            clan = await cur.fetchone()
            if clan is None:
                # 用户不存在，插入新用户
                tag = UtilityFunctions.get_clan_default_name()
                await cur.execute(
                    f"INSERT INTO {MAIN_DB}.clan_basic (clan_id, region_id, tag) VALUES (%s, %s, %s);",
                    [clan_id, region_id, tag]
                )
                await cur.execute(
                    f"INSERT INTO {MAIN_DB}.clan_info (clan_id) VALUES (%s);",
                    [clan_id]
                )
                await cur.execute(
                    f"INSERT INTO {MAIN_DB}.clan_users (clan_id) VALUES (%s);",
                    [clan_id]
                )
                await cur.execute(
                    f"INSERT INTO {MAIN_DB}.clan_season (clan_id) VALUES (%s);",
                    [clan_id]
                )
                data['tag'] = tag
                data['league'] = 5
            else:
                data['tag'] = clan[0]
                data['league'] = clan[1]
            
            await conn.commit()
            return JSONResponse.get_success_response(data)
        except Exception as e:
            await conn.rollback()
            raise e
        finally:
            await cur.close()
            await MysqlConnection.release_connection(conn)