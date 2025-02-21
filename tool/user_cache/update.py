import time
import hashlib
import traceback

from log import log as logger
from network import Network
from model import (
    check_user_basic, 
    check_user_info, 
    get_user_cache, 
    check_existing_ship, 
    update_user_ship, 
    update_user_ships
)

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
        account_id = user_data['user_basic']['account_id']
        region_id = user_data['user_basic']['region_id']
        ac_value = user_data['user_basic']['ac_value']
        
        # 首先更新active_level和是否有缓存数据判断用户是否需要更新
        if user_data['user_ships']['update_time'] != None:
            active_level = user_data['user_info']['active_level']
            update_interval_seconds = self.get_update_interval_time(user_data['user_basic']['region_id'],active_level)
            current_timestamp = int(time.time())
            if user_data['user_ships']['update_time']:
                update_interval_time = self.seconds_to_time(current_timestamp - user_data['user_ships']['update_time'])
                logger.debug(f'{region_id} - {account_id} | ├── 距离上次更新 {update_interval_time}')
            if (current_timestamp - user_data['user_ships']['update_time']) < update_interval_seconds:
                logger.debug(f'{region_id} - {account_id} | ├── 未到达更新时间，跳过更新')
                return
        # 需要更新，则请求数据用户数据
        user_basic = {
            'account_id': account_id,
            'region_id': region_id,
            'nickname': f'User_{account_id}'
        }
        # 用于更新user_info表的数据
        user_info = {
            'account_id': account_id,
            'region_id': region_id,
            'is_active': 1,
            'active_level': 0,
            'is_public': 1,
            'total_battles': 0,
            'last_battle_time': 0
        }
        user_cache = {
            'account_id': account_id,
            'region_id': region_id,
            'battles_count': 0
        }
        basic_data = await Network.get_basic_data(account_id,region_id,ac_value)
        for response in basic_data:
            if response['code'] != 1000 and response['code'] != 1001:
                logger.error(f"{region_id} - {account_id} | ├── 网络请求失败，Error: {response.get('message')}")
                return
        # 用户数据
        if basic_data[0]['code'] == 1001:
            # 用户数据不存在
            user_info['is_active'] = 0
            self.update_user_info(account_id, region_id, user_info)
            self.update_user_cache(account_id, region_id, user_cache)
            return
        else:
            user_basic['nickname'] = basic_data[0]['data'][str(account_id)]['name']
            if 'hidden_profile' in basic_data[0]['data'][str(account_id)]:
                # 隐藏战绩
                user_info['is_public'] = 0
                user_info['active_level'] = self.get_active_level(user_info)
                self.update_user_basic(account_id, region_id, user_basic)
                self.update_user_info(account_id, region_id, user_info)
                self.update_user_cache(account_id, region_id, user_cache)
                return
            user_basic_data = basic_data[0]['data'][str(account_id)]['statistics']
            if (
                user_basic_data == {} or
                user_basic_data['basic'] == {}
            ):
                # 用户没有数据
                user_info['is_active'] = 0
                self.update_user_basic(account_id, region_id, user_basic)
                self.update_user_info(account_id, region_id, user_info)
                self.update_user_cache(account_id, region_id, user_cache)
                return
            if user_basic_data['basic']['leveling_points'] == 0:
                # 用户没有数据
                user_info['total_battles'] = 0
                user_info['last_battle_time'] = 0
                user_info['active_level'] = self.get_active_level(user_info)
                self.update_user_basic(account_id, region_id, user_basic)
                self.update_user_info(account_id, region_id, user_info)
                self.update_user_cache(account_id, region_id, user_cache)
                return
            # 获取user_info的数据并更新数据库
            user_info['total_battles'] = user_basic_data['basic']['leveling_points']
            user_info['last_battle_time'] = user_basic_data['basic']['last_battle_time']
            user_info['active_level'] = self.get_active_level(user_info)
        if user_data['user_ships']['battles_count'] == user_info['total_battles']:
            user_cache['battles_count'] = user_info['total_battles']
            self.update_user_basic(account_id, region_id, user_basic)
            self.update_user_info(account_id, region_id, user_info)
            self.update_user_cache(account_id, region_id, user_cache)
            logger.debug(f'{region_id} - {account_id} | ├── 未有更新数据，跳过更新')
            return
        user_ships_data = await Network.get_cache_data(account_id,region_id,ac_value)
        if user_ships_data.get('code', None) != 1000:
            return
        new_user_data = user_ships_data['data']
        sorted_dict = dict(sorted(new_user_data['basic'].items()))
        new_hash_value = hashlib.sha256(str(sorted_dict).encode('utf-8')).hexdigest()
        if user_data['user_ships']['hash_value'] == new_hash_value:
            logger.debug(f'{region_id} - {account_id} | ├── 未有更新数据，跳过更新')
            user_cache['battles_count'] = user_info['total_battles']
            self.update_user_basic(account_id, region_id, user_basic)
            self.update_user_info(account_id, region_id, user_info)
            self.update_user_cache(account_id, region_id, user_cache)
            return
        else:
            user_cache['battles_count'] = user_info['total_battles']
            user_cache['hash_value'] = new_hash_value
            user_cache['ships_data'] = sorted_dict
            user_cache['details_data'] = new_user_data['details']
            self.update_user_basic(account_id, region_id, user_basic)
            self.update_user_info(account_id, region_id, user_info)
            self.update_user_cache(account_id, region_id, user_cache)
            return

    def update_user_basic(account_id: int, region_id: int, user_data: dict):
        # 更新user_basic表的信息
        result = check_user_basic(user_data)
        if result.get('code', None) != 1000:
            logger.error(f"{region_id} - {account_id} | ├── 数据库更新失败，Error: {result.get('code')} {result.get('message')}")
            return
        logger.debug(f"{region_id} - {account_id} | ├── 用户basic数据更新完成")
        return

    def update_user_info(account_id: int, region_id: int, user_data: dict):
        # 更新user_info表信息
        result = check_user_info(user_data)
        if result.get('code', None) != 1000:
            logger.error(f"{region_id} - {account_id} | ├── 数据库更新失败，Error: {result.get('code')} {result.get('message')}")
            return
        logger.debug(f"{region_id} - {account_id} | ├── 用户info数据更新完成")
        return
    
    def update_user_cache(account_id: int, region_id: int, user_data: dict):
        user_cache_result = get_user_cache(account_id, region_id)
        if user_cache_result.get('code', None) != 1000:
            logger.error(f"{region_id} - {account_id} | ├── 获取用户缓存数据失败，Error: {user_cache_result.get('code')} {user_cache_result.get('message')}")
            return
        ship_id_set = set()
        delete_ship_list = []
        replace_ship_dict = {}
        ship_data = None
        if 'hash_value' in user_data:
            for ship_id, ship_battles in user_data['ships_data'].items():
                if (
                    int(ship_id) not in user_cache_result['data']['ships_data'] or 
                    ship_battles != user_cache_result['data']['ships_data']
                ):
                    replace_ship_dict[int(ship_id)] = user_data['details_data'][ship_id]
                    ship_id_set.add(int(ship_id))
            data = {
                'account_id': account_id,
                'region_id': region_id,
                'ship_dict': replace_ship_dict
            }
            check_ship_id_result = check_existing_ship(ship_id_set)
            if check_ship_id_result.get('code', None) != 1000:
                return check_ship_id_result
            if delete_ship_list != [] or replace_ship_dict != {}:
                ship_data = data
            del user_data['details_data']
        if user_data:
            result = update_user_ships(user_data)
            if result.get('code', None) != 1000:
                logger.error(f"{region_id} - {account_id} | ├── 数据库更新失败，Error: {result.get('code')} {result.get('message')}")
                return
            logger.debug(f"{region_id} - {account_id} | ├── 用户ships数据更新完成")
        if ship_data:
            result = update_user_ship(ship_data)
            if result.get('code', None) != 1000:
                logger.error(f"{region_id} - {account_id} | ├── 数据库更新失败，Error: {result.get('code')} {result.get('message')}")
                return
            logger.debug(f"{region_id} - {account_id} | ├── 用户cache数据更新完成")
        return

    def seconds_to_time(seconds: int) -> str:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02}:{minutes:02}:{secs:02}"

    def get_active_level(user_info: dict):
        "获取用户数据对应的active_level"
        is_public = user_info['is_public']
        total_battles = user_info['total_battles']
        last_battle_time = user_info['last_battle_time']
        if not is_public:
            return 0
        if total_battles == 0 or last_battle_time == 0:
            return 1
        current_timestamp = int(time.time())
        time_differences = [
            (1 * 24 * 60 * 60, 2),
            (3 * 24 * 60 * 60, 3),
            (7 * 24 * 60 * 60, 4),
            (30 * 24 * 60 * 60, 5),
            (90 * 24 * 60 * 60, 6),
            (180 * 24 * 60 * 60, 7),
            (360 * 24 * 60 * 60, 8),
        ]
        time_since_last_battle = current_timestamp - last_battle_time
        for time_limit, return_value in time_differences:
            if time_since_last_battle <= time_limit:
                return return_value
        return 9

    def get_update_interval_time(region_id: int, active_level: int):
        "获取active_level对应的更新时间间隔"
        normal_time_dict = {
            0: 20*24*60*60,
            1: 30*24*60*60,
            2: 1*24*60*60,
            3: 3*24*60*60,
            4: 5*24*60*60,
            5: 7*24*60*60,
            6: 10*24*60*60,
            7: 14*24*60*60,
            8: 20*24*60*60,
            9: 30*24*60*60,
        }
        update_interval_seconds = normal_time_dict[active_level]
        return update_interval_seconds
