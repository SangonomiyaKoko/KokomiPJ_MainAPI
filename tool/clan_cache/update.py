import time
import asyncio
import traceback

from log import log as logger
from network import Network
from model import update_clan_info_batch, update_clan_basic_and_info, update_clan_season

class Update:
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
        if season_number == None or len(clan_data_list) == 0:
            return
        need_update_list = []
        update_result = update_clan_info_batch(region_id, season_number, clan_data_list)
        if update_result.get('code', None) != 1000:
            return
        need_update_list = update_result['data']
        logger.debug(f'{region_id} | ├── 需要更新工会数量 {len(need_update_list)}')
        for clan_id in need_update_list:
            clan_cvc_data = await Network.get_clan_cvc_data(clan_id,region_id,season_number)
            if clan_cvc_data == None:
                clan_cvc_data = await Network.get_clan_cvc_data2(clan_id,region_id,season_number)
            if clan_cvc_data.get('code', None) == 1002:
                clan_basic = {
                    'clan_id': clan_id,
                    'region_id': region_id,
                    'is_active': 0
                }
                self.update_clan_info(clan_id, region_id, clan_basic)
                logger.debug(f"{region_id} - {clan_id} | ├── 工会不存在，更新数据")
                continue
            if clan_cvc_data.get('code', None) != 1000:
                logger.error(f"{region_id} - {clan_id} | ├── 网络请求失败，Error: {clan_cvc_data.get('message')}")
                continue
            self.update_clan_season(clan_id, region_id, clan_cvc_data['data'])
        return

    def update_clan_info(clan_id: int, region_id: int, clan_data: dict):
        # 更新clan_basic和clan_info表的信息
        result = update_clan_basic_and_info(clan_data)
        if result.get('code', None) != 1000:
            logger.error(f"{region_id} - {clan_id} | ├── 数据库更新失败，Error: {result.get('code')} {result.get('message')}")
            return
        logger.debug(f"{region_id} - {clan_id} | ├── 工会info数据更新完成")
        return

    def update_clan_season(clan_id: int, region_id: int, clan_data: dict):
        # 更新clan_basic和clan_info表的信息
        result = update_clan_season(clan_data)
        if result.get('code', None) != 1000:
            logger.error(f"{region_id} - {clan_id} | ├── 数据库更新失败，Error: {result.get('code')} {result.get('message')}")
            return
        logger.debug(f"{region_id} - {clan_id} | ├── 工会season数据更新完成")
        return
