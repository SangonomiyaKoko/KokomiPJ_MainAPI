from aiomysql.connection import Connection
from aiomysql.cursors import Cursor

from app.db import MysqlConnection
from app.log import ExceptionLogger
from app.response import JSONResponse, ResponseDict


class RecentsUserModel:
    @ExceptionLogger.handle_database_exception_async
    async def get_recents_user_by_rid(region_id: int) -> ResponseDict:
        try:
            conn: Connection = await MysqlConnection.get_connection()
            await conn.begin()
            cur: Cursor = await conn.cursor()

            data = []
            await cur.execute(
                "SELECT account_id FROM kokomi.recents WHERE region_id = %s;",
                [region_id]
            )
            users = await cur.fetchall()
            for user in users:
                data.append(user[0])
            
            await conn.commit()
            return JSONResponse.get_success_response(data)
        except Exception as e:
            await conn.rollback()
            raise e
        finally:
            await cur.close()
            await MysqlConnection.release_connection(conn)