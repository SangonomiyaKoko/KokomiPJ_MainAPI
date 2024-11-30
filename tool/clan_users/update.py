import time
import hashlib
import traceback

from log import log as logger
from network import Network

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
            current_timestamp - clan_data['clan_users']['update_time'] <= 2*24*60*60
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
                await self.update_user_data(clan_id,region_id,clan_basic,None)
                logger.debug(f"{region_id} - {clan_id} | ├── 工会不存在，更新数据")
                return
            elif result.get('code', None) != 1000:
                return
            clan_users = {
                'clan_id': clan_id,
                'region_id': region_id,
                'hash_value': None,
                'user_list': None,
                'clan_users': None
            }
            new_hash_value = hashlib.sha256(str(result['data']['clan_users']['user_list']).encode('utf-8')).hexdigest()
            clan_users['hash_value'] = new_hash_value
            clan_users['user_list'] = result['data']['clan_users']['user_list']
            clan_users['clan_users'] = result['data']['clan_users']['clan_users']
            await self.update_user_data(clan_id,region_id,None,clan_users)
            return
        else:
            result = await Network.get_cache_data(clan_id, region_id)
            if result.get('code', None) == 1002:
                clan_basic = {
                    'clan_id': clan_id,
                    'region_id': region_id,
                    'is_active': 0
                }
                await self.update_user_data(clan_id,region_id,clan_basic,None)
                logger.debug(f"{region_id} - {clan_id} | ├── 工会不存在，更新数据")
                return
            elif result.get('code', None) != 1000:
                return
            clan_users = {
                'clan_id': clan_id,
                'region_id': region_id,
                'hash_value': None,
                'user_list': None,
                'clan_users': None
            }
            new_hash_value = hashlib.sha256(str(result['data']['clan_users']['user_list']).encode('utf-8')).hexdigest()
            clan_users['hash_value'] = new_hash_value
            clan_users['user_list'] = result['data']['clan_users']['user_list']
            clan_users['clan_users'] = result['data']['clan_users']['clan_users']
            await self.update_user_data(clan_id,region_id,result['data']['clan_basic'],clan_users)
            return

    async def update_user_data(
        clan_id: int, 
        region_id: int, 
        clan_basic: dict = None,
        clan_users: dict = None
    ) -> None:
        if clan_basic and clan_users:
            update_result = await Network.update_user_data({'clan_basic': clan_basic, 'clan_users': clan_users})
        else:
            if clan_basic:
                update_result = await Network.update_user_data({'clan_basic': clan_basic})
            if clan_users:
                update_result = await Network.update_user_data({'clan_users': clan_users})
        if update_result.get('code',None) != 1000:
            logger.error(f"{region_id} - {clan_id} | ├── 更新数据上传失败，Error: {update_result.get('message')}")
        else:
            logger.debug(f'{region_id} - {clan_id} | ├── 更新数据上传成功')
