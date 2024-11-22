import time
import hashlib
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

    async def service_master(self, user_data: dict):
        # 用于更新user_cache的数据
        account_id = user_data['user_basic']['account_id']
        region_id = user_data['user_basic']['region_id']
        ac_value = user_data['user_basic']['ac_value']
        
        # 首先更新active_level和是否有缓存数据判断用户是否需要更新
        if user_data['user_info']['update_time'] != None:
            active_level = user_data['user_info']['active_level']
            update_interval_time = self.get_update_interval_time(active_level)
            current_time = int(time.time())
            if current_time - user_data['user_ships']['update_time'] < update_interval_time:
                logger.debug(f'{region_id} - {account_id} | ├── 未到达更新时间，跳过更新')
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
        basic_data = await UserCache_Network.get_basic_data(account_id,region_id,ac_value)
        for response in basic_data:
            if response['code'] != 1000 and response['code'] != 1001:
                logger.error(f"{region_id} - {account_id} | ├── 网络请求失败，Error: {response.get('message')}")
                return
        # 用户数据
        if basic_data[0]['code'] == 1001:
            # 用户数据不存在
            user_info['is_active'] = 0
            await self.update_user_info_data(account_id,region_id,user_info)
            return
        else:
            user_basic['nickname'] = basic_data[0]['data'][str(account_id)]['name']
            # await self.update_user_basic_data(account_id,region_id,user_basic)
            if 'hidden_profile' in basic_data[0]['data'][str(account_id)]:
                # 隐藏战绩
                user_info['is_public'] = 0
                user_info['active_level'] = self.get_active_level(user_info)
                await self.update_user_basic_and_info_data(account_id,region_id,user_basic,user_info)
                return
            user_basic_data = basic_data[0]['data'][str(account_id)]['statistics']
            if (
                user_basic_data == {} or
                user_basic_data['basic'] == {} or
                user_basic_data['basic']['leveling_points'] == 0
            ):
                # 用户没有数据
                user_info['total_battles'] = 0
                user_info['last_battle_time'] = 0
                user_info['active_level'] = self.get_active_level(user_info)
                await self.update_user_basic_and_info_data(account_id,region_id,user_basic,user_info)
                return
            # 获取user_info的数据并更新数据库
            user_info['total_battles'] = user_basic_data['basic']['leveling_points']
            user_info['last_battle_time'] = user_basic_data['basic']['last_battle_time']
            user_info['active_level'] = self.get_active_level(user_info)
            await self.update_user_basic_and_info_data(account_id,region_id,user_basic,user_info)
        if user_data['user_ships']['battles_count'] == user_info['total_battles']:
            logger.debug(f'{region_id} - {account_id} | ├── 未有更新数据，跳过更新')
            return
        user_ships_data = await UserCache_Network.get_cache_data(account_id,region_id,ac_value)
        if user_ships_data.get('code', None) != 1000:
            return
        old_user_data = self.from_binary_data_dict(user_data['user_ships']['ships_data'])
        new_user_data = user_ships_data['data']
        sorted_dict = dict(sorted(new_user_data.items()))
        new_hash_value = hashlib.sha256(str(sorted_dict).encode('utf-8')).hexdigest()
        if user_data['user_ships']['hash_value'] == new_hash_value:
            logger.debug(f'{region_id} - {account_id} | ├── 未有更新数据，跳过更新')
            return
        user_cache = {
            'account_id': account_id,
            'region_id': region_id,
            'battles_count': user_info['total_battles'],
            'hash_value': new_hash_value,
            'ships_data': self.to_binary_data_dict(sorted_dict),
            'delete_ship_list': [],
            'replace_ship_dict': {}
        }
        for ship_id in new_user_data['basic'].keys():
            if ship_id not in old_user_data:
                user_cache['replace_ship_list'][ship_id] = new_user_data['details'][ship_id]
            if new_user_data['basic'][ship_id] != old_user_data[ship_id]:
                user_cache['replace_ship_list'][ship_id] = new_user_data['details'][ship_id]
        for ship_id in old_user_data.keys():
            if ship_id not in new_user_data['basic']:
                user_cache['delete_ship_list'].append(ship_id)
        await self.update_user_cache_data(account_id,region_id,user_cache)
        return

    async def update_user_cache_data(account_id: int, region_id: int, user_cache: dict) -> None:
        update_result = await UserCache_Network.update_user_cache_data(user_cache)
        if update_result.get('code',None) != 1000:
            logger.error(f"{region_id} - {account_id} | ├── UserCache数据更新失败，Error: {update_result.get('message')}")
        else:
            logger.debug(f'{region_id} - {account_id} | ├── UserCache数据更新成功')

    async def update_user_info_data(account_id: int, region_id: int, user_info: dict) -> None:
        update_result = await UserCache_Network.update_user_info_data(user_info)
        if update_result.get('code',None) != 1000:
            logger.error(f"{region_id} - {account_id} | ├── UserInfo数据更新失败，Error: {update_result.get('message')}")
        else:
            logger.debug(f'{region_id} - {account_id} | ├── UserInfo数据更新成功')

    # async def update_user_basic_data(account_id: int, region_id: int, user_basic: dict) -> None:
    #     update_result = await UserCache_Network.update_user_basic_data(user_basic)
    #     if update_result.get('code',None) != 1000:
    #         logger.error(f"{region_id} - {account_id} | ├── UserBasic数据更新失败，Error: {update_result.get('message')}")
    #     else:
    #         logger.debug(f'{region_id} - {account_id} | ├── UserBasic数据更新成功')

    async def update_user_basic_and_info_data(account_id: int, region_id: int, user_basic: dict = None, user_info: dict = None) -> None:
        data = {
            'basic': user_basic,
            'info': user_info
        }
        update_result = await UserCache_Network.update_user_basic_and_info_data(data)
        if update_result.get('code',None) != 1000:
            logger.error(f"{region_id} - {account_id} | ├── UserBasic数据更新失败，Error: {update_result.get('message')}")
            logger.error(f"{region_id} - {account_id} | ├── UserInfo数据更新失败，Error: {update_result.get('message')}")
        else:
            logger.debug(f'{region_id} - {account_id} | ├── UserBasic数据更新成功')
            logger.debug(f'{region_id} - {account_id} | ├── UserInfo数据更新成功')

    
    def from_binary_data_dict(self, binary_data):
        # 存储转换后的字典
        result = {}
        if binary_data is None or binary_data == b'\x00\x00\x00\x00\x00\x00\x00':
            return result
        # 每个数据项的字节数是 7 字节
        # 根据字节流的长度，计算出有多少个数据项
        num_items = len(binary_data) // 7
        for i in range(num_items):
            # 提取 7 字节的数据
            item_data = binary_data[i * 7:(i + 1) * 7]
            # 将字节数据转换为 key 和 value
            key, value = self.__from_binary_data(item_data)
            # 将 key 和 value 存入字典
            result[key] = value
        return result
    
    def to_binary_data_dict(self, data_dict):
        # 存储合并后的二进制数据
        result = bytearray()
        for key, value in data_dict.items():
            # 获取每个键值对的二进制数据并合并
            result.extend(self.__to_binary_data(key, value))
        # 返回合并后的二进制数据
        return bytes(result)
    
    def __to_binary_data(key, value):
        # 确保 key 和 value 都在允许的范围内
        if not (0 <= key < 2**34):
            raise ValueError("key must be a non-negative integer less than 2^34.")
        if not (0 <= value < 2**22):
            raise ValueError("value must be a non-negative integer less than 2^22.")
        # 将 key 和 value 转换为二进制字符串，确保它们有足够的位数
        key_bin = f'{key:034b}'  # 34 位二进制，确保 key 为 34 位
        value_bin = f'{value:022b}'  # 22 位二进制，确保 value 为 22 位
        # 将二进制字符串拼接成一个 56 位的字符串
        full_bin = key_bin + value_bin
        # 将 56 位二进制字符串按 8 位分割，并转换为字节
        byte_data = bytearray()
        for i in range(0, len(full_bin), 8):
            byte_data.append(int(full_bin[i:i+8], 2))  # 每 8 位转换为一个字节
        # 返回字节数据，应该是 7 字节大小
        return bytes(byte_data)
    
    def __from_binary_data(byte_data):
        # 确保字节数据的长度是7字节
        if len(byte_data) != 7:
            raise ValueError("Byte data must be exactly 7 bytes.")
        # 将字节数据转换为二进制字符串
        full_bin = ''.join(f'{byte:08b}' for byte in byte_data)
        # 提取前 34 位作为 key 和后 22 位作为 value
        key_bin = full_bin[:34]
        value_bin = full_bin[34:]
        # 将二进制字符串转换为整数
        key = int(key_bin, 2)
        value = int(value_bin, 2)
        return key, value

    def get_active_level(user_info: dict):
        "获取用户数据对应的active_level"
        is_public = user_info['is_public']
        total_battles = user_info['total_battles']
        last_battle_time = user_info['last_battle_time']
        if not is_public:
            return 0
        if total_battles == 0:
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
            0: 10*24*60*60,
            1: 20*24*60*60,
            2: 1*24*60*60,
            3: 3*24*60*60,
            4: 5*24*60*60,
            5: 7*24*60*60,
            6: 10*24*60*60,
            7: 14*24*60*60,
            8: 20*24*60*60,
            9: 25*24*60*60,
        }
        update_interval_seconds = normal_time_dict[active_level]
        return update_interval_seconds
