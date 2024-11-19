import asyncio

import aiomysql
from aiomysql.pool import Pool
from aiomysql.connection import Connection
from aiomysql.cursors import Cursor

from config import MYSQL_HOST, MYSQL_PASSWORD, MYSQL_PORT, MYSQL_USERNAME

test_user = [
    [1, 2023619512],
    [4, 213712262],
    [4, 211817574],
    [1, 2020485438],
    [5, 7062709322],
    [1, 2041010058],
    [4, 212311521],
    [5, 7050041300],
    [2, 575901955],
    [3, 1015532199],
    [1, 2040834546],
    [1, 2051458265],
    [1, 3003401142],
    [4, 262075625],
    [2, 694300486],
    [4, 257825627],
    [5, 7049437314],
    [3, 1052816271]
]


async def main():
    pool: Pool = await aiomysql.create_pool(
        host=MYSQL_HOST, 
        port=MYSQL_PORT, 
        user=MYSQL_USERNAME, 
        password=MYSQL_PASSWORD, 
        db='kokomi',
        autocommit = False
    )
    try:
        
        async with pool.acquire() as conn:
            conn: Connection
            async with conn.cursor() as cur:
                cur: Cursor
                await conn.begin()
                for user in test_user:
                    await cur.execute(
                        "INSERT INTO user_basic (account_id, region_id, username) VALUES (%s, %s, %s);",
                        [user[1],user[0], f'User_{user[1]}']
                    )
                    await cur.execute(
                        "INSERT INTO user_info (account_id) VALUES (%s);", 
                        [user[1]]
                    )
                    await cur.execute(
                        "INSERT INTO user_ships (account_id) VALUES (%s);", 
                        [user[1]]
                    )
                    await cur.execute(
                        "INSERT INTO user_pr (account_id) VALUES (%s);", 
                        [user[1]]
                    )
                await conn.commit()
    except:
        import traceback
        traceback.print_exc()
    finally:
        pool.close()
    print('测试数据插入完成')

if __name__ == '__main__':
    asyncio.run(
        main()
    )