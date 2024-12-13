import asyncio
from aiomysql.connection import Connection
from aiomysql.cursors import Cursor

from app.db import MysqlConnection
from app.log import ExceptionLogger
from app.response import JSONResponse, ResponseDict


class RankDataModel:
    @ExceptionLogger.handle_database_exception_async
    async def get_ship_data(ship_id, region_id) -> ResponseDict:
        '''获取单船数据

        参数:
            ship_id, region_id
            
        返回:
            ResponseDict
        '''
        try:
            conn: Connection = await MysqlConnection.get_connection()     # 获取连接
            await conn.begin()  # 开启事务
            
            cursor: Cursor = await conn.cursor()  # 获取游标
            data = []
            query = f'''SELECT account_id, battles_count, wins, damage_dealt, frags, exp, max_exp, max_damage_dealt, max_frags FROM ships.ship_{ship_id} WHERE battles_count > 80 AND region_id = %s;'''
            await cursor.execute(query, (region_id,))
            rows = await cursor.fetchall()
            for row in rows:
                data.append(row)
            if data == []:
                return JSONResponse.API_1006_UserDataisNone
            return JSONResponse.get_success_response(data)
        except Exception as e:
            raise e  # 抛出异常
        finally:
            await cursor.close()  # 关闭游标
            await MysqlConnection.release_connection(conn)  # 释放连接
            
    @ExceptionLogger.handle_database_exception_async
    async def get_user(user_id, region_id) -> ResponseDict:
        '''获取用户个人信息

        参数:
            user_id, region_id
        
        返回:
            ResponseDict
        '''
        try:
            connection: Connection = await MysqlConnection.get_connection()  # 获取连接
            await connection.begin()  # 开启事务
            cursor: Cursor = await connection.cursor()  # 获取游标

            await cursor.execute(
                '''SELECT username 
                FROM kokomi.user_basic 
                WHERE account_id = %s AND region_id = %s
                ''',(user_id, region_id)
                )
            
            data = await cursor.fetchall()

            
            return JSONResponse.get_success_response(data)  # 返回数据
        except Exception as e:
            raise e  # 抛出异常
        finally:
            await cursor.close()  # 关闭游标
            await MysqlConnection.release_connection(connection)  # 释放连接

    @ExceptionLogger.handle_database_exception_async
    async def get_clan_id(user_id) -> ResponseDict:
        '''获取工会id

        参数:
            user_id
            
        返回:
            ResponseDict(clan_id)
        '''
        try:
            connection: Connection = await MysqlConnection.get_connection()  # 获取连接
            await connection.begin()  # 开启事务
            cursor: Cursor = await connection.cursor()  # 获取游标

            await cursor.execute(
                '''SELECT clan_id
                FROM kokomi.user_clan 
                WHERE account_id = %s
                ''',(user_id,)
                )
            
            data = await cursor.fetchall()

            
            return JSONResponse.get_success_response(data)  # 返回数据
        except Exception as e:
            raise e  # 抛出异常
        finally:
            await cursor.close()  # 关闭游标
            await MysqlConnection.release_connection(connection)  # 释放连接
        
    @ExceptionLogger.handle_database_exception_async
    async def get_clan(clan_id, region_id) -> ResponseDict:
        '''获取工会信息

        参数:
            clan_id, region_id
        
        返回:
            ResponseDict(clan, league)
        '''
        try:
            connection: Connection = await MysqlConnection.get_connection()  # 获取连接
            await connection.begin()  # 开启事务
            cursor: Cursor = await connection.cursor()  # 获取游标

            await cursor.execute(
                '''SELECT tag, league
                FROM kokomi.clan_basic 
                WHERE clan_id = %s AND region_id = %s
                ''',[clan_id, region_id])
            
            data = await cursor.fetchall()

            
            return JSONResponse.get_success_response(data)  # 返回数据
        except Exception as e:
            raise e  # 抛出异常
        finally:
            await cursor.close()  # 关闭游标
            await MysqlConnection.release_connection(connection)  # 释放连接    
            
    @ExceptionLogger.handle_database_exception_async
    async def get_ship_id() -> ResponseDict:
        '''获取船只id

        参数:
            None
        
        返回:
            ResponseDict(ship_id)
        '''
        try:
            connection: Connection = await MysqlConnection.get_connection()  # 获取连接
            await connection.begin()  # 开启事务
            cursor: Cursor = await connection.cursor()  # 获取游标

            await cursor.execute(
                '''SELECT ship_id
                FROM ships.existing_ships
                ''')
            
            data = await cursor.fetchall()

            
            return JSONResponse.get_success_response(data)  # 返回数据
        except Exception as e:
            raise e  # 抛出异常
        finally:
            await cursor.close()  # 关闭游标
            await MysqlConnection.release_connection(connection)  # 释放连接    