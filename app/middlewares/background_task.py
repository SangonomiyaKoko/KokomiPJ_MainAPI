import time

import pymysql
from dbutils.pooled_db import PooledDB

from app.response import JSONResponse
from app.log import ExceptionLogger
from app.utils import UtilityFunctions


@ExceptionLogger.handle_database_exception_sync
def check_user_basic(pool: PooledDB, user_data: dict):
    '''检查用户数据是否需要更新

    参数:
        user_list [dict]
    '''
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
            "FROM user_basic WHERE region_id = %s and account_id = %s;", 
            [region_id, account_id]
        )
        user = cur.fetchone()
        if not user:
            cur.execute(
                "INSERT INTO user_basic (account_id, region_id, username) VALUES (%s, %s, %s);",
                [account_id, region_id, UtilityFunctions.get_user_default_name(account_id)]
            )
            cur.execute(
                "INSERT INTO user_info (account_id) VALUES (%s);",
                [account_id]
            )
            cur.execute(
                "INSERT INTO user_ships (account_id) VALUES (%s);",
                [account_id]
            )
            cur.execute(
                "INSERT INTO user_clan (account_id) VALUES (%s);",
                [account_id]
            )
            cur.execute(
                "UPDATE user_basic SET username = %s WHERE region_id = %s AND account_id = %s",
                [nickname, region_id, account_id]
            )
        else:
            # 根据数据库的数据判断用户是否更改名称
            if user['username'] != nickname and user['update_time'] != None:
                cur.execute(
                    "UPDATE user_basic SET username = %s WHERE region_id = %s and account_id = %s;", 
                    [nickname, region_id, account_id]
                )
                cur.execute(
                    "INSERT INTO user_history (account_id, username, start_time, end_time) VALUES (%s, %s, %s, %s);", 
                    [account_id, user['username'], user['update_time'], int(time.time())]
                )
            elif user['username'] != nickname and user['update_time'] == None:
                cur.execute(
                    "UPDATE user_basic SET username = %s WHERE region_id = %s and account_id = %s;",
                    [nickname, region_id, account_id]
                )
        conn.commit()
        return JSONResponse.API_1000_Success
    except Exception as e:
        raise e
    finally:
        if cur:
            cur.close()
        conn.close()  # 归还连接到连接池

@ExceptionLogger.handle_database_exception_sync
def check_clan_basic(pool: PooledDB, clan_data: dict):
    '''检查clan_basic是否需要更新

    参数：
        clan_list [clan_id,region_id,tag,league]
    '''
    conn = pool.connection()
    cur = None
    try:
        cur = conn.cursor(pymysql.cursors.DictCursor)
        clan_id = clan_data['clan_id']
        region_id = clan_data['region_id']
        tag = clan_data['tag']
        league = clan_data['league']
        cur.execute(
            "SELECT tag, league FROM clan_basic WHERE region_id = %s and clan_id = %s;", 
            [region_id, clan_id]
        )
        clan = cur.fetchone()
        conn.begin()
        if clan is None:
            # 工会不存在，插入新数据
            cur.execute(
                "INSERT INTO clan_basic (clan_id, region_id, tag, league) VALUES (%s, %s, %s, %s);", 
                [clan_id, region_id, UtilityFunctions.get_clan_default_name(), 5]
            )
            cur.execute(
                "INSERT INTO clan_info (clan_id) VALUES (%s);", 
                [clan_id]
            )
            cur.execute(
                "INSERT INTO clan_users (clan_id) VALUES (%s);", 
                [clan_id]
            )
            cur.execute(
                "INSERT INTO clan_season (clan_id) VALUES (%s);", 
                [clan_id]
            )
            cur.execute(
                "UPDATE clan_basic SET tag = %s, league = %s WHERE region_id = %s and clan_id = %s;",
                [tag, league, region_id, clan_id]
            )
        else:
            cur.execute(
                "UPDATE clan_basic SET tag = %s, league = %s WHERE region_id = %s and clan_id = %s;",
                [tag, league, region_id, clan_id]
            )
        conn.commit()
        return JSONResponse.API_1000_Success
    except Exception as e:
        raise e
    finally:
        if cur:
            cur.close()
        conn.close()  # 归还连接到连接池

@ExceptionLogger.handle_database_exception_sync
def check_user_info(pool: PooledDB, user_data: dict):
    '''检查并更新user_info表

    参数:
        user_list [dict]
    
    '''
    conn = pool.connection()
    cur = None
    try:
        conn.begin()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        account_id = user_data['account_id']
        cur.execute(
            "SELECT is_active, active_level, is_public, total_battles, last_battle_time FROM user_info WHERE account_id = %s;", 
            [account_id]
        )
        user = cur.fetchone()
        if user is None:
            # 正常来说这里不应该会遇到为空问题，因为先检查basic在检查info
            return JSONResponse.API_1008_UserNotExistinDatabase
        sql_str = ''
        params = []
        for field in ['is_active', 'active_level', 'is_public', 'total_battles', 'last_battle_time']:
            if (user_data[field] != None) and (user_data[field] != user[field]):
                sql_str += f'{field} = %s, '
                params.append(user_data[field])
        params = params + [account_id]
        cur.execute(
            f"UPDATE user_info SET {sql_str}updated_at = CURRENT_TIMESTAMP WHERE account_id = %s;", 
            params
        )
        conn.commit()
        return JSONResponse.API_1000_Success
    except Exception as e:
        raise e
    finally:
        if cur:
            cur.close()
        conn.close()  # 归还连接到连接池

@ExceptionLogger.handle_database_exception_sync
def check_user_recent(pool: PooledDB, user_data: dict):
    '''检查并更新recent表

    参数:
        user_data [dict]
    '''
    conn = pool.connection()
    cur = None
    try:
        cur = conn.cursor(pymysql.cursors.DictCursor)
        account_id = user_data['account_id']
        region_id = user_data['region_id']
        cur.execute(
            "SELECT recent_class, last_update_time "
            "FROM recent WHERE region_id = %s and account_id = %s;", 
            [region_id, account_id]
        )
        user = cur.fetchone()
        if user == None:
            return JSONResponse.API_1000_Success
        conn.begin()
        if user_data['recent_class'] and user['recent_class'] != user_data['recent_class']:
            cur.execute(
                "UPDATE recent SET recent_class = %s WHERE region_id = %s and account_id = %s;",
                [user_data['recent_class'], region_id, account_id]
            )
        if user_data['last_update_time'] and user['last_update_time'] > user_data['last_update_time']:
            cur.execute(
                "UPDATE recent SET last_update_time = %s WHERE region_id = %s and account_id = %s;",
                [user_data['last_update_time'], region_id, account_id]
            )
        conn.commit()
        return JSONResponse.API_1000_Success
    except Exception as e:
        raise e
    finally:
        if cur:
            cur.close()
        conn.close()  # 归还连接到连接池

@ExceptionLogger.handle_database_exception_sync
def check_user_ships(pool: PooledDB, user_data: dict):
    '''检查并更新user_ships和user_ship表

    参数:
        user_data [dict]
    '''
    conn = pool.connection()
    cur = None
    try:
        account_id = user_data['account_id']
        region_id = user_data['region_id']
        conn.begin()
        for del_ship_id in user_data['delete_ship_list']:
            table_name = f'user_ship_0{del_ship_id % 10}'
            cur.execute(
                "DELETE FROM %s "
                "WHERE ship_id = %s and region_id = %s and account_id = %s;",
                [table_name, del_ship_id, region_id, account_id]
            )
        for update_ship_id, ship_data in user_data['replace_ship_dict'].items():
            table_name = f'user_ship_0{update_ship_id % 10}'
            cur.execute(
                "UPDATE %s SET battles_count = %s, battle_type_1 = %s, battle_type_2 = %s, battle_type_3 = %s, wins = %s, "
                "damage_dealt = %s, frags = %s, exp = %s, survived = %s, scouting_damage = %s, art_agro = %s, "
                "planes_killed = %s, max_exp = %s, max_damage_dealt = %s, max_frags = %s"
                "WHERE ship_id = %s and region_id = %s and account_id = %s;",
                [table_name] + ship_data + [update_ship_id, region_id, account_id]
            )
            cur.execute(
                "INSERT INTO %s (ship_id, region_id, account_id, battles_count, battle_type_1, battle_type_2, "
                "battle_type_3, wins, damage_dealt, frags, exp, survived, scouting_damage, art_agro, planes_killed, "
                "max_exp, max_damage_dealt, max_frags) "
                "SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s "
                "WHERE NOT EXISTS (SELECT 1 FROM %s WHERE ship_id = %s and region_id = %s and account_id = %s);",
                [table_name] + [update_ship_id, region_id, account_id] + ship_data + [table_name] + [update_ship_id, region_id, account_id]
            )
        if user_data['hash_value']:
            cur.execute(
                "UPDATE user_ships "
                "SET battles_count = %s, hash_value = %s, ships_data = %s "
                "WHERE account_id = %s;", 
                [user_data['battles_count'], user_data['hash_value'], user_data['ships_data'], account_id]
            )
        else:
            cur.execute(
                "UPDATE user_ships "
                "SET battles_count = %s "
                "WHERE account_id = %s;", 
                [user_data['battles_count'], account_id]
            )
        conn.commit()
        return JSONResponse.API_1000_Success
    except Exception as e:
        raise e
    finally:
        if cur:
            cur.close()
        conn.close()  # 归还连接到连接池

@ExceptionLogger.handle_database_exception_sync
def update_user_clan(pool: PooledDB, user_data: dict):
    '''更新user_clan表

    此函数不能用来批量更新数据

    参数：
        user_clan_list [account_id,clan_id]
    '''
    conn = pool.connection()
    cur = None
    try:
        cur = conn.cursor(pymysql.cursors.DictCursor)
        account_id = user_data['account_id']
        clan_id = user_data['clan_id']
        conn.begin()
        cur.execute(
            "UPDATE user_clan SET clan_id = %s WHERE account_id = %s;",
            [clan_id, account_id]
        )
        conn.commit()
        return JSONResponse.API_1000_Success
    except Exception as e:
        raise e
    finally:
        if cur:
            cur.close()
        conn.close()  # 归还连接到连接池