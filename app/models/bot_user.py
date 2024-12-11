from aiomysql.connection import Connection
from aiomysql.cursors import Cursor

from app.db import MysqlConnection
from app.log import ExceptionLogger
from app.response import JSONResponse, ResponseDict

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
                "SELECT region_id, account_id FROM kokomi.bot_user_basic WHERE platform = %s AND user_id = %s;",
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
                "SELECT region_id, account_id FROM kokomi.bot_user_basic "
                "WHERE platform = %s AND user_id = %s;",
                [user_data['platform'], user_data['user_id']]
            )
            user = await cursor.fetchone()
            if user:
                await cursor.execute(
                    "UPDATE kokomi.bot_user_basic SET region_id = %s, account_id = %s "
                    "WHERE platform = %s AND user_id = %s;",
                    [user_data['region_id'],user_data['account_id'],user_data['platform'], user_data['user_id']]
                )
            else:
                await cursor.execute(
                    "INSERT INTO kokomi.bot_user_basic (platform, user_id, region_id, account_id) "
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