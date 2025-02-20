import time
import traceback
import pymysql
from db import DatabaseConnection

from utils import BinaryParserUtils, BinaryGeneratorUtils
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

        cur.execute(
            f"SELECT MAX(id) AS max_id FROM {MAIN_DB}.user_basic;"
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

def get_user_token():
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
            f"FROM {MAIN_DB}.user_token WHERE token_type = 1;"
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

def get_user_cache_batch(offset: int, limit = 1000):
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
            "SELECT b.region_id, b.account_id, i.is_active, i.active_level, UNIX_TIMESTAMP(i.updated_at) AS info_update_time, "
            "s.battles_count, s.hash_value, UNIX_TIMESTAMP(s.updated_at) AS update_time "
            f"FROM {MAIN_DB}.user_basic AS b "
            f"LEFT JOIN {MAIN_DB}.user_info AS i ON i.account_id = b.account_id "
            f"LEFT JOIN {MAIN_DB}.user_ships AS s ON s.account_id = b.account_id "
            "WHERE b.id BETWEEN %s AND %s;", 
            [offset+1, offset+limit]
        )
        rows = cur.fetchall()
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
                    'is_active': row['is_active'],
                    'active_level': row['active_level']
                },
                'user_ships':{
                    'battles_count': row['battles_count'],
                    'hash_value': row['hash_value'],
                    'update_time': row['update_time']
                }
            }
            data.append(user)
        
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

def check_user_basic(user_data: dict):
    '''检查用户数据是否需要更新

    参数:
        user_list [dict]
    '''
    pool = DatabaseConnection.get_pool()
    conn = pool.connection()
    cur = None
    try:
        conn.begin()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        account_id = user_data['account_id']
        region_id = user_data['region_id']
        nickname = user_data['nickname']
        cur.execute(
            "SELECT username, UNIX_TIMESTAMP(updated_at) AS update_time "
            f"FROM {MAIN_DB}.user_basic WHERE region_id = %s and account_id = %s;", 
            [region_id, account_id]
        )
        user = cur.fetchone()
        if not user:
            cur.execute(
                f"INSERT INTO {MAIN_DB}.user_basic (account_id, region_id, username) VALUES (%s, %s, %s);",
                [account_id, region_id, f'User_{account_id}']
            )
            cur.execute(
                f"INSERT INTO {MAIN_DB}.user_info (account_id) VALUES (%s);",
                [account_id]
            )
            cur.execute(
                f"INSERT INTO {MAIN_DB}.user_ships (account_id) VALUES (%s);",
                [account_id]
            )
            cur.execute(
                f"INSERT INTO {MAIN_DB}.user_clan (account_id) VALUES (%s);",
                [account_id]
            )
            cur.execute(
                f"UPDATE {MAIN_DB}.user_basic SET username = %s WHERE region_id = %s AND account_id = %s",
                [nickname, region_id, account_id]
            )
        else:
            # 根据数据库的数据判断用户是否更改名称
            if user['username'] != nickname and user['update_time'] != None:
                cur.execute(
                    f"UPDATE {MAIN_DB}.user_basic SET username = %s WHERE region_id = %s and account_id = %s;", 
                    [nickname, region_id, account_id]
                )
                cur.execute(
                    f"INSERT INTO {MAIN_DB}.user_history (account_id, username, start_time, end_time) VALUES "
                    "(%s, %s, FROM_UNIXTIME(%s), FROM_UNIXTIME(%s));", 
                    [account_id, user['username'], user['update_time'], int(time.time())]
                )
            elif user['update_time'] == None:
                cur.execute(
                    f"UPDATE {MAIN_DB}.user_basic SET username = %s WHERE region_id = %s and account_id = %s;",
                    [nickname, region_id, account_id]
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

def check_user_info(user_data: dict):
    '''检查并更新user_info表

    参数:
        user_list [dict]
    
    '''
    pool = DatabaseConnection.get_pool()
    conn = pool.connection()
    cur = None
    try:
        conn.begin()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        account_id = user_data['account_id']
        cur.execute(
            "SELECT is_active, active_level, is_public, total_battles, UNIX_TIMESTAMP(last_battle_at) AS last_battle_time "
            f"FROM {MAIN_DB}.user_info WHERE account_id = %s;", 
            [account_id]
        )
        user = cur.fetchone()
        if user is None:
            # 正常来说这里不应该会遇到为空问题，因为先检查basic在检查info
            conn.commit()
            return {'status': 'ok','code': 1008,'message': 'UserNotExistinDatabase','data' : None}
        sql_str = ''
        params = []
        for field in ['is_active', 'active_level', 'is_public', 'total_battles', 'last_battle_time']:
            if (user_data[field] != None) and (user_data[field] != user[field]):
                if field != 'last_battle_time':
                    sql_str += f'{field} = %s, '
                    params.append(user_data[field])
                else:
                    if user_data[field] != 0:
                        sql_str += f'last_battle_at = FROM_UNIXTIME(%s), '
                        params.append(user_data[field])
        params = params + [account_id]
        cur.execute(
            f"UPDATE {MAIN_DB}.user_info SET {sql_str}updated_at = CURRENT_TIMESTAMP WHERE account_id = %s;", 
            params
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

def get_user_cache(account_id: int, region_id: int):
    """获取用户的cache缓存"""
    pool = DatabaseConnection.get_pool()
    conn = pool.connection()
    cur = None
    try:
        conn.begin()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        cur.execute(
            "SELECT battles_count, hash_value, ships_data, UNIX_TIMESTAMP(updated_at) AS update_time "
            f"FROM {MAIN_DB}.user_ships WHERE account_id = %s;", 
            [account_id]
        )
        user = cur.fetchone()
        if user is None:
            # 用户不存在
            cur.execute(
                f"INSERT INTO {MAIN_DB}.user_basic (account_id, region_id, username) VALUES (%s, %s, %s);",
                [account_id, region_id, f'User_{account_id}']
            )
            cur.execute(
                f"INSERT INTO {MAIN_DB}.user_info (account_id) VALUES (%s);",
                [account_id]
            )
            cur.execute(
                f"INSERT INTO {MAIN_DB}.user_ships (account_id) VALUES (%s);",
                [account_id]
            )
            cur.execute(
                f"INSERT INTO {MAIN_DB}.user_clan (account_id) VALUES (%s);",
                [account_id]
            )
            data = {
                'battles_count': None,
                'hash_value': None,
                'ships_data': None,
                'update_time': None
            }
        else:
            data = {
                'battles_count': user['battles_count'],
                'hash_value': user['hash_value'],
                'ships_data': BinaryParserUtils.from_user_binary_data_to_dict(user['ships_data']),
                'update_time': user['update_time']
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

def check_existing_ship(ship_id_set: set):
    """检查ship_id是否存在于数据库"""
    pool = DatabaseConnection.get_pool()
    conn = pool.connection()
    cur = None
    try:
        conn.begin()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        cur.execute(
            f"SELECT ship_id FROM {CACHE_DB}.existing_ships"
        )
        not_exists_set = set()
        exists_list = []
        rows = cur.fetchall()
        for row in rows:
            exists_list.append(row['ship_id'])
        for ship_id in ship_id_set:
            if ship_id not in exists_list:
                not_exists_set.add(ship_id)
        for ship_id in not_exists_set:
            cur.execute(
                f'''CREATE TABLE IF NOT EXISTS {CACHE_DB}.ship_%s (
                    id               INT          AUTO_INCREMENT,
                    account_id       BIGINT       NOT NULL,
                    region_id        TINYINT      NOT NULL,
                    battles_count    INT          NOT NULL,
                    battle_type_1    INT          NOT NULL,
                    battle_type_2    INT          NOT NULL,
                    battle_type_3    INT          NOT NULL,
                    wins             INT          NOT NULL,
                    damage_dealt     BIGINT       NOT NULL,
                    frags            INT          NOT NULL,
                    exp              BIGINT       NOT NULL,
                    survived         INT          NOT NULL,
                    scouting_damage  BIGINT       NOT NULL,
                    art_agro         BIGINT       NOT NULL,
                    planes_killed    INT          NOT NULL,
                    max_exp          INT          NOT NULL,
                    max_damage_dealt INT          NOT NULL,
                    max_frags        INT          NOT NULL,
                    created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    PRIMARY KEY (id), 
                    UNIQUE INDEX idx_sid_rid_aid (region_id, account_id)
                );''',
                [ship_id]
            )
            cur.execute(
                f"INSERT INTO {CACHE_DB}.existing_ships ( ship_id ) VALUE ( %s )",
                [ship_id]
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


def update_user_ship(user_data: dict):
    '''检查并更新user_ship表

    参数:
        user_data [dict]
    '''
    pool = DatabaseConnection.get_pool()
    conn = pool.connection()
    cur = None
    try:
        conn.begin()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        
        account_id = user_data['account_id']
        region_id = user_data['region_id']
        delete_ship_list = user_data['delete_ship_list']
        replace_ship_dict = user_data['replace_ship_dict']
        for del_ship_id in delete_ship_list:
            cur.execute(
                f"DELETE FROM {CACHE_DB}.ship_%s "
                "WHERE region_id = %s AND account_id = %s;",
                [int(del_ship_id), region_id, account_id]
            )
        for update_ship_id, ship_data in replace_ship_dict.items():
            cur.execute(
                f"UPDATE {CACHE_DB}.ship_%s SET battles_count = %s, battle_type_1 = %s, battle_type_2 = %s, battle_type_3 = %s, wins = %s, "
                "damage_dealt = %s, frags = %s, exp = %s, survived = %s, scouting_damage = %s, art_agro = %s, "
                "planes_killed = %s, max_exp = %s, max_damage_dealt = %s, max_frags = %s "
                "WHERE region_id = %s AND account_id = %s;",
                [int(update_ship_id)] + ship_data + [region_id, account_id]
            )
            cur.execute(
                f"INSERT INTO {CACHE_DB}.ship_%s (account_id, region_id, battles_count, battle_type_1, battle_type_2, "
                "battle_type_3, wins, damage_dealt, frags, exp, survived, scouting_damage, art_agro, planes_killed, "
                "max_exp, max_damage_dealt, max_frags) "
                "SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s "
                f"WHERE NOT EXISTS (SELECT 1 FROM {CACHE_DB}.ship_%s WHERE region_id = %s AND account_id = %s);",
                [int(update_ship_id)] + [account_id, region_id] + ship_data + [int(update_ship_id)] + [region_id, account_id]
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


def update_user_ships(user_data: dict):
    '''检查并更新user_ships表

    参数:
        user_data [dict]
    '''
    pool = DatabaseConnection.get_pool()
    conn = pool.connection()
    cur = None
    try:
        conn.begin()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        
        account_id = user_data['account_id']
        if user_data['hash_value']:
            cur.execute(
                f"UPDATE {MAIN_DB}.user_ships "
                "SET battles_count = %s, hash_value = %s, ships_data = %s, updated_at = CURRENT_TIMESTAMP "
                "WHERE account_id = %s;", 
                [
                    user_data['battles_count'], 
                    user_data['hash_value'], 
                    BinaryGeneratorUtils.to_user_binary_data_from_dict(user_data['ships_data']), 
                    account_id
                ]
            )
        else:
            cur.execute(
                f"UPDATE {MAIN_DB}.user_ships "
                "SET battles_count = %s, updated_at = CURRENT_TIMESTAMP "
                "WHERE account_id = %s;", 
                [user_data['battles_count'], account_id]
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