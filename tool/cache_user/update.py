import time
import traceback

from log import log as recent_logger
from network import UserCache_Network

class UserCache_Update:
    @classmethod
    async def main(self, account_id: int, region_id: int, ac_value: str = None):
        '''Recent数据库更新入口函数

        对于Slave服务来说，只是负责user_info的更新

        对于Master服务来说，还需要负责数据库的更新
        '''
        start_time = time.time()
        try:
            recent_logger.debug(f'{region_id} - {account_id} | ┌── 开始用户更新流程')
        except:
            error = traceback.format_exc()
            recent_logger.error(f'{region_id} - {account_id} | ├── 数据更新时发生错误')
            recent_logger.error(f'Error: {error}')
        finally:
            cost_time = time.time() - start_time
            recent_logger.debug(f'{region_id} - {account_id} | ├── 用户更新完成')
            recent_logger.debug(f'{region_id} - {account_id} | └── 本次耗时: {round(cost_time,2)} s')

    async def service_master(account_id: int, region_id: int, ac_value: str = None):
        # 从数据库中获取user_recent和user_info数据
        result = await UserCache_Network.get_user_cache(account_id,region_id)
        if result.get('code', None) != 1000:
            recent_logger.error(f"{region_id} - {account_id} | ├── 网络请求失败，Error: {result.get('message')}")
            return