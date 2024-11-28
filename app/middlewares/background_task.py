import time

import pymysql
from dbutils.pooled_db import PooledDB

from app.response import JSONResponse
from app.log import ExceptionLogger
from app.utils import UtilityFunctions, BinaryGeneratorUtils, BinaryParserUtils


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
            "FROM kokomi.user_basic WHERE region_id = %s and account_id = %s;", 
            [region_id, account_id]
        )
        user = cur.fetchone()
        if not user:
            cur.execute(
                "INSERT INTO kokomi.user_basic (account_id, region_id, username) VALUES (%s, %s, %s);",
                [account_id, region_id, UtilityFunctions.get_user_default_name(account_id)]
            )
            cur.execute(
                "INSERT INTO kokomi.user_info (account_id) VALUES (%s);",
                [account_id]
            )
            cur.execute(
                "INSERT INTO kokomi.user_ships (account_id) VALUES (%s);",
                [account_id]
            )
            cur.execute(
                "INSERT INTO kokomi.user_clan (account_id) VALUES (%s);",
                [account_id]
            )
            cur.execute(
                "UPDATE kokomi.user_basic SET username = %s WHERE region_id = %s AND account_id = %s",
                [nickname, region_id, account_id]
            )
        else:
            # 根据数据库的数据判断用户是否更改名称
            if user['username'] != nickname and user['update_time'] != None:
                cur.execute(
                    "UPDATE kokomi.user_basic SET username = %s WHERE region_id = %s and account_id = %s;", 
                    [nickname, region_id, account_id]
                )
                cur.execute(
                    "INSERT INTO kokomi.user_history (account_id, username, start_time, end_time) VALUES (%s, %s, FROM_UNIXTIME(%s), FROM_UNIXTIME(%s));", 
                    [account_id, user['username'], user['update_time'], int(time.time())]
                )
            elif user['update_time'] == None:
                cur.execute(
                    "UPDATE kokomi.user_basic SET username = %s WHERE region_id = %s and account_id = %s;",
                    [nickname, region_id, account_id]
                )
        
        conn.commit()
        return JSONResponse.API_1000_Success
    except Exception as e:
        conn.rollback()
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
        conn.begin()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        clan_id = clan_data['clan_id']
        region_id = clan_data['region_id']
        tag = clan_data['tag']
        league = clan_data['league']
        cur.execute(
            "SELECT tag, league FROM kokomi.clan_basic WHERE region_id = %s and clan_id = %s;", 
            [region_id, clan_id]
        )
        clan = cur.fetchone()
        if clan is None:
            # 工会不存在，插入新数据
            cur.execute(
                "INSERT INTO kokomi.clan_basic (clan_id, region_id, tag, league) VALUES (%s, %s, %s, %s);", 
                [clan_id, region_id, UtilityFunctions.get_clan_default_name(), 5]
            )
            cur.execute(
                "INSERT INTO kokomi.clan_info (clan_id) VALUES (%s);", 
                [clan_id]
            )
            cur.execute(
                "INSERT INTO kokomi.clan_users (clan_id) VALUES (%s);", 
                [clan_id]
            )
            cur.execute(
                "INSERT INTO kokomi.clan_season (clan_id) VALUES (%s);", 
                [clan_id]
            )
            cur.execute(
                "UPDATE kokomi.clan_basic SET tag = %s, league = %s WHERE region_id = %s and clan_id = %s;",
                [tag, league, region_id, clan_id]
            )
        else:
            cur.execute(
                "UPDATE kokomi.clan_basic SET tag = %s, league = %s WHERE region_id = %s and clan_id = %s;",
                [tag, league, region_id, clan_id]
            )
        
        conn.commit()
        return JSONResponse.API_1000_Success
    except Exception as e:
        conn.rollback()
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
            "SELECT is_active, active_level, is_public, total_battles, UNIX_TIMESTAMP(last_battle_at) AS last_battle_time "
            "FROM kokomi.user_info WHERE account_id = %s;", 
            [account_id]
        )
        user = cur.fetchone()
        if user is None:
            # 正常来说这里不应该会遇到为空问题，因为先检查basic在检查info
            conn.commit()
            return JSONResponse.API_1008_UserNotExistinDatabase
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
            f"UPDATE kokomi.user_info SET {sql_str}updated_at = CURRENT_TIMESTAMP WHERE account_id = %s;", 
            params
        )

        conn.commit()
        return JSONResponse.API_1000_Success
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        if cur:
            cur.close()
        conn.close()  # 归还连接到连接池

@ExceptionLogger.handle_database_exception_sync
def check_clan_info(pool: PooledDB, clan_data: dict):
    '''检查并更新user_info表

    参数:
        user_list [dict]
    
    '''
    conn = pool.connection()
    cur = None
    try:
        conn.begin()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        clan_id = clan_data['clan_id']
        cur.execute(
            "SELECT is_active, season, public_rating, league, division, division_rating, "
            "UNIX_TIMESTAMP(last_battle_at) AS last_battle_time "
            "FROM kokomi.clan_info WHERE clan_id = %s;", 
            [clan_id]
        )
        clan = cur.fetchone()
        if clan is None:
            # 正常来说这里不应该会遇到为空问题，因为先检查basic在检查info
            conn.commit()
            return JSONResponse.API_1009_ClanNotExistinDatabase
        if clan_data['is_active'] == False:
            cur.execute(
                "UPDATE kokomi.clan_info SET is_active = %s, updated_at = CURRENT_TIMESTAMP WHERE clan_id = %s;",
                [0, clan_id]
            )
        else:
            if (
                clan_data['season_number'] != clan['season'] or
                clan_data['public_rating'] != clan['public_rating'] or
                clan_data['last_battle_at'] != clan['last_battle_time']
            ):
                if clan_data['last_battle_at']:
                    cur.execute(
                        "UPDATE kokomi.clan_info SET is_active = %s, season = %s, public_rating = %s, league = %s, "
                        "division = %s, division_rating = %s, last_battle_at = FROM_UNIXTIME(%s) "
                        "WHERE clan_id = %s",
                        [
                            1, clan_data['season_number'], clan_data['public_rating'],clan_data['league'],clan_data['division'],
                            clan_data['division_rating'],clan_data['last_battle_at'],clan_id
                        ]
                    )
                else:
                    cur.execute(
                        "UPDATE kokomi.clan_info SET is_active = %s, season = %s, public_rating = %s, league = %s, "
                        "division = %s, division_rating = %s "
                        "WHERE clan_id = %s",
                        [
                            1, clan_data['season_number'], clan_data['public_rating'],clan_data['league'],
                            clan_data['division'], clan_data['division_rating'],clan_id
                        ]
                    )

        conn.commit()
        return JSONResponse.API_1000_Success
    except Exception as e:
        conn.rollback()
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
        conn.begin()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        account_id = user_data['account_id']
        region_id = user_data['region_id']
        cur.execute(
            "SELECT recent_class, UNIX_TIMESTAMP(last_update_at) AS last_update_time "
            "FROM kokomi.recent WHERE region_id = %s and account_id = %s;", 
            [region_id, account_id]
        )
        user = cur.fetchone()
        if user == None:
            conn.commit()
            return JSONResponse.API_1000_Success
        if user_data['recent_class'] and (user['recent_class'] != user_data['recent_class']):
            cur.execute(
                "UPDATE kokomi.recent SET recent_class = %s WHERE region_id = %s and account_id = %s;",
                [user_data['recent_class'], region_id, account_id]
            )
        if not user['last_update_time']:
            cur.execute(
                "UPDATE kokomi.recent SET last_update_at = FROM_UNIXTIME(%s) WHERE region_id = %s and account_id = %s;",
                [user_data['last_update_time'], region_id, account_id]
            )
        elif user_data['last_update_time'] and (user['last_update_time'] > user_data['last_update_time']):
            cur.execute(
                "UPDATE kokomi.recent SET last_update_at = FROM_UNIXTIME(%s) WHERE region_id = %s and account_id = %s;",
                [user_data['last_update_time'], region_id, account_id]
            )
        
        conn.commit()
        return JSONResponse.API_1000_Success
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        if cur:
            cur.close()
        conn.close()  # 归还连接到连接池

@ExceptionLogger.handle_database_exception_sync
def update_user_ship(pool: PooledDB, user_data: dict):
    '''检查并更新user_ship表

    参数:
        user_data [dict]
    '''
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
                "DELETE FROM ships.ship_%s "
                "WHERE ship_id = %s AND region_id = %s AND account_id = %s;",
                [int(del_ship_id), int(del_ship_id), region_id, account_id]
            )
        for update_ship_id, ship_data in replace_ship_dict.items():
            cur.execute(
                "UPDATE ships.ship_%s SET battles_count = %s, battle_type_1 = %s, battle_type_2 = %s, battle_type_3 = %s, wins = %s, "
                "damage_dealt = %s, frags = %s, exp = %s, survived = %s, scouting_damage = %s, art_agro = %s, "
                "planes_killed = %s, max_exp = %s, max_damage_dealt = %s, max_frags = %s "
                "WHERE ship_id = %s AND region_id = %s AND account_id = %s;",
                [int(update_ship_id)] + ship_data + [int(update_ship_id), region_id, account_id]
            )
            cur.execute(
                "INSERT INTO ships.ship_%s (ship_id, region_id, account_id, battles_count, battle_type_1, battle_type_2, "
                "battle_type_3, wins, damage_dealt, frags, exp, survived, scouting_damage, art_agro, planes_killed, "
                "max_exp, max_damage_dealt, max_frags) "
                "SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s "
                "WHERE NOT EXISTS (SELECT 1 FROM ships.ship_%s WHERE ship_id = %s AND region_id = %s AND account_id = %s);",
                [int(update_ship_id)] + [int(update_ship_id), region_id, account_id] + ship_data + [int(update_ship_id)] + \
                [int(update_ship_id), region_id, account_id]
            )
        
        conn.commit()
        return JSONResponse.API_1000_Success
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        if cur:
            cur.close()
        conn.close()  # 归还连接到连接池

@ExceptionLogger.handle_database_exception_sync
def update_clan_users(pool: PooledDB, clan_id: int, hash_value, user_data: list):
    '''更新clan_users表'''
    conn = pool.connection()
    cur = None
    try:
        conn.begin()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        cur.execute(
            "SELECT hash_value, users_data, users_data, UNIX_TIMESTAMP(updated_at) AS update_time "
            "FROM kokomi.clan_users WHERE clan_id = %s;", 
            [clan_id]
        )
        clan = cur.fetchone()
        if clan is None:
            conn.commit()
            return JSONResponse.API_1009_ClanNotExistinDatabase
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
            "UPDATE kokomi.clan_users "
            "SET hash_value = %s, users_data = %s "
            "WHERE clan_id = %s",
            [hash_value, BinaryGeneratorUtils.to_clan_binary_data_from_list(user_data),clan_id]
        )
        for account_id in join_user_list:
            cur.execute(
                "INSERT INTO kokomi.clan_history (account_id, clan_id, action_type) VALUES (%s, %s, %s);",
                [account_id, clan_id, 1]
            )
        for account_id in leave_user_list:
            cur.execute(
                "INSERT INTO kokomi.clan_history (account_id, clan_id, action_type) VALUES (%s, %s, %s);",
                [account_id, clan_id, 2]
            )
        
        conn.commit()
        return JSONResponse.API_1000_Success
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        if cur:
            cur.close()
        conn.close()  # 归还连接到连接池

@ExceptionLogger.handle_database_exception_sync
def update_users_clan(pool: PooledDB, clan_id: int, user_data: list):
    '''更新user_clan表'''
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
            "UPDATE kokomi.user_clan "
            "SET clan_id = %s "
            f"WHERE account_id IN ( %s{sql_str} );", 
            [clan_id] + [user_data[0]] + params
        )

        conn.commit()
        return JSONResponse.API_1000_Success
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        if cur:
            cur.close()
        conn.close()  # 归还连接到连接池

@ExceptionLogger.handle_database_exception_sync
def update_user_ships(pool: PooledDB, user_data: dict):
    '''检查并更新user_ships表

    参数:
        user_data [dict]
    '''
    conn = pool.connection()
    cur = None
    try:
        conn.begin()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        
        account_id = user_data['account_id']
        if user_data['hash_value']:
            cur.execute(
                "UPDATE kokomi.user_ships "
                "SET battles_count = %s, hash_value = %s, ships_data = %s "
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
                "UPDATE kokomi.user_ships "
                "SET battles_count = %s "
                "WHERE account_id = %s;", 
                [user_data['battles_count'], account_id]
            )

        conn.commit()
        return JSONResponse.API_1000_Success
    except Exception as e:
        conn.rollback()
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
        conn.begin()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        account_id = user_data['account_id']
        clan_id = user_data['clan_id']
        if clan_id:
            cur.execute(
                "UPDATE kokomi.user_clan SET clan_id = %s WHERE account_id = %s;",
                [clan_id, account_id]
            )
        else:
            cur.execute(
                "UPDATE kokomi.user_clan SET updated_at = CURRENT_TIMESTAMP WHERE account_id = %s;",
                [account_id]
            )

        conn.commit()
        return JSONResponse.API_1000_Success
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        if cur:
            cur.close()
        conn.close()  # 归还连接到连接池