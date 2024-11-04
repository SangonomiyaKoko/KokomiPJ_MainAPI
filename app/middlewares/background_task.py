import uuid
import traceback

import pymysql
from pymysql.err import ProgrammingError

from app.response import JSONResponse
from app.log import write_error_info



def check_user_basic(
    pool,
    users: list
):
    '''检查用户数据是否需要更新
    
    '''
    conn = pool.connection()
    cur = None
    try:
        cur = conn.cursor(pymysql.cursors.DictCursor)
        for account_id, region_id, nickname in users:
            cur.execute(
                "SELECT username FROM user_basic WHERE region_id = %s and account_id = %s;", 
                [region_id, account_id]
            )
            user = cur.fetchone()
            if user is None:
                # 用户不存在，插入新数据
                cur.execute(
                    "INSERT INTO user_basic (account_id, region_id, username) VALUES (%s, %s, %s);",
                    [account_id, region_id, nickname]
                )
                cur.execute(
                    "INSERT INTO user_info (account_id) VALUES (%s);", 
                    [account_id]
                )
                cur.execute(
                    "INSERT INTO user_cache (account_id) VALUES (%s);", 
                    [account_id]
                )
                conn.commit()
            else:
                if user['username'] != nickname:
                    cur.execute(
                        "UPDATE user_basic SET username = %s, updated_at = CURRENT_TIMESTAMP WHERE region_id = %s and account_id = %s;", 
                        [nickname, region_id, account_id]
                    )
                    conn.commit()
                else:
                    cur.execute(
                        "UPDATE user_basic SET updated_at = CURRENT_TIMESTAMP WHERE region_id = %s and account_id = %s;", 
                        [region_id, account_id]
                    )
                    conn.commit()
        return JSONResponse.API_1000_Success
    except ProgrammingError as e:
        error_id = str(uuid.uuid4())
        write_error_info(
            error_id = error_id,
            error_type = 'MySQL',
            error_name = f'ERROR_{e.args[0]}',
            error_file = __file__,
            error_info = f'\n{str(e.args[1])}'
        )
        return JSONResponse.get_error_response(3000,'DatabaseError',error_id)
    except Exception as e:
        error_id = str(uuid.uuid4())
        write_error_info(
            error_id = error_id,
            error_type = 'Program',
            error_name = str(type(e).__name__),
            error_file = __file__,
            error_info = f'\n{traceback.format_exc()}'
        )
        return JSONResponse.get_error_response(5000,'ProgramError',error_id)
    finally:
        if cur:
            cur.close()
        conn.close()  # 归还连接到连接池


def check_clan_tag_and_league(
    pool,
    clans: list
):
    '''检查clan_basic是否需要更新

    参数：
        clan_list
    
    '''
    conn = pool.connection()
    cur = None
    try:
        cur = conn.cursor(pymysql.cursors.DictCursor)
        for clan_id, region_id, tag, league in clans:
            cur.execute(
                "SELECT tag, league FROM clan_basic WHERE region_id = %s and clan_id = %s;", 
                [region_id, clan_id]
            )
            clan = cur.fetchone()
            if clan is None:
                # 工会不存在，插入新数据
                cur.execute(
                    "INSERT INTO clan_basic (clan_id, region_id, tag) VALUES (%s, %s, %s);",
                    [clan_id, region_id, tag]
                )
                cur.execute(
                    "INSERT INTO clan_info (clan_id) VALUES (%s);", 
                    [clan_id]
                )
                cur.execute(
                    "INSERT INTO clan_cache (clan_id) VALUES (%s);", 
                    [clan_id]
                )
                conn.commit()
            else:
                # 工会存在，检查数据是否需要更新
                if clan['tag'] == tag and clan['league'] == league:
                    cur.execute(
                        "UPDATE clan_basic SET updated_at = CURRENT_TIMESTAMP WHERE region_id = %s and clan_id = %s;",
                        [region_id, clan_id]
                    )
                    conn.commit()
                else:
                    sql_str = ''
                    params = []
                    if clan[0] != tag:
                        sql_str += 'tag = %s, '
                        params.append(tag)
                    if clan[1] != league:
                        sql_str += 'league = %s, '
                        params.append(league)
                    params = params + [region_id, clan_id]
                    cur.execute(
                        f"UPDATE clan_basic SET {sql_str}updated_at = CURRENT_TIMESTAMP WHERE region_id = %s and clan_id = %s;",
                        params
                    )
                    conn.commit()
        return JSONResponse.API_1000_Success
    except ProgrammingError as e:
        error_id = str(uuid.uuid4())
        write_error_info(
            error_id = error_id,
            error_type = 'MySQL',
            error_name = f'ERROR_{e.args[0]}',
            error_file = __file__,
            error_info = f'\n{str(e.args[1])}'
        )
        return JSONResponse.get_error_response(3000,'DatabaseError',error_id)
    except Exception as e:
        error_id = str(uuid.uuid4())
        write_error_info(
            error_id = error_id,
            error_type = 'Program',
            error_name = str(type(e).__name__),
            error_file = __file__,
            error_info = f'\n{traceback.format_exc()}'
        )
        return JSONResponse.get_error_response(5000,'ProgramError',error_id)
    finally:
        if cur:
            cur.close()
        conn.close()  # 归还连接到连接池