import time
import pymysql
import traceback
from db import DatabaseConnection

from config import settings
from log import log as logger
from utils import BinaryGeneratorUtils, BinaryParserUtils

MAIN_DB = settings.DB_NAME_MAIN
BOT_DB = settings.DB_NAME_BOT
CACHE_DB = settings.DB_NAME_SHIP


def get_clan_max_number():
    '''获取工会表中id参数最大值'''
    pool = DatabaseConnection.get_pool()
    conn = pool.connection()
    cur = None
    try:
        conn.begin()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        
        cur.execute(
            f"SELECT MAX(id) AS max_id FROM {MAIN_DB}.clan_basic;"
        )
        data = cur.fetchone()
        
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


def get_clan_cache_batch(offset: int, limit = 1000):
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
            "SELECT b.clan_id, b.region_id, i.is_active, UNIX_TIMESTAMP(i.updated_at) AS info_update_time, "
            "u.hash_value, UNIX_TIMESTAMP(u.updated_at) AS users_update_time "
            f"FROM {MAIN_DB}.clan_basic AS b "
            f"LEFT JOIN {MAIN_DB}.clan_info AS i ON b.clan_id = i.clan_id "
            f"LEFT JOIN {MAIN_DB}.clan_users AS u ON b.clan_id = u.clan_id "
            "WHERE b.id BETWEEN %s AND %s;", 
            [offset + 1, offset + limit]
        )
        rows = cur.fetchall()
        for row in rows:
            # 排除已注销账号的数据，避免浪费服务器资源
            if row['info_update_time'] and not row['is_active']:
                continue
            user = {
                'clan_basic': {
                    'region_id': row['region_id'],
                    'clan_id': row['clan_id']
                },
                'clan_info': {
                    'is_active': row['is_active'],
                    'update_time': row['info_update_time']
                },
                'clan_users':{
                    'hash_value': row['hash_value'],
                    'update_time': row['users_update_time']
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

def check_and_insert_missing_users(users: list):
    '''检查并插入缺失的用户id

    只支持同一服务器下的用户
    
    参数:
        user: [{...}]
    '''
    pool = DatabaseConnection.get_pool()
    conn = pool.connection()
    cur = None
    try:
        conn.begin()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        sql_str = ''
        params = [users[0][1],users[0][0]]
        for user in users[1:]:
            sql_str += ', %s'
            params.append(user[0])
        cur.execute(
            "SELECT account_id, username, UNIX_TIMESTAMP(updated_at) AS update_time "
            f"FROM {MAIN_DB}.user_basic WHERE region_id = %s AND account_id in ( %s{sql_str} );",
            params
        )
        exists_users = {}
        rows = cur.fetchall()
        for row in rows:
            exists_users[row['account_id']] = [row['username'],row['update_time']]
        for user in users:
            account_id = user[0]
            region_id = user[1]
            nickname = user[2]
            if account_id not in exists_users:
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
                if exists_users[account_id][1] == None:
                    cur.execute(
                        f"UPDATE {MAIN_DB}.user_basic SET username = %s WHERE region_id = %s AND account_id = %s",
                        [nickname, region_id, account_id]
                    )
                elif nickname != exists_users[account_id][0]:
                    cur.execute(
                        f"UPDATE {MAIN_DB}.user_basic SET username = %s WHERE region_id = %s and account_id = %s;", 
                        [nickname, region_id, account_id]
                    ) 
                    cur.execute(
                        f"INSERT INTO {MAIN_DB}.user_history (account_id, username, start_time, end_time) "
                        "VALUES (%s, %s, FROM_UNIXTIME(%s), FROM_UNIXTIME(%s));", 
                        [account_id, exists_users[account_id][0], exists_users[account_id][1], int(time.time())]
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

def update_clan_users(clan_id: int, hash_value: str, user_data: list):
    '''更新clan_users表'''
    pool = DatabaseConnection.get_pool()
    conn = pool.connection()
    cur = None
    try:
        conn.begin()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        cur.execute(
            "SELECT hash_value, users_data, users_data, UNIX_TIMESTAMP(updated_at) AS update_time "
            f"FROM {MAIN_DB}.clan_users WHERE clan_id = %s;", 
            [clan_id]
        )
        clan = cur.fetchone()
        if clan is None:
            conn.commit()
            return {'status': 'ok','code': 1009,'message': 'ClanNotExistinDatabase','data' : None}
        # 判断是否有工会人员变动
        join_user_list = []
        leave_user_list = []
        if clan['update_time'] and clan['hash_value'] != hash_value:
            old_user_list = BinaryParserUtils.from_clan_binary_data_to_list(clan['users_data'])
            for account_id in user_data:
                if account_id not in old_user_list:
                    join_user_list.append(account_id)
            for account_id in old_user_list:
                if account_id not in user_data:
                    leave_user_list.append(account_id)
        cur.execute(
            f"UPDATE {MAIN_DB}.clan_users "
            "SET hash_value = %s, users_data = %s, updated_at = CURRENT_TIMESTAMP "
            "WHERE clan_id = %s",
            [hash_value, BinaryGeneratorUtils.to_clan_binary_data_from_list(user_data),clan_id]
        )
        for account_id in join_user_list:
            cur.execute(
                f"INSERT INTO {MAIN_DB}.clan_history (account_id, clan_id, action_type) VALUES (%s, %s, %s);",
                [account_id, clan_id, 1]
            )
        for account_id in leave_user_list:
            cur.execute(
                f"INSERT INTO {MAIN_DB}.clan_history (account_id, clan_id, action_type) VALUES (%s, %s, %s);",
                [account_id, clan_id, 2]
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

def update_users_clan(clan_id: int, user_data: list):
    '''更新user_clan表'''
    pool = DatabaseConnection.get_pool()
    conn = pool.connection()
    cur = None
    try:
        conn.begin()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        sql_str = ''
        params = []
        for aid in user_data[1:]:
            sql_str += ', %s'
            params.append(aid)
        cur.execute(
            f"UPDATE {MAIN_DB}.user_clan "
            "SET clan_id = %s, updated_at = CURRENT_TIMESTAMP "
            f"WHERE account_id IN ( %s{sql_str} );", 
            [clan_id] + [user_data[0]] + params
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