from aiomysql.connection import Connection
from aiomysql.cursors import Cursor

from app.db import MysqlConnection
from app.response import JSONResponse, ResponseDict
from app.log import ExceptionLogger

from .db_name import MAIN_DB


class UserAccessToken:
    '''存储用户ac数据

    VortexAPI的AccessToken
    
    account_id： 'access_token'
    '''
    access_token_list = {1:{},2:{},3:{},4:{211817574:'X3mXceQus5lufCl5pJi5CMG6IKY'},5:{}} # 测试数据
    
    @ExceptionLogger.handle_database_exception_async
    async def get_ac_value_by_type(token_type: int = 1) -> ResponseDict:
        '''获取某个type下所有用户的ac数据

        获取此数据主要是因为提供token1的用户一般比较少，所以直接读取全部数据比带条件的方便

        注意，此处没有使用索引，走的全表扫描

        参数:
            - token_type
        
        返回:
            - ResponseDict
        '''
        try:
            conn: Connection = await MysqlConnection.get_connection()
            await conn.begin()
            cur: Cursor = await conn.cursor()

            data = []
            await cur.execute(
                "SELECT account_id, region_id, token_value, expired_at "
                f"FROM {MAIN_DB}.user_token WHERE token_type = %s;",
                [token_type]
            )
            users = await cur.fetchall()
            for user in users:
                if user[1] != token_type:
                    continue
                data.append({
                    'account_id': user[0],
                    'region_id': user[1],
                    'token_value': user[2]
                })

            await conn.commit()
            return JSONResponse.get_success_response(data)
        except Exception as e:
            await conn.rollback()
            raise e
        finally:
            await cur.close()
            await MysqlConnection.release_connection(conn)
    
    @ExceptionLogger.handle_database_exception_async
    async def get_ac_value_by_rid(region_id: int, token_type: int = 1) -> ResponseDict:
        '''获取某个服务器下所有用户的ac数据

        主要用于用户更新服务

        参数:
            - region_id
            - token_type
        
        返回:
            - ResponseDict
        '''
        try:
            conn: Connection = await MysqlConnection.get_connection()
            await conn.begin()
            cur: Cursor = await conn.cursor()

            data = {}
            await cur.execute(
                "SELECT account_id, token_type, token_value, expired_at "
                f"FROM {MAIN_DB}.user_token WHERE region_id = %s;",
                [region_id]
            )
            users = await cur.fetchall()
            for user in users:
                if user[1] != token_type:
                    continue
                data[user[0]] = user[2]

            await conn.commit()
            return JSONResponse.get_success_response(data)
        except Exception as e:
            await conn.rollback()
            raise e
        finally:
            await cur.close()
            await MysqlConnection.release_connection(conn)
    
    @ExceptionLogger.handle_database_exception_async
    async def get_ac_value_by_id(account_id: int, region_id: int, token_type: int = 1) -> ResponseDict:
        '''获取某个用户的ac数据

        主要用于用户更新服务

        参数:
            - region_id
            - token_type
        
        返回:
            - ResponseDict
        '''
        try:
            conn: Connection = await MysqlConnection.get_connection()
            await conn.begin()
            cur: Cursor = await conn.cursor()

            data = {}
            await cur.execute(
                "SELECT token_value, expired_at "
                f"FROM {MAIN_DB}.user_token WHERE region_id = %s AND account_id = %s AND token_type = %s;",
                [region_id, account_id, token_type]
            )
            user = await cur.fetchone()
            if user:
                data['token_value'] = user[0]

            await conn.commit()
            return JSONResponse.get_success_response(data)
        except Exception as e:
            await conn.rollback()
            raise e
        finally:
            await cur.close()
            await MysqlConnection.release_connection(conn)
    
    @ExceptionLogger.handle_database_exception_async
    async def set_ac_value(
        account_id: int, 
        region_id: int, 
        token_value: str, 
        token_type: int = 1, 
        expired_at: int = None
    ) -> ResponseDict:
        '''写入或者更新某个用户的ac数据'''
        try:
            conn: Connection = await MysqlConnection.get_connection()
            await conn.begin()
            cur: Cursor = await conn.cursor()

            data = {}
            await cur.execute(
                "SELECT token_value, expired_at "
                f"FROM {MAIN_DB}.user_token WHERE region_id = %s AND account_id = %s AND token_type = %s;",
                [region_id, account_id, token_type]
            )
            user = await cur.fetchone()
            if user:
                await cur.execute(
                    f"UPDATE {MAIN_DB}.user_token SET token_type = %s, token_value = %s WHERE region_id = %s AND account_id = %s;",
                    [token_type, token_value, account_id, region_id]
                )
            else:
                await cur.execute(
                    f"INSERT INTO {MAIN_DB}.user_token (account_id, region_in, token_type, token_value) VALUES (%s, %s, %s, %s);",
                    [account_id, region_id, token_type, token_value]
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
    async def delete_ac_value_by_id(account_id: int, region_id: int, token_type: int = 1) -> ResponseDict:
        '''删除某个用户的ac数据'''
        try:
            conn: Connection = await MysqlConnection.get_connection()
            await conn.begin()
            cur: Cursor = await conn.cursor()

            data = {}
            await cur.execute(
                "DELETE FROM {MAIN_DB}.user_token WHERE region_id = %s AND account_id = %s AND token_type = %s;",
                [region_id, account_id, token_type]
            )
            user = await cur.fetchone()
            if user:
                data['token_value'] = user[0]

            await conn.commit()
            return JSONResponse.get_success_response(data)
        except Exception as e:
            await conn.rollback()
            raise e
        finally:
            await cur.close()
            await MysqlConnection.release_connection(conn)
    
class UserAccessToken2:
    '''用户ac2数据
    
    OfficialAPI的AccessToken
    '''

    def get_ac_value_by_id(account_id: int, region_id: int) -> str | None:
        if account_id == 2023619512:
            # 测试Token过期时间：2024/12/15 23:59:59
            return '368a12ec52c9572915f0620c67c83ab7a5396cd4' # 测试数据
        else:
            return None
    
    def set_ac_value(account_id: int, region_id: int, ac_value: str):
        return None