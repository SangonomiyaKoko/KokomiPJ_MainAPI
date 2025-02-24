import time
import traceback
import pymysql
from db import DatabaseConnection

from config import settings
from log import log as logger

MAIN_DB = settings.DB_NAME_MAIN
BOT_DB = settings.DB_NAME_BOT
CACHE_DB = settings.DB_NAME_SHIP


def get_ship_list():
    """获取存在的船只id列表"""
    pool = DatabaseConnection.get_pool()
    conn = pool.connection()
    cur = None
    try:
        conn.begin()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        cur.execute(
            f"SELECT ship_id FROM {CACHE_DB}.existing_ships"
        )
        data = []
        rows = cur.fetchall()
        for row in rows:
            data.append(row['ship_id'])
        
        conn.commit()
        return {'status': 'ok','code': 1000,'message': 'Success','data': data}
    except Exception:
        conn.rollback()
        logger.error(traceback.format_exc())
        return {'status': 'error','code': 3000,'message': 'DatabaseError','data': None}
    finally:
        if cur:
            cur.close()
        conn.close()

def get_game_version():
    """从数据库中读取当前的版本，主要是用于接口维护的时候"""
    pool = DatabaseConnection.get_pool()
    conn = pool.connection()
    cur = None
    try:
        conn.begin()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        cur.execute(
            f"SELECT region_id, game_version, UNIX_TIMESTAMP(version_start) AS start_time FROM {MAIN_DB}.region_version;"
        )
        rows = cur.fetchall()
        data = {}
        for row in rows:
            data[row['region_id']] = [row['game_version'], row['start_time']]
        
        conn.commit()
        return {'status': 'ok','code': 1000,'message': 'Success','data': data}
    except Exception:
        conn.rollback()
        logger.error(traceback.format_exc())
        return {'status': 'error','code': 3000,'message': 'DatabaseError','data': None}
    finally:
        if cur:
            cur.close()
        conn.close()

def update_game_version(region_id: int, game_version: str):
    pool = DatabaseConnection.get_pool()
    conn = pool.connection()
    cur = None
    try:
        conn.begin()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        version = ".".join(game_version.split(".")[:2])
        cur.execute(
            f"SELECT game_version FROM {MAIN_DB}.region_version WHERE region_id = %s;",
            [region_id]
        )
        row = cur.fetchone()
        if row['game_version'] != version:
            cur.execute(
                f"UPDATE {MAIN_DB}.region_version SET game_version = %s, "
                "version_start = CURRENT_TIMESTAMP, full_version = %s WHERE region_id = %s;",
                [version, game_version, region_id]
            )
        else:
            cur.execute(
                f"UPDATE {MAIN_DB}.region_version SET full_version = %s WHERE region_id = %s;",
                [game_version, region_id]
            )
        
        conn.commit()
        return {'status': 'ok','code': 1000,'message': 'Success','data': None}
    except Exception:
        conn.rollback()
        logger.error(traceback.format_exc())
        return {'status': 'error','code': 3000,'message': 'DatabaseError','data': None}
    finally:
        if cur:
            cur.close()
        conn.close()


def get_ship_max_number(ship_id: int):
    '''获取数据库中id的最大值

    获取id的最大值，用于数据库遍历更新时确定边界

    参数:
        - ship_id
    '''
    pool = DatabaseConnection.get_pool()
    conn = pool.connection()
    cur = None
    try:
        conn.begin()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        cur.execute(
            f"SELECT MAX(id) AS max_id FROM {CACHE_DB}.ship_{ship_id};"
        )
        data = cur.fetchone()
        
        conn.commit()
        return {'status': 'ok','code': 1000,'message': 'Success','data': data}
    except Exception:
        conn.rollback()
        logger.error(traceback.format_exc())
        return {'status': 'error','code': 3000,'message': 'DatabaseError','data': None}
    finally:
        if cur:
            cur.close()
        conn.close()

def get_cache_batch(ship_id: int, offset: int, limit = 1000):
    '''批量获取用户缓存的数据

    获取用户缓存数据，用于缓存的更新

    参数:
        offset: 从哪个id开始读取
        limit: 每次读取多少条数据
    '''
    pool = DatabaseConnection.get_pool()
    conn = pool.connection()
    cur = None
    try:
        conn.begin()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        data = []
        cur.execute(
            "SELECT account_id, region_id, battles_count, battle_type_1, battle_type_2, "
            "battle_type_3, wins, damage_dealt, frags, exp, survived, scouting_damage, "
            "art_agro, planes_killed, max_exp, max_damage_dealt, max_frags "
            f"FROM {CACHE_DB}.ship_%s "
            "WHERE id BETWEEN %s AND %s;", 
            [ship_id, offset+1, offset+limit]
        )
        data = cur.fetchall()
        
        conn.commit()
        return {'status': 'ok','code': 1000,'message': 'Success','data': data}
    except Exception:
        conn.rollback()
        logger.error(traceback.format_exc())
        return {'status': 'error','code': 3000,'message': 'DatabaseError','data': None}
    finally:
        if cur:
            cur.close()
        conn.close()

def get_user_name(user_list: list):
    pool = DatabaseConnection.get_pool()
    conn = pool.connection()
    cur = None
    try:
        conn.begin()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        data = {}
        i = 0
        limit = 1000
        while user_list[i: i + limit] != []:
            region_list = []
            id_list = []
            for user in user_list[i: i + limit]:
                region_list.append(user[0])
                id_list.append(user[1])
            region_ids_str = ', '.join(map(str, region_list))
            id_ids_str = ', '.join(map(str, id_list))
            cur.execute(
                f"SELECT b.account_id, b.region_id, i.active_level, b.username, c.clan_id FROM {MAIN_DB}.user_basic AS b "
                F"LEFT JOIN {MAIN_DB}.user_info AS i ON b.account_id = i.account_id "
                f"LEFT JOIN {MAIN_DB}.user_clan AS c ON b.account_id = c.account_id "
                f"WHERE b.region_id IN ({region_ids_str}) AND b.account_id IN ({id_ids_str});"
            )
            rows = cur.fetchall()
            for row in rows:
                data[row['account_id']] = [row['username'], row['region_id'], row['clan_id'], row['active_level']]
            i += limit
        
        conn.commit()
        return {'status': 'ok','code': 1000,'message': 'Success','data': data}
    except Exception:
        conn.rollback()
        logger.error(traceback.format_exc())
        return {'status': 'error','code': 3000,'message': 'DatabaseError','data': None}
    finally:
        if cur:
            cur.close()
        conn.close()

def get_clan_tag(clan_list: list):
    pool = DatabaseConnection.get_pool()
    conn = pool.connection()
    cur = None
    try:
        conn.begin()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        data = {}
        i = 0
        limit = 1000
        while clan_list[i: i + limit] != []:
            region_list = []
            id_list = []
            for user in clan_list[i: i + limit]:
                region_list.append(user[0])
                id_list.append(user[1])
            region_ids_str = ', '.join(map(str, region_list))
            id_ids_str = ', '.join(map(str, id_list))
            cur.execute(
                f"SELECT clan_id, tag, league FROM {MAIN_DB}.clan_basic "
                f"WHERE region_id IN ({region_ids_str}) AND clan_id IN ({id_ids_str});"
            )
            rows = cur.fetchall()
            for row in rows:
                data[row['clan_id']] = [row['tag'], row['league']]
            i += limit
        
        conn.commit()
        return {'status': 'ok','code': 1000,'message': 'Success','data': data}
    except Exception:
        conn.rollback()
        logger.error(traceback.format_exc())
        return {'status': 'error','code': 3000,'message': 'DatabaseError','data': None}
    finally:
        if cur:
            cur.close()
        conn.close()
