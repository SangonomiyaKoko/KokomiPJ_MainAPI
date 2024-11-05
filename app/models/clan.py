import uuid
import traceback
from aiomysql import MySQLError
from aiomysql.connection import Connection
from aiomysql.cursors import Cursor

from app.db import MysqlConnection
from app.response import JSONResponse
from app.utils import TimeFormat
from app.log import write_error_info

class ClanModel:
    async def get_clan_tag_and_league(
        clan_id: int, 
        region_id: int
    ) -> dict:
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
        conn: Connection = await MysqlConnection.get_connection()
        cur: Cursor = await conn.cursor()
        try:
            data= {
                'tag': None,
                'league': None,
                'updated_at': 0
            }
            await cur.execute(
                "SELECT tag, league, UNIX_TIMESTAMP(updated_at) AS update_time FROM clan_basic WHERE region_id = %s and clan_id = %s;", 
                [region_id, clan_id]
            )
            clan = await cur.fetchone()
            if clan is None:
                await conn.begin()
                # 用户不存在，插入新用户
                tag = 'N/A'
                await cur.execute(
                    "INSERT IGNORE INTO clan_basic (clan_id, region_id, tag) VALUES (%s, %s, %s);",
                    [clan_id, region_id, tag]
                )
                await cur.execute(
                    "INSERT IGNORE INTO clan_info (clan_id) VALUES (%s);", 
                    [clan_id]
                )
                await cur.execute(
                    "INSERT IGNORE INTO user_cache (clan_id) VALUES (%s);", 
                    [clan_id]
                )
                await conn.commit()
                data['tag'] = tag
                data['league'] = 5
            else:
                data['tag'] = clan[0]
                data['league'] = clan[1]
                data['updated_at'] = clan[2]
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
            

    # async def update_clan_tag_and_league(
    #     clan_id: int,
    #     region_id: int,
    #     tag: str,
    #     league: int
    # ) -> dict:
    #     '''更新表中工会名称

    #     更新clan_basic中工会名称（用于后台任务更新）

    #     注：调用前需先确保数据不为空

    #     参数：
    #         clan_id: 工会id
    #         region_id: 服务器id
    #         tag: 用户名称
    #         league: 工会段位

    #     返回：
    #         None
    #     '''
    #     conn: Connection = await MysqlConnection.get_connection()
    #     cur: Cursor = await conn.cursor()
    #     try:
    #         await cur.execute(
    #             "UPDATE clan_basic SET tag = %s, league = %s WHERE region_id = %s and clan_id = %s", 
    #             [tag, league, region_id, clan_id]
    #         )
    #         await conn.commit()
    #         return JSONResponse.API_1000_Success
    #     except MySQLError as e:
    #         await conn.rollback()
    #         error_id = str(uuid.uuid4())
    #         write_error_info(
    #             error_id = error_id,
    #             error_type = 'MySQL',
    #             error_name = f'ERROR_{e.args[0]}',
    #             error_file = __file__,
    #             error_info = f'\n{str(e.args[1])}'
    #         )
    #         return JSONResponse.get_error_response(3000,'DatabaseError',error_id)
    #     except Exception as e:
    #         error_id = str(uuid.uuid4())
    #         write_error_info(
    #             error_id = error_id,
    #             error_type = 'Program',
    #             error_name = str(type(e).__name__),
    #             error_file = __file__,
    #             error_info = f'\n{traceback.format_exc()}'
    #         )
    #         return JSONResponse.get_error_response(5000,'ProgramError',error_id)
    #     finally:
    #         await cur.close()
    #         await MysqlConnection.release_connection(conn)