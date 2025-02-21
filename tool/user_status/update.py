import time
import traceback

from log import log as logger
from model import get_ship_max_number, get_cache_batch

class Update:
    @classmethod
    async def main(self, ship_id: int):
        '''UserCache更新入口函数
        '''
        start_time = time.time()
        try:
            logger.debug(f'{ship_id} | ┌── 开始统计更新流程')
            await self.service_master(self, ship_id)
        except:
            error = traceback.format_exc()
            logger.error(f'{ship_id} | ├── 数据更新时发生错误')
            logger.error(f'Error: {error}')
        finally:
            cost_time = time.time() - start_time
            logger.debug(f'{ship_id} | └── 本次更新完成, 耗时: {round(cost_time,2)} s')

    async def service_master(self, ship_id: int):
        request_result = get_ship_max_number(ship_id)
        if request_result['code'] != 1000:
            logger.error(f"{ship_id} | ├── 获取表MaxID时发生错误，Error: {request_result.get('message')}")
            return
        max_offset = request_result['data']['max_id']
        limit = 1000
        offset = 0
        result = {
            0: {}, 1: {}, 2: {}, 3: {}, 4: {}, 5: {}
        }
        leader_list = []
        update_keys = [
            'battles_count', 'wins', 'damage_dealt',
            'frags', 'exp', 'survived', 'scouting_damage',
            'art_agro', 'planes_killed'
        ]
        while offset <= max_offset:
            cache_result = get_cache_batch(ship_id, offset, limit)
            if cache_result['code'] == 1000:
                i = 1
                for user in cache_result['data']:
                    if user['battles_count'] >= 50:
                        leader_list.append(user)
                    region_id = user['region_id']
                    if result[0] == {}:
                        for key in update_keys:
                            result[0][key] = 0
                    if result[region_id] == {}:
                        for key in update_keys:
                            result[region_id][key] = 0
                    else:
                        for key in update_keys:
                            result[0][key] += user[key]
                            result[region_id][key] += user[key]
                    i += 1
            else:
                logger.error(f"{ship_id} | ├── 获取cache时发生错误，Error: {cache_result.get('message')}")
            offset += limit
        print(result)
        status_result = {
            0: {}, 1: {}, 2: {}, 3: {}, 4: {}, 5: {}
        }
        for region_id in result.keys():
            if result[region_id] != {}:
                for key in update_keys:
                    status_result[region_id][key] = 0
                if result[region_id][update_keys[0]] == 0:
                    continue
                status_result[region_id][update_keys[0]] = result[region_id][update_keys[0]]
                for key in update_keys[1:]:
                    status_result[region_id][key] = round(result[region_id][key]/result[region_id][update_keys[0]],6)
        print(status_result)
        return 