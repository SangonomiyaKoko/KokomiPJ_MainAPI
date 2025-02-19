import time
import traceback
import pymysql
from db import DatabaseConnection

from config import settings
from log import log as logger

MAIN_DB = settings.DB_NAME_MAIN
BOT_DB = settings.DB_NAME_BOT
CACHE_DB = settings.DB_NAME_SHIP


def update_clan_info_batch(region_id: int, season_number: int, clan_data_list: list):
    """更新clan_info表中工会赛季信息，同时根据info表和season表的差异判断是否需要进一步更新season表"""
    pool = DatabaseConnection.get_pool()
    conn = pool.connection()
    cur = None
    try:
        conn.begin()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        cur.execute(
            f"SELECT season_number FROM {MAIN_DB}.region_season WHERE region_id = %s;",
            [region_id]
        )
        season_number_in_db = cur.fetchone()
        if season_number != season_number_in_db['season_number']:
            # 数据在数据库中，但是赛季更改，直接写入数据
            cur.execute(
                f"UPDATE {MAIN_DB}.region_season SET season_number = %s WHERE region_id = %s;",
                [season_number, region_id]
            )
        sql_str = ''
        params = [region_id, clan_data_list[0]['id']]
        for clan_data in clan_data_list[1:]:
            sql_str += ', %s'
            params.append(clan_data['id'])
        cur.execute(
            "SELECT b.clan_id, b.tag, b.league AS league_, UNIX_TIMESTAMP(b.updated_at) AS basic_update_time, "
            "i.is_active, i.season, i.public_rating, i.league, i.division, i.division_rating, "
            "UNIX_TIMESTAMP(i.last_battle_at) AS info_last_battle_time, "
            "s.season AS season_, UNIX_TIMESTAMP(s.last_battle_at) AS season_last_battle_time "
            f"FROM {MAIN_DB}.clan_basic AS b "
            f"LEFT JOIN {MAIN_DB}.clan_info AS i ON b.clan_id = i.clan_id "
            f"LEFT JOIN {MAIN_DB}.clan_season AS s ON b.clan_id = s.clan_id "
            f"WHERE b.region_id = %s AND b.clan_id in ( %s{sql_str} );",
            params
        )
        need_update_clan = []
        clans = cur.fetchall()
        exists_clans = {}
        current_timestamp = int(time.time())
        for clan in clans:
            exists_clans[clan['clan_id']] = clan
        for clan_data in clan_data_list:
            # 批量更新写入数据
            clan_id = clan_data['id']
            if clan_id not in exists_clans:
                # 用户不存在于数据库中，直接写入
                cur.execute(
                    f"INSERT INTO {MAIN_DB}.clan_basic (clan_id, region_id, tag) VALUES (%s, %s, %s);",
                    [clan_id, region_id, clan_data['tag']]
                )
                cur.execute(
                    f"INSERT INTO {MAIN_DB}.clan_info (clan_id) VALUES (%s);",
                    [clan_id]
                )
                cur.execute(
                    f"INSERT INTO {MAIN_DB}.clan_users (clan_id) VALUES (%s);",
                    [clan_id]
                )
                cur.execute(
                    f"INSERT INTO {MAIN_DB}.clan_season (clan_id) VALUES (%s);",
                    [clan_id]
                )
                cur.execute(
                    f"UPDATE {MAIN_DB}.clan_basic SET tag = %s, league = %s WHERE region_id = %s AND clan_id = %s",
                    [clan_data['tag'],clan_data['league'],region_id,clan_id]
                )
                cur.execute(
                    f"UPDATE {MAIN_DB}.clan_info SET is_active = %s, season = %s, public_rating = %s, league = %s, "
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
                    not exists_clans[clan_id]['basic_update_time'] or
                    (current_timestamp - exists_clans[clan_id]['basic_update_time']) > 3*24*60*60 or 
                    clan_data['tag'] != exists_clans[clan_id]['tag'] or 
                    clan_data['league'] != exists_clans[clan_id]['league_']
                ):
                    cur.execute(
                        f"UPDATE {MAIN_DB}.clan_basic SET tag = %s, league = %s, updated_at = CURRENT_TIMESTAMP "
                        "WHERE region_id = %s AND clan_id = %s",
                        [clan_data['tag'],clan_data['league'],region_id,clan_id]
                    )
                if (
                    season_number != exists_clans[clan_id]['season'] or
                    clan_data['public_rating'] != exists_clans[clan_id]['public_rating'] or
                    clan_data['last_battle_at'] != exists_clans[clan_id]['info_last_battle_time']
                ):
                    cur.execute(
                        f"UPDATE {MAIN_DB}.clan_info SET is_active = %s, season = %s, public_rating = %s, league = %s, "
                        "division = %s, division_rating = %s, last_battle_at = FROM_UNIXTIME(%s) "
                        "WHERE clan_id = %s",
                        [
                            1, season_number, clan_data['public_rating'],clan_data['league'],clan_data['division'],
                            clan_data['division_rating'],clan_data['last_battle_at'],clan_id
                        ]
                    )
                if (
                    exists_clans[clan_id]['season_'] != season_number or
                    not exists_clans[clan_id]['info_last_battle_time'] or
                    not exists_clans[clan_id]['season_last_battle_time'] or
                    exists_clans[clan_id]['info_last_battle_time'] != exists_clans[clan_id]['season_last_battle_time']
                ):
                    need_update_clan.append(clan_id)
        
        conn.commit()
        return {'status': 'ok','code': 1000,'message': 'Success','data': need_update_clan}
    except Exception as e:
        conn.rollback()
        logger.error(traceback.format_exc())
        return {'status': 'error','code': 3000,'message': 'DatabaseError','data': None}
    finally:
        if cur:
            cur.close()
        conn.close()

def update_clan_basic_and_info(clan_data: dict):
    '''更新clan_info表

    更新工会的info数据

    参数:
        clan_data
    
    返回:
        ResponseDict
    '''
    pool = DatabaseConnection.get_pool()
    conn = pool.connection()
    cur = None
    try:
        conn.begin()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        clan_id = clan_data['clan_id']
        region_id = clan_data['region_id']
        cur.execute(
            "SELECT b.clan_id, b.tag, b.league, UNIX_TIMESTAMP(b.updated_at) AS basic_update_time, "
            "i.is_active, i.season, i.public_rating, i.league, i.division, i.division_rating, "
            "UNIX_TIMESTAMP(i.last_battle_at) AS info_last_battle_time "
            f"FROM {MAIN_DB}.clan_basic AS b "
            f"LEFT JOIN {MAIN_DB}.clan_info AS i ON b.clan_id = i.clan_id "
            "WHERE b.region_id = %s AND b.clan_id = %s;",
            [region_id, clan_id]
        )
        clan = cur.fetchone()
        if clan == None:
            conn.commit()
            return {'status': 'ok','code': 1009,'message': 'ClanNotExistinDatabase','data' : None}
        if clan_data['is_active'] == 0:
            cur.execute(
                f"UPDATE {MAIN_DB}.clan_info SET is_active = %s, updated_at = CURRENT_TIMESTAMP WHERE clan_id = %s;",
                [0, clan_id]
            )
        else:
            current_timestamp = int(time.time())
            if (
                not clan[3] or 
                current_timestamp - clan['basic_update_time'] > 2*24*60*60 or
                (clan_data['tag'] and clan_data['tag'] != clan['b.tag']) or
                clan_data['league'] != clan['b.league']
            ):
                cur.execute(
                    f"UPDATE {MAIN_DB}.clan_basic SET tag = %s, league = %s, updated_at = CURRENT_TIMESTAMP "
                    "WHERE region_id = %s AND clan_id = %s;",
                    [clan_data['tag'],clan_data['league'],region_id,clan_id]
                )
            if (
                clan_data['season_number'] != clan['i.season'] or
                clan_data['public_rating'] != clan['i.public_rating'] or
                clan_data['last_battle_at'] != clan['info_last_battle_time']
            ):
                cur.execute(
                    f"UPDATE {MAIN_DB}.clan_info SET is_active = %s, season = %s, public_rating = %s, league = %s, "
                    "division = %s, division_rating = %s, last_battle_at = FROM_UNIXTIME(%s) "
                    "WHERE clan_id = %s",
                    [
                        1, clan_data['season_number'], clan_data['public_rating'],clan_data['league'],
                        clan_data['division'], clan_data['division_rating'],clan_data['last_battle_at'],clan_id
                    ]
                )
        
        conn.commit()
        return {'status': 'ok', 'code': 1000, 'message': 'Success', 'data': None}
    except Exception as e:
        conn.rollback()
        logger.error(traceback.format_exc())
        return {'status': 'error','code': 3000,'message': 'DatabaseError','data': None}
    finally:
        if cur:
            cur.close()
        conn.close()

def update_clan_season(clan_season: dict):
    pool = DatabaseConnection.get_pool()
    conn = pool.connection()
    cur = None
    try:
        conn.begin()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        clan_id = clan_season['clan_id']
        region_id = clan_season['region_id']
        season_number = clan_season['season_number']
        last_battle_time = clan_season['last_battle_time']
        team_data_1 = clan_season['team_data'][1]
        team_data_2 = clan_season['team_data'][2]
        cur.execute(
            "SELECT season, UNIX_TIMESTAMP(last_battle_at) AS last_battle_time, team_data_1, team_data_2 "
            f"FROM {MAIN_DB}.clan_season WHERE clan_id = %s;",
            [clan_id]
        )
        clan = cur.fetchone()
        if clan == None:
            conn.commit()
            return {'status': 'ok','code': 1009,'message': 'ClanNotExistinDatabase','data' : None}
        if clan['season'] != season_number:
            cur.execute(
                f"UPDATE {MAIN_DB}.clan_season SET season = %s, last_battle_at = FROM_UNIXTIME(%s), "
                "team_data_1 = %s, team_data_2 = %s WHERE clan_id = %s",
                [
                    season_number,last_battle_time, 
                    str(team_data_1),str(team_data_2),clan_id
                ]
            )
            conn.commit()
            return {'status': 'ok','code': 1000,'message': 'Success','data': None}
        if clan['last_battle_time'] != last_battle_time:
            cur.execute(
                f"UPDATE {MAIN_DB}.clan_season SET season = %s, last_battle_at = FROM_UNIXTIME(%s), "
                "team_data_1 = %s, team_data_2 = %s WHERE clan_id = %s",
                [
                    season_number,last_battle_time, 
                    str(team_data_1),str(team_data_2),clan_id
                ]
            )
            # 判断是否需要插入数据
            insert_data_list = []
            old_team_data = {
                1: eval(clan['team_data_1']) if clan['team_data_1'] else None,
                2: eval(clan['team_data_2']) if clan['team_data_2'] else None
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
                            new_team_data[team_number]['stage_progress'] != None and 
                            new_team_data[team_number]['stage_progress'] != '[]'
                        ):
                            stage_progress = eval(new_team_data[team_number]['stage_progress'])
                            if stage_progress[len(stage_progress) - 1] == 1:
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
                    cur.execute(
                        f"INSERT INTO {MAIN_DB}.clan_battle_s%s ( "
                        "battle_time, clan_id, region_id, team_number, battle_result, battle_rating, battle_stage, "
                        "league, division, division_rating, public_rating, stage_type, stage_progress"
                        " ) VALUES ( FROM_UNIXTIME(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s );",
                        [season_number] + insert_data
                    )
                else:
                    cur.execute(
                        f"INSERT INTO {MAIN_DB}.clan_battle_s%s ( "
                        "battle_time, clan_id, region_id, team_number, battle_result "
                        " ) VALUES ( FROM_UNIXTIME(%s), %s, %s, %s, %s );",
                        [season_number] + insert_data
                    )

        conn.commit()
        return {'status': 'ok','code': 1000,'message': 'Success','data': None}
    except Exception as e:
        conn.rollback()
        logger.error(traceback.format_exc())
        return {'status': 'error','code': 3000,'message': 'DatabaseError','data': None}
    finally:
        if cur:
            cur.close()
        conn.close()