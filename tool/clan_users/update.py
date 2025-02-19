import time
import hashlib
import traceback

from log import log as logger
from network import Network
from utils import HashUtils
from model import check_and_insert_missing_users, update_clan_users, update_users_clan, update_clan_basic_and_info

class Update:
    @classmethod
    async def main(self, clan_id: int, region_id: int, clan_data: dict):
        '''UserCache更新入口函数
        '''
        start_time = time.time()
        try:
            logger.debug(f'{region_id} - {clan_id} | ┌── 开始用户更新流程')
            await self.service_master(self, clan_id, region_id, clan_data)
        except:
            error = traceback.format_exc()
            logger.error(f'{region_id} - {clan_id} | ├── 数据更新时发生错误')
            logger.error(f'Error: {error}')
        finally:
            cost_time = time.time() - start_time
            logger.debug(f'{region_id} - {clan_id} | └── 本次更新完成, 耗时: {round(cost_time,2)} s')

    async def service_master(self, clan_id: int, region_id: int, clan_data: dict):
        current_timestamp = int(time.time())
        if clan_data['clan_info']['update_time'] and clan_data['clan_users']['update_time'] and (
            current_timestamp - clan_data['clan_users']['update_time'] <= 24*60*60
        ):
            logger.debug(f'{region_id} - {clan_id} | ├── 未到达更新时间，跳过更新')
            return
        if clan_data['clan_info']['update_time']:
            result = await Network.get_basic_data(clan_id, region_id)
            if result.get('code', None) == 1002:
                clan_basic = {
                    'clan_id': clan_id,
                    'region_id': region_id,
                    'is_active': 0
                }
                logger.debug(f"{region_id} - {clan_id} | ├── 工会不存在，更新数据")
                self.update_clan_info(clan_id, region_id, clan_basic)
                return
            elif result.get('code', None) != 1000:
                return
            self.update_clan_users(clan_id, region_id, result['data']['clan_users']['clan_users'])
            return
        else:
            result = await Network.get_cache_data(clan_id, region_id)
            if result.get('code', None) == 1002:
                clan_basic = {
                    'clan_id': clan_id,
                    'region_id': region_id,
                    'is_active': 0
                }
                logger.debug(f"{region_id} - {clan_id} | ├── 工会不存在，更新数据")
                self.update_clan_info(clan_id, region_id, clan_basic)
                return
            elif result.get('code', None) != 1000:
                return
            self.update_clan_info(clan_id, region_id, result['data']['clan_basic'])
            self.update_clan_users(clan_id, region_id, result['data']['clan_users']['clan_users'])
            return
    
    def update_clan_users(clan_id: int, region_id: int, clan_users: list):
        # 首先检查传入的用户是否都在数据库中存在
        result = check_and_insert_missing_users(clan_users)
        if result.get('code', None) != 1000:
            logger.error(f"{region_id} - {clan_id} | ├── 数据库更新失败，Error: {result.get('code')} {result.get('message')}")
            return
        # 批量更新用户达到user_clan表
        user_data = []
        for user in clan_users:
            user_data.append(user[0])
        if len(user_data) != 0:
            result = update_users_clan(clan_id, user_data)
            if result.get('code', None) != 1000:
                logger.error(f"{region_id} - {clan_id} | ├── 数据库更新失败，Error: {result.get('code')} {result.get('message')}")
                return
        # 最后更新工会内所有用户的数据
        user_data.sort()
        hash_value = HashUtils.get_clan_users_hash(user_data)
        result = update_clan_users(clan_id, hash_value, user_data)
        if result.get('code', None) != 1000:
            logger.error(f"{region_id} - {clan_id} | ├── 数据库更新失败，Error: {result.get('code')} {result.get('message')}")
            return
        logger.debug(f"{region_id} - {clan_id} | ├── 工会User数据更新完成")
        return

    def update_clan_info(clan_id: int, region_id: int, clan_data: dict):
        # 更新clan_basic和clan_info表的信息
        result = update_clan_basic_and_info(clan_data)
        if result.get('code', None) != 1000:
            logger.error(f"{region_id} - {clan_id} | ├── 数据库更新失败，Error: {result.get('code')} {result.get('message')}")
            return
        logger.debug(f"{region_id} - {clan_id} | ├── 工会info数据更新完成")
        return
