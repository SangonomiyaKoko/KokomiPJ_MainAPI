from aiomysql.connection import Connection
from aiomysql.cursors import Cursor

from app.db import MysqlConnection
from app.response import JSONResponse, ResponseDict
from app.log import ExceptionLogger
from app.utils import UtilityFunctions, TimeFormat

class ClanModel:

    @ExceptionLogger.handle_database_exception_async
    async def get_clan_max_number() -> ResponseDict:
        '''获取数据库中id的最大值

        获取id的最大值，用于数据库遍历更新时确定边界

        参数:
            - None
        
        返回:
            - ResponseDict
        '''
        try:
            conn: Connection = await MysqlConnection.get_connection()
            await conn.begin()
            cur: Cursor = await conn.cursor()

            data = {
                'max_id': 0
            }
            await cur.execute(
                "SELECT MAX(id) AS max_id FROM kokomi.clan_basic;"
            )
            user = await cur.fetchone()
            data['max_id'] = user[0]

            await conn.commit()
            return JSONResponse.get_success_response(data)
        except Exception as e:
            await conn.rollback()
            raise e
        finally:
            await cur.close()
            await MysqlConnection.release_connection(conn)

    @ExceptionLogger.handle_database_exception_async
    async def get_clan_cache_batch(offset: int, limit = 1000) -> ResponseDict:
        '''批量获取用户缓存的数据

        获取用户缓存数据，用于缓存的更新

        参数:
            offset: 从哪个id开始读取
            limit: 每次读取多少条数据
        
        返回值:
            ResponseDict
        '''
        try:
            conn: Connection = await MysqlConnection.get_connection()
            await conn.begin()
            cur: Cursor = await conn.cursor()

            data = []
            await cur.execute(
                "SELECT b.clan_id, b.region_id, i.is_active, UNIX_TIMESTAMP(i.updated_at) AS info_update_time, "
                "u.hash_value, UNIX_TIMESTAMP(u.updated_at) AS users_update_time "
                "FROM kokomi.clan_basic AS b "
                "LEFT JOIN kokomi.clan_info AS i ON b.clan_id = i.clan_id "
                "LEFT JOIN kokomi.clan_users AS u ON b.clan_id = u.clan_id "
                "ORDER BY b.id LIMIT %s OFFSET %s;", 
                [limit, offset]
            )
            rows = await cur.fetchall()
            for row in rows:
                # 排除已注销账号的数据，避免浪费服务器资源
                if row[3] and not row[2]:
                    continue
                user = {
                    'clan_basic': {
                        'region_id': row[1],
                        'clan_id': row[0]
                    },
                    'clan_info': {
                        'is_active': row[2],
                        'update_time': row[3]
                    },
                    'clan_users':{
                        'hash_value': row[4],
                        'update_time': row[5]
                    }
                }
                data.append(user)
            
            await conn.commit()
            return JSONResponse.get_success_response(data)
        except Exception as e:
            await conn.rollback()
            raise e
        finally:
            await cur.close()
            await MysqlConnection.release_connection(conn)

    @ExceptionLogger.handle_database_exception_async
    async def get_clan_by_rid(region_id: int) -> ResponseDict:
        try:
            conn: Connection = await MysqlConnection.get_connection()
            await conn.begin()
            cur: Cursor = await conn.cursor()

            data = []
            await cur.execute(
                "SELECT b.clan_id, i.is_active, UNIX_TIMESTAMP(i.updated_at) AS info_update_time, "
                "u.hash_value, UNIX_TIMESTAMP(u.updated_at) AS users_update_time "
                "FROM kokomi.clan_basic AS b "
                "LEFT JOIN kokomi.clan_info AS i ON b.clan_id = i.clan_id "
                "LEFT JOIN kokomi.clan_users AS u ON b.clan_id = u.clan_id "
                "WHERE b.region_id = %s;",
                [region_id]
            )
            users = await cur.fetchall()
            for user in users:
                # 排除不活跃的用户数据
                if user[2] and not user[1]:
                    continue
                data.append({
                    'clan_id': user[0],
                    'hash_value': user[3],
                    'update_time': user[4]
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
                "SELECT tag, league, UNIX_TIMESTAMP(updated_at) AS update_time FROM kokomi.clan_basic WHERE region_id = %s and clan_id = %s;", 
                [region_id, clan_id]
            )
            clan = await cur.fetchone()
            if clan is None:
                # 用户不存在，插入新用户
                tag = UtilityFunctions.get_clan_default_name()
                await cur.execute(
                    "INSERT INTO kokomi.clan_basic (clan_id, region_id, tag) VALUES (%s, %s, %s);",
                    [clan_id, region_id, tag]
                )
                await cur.execute(
                    "INSERT INTO kokomi.clan_info (clan_id) VALUES (%s);",
                    [clan_id]
                )
                await cur.execute(
                    "INSERT INTO kokomi.clan_users (clan_id) VALUES (%s);",
                    [clan_id]
                )
                await cur.execute(
                    "INSERT INTO kokomi.clan_season (clan_id) VALUES (%s);",
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

    @ExceptionLogger.handle_database_exception_async
    async def update_clan_season(clan_season: dict) -> ResponseDict:
        try:
            conn: Connection = await MysqlConnection.get_connection()
            await conn.begin()
            cur: Cursor = await conn.cursor()

            clan_id = clan_season['clan_id']
            region_id = clan_season['region_id']
            season_number = clan_season['season_number']
            last_battle_time = clan_season['last_battle_time']
            team_data_1 = clan_season['team_data']['1']
            team_data_2 = clan_season['team_data']['2']
            await cur.execute(
                "SELECT season, UNIX_TIMESTAMP(last_battle_at) AS last_battle_time, team_data_1, team_data_2 "
                "FROM kokomi.clan_season WHERE clan_id = %s;",
                [clan_id]
            )
            clan = await cur.fetchone()
            if clan == None:
                await conn.commit()
                return JSONResponse.API_1009_ClanNotExistinDatabase
            if clan[0] != season_number:
                await cur.execute(
                    "UPDATE kokomi.clan_season SET season = %s, last_battle_at = FROM_UNIXTIME(%s), "
                    "team_data_1 = %s, team_data_2 = %s WHERE clan_id = %s",
                    [
                        season_number,last_battle_time, 
                        str(team_data_1),str(team_data_2),clan_id
                    ]
                )
                await conn.commit()
                return JSONResponse.API_1000_Success
            #if clan[1] != last_battle_time:
            if clan[1] == last_battle_time:
                await cur.execute(
                    "UPDATE kokomi.clan_season SET season = %s, last_battle_at = FROM_UNIXTIME(%s), "
                    "team_data_1 = %s, team_data_2 = %s WHERE clan_id = %s",
                    [
                        season_number,last_battle_time, 
                        str(team_data_1),str(team_data_2),clan_id
                    ]
                )
                # 判断是否需要插入数据
                insert_data_list = []
                old_team_data = {
                    1: eval(clan[2]) if clan[2] else None,
                    2: eval(clan[3]) if clan[3] else None
                }
                new_team_data = {
                    1: team_data_1,
                    2: team_data_2
                }
                for team_number in [1, 2]:
                    if new_team_data[team_number] == None:
                        continue
                    if old_team_data[team_number]:
                        battles = new_team_data[team_number]['battles_count'] - old_team_data[team_number]['battles_count']
                        wins = new_team_data[team_number]['wins_count'] - old_team_data[team_number]['wins_count']
                        if battles > 2 or battles <= 0:
                            continue
                        battle_time = last_battle_time
                        if battles == 1:
                            temp_list = None
                            temp_list = [battle_time, clan_id, region_id, team_number]
                            if wins == 1:
                                temp_list += ['victory']
                            else:
                                temp_list += ['defeat']
                            battle_rating = new_team_data[team_number]['public_rating'] - old_team_data[team_number]['public_rating']
                            if battle_rating > 0:
                                temp_list += ['+'+str(battle_rating)]
                            elif battle_rating < 0:
                                temp_list += [str(battle_rating)]
                            else:
                                temp_list += [None]
                            if (
                                new_team_data[team_number]['stage_type'] and 
                                new_team_data[team_number]['stage_progress'] != None
                            ):
                                if new_team_data[team_number]['stage_progress'][len(new_team_data[team_number]['stage_progress']) - 1] == 1:
                                    temp_list += ['+★']
                                else:
                                    temp_list += ['+☆']
                            else:
                                temp_list += [None]
                            temp_list += [
                                new_team_data[team_number]['league'],
                                new_team_data[team_number]['division'],
                                new_team_data[team_number]['division_rating'],
                                new_team_data[team_number]['public_rating'],
                                new_team_data[team_number]['stage_type'],
                                new_team_data[team_number]['stage_progress']
                            ]
                            insert_data_list.append(temp_list)
                        else:
                            temp_list = [battle_time, clan_id, region_id, team_number]
                            if wins == 2:
                                insert_data_list.append(temp_list+['victory'])
                                insert_data_list.append(temp_list+['victory'])
                            elif wins == 1:
                                insert_data_list.append(temp_list+['victory'])
                                insert_data_list.append(temp_list+['defeat'])
                            else:
                                insert_data_list.append(temp_list+['defeat'])
                                insert_data_list.append(temp_list+['defeat'])
                    else:
                        battles = new_team_data[team_number]['battles_count']
                        wins = new_team_data[team_number]['wins_count']
                        if battles > 2 and battles <= 0:
                            continue
                        battle_time = last_battle_time
                        if battles == 1:
                            temp_list = None
                            temp_list = [battle_time, clan_id, region_id, team_number]
                            if wins == 1:
                                temp_list += ['victory']
                            else:
                                temp_list += ['defeat']
                            temp_list += [
                                None, None,
                                new_team_data[team_number]['league'],
                                new_team_data[team_number]['division'],
                                new_team_data[team_number]['division_rating'],
                                new_team_data[team_number]['public_rating'],
                                new_team_data[team_number]['stage_type'],
                                new_team_data[team_number]['stage_progress']
                            ]
                            insert_data_list.append(temp_list)
                        else:
                            temp_list = [battle_time, clan_id, region_id, team_number]
                            if wins == 2:
                                insert_data_list.append(temp_list+['victory'])
                                insert_data_list.append(temp_list+['victory'])
                            elif wins == 1:
                                insert_data_list.append(temp_list+['victory'])
                                insert_data_list.append(temp_list+['defeat'])
                            else:
                                insert_data_list.append(temp_list+['defeat'])
                                insert_data_list.append(temp_list+['defeat'])
                for insert_data in insert_data_list:
                    if len(insert_data) == 13:
                        await cur.execute(
                            "INSERT INTO kokomi.clan_battle_s%s ( "
                            "battle_time, clan_id, region_id, team_number, battle_result, battle_rating, battle_stage, "
                            "league, division, division_rating, public_rating, stage_type, stage_progress"
                            " ) VALUES ( FROM_UNIXTIME(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s );",
                            [season_number] + insert_data
                        )
                    else:
                        await cur.execute(
                            "INSERT INTO kokomi.clan_battle_s%s ( "
                            "battle_time, clan_id, region_id, team_number, battle_result "
                            " ) VALUES ( FROM_UNIXTIME(%s), %s, %s, %s, %s );",
                            [season_number] + insert_data
                        )
            await conn.commit() 
            return JSONResponse.API_1000_Success
        except Exception as e:
            await conn.rollback()
            raise e
        finally:
            await cur.close()
            await MysqlConnection.release_connection(conn)
    
    @ExceptionLogger.handle_database_exception_async
    async def update_clan_basic(clan_data: dict) -> ResponseDict:
        '''更新user_info表

        更新工会的info数据

        参数:
            clan_data
        
        返回:
            ResponseDict
        '''
        try:
            conn: Connection = await MysqlConnection.get_connection()
            await conn.begin()
            cur: Cursor = await conn.cursor()

            clan_id = clan_data['clan_id']
            region_id = clan_data['region_id']
            await cur.execute(
                "SELECT b.clan_id, b.tag, b.league, UNIX_TIMESTAMP(b.updated_at) AS basic_update_time, "
                "i.is_active, i.season, i.public_rating, i.league, i.division, i.division_rating, "
                "UNIX_TIMESTAMP(i.last_battle_at) AS info_last_battle_time "
                "FROM kokomi.clan_basic AS b "
                "LEFT JOIN kokomi.clan_info AS i ON b.clan_id = i.clan_id "
                "WHERE b.region_id = %s AND b.clan_id = %s;",
                [region_id, clan_id]
            )
            clan = await cur.fetchone()
            if clan == None:
                await conn.commit()
                return JSONResponse.API_1009_ClanNotExistinDatabase
            if clan_data['is_active'] == 0:
                await cur.execute(
                    "UPDATE kokomi.clan_info SET is_active = %s, updated_at = CURRENT_TIMESTAMP WHERE clan_id = %s;",
                    [0, clan_id]
                )
            else:
                current_timestamp = TimeFormat.get_current_timestamp()
                if (
                    not clan[3] or 
                    current_timestamp - clan[3] > 2*24*60*60 or
                    (clan_data['tag'] and clan_data['tag'] != clan[1]) or
                    clan_data['league'] != clan[2]
                ):
                    await cur.execute(
                        "UPDATE kokomi.clan_basic SET tag = %s, league = %s, updated_at = CURRENT_TIMESTAMP "
                        "WHERE region_id = %s AND clan_id = %s;",
                        [clan_data['tag'],clan_data['league'],region_id,clan_id]
                    )
                if (
                    clan_data['season_number'] != clan[5] or
                    clan_data['public_rating'] != clan[6] or
                    clan_data['last_battle_at'] != clan[10]
                ):
                    await cur.execute(
                        "UPDATE kokomi.clan_info SET is_active = %s, season = %s, public_rating = %s, league = %s, "
                        "division = %s, division_rating = %s, last_battle_at = FROM_UNIXTIME(%s) "
                        "WHERE clan_id = %s",
                        [
                            1, clan_data['season_number'], clan_data['public_rating'],clan_data['league'],
                            clan_data['division'], clan_data['division_rating'],clan_data['last_battle_at'],clan_id
                        ]
                    )
            await conn.commit()
            return JSONResponse.API_1000_Success
        except Exception as e:
            await conn.rollback()
            raise e
        finally:
            await cur.close()
            await MysqlConnection.release_connection(conn)

    @ExceptionLogger.handle_database_exception_async
    async def update_clan_info_batch(region_id: int, season_number: int, clan_data_list: list) -> ResponseDict:
        try:
            conn: Connection = await MysqlConnection.get_connection()
            await conn.begin()
            cur: Cursor = await conn.cursor()

            await cur.execute(
                "SELECT season_number FROM kokomi.region_season WHERE region_id = %s;",
                [region_id]
            )
            season_number_in_db = await cur.fetchone()
            if season_number != season_number_in_db[0]:
                # 数据在数据库中，但是赛季更改，直接写入数据
                await cur.execute(
                    "UPDATE kokomi.region_season SET season_number = %s WHERE region_id = %s;",
                    [season_number, region_id]
                )
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
                "FROM kokomi.clan_basic AS b "
                "LEFT JOIN kokomi.clan_info AS i ON b.clan_id = i.clan_id "
                "LEFT JOIN kokomi.clan_season AS s ON b.clan_id = s.clan_id "
                f"WHERE b.region_id = %s AND b.clan_id in ( %s{sql_str} );",
                params
            )
            need_update_clan = []
            clans = await cur.fetchall()
            exists_clans = {}
            current_timestamp = TimeFormat.get_current_timestamp()
            for clan in clans:
                exists_clans[clan[0]] = clan[1:]
            for clan_data in clan_data_list:
                # 批量更新写入数据
                clan_id = clan_data['id']
                if clan_id not in exists_clans:
                    # 用户不存在于数据库中，直接写入
                    await cur.execute(
                        "INSERT INTO kokomi.clan_basic (clan_id, region_id, tag) VALUES (%s, %s, %s);",
                        [clan_id, region_id, clan_data['tag']]
                    )
                    await cur.execute(
                        "INSERT INTO kokomi.clan_info (clan_id) VALUES (%s);",
                        [clan_id]
                    )
                    await cur.execute(
                        "INSERT INTO kokomi.clan_users (clan_id) VALUES (%s);",
                        [clan_id]
                    )
                    await cur.execute(
                        "INSERT INTO kokomi.clan_season (clan_id) VALUES (%s);",
                        [clan_id]
                    )
                    await cur.execute(
                        "UPDATE kokomi.clan_basic SET tag = %s, league = %s WHERE region_id = %s AND clan_id = %s",
                        [clan_data['tag'],clan_data['league'],region_id,clan_id]
                    )
                    await cur.execute(
                        "UPDATE kokomi.clan_info SET is_active = %s, season = %s, public_rating = %s, league = %s, "
                        "division = %s, division_rating = %s, last_battle_at = FROM_UNIXTIME(%s) "
                        "WHERE clan_id = %s",
                        [
                            1,season_number,clan_data['public_rating'],clan_data['league'],clan_data['division'],
                            clan_data['division_rating'],clan_data['last_battle_at'],clan_id
                        ]
                    )
                    need_update_clan.append(clan_id)
                else:
                    # 数据在数据库中，且没有赛季更改，检验数据是否改变再决定是否更新数据
                    if (
                        not exists_clans[clan_id][2] or
                        (current_timestamp - exists_clans[clan_id][2]) > 3*24*60*60 or 
                        clan_data['tag'] != exists_clans[clan_id][0] or 
                        clan_data['league'] != exists_clans[clan_id][1]
                    ):
                        await cur.execute(
                            "UPDATE kokomi.clan_basic SET tag = %s, league = %s, updated_at = CURRENT_TIMESTAMP "
                            "WHERE region_id = %s AND clan_id = %s",
                            [clan_data['tag'],clan_data['league'],region_id,clan_id]
                        )
                    if (
                        season_number != exists_clans[clan_id][4] or
                        clan_data['public_rating'] != exists_clans[clan_id][5] or
                        clan_data['last_battle_at'] != exists_clans[clan_id][9]
                    ):
                        await cur.execute(
                            "UPDATE kokomi.clan_info SET is_active = %s, season = %s, public_rating = %s, league = %s, "
                            "division = %s, division_rating = %s, last_battle_at = FROM_UNIXTIME(%s) "
                            "WHERE clan_id = %s",
                            [
                                1, season_number, clan_data['public_rating'],clan_data['league'],clan_data['division'],
                                clan_data['division_rating'],clan_data['last_battle_at'],clan_id
                            ]
                        )
                    if (
                        exists_clans[clan_id][10] != season_number or
                        not exists_clans[clan_id][9] or
                        not exists_clans[clan_id][11] or
                        exists_clans[clan_id][9] != exists_clans[clan_id][11]
                    ):
                        need_update_clan.append(clan_id)
            await conn.commit()
            return JSONResponse.get_success_response(need_update_clan)
        except Exception as e:
            await conn.rollback()
            raise e
        finally:
            await cur.close()
            await MysqlConnection.release_connection(conn)