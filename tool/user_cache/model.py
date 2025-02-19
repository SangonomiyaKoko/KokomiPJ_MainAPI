import time
import traceback
import pymysql
from db import DatabaseConnection

from config import settings
from log import log as logger

MAIN_DB = settings.DB_NAME_MAIN
BOT_DB = settings.DB_NAME_BOT
CACHE_DB = settings.DB_NAME_SHIP


async def get_user_max_number():
    '''获取数据库中id的最大值

    获取id的最大值，用于数据库遍历更新时确定边界

    参数:
        - None
    '''
    pool = DatabaseConnection.get_pool()
    conn = pool.connection()
    cur = None
    try:
        conn.begin()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        await cur.execute(
            f"SELECT MAX(id) AS max_id FROM {MAIN_DB}.user_basic;"
        )
        data = await cur.fetchone()
        
        conn.commit()
        return {'status': 'ok','code': 1000,'message': 'Success','data': data}
    except Exception as e:
        conn.rollback()
        logger.error(traceback.format_exc())
        return {'status': 'error','code': 3000,'message': 'DatabaseError','data': None}
    finally:
        if cur:
            cur.close()
        conn.close()


async def get_user_cache_batch(offset: int, limit = 1000):
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
        await cur.execute(
            "SELECT b.region_id, b.account_id, i.is_active, i.active_level, UNIX_TIMESTAMP(i.updated_at) AS info_update_time, "
            "s.battles_count, s.hash_value, UNIX_TIMESTAMP(s.updated_at) AS update_time "
            f"FROM {MAIN_DB}.user_basic AS b "
            f"LEFT JOIN {MAIN_DB}.user_info AS i ON i.account_id = b.account_id "
            f"LEFT JOIN {MAIN_DB}.user_ships AS s ON s.account_id = b.account_id "
            "WHERE b.id BETWEEN %s AND %s;", 
            [offset+1, offset+limit]
        )
        rows = await cur.fetchall()
        for row in rows:
            # 排除已注销账号的数据，避免浪费服务器资源
            if row['info_update_time'] and not row['is_active']:
                continue
            user = {
                'user_basic': {
                    'region_id': row['region_id'],
                    'account_id': row['account_id'],
                    'ac_value': None
                },
                'user_info': {
                    'is_active': row[2],
                    'active_level': row[3]
                },
                'user_ships':{
                    'battles_count': row[5],
                    'hash_value': row[6],
                    'update_time': row[7]
                }
            }
            data.append(user)
        
        conn.commit()
        return {'status': 'ok','code': 1000,'message': 'Success','data': data}
    except Exception as e:
        conn.rollback()
        logger.error(traceback.format_exc())
        return {'status': 'error','code': 3000,'message': 'DatabaseError','data': None}
    finally:
        if cur:
            cur.close()
        conn.close()