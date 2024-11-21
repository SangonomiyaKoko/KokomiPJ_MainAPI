import pymysql

from app.response import JSONResponse
from app.log import ExceptionLogger


@ExceptionLogger.handle_database_exception_sync
def check_user_basic(
    pool,
    users: list
):
    '''检查用户数据是否需要更新

    参数:
        user_list [account_id,region_id,nickname]
    '''
    conn = pool.connection()
    cur = None
    try:
        if users == []:
            return JSONResponse.API_1000_Success
        cur = conn.cursor(pymysql.cursors.DictCursor)
        for account_id, region_id, nickname in users:
            cur.execute(
                "SELECT username FROM user_basic WHERE region_id = %s and account_id = %s;", 
                [region_id, account_id]
            )
            user = cur.fetchone()
            conn.begin()
            if user is None:
                # 用户不存在，插入新数据
                cur.execute(
                    "INSERT IGNORE INTO user_basic (account_id, region_id, username) VALUES (%s, %s, %s);",
                    [account_id, region_id, nickname]
                )
                cur.execute(
                    "INSERT IGNORE INTO user_info (account_id) VALUES (%s);", 
                    [account_id]
                )
                cur.execute(
                    "INSERT IGNORE INTO user_cache (account_id) VALUES (%s);", 
                    [account_id]
                )
            else:
                if user['username'] != nickname:
                    cur.execute(
                        "UPDATE user_basic SET username = %s, updated_at = CURRENT_TIMESTAMP WHERE region_id = %s and account_id = %s;", 
                        [nickname, region_id, account_id]
                    )
                else:
                    cur.execute(
                        "UPDATE user_basic SET updated_at = CURRENT_TIMESTAMP WHERE region_id = %s and account_id = %s;", 
                        [region_id, account_id]
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
                    "INSERT IGNORE INTO clan_basic (clan_id, region_id, tag, league) VALUES (%s, %s, %s, %s);",
                    [clan_id, region_id, tag, league]
                )
                cur.execute(
                    "INSERT IGNORE INTO clan_info (clan_id) VALUES (%s);", 
                    [clan_id]
                )
                cur.execute(
                    "INSERT IGNORE INTO clan_cache (clan_id) VALUES (%s);", 
                    [clan_id]
                )
            else:
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
def check_user_info(
    pool,
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
                "SELECT clan_id FROM user_clan WHERE account_id = %s;",
                account_id
            )
            user_clan = cur.fetchone()
            if user_clan:
                if user_clan['clan_id'] == clan_id:
                    sql_list.append((
                        "UPDATE user_clan SET updated_at = CURRENT_TIMESTAMP WHERE account_id = %s;",
                        [account_id]
                    ))
                else:
                    sql_list.append((
                        "UPDATE user_clan SET clan_id = %s, updated_at = CURRENT_TIMESTAMP WHERE account_id = %s;",
                        [clan_id, account_id]
                    ))
            else:
                sql_list.append((
                    "INSERT INTO user_clan (account_id, clan_id) VALUES (%s, %s);",
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