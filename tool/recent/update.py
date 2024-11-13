import os
import time
import traceback

from log import log as recent_logger
from database import Recent_DB
from network import Recent_Network
from config import REGION_UTC_LIST, CLIENT_TYPE

special_time_dict = {
    0: 8*60*60,
    1: 8*60*60,
    2: 1*60*60,
    3: 2*60*60,
    4: 4*60*60,
    5: 4*60*60,
    6: 4*60*60,
    7: 6*60*60,
    8: 6*60*60,
    9: 8*60*60,
}
normal_time_dict = {
    0: 2*60*60,
    1: 2*60*60,
    2: 20*60,
    3: 30*60,
    4: 40*60,
    5: 1*60*60,
    6: 2*60*60,
    7: 3*60*60,
    8: 3*60*60,
    9: 4*60*60,
}

class Recent_Update:
    @classmethod
    async def main(self, account_id: int, region_id: int, ac_value: str = None):
        '''Recent数据库更新入口函数

        对于Slave服务来说，只是负责user_info的更新

        对于Master服务来说，还需要负责数据库的更新
        '''
        try:
            if CLIENT_TYPE == 'slave':
                await self.service_slave(self, account_id,region_id,ac_value)
            else:
                await self.service_master(self, account_id,region_id,ac_value)
        except:
            error = traceback.format_exc()
            recent_logger.error(f'{region_id} - {account_id} | 数据更新时发生错误')
            recent_logger.error(f'Error: {error}')
    
    async def service_slave(self, account_id: int, region_id: int, ac_value: str) -> None:
        result = await Recent_Network.get_user_info_data(account_id)
        if result.get('code', None) != 1000:
            recent_logger.error(f"{region_id} - {account_id} | 网络请求失败，Error: {result.get('message')}")
            return
        user_active_level = result['data']['active_level']
        user_update_time = result['data']['update_time']
        update_interval_seconds = self.get_update_interval_time(region_id,user_active_level)
        current_timestamp = int(time.time())
        if current_timestamp - user_update_time > update_interval_seconds:
            recent_logger.debug(f'{region_id} - {account_id} | 开始更新数据')
            user_basic = {
                'account_id': account_id,
                'region_id': region_id,
                'nickname': f'User_{account_id}'
            }
            # 用于更新user_info表的数据
            user_info = {
                'account_id': account_id,
                'is_active': 1,
                'active_level': 0,
                'is_public': 1,
                'total_battles': 0,
                'last_battle_time': 0
            }
            basic_data = await Recent_Network.get_basic_data(account_id,region_id,ac_value)
            for response in basic_data:
                if response['code'] != 1000 and response['code'] != 1001:
                    recent_logger.error(f"{region_id} - {account_id} | 网络请求失败，Error: {response.get('message')}")
                    return
            # 用户数据
            if basic_data[0]['code'] == 1001:
                # 用户数据不存在
                user_info['is_active'] = 0
                await self.update_user_info_data(account_id,region_id,user_info)
                request_result = await Recent_Network.del_user_recent(account_id,region_id)
                if request_result.get('code', None) != 1000:
                    recent_logger.error(f"{region_id} - {account_id} | 网络请求失败，Error: {request_result.get('message')}")
                else:
                    recent_logger.info(f'{region_id} - {account_id} | 删除用户，因为未有数据')
                return
            else:
                user_basic['nickname'] = basic_data[0]['data'][str(account_id)]['name']
                await self.update_user_basic_data(account_id,region_id,user_basic)
                if 'hidden_profile' in basic_data[0]['data'][str(account_id)]:
                    # 隐藏战绩
                    user_info['is_public'] = 0
                    user_info['active_level'] = self.get_active_level(user_info)
                    await self.update_user_info_data(account_id,region_id,user_info)
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
                    await self.update_user_info_data(account_id,region_id,user_info)
                    return
                # 获取user_info的数据并更新数据库
                user_info['total_battles'] = user_basic_data['basic']['leveling_points']
                user_info['last_battle_time'] = user_basic_data['basic']['last_battle_time']
                user_info['active_level'] = self.get_active_level(user_info)
                await self.update_user_info_data(account_id,region_id,user_info)
                return
        else:
            recent_logger.debug(f'{region_id} - {account_id} | 未到达更新时间，跳过更新')

    async def service_master(self, account_id: int, region_id: int, ac_value: str) -> None:
        # 从数据库中获取user_recent和user_info数据
        result = await Recent_Network.get_user_recent(account_id,region_id)
        if result.get('code', None) != 1000:
            recent_logger.error(f"{region_id} - {account_id} | 网络请求失败，Error: {result.get('message')}")
            return
        user_recent_result = result['data']['user_recent']
        user_info_result = result['data']['user_info']
        # 检查是否被丢弃
        if user_recent_result['recent_class'] == 0 or user_info_result['is_active'] == 0:
            await self.delete_user_recent(account_id, region_id)
            return
        current_timestamp = int(time.time())
        # 检查recent表中的数据，判断用户是否需要数据降级
        if current_timestamp - user_info_result['last_battle_time'] > 360*24*60*60:
            await self.delete_user_recent(account_id, region_id)
            return
        query_interval_seconds = current_timestamp - user_recent_result['last_query_time']
        if query_interval_seconds > 360*24*60*60:
            await self.delete_user_recent(account_id, region_id)
            return
        if query_interval_seconds > 90*24*60*60:
            if query_interval_seconds > 180*24*60*60:
                new_recent_class = 30
            else:
                new_recent_class = 60
            user_recent = {
                'account_id': account_id,
                'region_id': region_id,
                'recent_class': new_recent_class
            }
            await self.update_user_recent(user_recent)
            return
        new_user = False
        if user_info_result['is_active'] == -1:
            new_user = True
        recent_db_path = Recent_DB.get_recent_db_path(account_id,region_id)
        if os.path.exists(recent_db_path) == False:
            Recent_DB.create_user_db(recent_db_path)
            new_user = True
        # 用于搜索recent数据库的主键
        date_1 = time.strftime("%Y%m%d", time.localtime(current_timestamp))
        date_2 = time.strftime("%Y%m%d", time.localtime(current_timestamp-24*60*60))
        date_3 = time.strftime("%Y%m%d", time.localtime(current_timestamp-user_recent_result['recent_class']*24*60*60))
        # 从数据库中读取数据
        user_db_path = Recent_DB.get_recent_db_path(account_id,region_id)
        user_info_data = Recent_DB.get_user_info(user_db_path)
        if user_info_data == None or user_info_data == []:
            new_user = True
        else:
            # 检查存储的数据是否超过允许的储存的上限
            # 如果超过则删除超过部分的数据
            if len(user_info_data) > user_recent_result['recent_class'] + 1:
                del_table_dict = {}
                del_date_dict = {}
                # 获取需要删除date下的table_name
                for user_info in user_info_data:
                    if int(user_info[0]) < int(date_3):
                        del_table_dict[user_info[1]] = 0
                        del_date_dict[user_info[0]] = 0
                # 检查table_name是否在其他date中需要
                for user_info in user_info_data:
                    if int(user_info[0]) >= int(date_3):
                        if user_info[1] in del_table_dict:
                            del del_table_dict[user_info[1]]
                # 删除date和table
                del_date_number = Recent_DB.delete_date_and_table(user_db_path,del_date_dict.keys(),del_table_dict.keys())
                recent_logger.debug(f'{region_id} - {account_id} | 删除 {del_date_number} 天数据')
                
        # 判断是否是同一天，反之copy昨天的数据
        # 主要是确保每天都有数据，即使没有更新
        date_1_data = 0
        date_2_data = 0
        for user_info in user_info_data:
            if user_info[0] == date_1:
                date_1_data = 1
            if user_info[0] == date_2:
                date_2_data = 1
        if not date_1_data and date_2_data:
            if Recent_DB.copy_user_info(recent_db_path,date_1,date_2):
                recent_logger.info(f'{region_id} - {account_id} | 用户跨日数据复制')
                return
        elif not date_1_data and not date_2_data:
            new_user = True
        
        
        user_update_time = user_info_result['update_time']
        user_active_level = user_info_result['active_level']
        update_interval_seconds = self.get_update_interval_time(region_id,user_active_level)
        current_timestamp = int(time.time())
        if current_timestamp - user_update_time > update_interval_seconds:
            # 请求并更新usr_info
            recent_logger.debug(f'{region_id} - {account_id} | 用户开始更新')
        else:
            user_db_info = Recent_DB.get_user_info_by_date(recent_db_path,date_1)
            if not user_db_info or user_info_result['total_battles'] != user_db_info[3]:
                # 请求并更新user_info
                recent_logger.debug(f'{region_id} - {account_id} | 用户开始更新')
            else:
                recent_logger.debug(f'{region_id} - {account_id} | 用户不需要更新')
                return
        # 更新用户数据库
        user_basic = {
            'account_id': account_id,
            'region_id': region_id,
            'nickname': f'User_{account_id}'
        }
        # 用于更新user_info表的数据
        user_info = {
            'account_id': account_id,
            'is_active': True,
            'active_level': 0,
            'is_public': True,
            'total_battles': 0,
            'last_battle_time': 0
        }
        current_timestamp = int(time.time())
        date_1 = time.strftime("%Y%m%d", time.localtime(current_timestamp))
        date_2 = time.strftime("%Y%m%d", time.localtime(current_timestamp-24*60*60))
        basic_data = await Recent_Network.get_basic_data(account_id,region_id,ac_value)
        for response in basic_data:
            if response['code'] != 1000 and response['code'] != 1001:
                recent_logger.error(f"{region_id} - {account_id} | 网络请求失败，Error: {response.get('message')}")
                return
        
        # 用户数据
        if basic_data[0]['code'] == 1001:
            # 用户数据不存在
            user_info['is_active'] = False
            await self.update_user_info_data(account_id,region_id,user_info)
            request_result = await Recent_Network.del_user_recent(account_id,region_id)
            if request_result.get('code', None) != 1000:
                recent_logger.error(f"{region_id} - {account_id} | 网络请求失败，Error: {request_result.get('message')}")
            else:
                await self.delete_user_recent(account_id, region_id)
            return
        user_basic['nickname'] = basic_data[0]['data'][str(account_id)]['name']
        await self.update_user_basic_data(account_id,region_id,user_basic)
        if 'hidden_profile' in basic_data[0]['data'][str(account_id)]:
            # 隐藏战绩
            user_info['is_public'] = False
            user_info['active_level'] = self.get_active_level(user_info)
            await self.update_user_info_data(account_id,region_id,user_info)
            Recent_DB.insert_database(
                db_path=recent_db_path,
                date=date_1,
                valid=True,
                update_time=int(time.time()),
                level_point=0,
                karma=0,
                battles_count=None,
                table_name=None,
                ship_info_data=None
            )
            user_recent = {
                'account_id': account_id,
                'region_id': region_id,
                'last_update_time': current_timestamp
            }
            await Recent_Network.update_user_recent(user_recent)
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
            await self.update_user_info_data(account_id,region_id,user_info)
            await self.delete_user_recent(account_id, region_id)
            return
        # 获取user_info的数据并更新数据库
        user_info['total_battles'] = user_basic_data['basic']['leveling_points']
        user_info['last_battle_time'] = user_basic_data['basic']['last_battle_time']
        user_info['active_level'] = self.get_active_level(user_info)
        await self.update_user_info_data(account_id,region_id,user_info)
        if not new_user:
            user_db_info = Recent_DB.get_user_info_by_date(recent_db_path,date_1)
            if not user_db_info and user_info['total_battles'] == user_db_info[3]:
                recent_logger.debug(f'{region_id} - {account_id} | 未有数据，暂不需要更新')
                return
        user_details_data = await Recent_Network.get_recent_data(account_id,region_id,ac_value)
        for response in user_details_data:
            if response.get('code', None) != 1000:
                recent_logger.error(f"{region_id} - {account_id} | 网络请求失败，Error: {response.get('message')}")
        current_timestamp = int(time.time())
        details_data = Recent_Network.data_processing(account_id,user_details_data)
        if new_user:
            Recent_DB.insert_database(
                db_path=recent_db_path,
                date=date_2,
                valid=False,
                update_time=current_timestamp,
                level_point=user_basic_data['basic']['leveling_points'],
                karma=user_basic_data['basic']['karma'],
                battles_count=details_data['battles_count'],
                table_name=f'day_{date_2}',
                ship_info_data=details_data['ships']
            )
            Recent_DB.insert_database(
                db_path=recent_db_path,
                date=date_1,
                valid=False,
                update_time=current_timestamp,
                level_point=user_basic_data['basic']['leveling_points'],
                karma=user_basic_data['basic']['karma'],
                battles_count=details_data['battles_count'],
                table_name=f'day_{date_2}',
                ship_info_data=None
            )
        else:
            Recent_DB.insert_database(
                db_path=recent_db_path,
                date=date_1,
                valid=False,
                update_time=current_timestamp,
                level_point=user_basic_data['basic']['leveling_points'],
                karma=user_basic_data['basic']['karma'],
                battles_count=details_data['battles_count'],
                table_name=f'day_{date_1}',
                ship_info_data=details_data['ships']
            )
        user_recent = {
            'account_id': account_id,
            'region_id': region_id,
            'last_update_time': current_timestamp
        }
        await self.update_user_recent_data(account_id,region_id,user_recent)
        return
    
    async def update_user_recent_data(account_id: int, region_id: int, user_recent: dict) -> None:
        update_result = await Recent_Network.update_user_recent(user_recent)
        if update_result.get('code',None) != 1000:
            recent_logger.error(f"{region_id} - {account_id} | UserRecent数据更新失败，Error: {update_result.get('message')}")
        else:
            recent_logger.debug(f'{region_id} - {account_id} | UserRecent数据更新成功')

    async def update_user_info_data(account_id: int, region_id: int, user_info: dict) -> None:
        update_result = await Recent_Network.post_user_info_data(user_info)
        if update_result.get('code',None) != 1000:
            recent_logger.error(f"{region_id} - {account_id} | UserInfo数据更新失败，Error: {update_result.get('message')}")
        else:
            recent_logger.debug(f'{region_id} - {account_id} | UserInfo数据更新成功')

    async def update_user_basic_data(account_id: int, region_id: int, user_basic: dict) -> None:
        update_result = await Recent_Network.post_user_basic_data(user_basic)
        if update_result.get('code',None) != 1000:
            recent_logger.error(f"{region_id} - {account_id} | UserBasic数据更新失败，Error: {update_result.get('message')}")
        else:
            recent_logger.debug(f'{region_id} - {account_id} | UserBasic数据更新成功')

    async def delete_user_recent(account_id: int, region_id: int):
        "删除用户的recent功能"
        request_result = await Recent_Network.del_user_recent(account_id,region_id)
        if request_result.get('code', None) != 1000:
            recent_logger.error(f"{region_id} - {account_id} | 网络请求失败，Error: {request_result.get('message')}")
        else:
            recent_logger.info(f'{region_id} - {account_id} | 删除用户，因为长时间未活跃')

    async def update_user_recent(user_recent: dict):
        "更新用户的recent功能的数据"
        request_result = await Recent_Network.update_user_recent(user_recent)
        if request_result.get('code', None) != 1000:
            recent_logger.error(f"{user_recent['region_id']} - {user_recent['account_id']} | 网络请求失败，Error: {request_result.get('message')}")
        else:
            recent_logger.info(f"{user_recent['region_id']} - {user_recent['account_id']} | 用户存储降级，因为长时间未活跃")

    def get_active_level(user_info: dict):
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
        current_timestamp = time.time()
        time_zone = REGION_UTC_LIST[region_id]
        utc_time = time.gmtime(current_timestamp + time_zone * 3600)
        current_hour = time.strftime("%H", utc_time)
        if current_hour in ['22','23','00','01']:
            special_time = True
        else:
            special_time = False

        if special_time:
            update_interval_seconds = special_time_dict[active_level]
        else:
            update_interval_seconds = normal_time_dict[active_level]
        if CLIENT_TYPE == 'slave':
            return update_interval_seconds
        else:
            return update_interval_seconds * 2

