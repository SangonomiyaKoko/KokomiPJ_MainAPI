import time
import traceback

from log import log as logger
from network import Network

class Update:
    @classmethod
    async def main(self, clan_id: int, region_id: int):
        '''UserCache更新入口函数
        '''
        start_time = time.time()
        try:
            logger.debug(f'{region_id} - {clan_id} | ┌── 开始用户更新流程')
            await self.service_master(self, clan_id, region_id)
        except:
            error = traceback.format_exc()
            logger.error(f'{region_id} - {clan_id} | ├── 数据更新时发生错误')
            logger.error(f'Error: {error}')
        finally:
            cost_time = time.time() - start_time
            logger.debug(f'{region_id} - {clan_id} | └── 本次更新完成, 耗时: {round(cost_time,2)} s')

    async def service_master(self, clan_id: int, region_id: int):
        result = await Network.get_clan_data(region_id, clan_id)
        if result.get('code', None) != 1000:
            logger.error(f"{region_id} - {clan_id} | ├── 网络请求失败，Error: {result.get('message')}")
            return
        await self.update_user_data(clan_id,region_id,result['data'])
        return
    
    async def update_user_data(
        clan_id: int, 
        region_id: int, 
        clan_users: dict
    ) -> None:
        update_result = await Network.update_user_data(clan_users)
        if update_result.get('code',None) != 1000:
            logger.error(f"{region_id} - {clan_id} | ├── 更新数据上传失败，Error: {update_result.get('message')}")
        else:
            logger.debug(f'{region_id} - {clan_id} | ├── 更新数据上传成功')
