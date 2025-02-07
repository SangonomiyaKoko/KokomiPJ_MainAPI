from aiomysql.connection import Connection
from aiomysql.cursors import Cursor

from app.db import MysqlConnection
from app.log import ExceptionLogger
from app.response import JSONResponse, ResponseDict

from .db_name import CACHE_DB


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