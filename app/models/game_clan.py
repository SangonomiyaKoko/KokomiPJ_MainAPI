from aiomysql.connection import Connection
from aiomysql.cursors import Cursor

from app.db import MysqlConnection
from app.response import JSONResponse, ResponseDict
from app.log import ExceptionLogger
from app.utils import UtilityFunctions, TimeFormat

class ClanModel:
    async def get_clan_by_rid(region_id: int) -> ResponseDict:
        try:
            conn: Connection = await MysqlConnection.get_connection()
            await conn.begin()
            cur: Cursor = await conn.cursor()

            data = []
            await cur.execute(
                "SELECT b.clan_id, u.hash_value, UNIX_TIMESTAMP(u.updated_at) AS update_time "
                "FROM clan_basic AS b "
                "LEFT JOIN clan_users AS u "
                "ON b.clan_id = u.clan_id "
                "WHERE b.region_id = %s;",
                [region_id]
            )
            users = await cur.fetchall()
            for user in users:
                data.append({
                    'clan_id': user[0],
                    'hash_value': user[1],
                    'update_time': user[2]
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

    async def update_clan_info_batch(region_id: int, season_number: int, clan_data_list: list) -> ResponseDict:
        try:
            conn: Connection = await MysqlConnection.get_connection()
            await conn.begin()
            cur: Cursor = await conn.cursor()

            await cur.execute(
                "SELECT season_number FROM region_season WHERE region_id = %s;",
                [region_id]
            )
            season_number_in_db = await cur.fetchone()
            sql_str = ''
            params = [region_id, clan_data_list[0]['id']]
            for clan_data in clan_data_list[1:]:
                sql_str += ', %s'
                params.append(clan_data['id'])
            await cur.execute(
                "SELECT b.clan_id, b.tag, b.league, UNIX_TIMESTAMP(b.updated_at) AS basic_update_time, "
                "i.is_active, i.season, i.public_rating, i.league, i.division, i.division_rating, "
                "UNIX_TIMESTAMP(i.last_battle_at) AS info_last_battle_time, "
                "s.season, UNIX_TIMESTAMP(s.last_battle_at) AS season_last_battle_time "
                "FROM clan_basic AS b "
                "LEFT JOIN clan_info AS i ON b.clan_id = i.clan_id "
                "LEFT JOIN clan_season AS s ON b.clan_id = s.clan_id "
                f"WHERE b.region_id = %s AND b.clan_id in ( %s{sql_str} );",
                params
            )
            need_update_clan = {
                'region_id': region_id,
                'season_number': season_number,
                'clan_id_list': []
            }
            clans = await cur.fetchall()
            exists_clans = {}
            current_timestamp = TimeFormat.get_current_timestamp
            for clan in clans:
                exists_clans[clan[0]] = clan[1:]
            for clan_data in clan_data_list:
                # 批量更新写入数据
                clan_id = clan_data['id']
                if clan_id not in exists_clans:
                    # 用户不存在于数据库中，直接写入
                    await cur.execute(
                        "INSERT INTO clan_basic (clan_id, region_id, tag) VALUES (%s, %s, %s);",
                        [clan_id, region_id, clan_data['tag']]
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
                    await cur.execute(
                        "UPDATE clan_basic SET tag = %s, league = %s WHERE region_id = %s AND clan_id = %s",
                        [clan_data['tag'],clan_data['league'],region_id,clan_id]
                    )
                    await cur.execute(
                        "UPDATE clan_info SET is_active = %s, season = %s, public_rating = %s, league = %s, "
                        "division = %s, division_rating = %s, last_battle_at = FROM_UNIXTIME(%s) "
                        "WHERE clan_id = %s",
                        [
                            1,season_number,clan_data['public_rating'],clan_data['league'],clan_data['division'],
                            clan_data['division_rating'],clan_data['last_battle_at'],clan_id
                        ]
                    )
                    need_update_clan['clan_id_list'].append(clan_id)
                else:
                    if season_number != season_number_in_db:
                        # 数据在数据库中，但是赛季更改，直接写入数据
                        await cur.execute(
                            "UPDATE region_season SET season_number = %s WHERE region_id = %s;",
                            [season_number, region_id]
                        )
                        await cur.execute(
                            "UPDATE clan_basic SET tag = %s, league = %s WHERE region_id = %s AND clan_id = %s",
                            [clan_data['tag'],clan_data['league'],region_id,clan_id]
                        )
                        await cur.execute(
                            "UPDATE clan_info SET public_rating = %s, league = %s, "
                            "division = %s, division_rating = %s, last_battle_at = FROM_UNIXTIME(%s) "
                            "WHERE clan_id = %s",
                            [
                                clan_data['public_rating'],clan_data['league'],clan_data['division'],
                                clan_data['division_rating'],clan_data['last_battle_at'],clan_id
                            ]
                        )
                        need_update_clan['clan_id_list'].append(clan_id)
                    else:
                        # 数据在数据库中，且没有赛季更改，检验数据是否改变再决定是否更新数据
                        if (
                            int(current_timestamp) - exists_clans[clan_id][2] > 2*24*60*60 or 
                            clan_data['tag'] != exists_clans[clan_id][0] or 
                            clan_data['league'] != exists_clans[clan_id][1]
                        ):
                            await cur.execute(
                                "UPDATE clan_basic SET tag = %s, league = %s WHERE region_id = %s AND clan_id = %s",
                                [clan_data['tag'],clan_data['league'],region_id,clan_id]
                            )
                        if (
                            clan_data['public_rating'] != exists_clans[clan_id][5] or
                            clan_data['last_battle_at'] != exists_clans[clan_id][9]
                        ):
                            await cur.execute(
                                "UPDATE clan_info SET public_rating = %s, league = %s, "
                                "division = %s, division_rating = %s, last_battle_at = FROM_UNIXTIME(%s) "
                                "WHERE clan_id = %s",
                                [
                                    clan_data['public_rating'],clan_data['league'],clan_data['division'],
                                    clan_data['division_rating'],clan_data['last_battle_at'],clan_id
                                ]
                            )
                        if (
                            exists_clans[clan_id][10] != season_number or
                            not exists_clans[clan_id][9] or
                            not exists_clans[clan_id][11] or
                            exists_clans[clan_id][9] != exists_clans[clan_id][11]
                        ):
                            need_update_clan['clan_id_list'].append(clan_id)
            await conn.commit()
            return JSONResponse.get_success_response(need_update_clan)
        except Exception as e:
            await conn.rollback()
            raise e
        finally:
            await cur.close()
            await MysqlConnection.release_connection(conn)