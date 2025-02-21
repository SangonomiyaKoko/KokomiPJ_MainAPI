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