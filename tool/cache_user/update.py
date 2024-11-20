import time
import traceback

from log import log as logger
from network import UserCache_Network

class UserCache_Update:
    @classmethod
    async def main(self, account_id: int, region_id: int, ac_value: str = None):
        '''UserCache更新入口函数
        '''
        start_time = time.time()
        try:
            logger.debug(f'{region_id} - {account_id} | ┌── 开始用户更新流程')
        except:
            error = traceback.format_exc()
            logger.error(f'{region_id} - {account_id} | ├── 数据更新时发生错误')
            logger.error(f'Error: {error}')
        finally:
            cost_time = time.time() - start_time
            logger.debug(f'{region_id} - {account_id} | ├── 用户更新完成')
            logger.debug(f'{region_id} - {account_id} | └── 本次耗时: {round(cost_time,2)} s')

    async def service_master(account_id: int, region_id: int, ac_value: str = None, user_data: dict = None):
        ...