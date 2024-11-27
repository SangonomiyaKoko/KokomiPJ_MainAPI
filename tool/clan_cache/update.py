import time
import asyncio
import traceback

from log import log as logger
from network import Network

class Update:
    '''
    
    '''
    @classmethod
    async def main(self, region_id: int):
        '''UserCache更新入口函数
        '''
        start_time = time.time()
        try:
            logger.debug(f'{region_id} | ┌── 开始工会更新流程')
            await self.service_master(self, region_id)
        except:
            error = traceback.format_exc()
            logger.error(f'{region_id} | ├── 数据更新时发生错误')
            logger.error(f'Error: {error}')
        finally:
            cost_time = time.time() - start_time
            logger.debug(f'{region_id} | └── 本次更新完成, 耗时: {round(cost_time,2)} s')

    async def service_master(self, region_id: int):
        season_number, clan_data_list = await Network.get_clan_rank_data(region_id)
        logger.debug(f'{region_id} | ├── 当前赛季代码 {season_number}')
        logger.debug(f'{region_id} | ├── 当前工会数量 {len(clan_data_list)}')
        if len(clan_data_list) == 0:
            return
        need_update_list = []
        chunk_size = 50  # 每次获取50个数据
        for i in range(0, len(clan_data_list), chunk_size):
            chunk = clan_data_list[i:i + chunk_size]
            if len(chunk) > 0:
                data = {
                    'region_id': region_id,
                    'season_number': season_number,
                    'clan_list': chunk
                }
                update_result = await self.update_clan_data(i, region_id, data)
                need_update_list = need_update_list + update_result
        print(f'需要更新用户的数量 {len(need_update_list)}')
    
    async def update_clan_data(i: int, region_id: int, clan_data: dict) -> None:
        update_result = await Network.update_clan_data({'clan_info': clan_data})
        if update_result.get('code',None) != 1000:
            logger.error(f"{region_id} | ├── 更新数据上传失败，数据切片{i}，Error: {update_result.get('message')}")
            return []
        else:
            logger.debug(f'{region_id} | ├── 更新数据上传成功，数据切片{i}')
            return update_result['data']
