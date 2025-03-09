import time
import traceback
import pymysql
from db import DatabaseConnection

from config import settings
from log import log as logger

MAIN_DB = settings.DB_NAME_MAIN
BOT_DB = settings.DB_NAME_BOT
CACHE_DB = settings.DB_NAME_SHIP


def get_user_token(region_id: int):
    """获取所有的用户token"""
    pool = DatabaseConnection.get_pool()
    conn = pool.connection()
    cur = None
    try:
        conn.begin()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        data = {}
        cur.execute(
            "SELECT account_id, region_id, token_value "
            f"FROM {MAIN_DB}.user_token WHERE token_type = 1 AND region_id = %s;",
            [region_id]
        )
        rows = cur.fetchall()
        for row in rows:
            data[str(row['region_id'])+str(row['account_id'])] = row['token_value']
        
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

def get_recent_users(region_id: int):
    """获取存在的船只id列表"""
    pool = DatabaseConnection.get_pool()
    conn = pool.connection()
    cur = None
    try:
        conn.begin()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        data = []
        cur.execute(
            "SELECT account_id, region_id "
            f"FROM {MAIN_DB}.recent WHERE region_id = %s;",
            [region_id]
        )
        rows = cur.fetchall()
        for row in rows:
            data.append(row['account_id'])
        
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

def get_user_info(account_id: int, region_id: int):
    """获取用户的"""
    pool = DatabaseConnection.get_pool()
    conn = pool.connection()
    cur = None
    try:
        conn.begin()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        data = {
            'account_id': None,
            'region_id': None,
            'info': None
        }
        cur.execute(
            "SELECT b.account_id, b.region_id, i.is_active, i.active_level, i.is_public, i.total_battles, "
            "UNIX_TIMESTAMP(i.last_battle_at) AS last_battle_time, UNIX_TIMESTAMP(i.updated_at) AS update_time "
            f"FROM {MAIN_DB}.user_basic as b "
            f"LEFT JOIN {MAIN_DB}.user_info as i ON i.account_id = b.account_id "
            "WHERE b.region_id = %s AND b.account_id = %s;",
            [region_id, account_id]
        )
        row = cur.fetchone()
        if not row:
            return {'status': 'ok','code': 1000,'message': 'Success','data': None}
        data['account_id'] = row['account_id']
        data['region_id'] = row['region_id']
        data['info'] = {
            'is_active': row['is_active'],
            'active_level': row['active_level'],
            'is_public': row['is_public'],
            'total_battles': row['total_battles'],
            'last_battle_time': row['last_battle_time'],
            'update_time': row['update_time']
        }

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

def get_user_recent(account_id: int, region_id: int):
    """获取用户的"""
    pool = DatabaseConnection.get_pool()
    conn = pool.connection()
    cur = None
    try:
        conn.begin()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        data = {
            'account_id': None,
            'region_id': None,
            'info': None,
            'recent': None
        }
        cur.execute(
            "SELECT b.account_id, b.region_id, i.is_active, i.active_level, i.is_public, i.total_battles, "
            "UNIX_TIMESTAMP(i.last_battle_at) AS last_battle_time, UNIX_TIMESTAMP(i.updated_at) AS update_time, r.recent_class, "
            "UNIX_TIMESTAMP(r.last_query_at) AS last_query_time, UNIX_TIMESTAMP(r.last_update_at) AS recent_update_time "
            f"FROM {MAIN_DB}.user_basic AS b LEFT JOIN {MAIN_DB}.user_info AS i ON i.account_id = b.account_id "
            f"LEFT JOIN {MAIN_DB}.recent AS r ON r.region_id = b.region_id AND r.account_id = b.account_id "
            "WHERE b.region_id = %s AND b.account_id = %s;",
            [region_id, account_id]
        )
        row = cur.fetchone()
        if not row:
            return {'status': 'ok','code': 1000,'message': 'Success','data': None}
        data['account_id'] = row['account_id']
        data['region_id'] = row['region_id']
        data['info'] = {
            'is_active': row['is_active'],
            'active_level': row['active_level'],
            'is_public': row['is_public'],
            'total_battles': row['total_battles'],
            'last_battle_time': row['last_battle_time'],
            'update_time': row['update_time']
        }
        data['recent'] = {
            'recent_class': row['recent_class'],
            'last_query_time': row['last_query_time'],
            'last_update_time': row['recent_update_time']
        }

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

def delete_user_recent(region_id: int, account_id: int):
    pool = DatabaseConnection.get_pool()
    conn = pool.connection()
    cur = None
    try:
        conn.begin()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        cur.execute(
            f"DELETE FROM {MAIN_DB}.rececnt WHERE region_id = %s AND account_id = %s;",
            [region_id, account_id]
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

def update_user_recent(region_id: int, account_id: int, recent_class: int = None, last_update_time: int = None):
    pool = DatabaseConnection.get_pool()
    conn = pool.connection()
    cur = None
    try:
        conn.begin()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        if recent_class:
            cur.execute(
                f"UPDATE {MAIN_DB}.recent SET recent_class = %s "
                "WHERE region_id = %s AND account_id = %s;",
                [recent_class, region_id, account_id]
            )
        if last_update_time:
            cur.execute(
                f"UPDATE {MAIN_DB}.recent SET last_update_at = FROM_UNIXTIME(%s) "
                "WHERE region_id = %s AND account_id = %s;",
                [last_update_time, region_id, account_id]
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
