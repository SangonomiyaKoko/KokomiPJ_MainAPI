from aiomysql.connection import Connection
from aiomysql.cursors import Cursor

from app.db import MysqlConnection
from app.response import JSONResponse, ResponseDict
from app.log import ExceptionLogger
from app.utils import UtilityFunctions

class ClanModel:
    @ExceptionLogger.handle_database_exception_async
    async def get_clan_tag_and_league(clan_id: int, region_id: int) -> ResponseDict:
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
                'league': None,
                'updated_at': None
            }
            await cur.execute(
                "SELECT tag, league, UNIX_TIMESTAMP(updated_at) AS update_time FROM clan_basic WHERE region_id = %s and clan_id = %s;", 
                [region_id, clan_id]
            )
            clan = await cur.fetchone()
            if clan is None:
                # 用户不存在，插入新用户
                tag = UtilityFunctions.get_clan_default_name()
                await cur.execute(
                    "INSERT INTO clan_basic (clan_id, region_id, tag) VALUES (%s, %s, %s);",
                    [clan_id, region_id, tag]
                )
                await cur.execute(
                    "INSERT INTO clan_info (clan_id) VALUES (%s);",
                    [clan_id]
                )
                await cur.execute(
                    "INSERT INTO clan_users (clan_id) VALUES (%s);",
                    [clan_id]
                )
                await cur.execute(
                    "INSERT INTO clan_season (clan_id) VALUES (%s);",
                    [clan_id]
                )
                data['tag'] = tag
                data['league'] = 5
            else:
                data['tag'] = clan[0]
                data['league'] = clan[1]
                data['updated_at'] = clan[2]
            
            await conn.commit()
            return JSONResponse.get_success_response(data)
        except Exception as e:
            await conn.rollback()
            raise e
        finally:
            await cur.close()
            await MysqlConnection.release_connection(conn)