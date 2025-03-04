from aiomysql.connection import Connection
from aiomysql.cursors import Cursor

from app.db import MysqlConnection
from app.log import ExceptionLogger
from app.response import JSONResponse, ResponseDict
from app.utils import BinaryGeneratorUtils

from .db_name import CACHE_DB, MAIN_DB


class ShipsCacheModel:
    @ExceptionLogger.handle_database_exception_async
    async def check_existing_ship(ship_id_list: set) -> ResponseDict:
        '''检查ship_id是否存在于数据库

        方法描述

        参数:
            ship_id_list
        
        返回:
            ResponseDict
        '''
        try:
            conn: Connection = await MysqlConnection.get_connection()
            await conn.begin()
            cur: Cursor = await conn.cursor()

            await cur.execute(
                f"SELECT ship_id FROM {CACHE_DB}.existing_ships"
            )
            not_exists_set = set()
            exists_list = []
            rows = await cur.fetchall()
            for row in rows:
                exists_list.append(row[0])
            for ship_id in ship_id_list:
                if ship_id not in exists_list:
                    not_exists_set.add(ship_id)
            for ship_id in not_exists_set:
                await cur.execute(
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
                await cur.execute(
                    f"INSERT INTO {CACHE_DB}.existing_ships ( ship_id ) VALUE ( %s )",
                    [ship_id]
                )
            
            await conn.commit()
            return JSONResponse.API_1000_Success
        except Exception as e:
            await conn.rollback()
            raise e
        finally:
            await cur.close()
            await MysqlConnection.release_connection(conn)
    
    @ExceptionLogger.handle_database_exception_async
    async def update_user_ships(user_data: dict) -> ResponseDict:
        '''更新用户的船只缓存数据

        更新用户的user_ships和ship数据

        参数:
            user_data
        
        返回:
            ResponseDict
        '''
        try:
            conn: Connection = await MysqlConnection.get_connection()
            await conn.begin()
            cur: Cursor = await conn.cursor()

            account_id = user_data['account_id']
            region_id = user_data['region_id']
            if 'hash_value' in user_data:
                await cur.execute(
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
                replace_ship_dict = user_data['ship_dict']
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
            else:
                await cur.execute(
                    f"UPDATE {MAIN_DB}.user_ships "
                    "SET battles_count = %s, updated_at = CURRENT_TIMESTAMP "
                    "WHERE account_id = %s;", 
                    [user_data['battles_count'], account_id]
                )
            
            await conn.commit()
            return JSONResponse.API_1000_Success
        except Exception as e:
            await conn.rollback()
            raise e
        finally:
            await cur.close()
            await MysqlConnection.release_connection(conn)