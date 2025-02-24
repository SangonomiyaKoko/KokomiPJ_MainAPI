from aiomysql.connection import Connection
from aiomysql.cursors import Cursor

from app.db import MysqlConnection
from app.log import ExceptionLogger
from app.response import JSONResponse, ResponseDict

from .db_name import MAIN_DB


class GameModel:
    @ExceptionLogger.handle_database_exception_async
    async def get_game_version(region_id: int) -> ResponseDict:
        '''获取数据库中存储的游戏版本

        方法描述

        参数:
            params
        
        返回:
            ResponseDict
        '''
        try:
            conn: Connection = await MysqlConnection.get_connection()
            await conn.begin()
            cur: Cursor = await conn.cursor()

            data = {
                'version': None
            }
            await cur.execute(
                f"SELECT game_version FROM {MAIN_DB}.region_version WHERE region_id = %s;",
                [region_id]
            )
            game = await cur.fetchone()
            if game == None:
                raise ValueError('Table Not Found')
            else:
                data['version'] = game[0]

            await conn.commit()
            return JSONResponse.get_success_response(data)
        except Exception as e:
            await conn.rollback()
            raise e
        finally:
            await cur.close()
            await MysqlConnection.release_connection(conn)

    @ExceptionLogger.handle_database_exception_async
    async def update_game_version(region_id: int, game_version: str) -> ResponseDict:
        '''更新数据库中存储的游戏版本

        方法描述

        参数:
            params
        
        返回:
            ResponseDict
        '''
        try:
            conn: Connection = await MysqlConnection.get_connection()
            await conn.begin()
            cur: Cursor = await conn.cursor()

            version = ".".join(game_version.split(".")[:2])
            await cur.execute(
                f"SELECT game_version FROM {MAIN_DB}.region_version WHERE region_id = %s;",
                [region_id]
            )
            row = await cur.fetchone()
            if row[0] != version:
                await cur.execute(
                    f"UPDATE {MAIN_DB}.region_version SET game_version = %s, "
                    "version_start = CURRENT_TIMESTAMP, full_version = %s WHERE region_id = %s;",
                    [version, game_version, region_id]
                )
            else:
                await cur.execute(
                    f"UPDATE {MAIN_DB}.region_version SET full_version = %s WHERE region_id = %s;",
                    [game_version, region_id]
                )

            await conn.commit()
            return JSONResponse.API_1000_Success
        except Exception as e:
            await conn.rollback()
            raise e
        finally:
            await cur.close()
            await MysqlConnection.release_connection(conn)