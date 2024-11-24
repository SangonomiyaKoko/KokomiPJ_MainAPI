import time
import traceback

from log import log as logger
from network import Network

class Update:
    @classmethod
    async def main(self, user_data: dict):
        '''UserCache更新入口函数
        '''
        start_time = time.time()
        try:
            account_id = user_data['user_basic']['account_id']
            region_id = user_data['user_basic']['region_id']
            logger.debug(f'{region_id} - {account_id} | ┌── 开始用户更新流程')
            await self.service_master(self, user_data)
        except:
            error = traceback.format_exc()
            logger.error(f'{region_id} - {account_id} | ├── 数据更新时发生错误')
            logger.error(f'Error: {error}')
        finally:
            cost_time = time.time() - start_time
            logger.debug(f'{region_id} - {account_id} | └── 本次更新完成, 耗时: {round(cost_time,2)} s')

    async def service_master(self, user_data: dict):
        # 用于更新user_cache的数据
        ...
