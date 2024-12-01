import os
import json
import asyncio

import aiomysql
from aiomysql.pool import Pool
from aiomysql.connection import Connection
from aiomysql.cursors import Cursor

from config import MYSQL_HOST, MYSQL_PASSWORD, MYSQL_PORT, MYSQL_USERNAME


file_path = os.path.dirname(__file__)

def check_aid_and_rid(account_id: int, region_id: int) -> bool:
    "检查account_id和region_id是否合法"
    if not (isinstance(account_id, int) and isinstance(region_id, int)):
        return False
    if region_id < 1 and region_id > 5:
        return False
    account_id_len = len(str(account_id))
    if account_id_len > 10:
        return False
    # 由于不知道后续会使用什么字段
    # 目前的检查逻辑是判断aid不在其他的字段内

    # 俄服 1-9 [~5字段]
    if region_id == 4 and account_id_len < 9:
        return True
    elif (
        region_id == 4 and 
        account_id_len == 9 and 
        int(account_id/100000000) not in [5,6,7,8,9]
    ):
        return True
    # 欧服 9 [5~字段] 
    if (
        region_id == 2 and
        account_id_len == 9 and
        int(account_id/100000000) not in [1,2,3,4]
    ):
        return True
    # 亚服 10 [2-3字段]
    if (
        region_id == 1 and 
        account_id_len == 10 and
        int(account_id/1000000000) not in [1,7]
    ):
        return True
    # 美服 10 [1字段]
    if (
        region_id == 3 and
        account_id_len == 10 and
        int(account_id/1000000000) not in [2,3,7]
    ):
        return True
    # 国服 10 [7字段]
    if (
        region_id == 5 and
        account_id_len == 10 and
        int(account_id/1000000000) not in [1,2,3]
    ):
        return True
    return False

def check_cid_and_rid(clan_id: int, region_id: int) -> bool:
    "检查clan_id和region_id是否合法"
    if not (isinstance(clan_id, int) and isinstance(region_id, int)):
        return False
    if region_id < 1 and region_id > 5:
        return False
    clan_id_len = len(str(clan_id))
    # 亚服 10 [2字端]
    if (
        region_id == 1 and 
        clan_id_len == 10 and
        int(clan_id/1000000000) == 2
    ):
        return True
    # 欧服 9 [5字段]
    if (
        region_id == 2 and 
        clan_id_len == 9 and
        int(clan_id/100000000) == 5
    ):
        return True
    # 美服 10 [1字段]
    if (
        region_id == 3 and 
        clan_id_len == 10 and
        int(clan_id/1000000000) == 1
    ):
        return True
    # 俄服 6 [4字段]
    if (
        region_id == 4 and 
        clan_id_len == 6 and
        int(clan_id/100000) == 4
    ):
        return True
    # 国服 10 [7字段]
    if (
        region_id == 5 and 
        clan_id_len == 10 and
        int(clan_id/1000000000) == 7
    ):
        return True
    return False

async def main(name):
    pool: Pool = await aiomysql.create_pool(
        host=MYSQL_HOST, 
        port=MYSQL_PORT, 
        user=MYSQL_USERNAME, 
        password=MYSQL_PASSWORD, 
        db='kokomi'
    )
    try:
        json_path = os.path.join(file_path, 'old', f'clan_{name}.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        async with pool.acquire() as conn:
            conn: Connection
            async with conn.cursor() as cur:
                cur: Cursor
                i = 0
                j = 0
                for region_id, user_id in data:
                    if i >= 10000:
                        j += 1
                        i = 0
                        print(j*10000)
                    # if check_aid_and_rid(user_id, region_id):
                    #     await cur.execute(
                    #     "INSERT INTO kokomi.user_basic (account_id, region_id, username) VALUES (%s, %s, %s);",
                    #         [user_id, region_id, f'User_{user_id}']
                    #     )
                    #     await cur.execute(
                    #         "INSERT INTO kokomi.user_info (account_id) VALUES (%s);",
                    #         [user_id]
                    #     )
                    #     await cur.execute(
                    #         "INSERT INTO kokomi.user_ships (account_id) VALUES (%s);",
                    #         [user_id]
                    #     )
                    #     await cur.execute(
                    #         "INSERT INTO kokomi.user_clan (account_id) VALUES (%s);",
                    #         [user_id]
                    #     )
                    # else:
                    #     print(f'{region_id} {user_id} 不合法')
                    if check_cid_and_rid(user_id, region_id):
                        await cur.execute(
                            "INSERT INTO kokomi.clan_basic (clan_id, region_id, tag) VALUES (%s, %s, %s);",
                            [user_id, region_id, 'N/A']
                        )
                        await cur.execute(
                            "INSERT INTO kokomi.clan_info (clan_id) VALUES (%s);",
                            [user_id]
                        )
                        await cur.execute(
                            "INSERT INTO kokomi.clan_users (clan_id) VALUES (%s);",
                            [user_id]
                        )
                        await cur.execute(
                            "INSERT INTO kokomi.clan_season (clan_id) VALUES (%s);",
                            [user_id]
                        )
                    else:
                        print(f'{region_id} {user_id} 不合法')
                    i += 1
            await conn.commit()
    except:
        import traceback
        traceback.print_exc()
    finally:
        pool.close()
    print('数据库创建完成')

if __name__ == '__main__':
    asyncio.run(
        main(1)
    )