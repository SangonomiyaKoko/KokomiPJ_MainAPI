import time

import pymysql
from dbutils.pooled_db import PooledDB, PooledSharedDBConnection, PooledDedicatedDBConnection

from app.response import JSONResponse
from app.log import ExceptionLogger


@ExceptionLogger.handle_database_exception_sync
def check_user_basic(
    pool: PooledDB,
    users: list
):
    '''检查用户数据是否需要更新

    参数:
        user_list [dict]
    '''
    conn = pool.connection()
    cur = None
    try:
        if users == []:
            return JSONResponse.API_1000_Success
        cur = conn.cursor(pymysql.cursors.DictCursor)
        for temp in users:
            account_id = temp['account_id']
            region_id = temp['region_id']
            nickname = temp['nickname']
            cur.execute(
                "SELECT username, UNIX_TIMESTAMP(updated_at) AS update_time "
                "FROM user_basic WHERE region_id = %s and account_id = %s;", 
                [region_id, account_id]
            )
            user = cur.fetchone()
            conn.begin()
            if user is None:
                # 用户不存在，插入新数据
                cur.execute(
                    "INSERT INTO user_basic (account_id, region_id, username) VALUES (%s, %s, %s);"
                    "INSERT INTO user_info (account_id) VALUES (%s);"
                    "INSERT INTO user_ships (account_id) VALUES (%s);"
                    "INSERT INTO user_clan (account_id) VALUES (%s);",
                    [account_id, region_id, nickname, account_id, account_id, account_id]
                )
                user = {
                    'username': nickname,
                    'update_time': None
                }
            if user['username'] != nickname:
                cur.execute(
                    "UPDATE user_basic SET username = %s WHERE region_id = %s and account_id = %s;"
                    "INSERT INTO user_history (account_id, username, start_time, end_time) VALUES (%s, %s, %s, %s);", 
                    [nickname, region_id, account_id, account_id, user['nickname'], user['update_time'], int(time.time())]
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
def check_user_info(
    pool: PooledDB,
    users: list
):
    '''检查并更新user_info表

    参数:
        user_list [dict]
    
    '''
    conn = pool.connection()
    cur = None
    try:
        if users == []:
            return JSONResponse.API_1000_Success
        cur = conn.cursor(pymysql.cursors.DictCursor)
        sql_list = []
        for user_info in users:
            account_id = user_info['account_id']
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
                if user_info[field] != user[field]:
                    sql_str += f'{field} = %s, '
                    params.append(user_info[field])
            params = params + [account_id]
            sql_list.append((
                f"UPDATE user_info SET {sql_str}updated_at = CURRENT_TIMESTAMP WHERE account_id = %s;", 
                params
            ))
        conn.begin()
        for sql, params in sql_list:
            cur.execute(sql, params)
        conn.commit()
        return JSONResponse.API_1000_Success
    except Exception as e:
        raise e
    finally:
        if cur:
            cur.close()
        conn.close()  # 归还连接到连接池

@ExceptionLogger.handle_database_exception_sync
def check_clan_tag_and_league(
    pool,
    clans: list
):
    '''检查clan_basic是否需要更新

    参数：
        clan_list [clan_id,region_id,tag,league]
    '''
    conn = pool.connection()
    cur = None
    try:
        if clans == []:
            return JSONResponse.API_1000_Success
        cur = conn.cursor(pymysql.cursors.DictCursor)
        for clan_id, region_id, tag, league in clans.items():
            cur.execute(
                "SELECT tag, league FROM clan_basic WHERE region_id = %s and clan_id = %s;", 
                [region_id, clan_id]
            )
            clan = cur.fetchone()
            conn.begin()
            if clan is None:
                # 工会不存在，插入新数据
                cur.execute(
                    "INSERT INTO clan_basic (clan_id, region_id, tag) VALUES (%s, %s, %s);"
                    "INSERT INTO clan_info (clan_id) VALUES (%s);"
                    "INSERT INTO clan_users (clan_id) VALUES (%s);"
                    "INSERT INTO clan_season (clan_id) VALUES (%s);", 
                    [clan_id, region_id, tag, clan_id, clan_id, clan_id]
                )
                clan = {
                    'tag': tag,
                    'leauge': 5
                }
            # 工会存在，检查数据是否需要更新
            if clan['tag'] == tag and clan['league'] == league:
                cur.execute(
                    "UPDATE clan_basic SET updated_at = CURRENT_TIMESTAMP WHERE region_id = %s and clan_id = %s;",
                    [region_id, clan_id]
                )
            else:
                sql_str = ''
                params = []
                if clan['tag'] != tag:
                    sql_str += 'tag = %s, '
                    params.append(tag)
                if clan['league'] != league:
                    sql_str += 'league = %s, '
                    params.append(league)
                params = params + [region_id, clan_id]
                cur.execute(
                    f"UPDATE clan_basic SET {sql_str}updated_at = CURRENT_TIMESTAMP WHERE region_id = %s and clan_id = %s;",
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
def update_user_clan(
    pool,
    user_clans: list
):
    '''更新user_clan表

    参数：
        user_clan_list [account_id,clan_id]
    
    '''
    conn = pool.connection()
    cur = None
    try:
        if user_clans == []:
            return JSONResponse.API_1000_Success
        cur = conn.cursor(pymysql.cursors.DictCursor)
        sql_list = []
        for account_id, clan_id in user_clans:
            cur.execute(
                "SELECT clan_id FROM clan_user WHERE account_id = %s;",
                account_id
            )
            user_clan = cur.fetchone()
            if user_clan:
                if user_clan['clan_id'] == clan_id:
                    sql_list.append((
                        "UPDATE clan_user SET updated_at = CURRENT_TIMESTAMP WHERE account_id = %s;",
                        [account_id]
                    ))
                else:
                    sql_list.append((
                        "UPDATE clan_user SET clan_id = %s, updated_at = CURRENT_TIMESTAMP WHERE account_id = %s;",
                        [clan_id, account_id]
                    ))
            else:
                sql_list.append((
                    "INSERT INTO clan_user (account_id, clan_id) VALUES (%s, %s);",
                    [account_id,clan_id]
                ))
        conn.begin()
        for sql, params in sql_list:
            cur.execute(sql,params)
        conn.commit()
        return JSONResponse.API_1000_Success
    except Exception as e:
        raise e
    finally:
        if cur:
            cur.close()
        conn.close()  # 归还连接到连接池