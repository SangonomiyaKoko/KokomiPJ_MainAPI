import os
import json
import time
import csv
import traceback

from log import log as logger
from config import settings
from model import get_ship_max_number, get_cache_batch, get_clan_tag, get_user_name


OLD_SHIP_ID_LIST = [
    '4281317360',
    '4285511376',
    '4181112624',
    '4292851408',
    '4283414224',
    '3763320816',
    '4289607376',
    '4292851696',
    '4277057520',
    '4181603792',
    '4184749520',
    '4179015472',
    '4284364496',
    '4183209776',
    '4287543280',
    '4180555216',
    '4181112816',
    '3762272240',
    '3762272048',
    '4284463088',
    '4290754544',
    '4184782288',
    '4277122768',
    '4183209968',
    '4280203248',
    '4288657392',
    '4288657104',
    '4288558800',
    '4179015664',
    '4282300400',
    '4183700944',
    '4282365648',
    '4279220208',
    '3763320528',
    '4287510224',
    '4282365936',
    '4279219920'
]

class Update:
    @classmethod
    async def main(self, ship_id: int, version: dict, user_cache: dict, clan_cache: dict, ship_data: dict):
        '''UserCache更新入口函数
        '''
        start_time = time.time()
        try:
            logger.debug(f'{ship_id} | ┌── 开始统计更新流程')
            await self.service_master(self, ship_id, version, user_cache, clan_cache, ship_data)
        except:
            error = traceback.format_exc()
            logger.error(f'{ship_id} | ├── 数据更新时发生错误')
            logger.error(f'Error: {error}')
        finally:
            cost_time = time.time() - start_time
            logger.debug(f'{ship_id} | └── 本次更新完成, 耗时: {round(cost_time,2)} s')

    async def service_master(self, ship_id: int, version: dict, user_cache: dict, clan_cache: dict, ship_data: dict):
        request_result = get_ship_max_number(ship_id)
        if request_result['code'] != 1000:
            logger.error(f"{ship_id} | ├── 获取表MaxID时发生错误，Error: {request_result.get('message')}")
            return
        max_offset = request_result['data']['max_id']
        limit = 1000
        offset = 0
        total_result = {
            0: {}, 1: {}, 2: {}, 3: {}, 4: {}, 5: {}
        }
        status_result = {
            0: {}, 1: {}, 2: {}, 3: {}, 4: {}, 5: {}
        }
        overall_result = {}
        leader_list = []    # 符合排行榜场次的用户
        update_keys = [
            'battles_count', 'wins', 'damage_dealt',
            'frags', 'exp', 'survived', 'scouting_damage',
            'art_agro', 'planes_killed'
        ]
        ship_tier = ship_data.get(ship_id, 1)
        leaderboard_limit = {
            6: 40, 7: 40,
            8: 40, 9: 50,
            10: 60, 11: 60
        }
        while offset <= max_offset:
            cache_result = get_cache_batch(ship_id, offset, limit)
            if cache_result['code'] == 1000:
                i = 1
                for user in cache_result['data']:
                    if user['battles_count'] >= leaderboard_limit.get(ship_tier, 99999):
                        leader_list.append(user)
                    region_id = user['region_id']
                    if total_result[0] == {}:
                        for key in update_keys:
                            total_result[0][key] = 0
                    if total_result[region_id] == {}:
                        for key in update_keys:
                            total_result[region_id][key] = 0
                    else:
                        for key in update_keys:
                            total_result[0][key] += user[key]
                            total_result[region_id][key] += user[key]
                    i += 1
            else:
                logger.error(f"{ship_id} | ├── 获取cache时发生错误，Error: {cache_result.get('message')}")
            offset += limit
        for region_id in total_result.keys():
            if total_result[region_id] != {}:
                for key in update_keys:
                    status_result[region_id][key] = 0
                if total_result[region_id][update_keys[0]] == 0:
                    continue
                status_result[region_id][update_keys[0]] = total_result[region_id][update_keys[0]]
                for key in update_keys[1:]:
                    status_result[region_id][key] = round(total_result[region_id][key]/total_result[region_id][update_keys[0]],6)
        for key in update_keys[1:]:
            sum_times = 0
            sum_value = 0
            for region_id in [1, 2, 3, 4, 5]:
                if status_result[region_id] != {} and status_result[region_id]['battles_count'] != 0:
                    sum_value += status_result[region_id][key]
                    sum_times += 1
            if sum_times:
                overall_result['key'] = round(sum_value/sum_times,6)
        for region_id in [0, 1, 2, 3, 4, 5]:
            if region_id != 0:
                result = {
                    'total': total_result[region_id],
                    'status': status_result[region_id]
                }
            else:
                result = {
                    'total': total_result[region_id],
                    'status': status_result[region_id],
                    'overview': overall_result,
                    'region': {
                        '1': status_result[1],
                        '2': status_result[2],
                        '3': status_result[3],
                        '4': status_result[4],
                        '5': status_result[5]
                    }
                }
            if result['total'] == {}:
                continue
            if region_id == 0:
                file_path = os.path.join(settings.CACHE_PATH, 'main.json')
                self.update_json(file_path, ship_id, result)
            else:
                region_version = version.get(region_id)[0]
                file_path = os.path.join(settings.CACHE_PATH, str(region_id), f'{region_version}.json')
                self.update_json(file_path, ship_id, result)
        # 用户缓存数据读取
        logger.debug(f"{ship_id} | ├── 船只服务器数据更新完成")
        if str(ship_id) in OLD_SHIP_ID_LIST or ship_tier <= 5:
            logger.debug(f"{ship_id} | ├── 船只不符合排行榜要求")
            return
        nocache_user = []
        nocache_clan = []
        for user in leader_list:
            if user['account_id'] not in user_cache:
                nocache_user.append([user['region_id'], user['account_id']])
        user_cache_result = get_user_name(nocache_user)
        if user_cache_result['code'] != 1000:
            logger.error(f"{ship_id} | ├── 读取用户名称数据失败")
        else:
            for k, v in user_cache_result['data'].items():
                user_cache[k] = [v[0], v[2], v[3]]
                if v[2] and v[2] not in clan_cache:
                    nocache_clan.append([v[1], v[2]])
            logger.debug(f"{ship_id} | ├── 读取 {len(nocache_user)} 个用户缓存")
        clan_cache_result = get_clan_tag(nocache_clan)
        if clan_cache_result['code'] != 1000:
            logger.error(f"{ship_id} | ├── 读取工会名称数据失败")
        else:
            for k, v in clan_cache_result['data'].items():
                clan_cache[k] = [v[0], v[1]]
            logger.debug(f"{ship_id} | ├── 读取 {len(nocache_clan)} 个工会缓存")
        # 计算排行榜
        leaderboard = {}
        sort_dict = {}
        remove_user = 0
        for user in leader_list:
            user_info = user_cache.get(user['account_id'], ['NULL', None, 0])
            clan_info = clan_cache.get(user_info[1], ['NULL', 5]) if user_info[1] else None
            if user_info[2] == 9:
                remove_user += 1
                continue
            battles_count = user['battles_count']
            user_ship_data = [
                battles_count, user['wins'], user['damage_dealt'], user['frags']
            ]
            basic_rating = self.get_rating_by_data(
                ship_data = user_ship_data,
                server_data = [
                    status_result[0]['wins'], 
                    status_result[0]['damage_dealt'], 
                    status_result[0]['frags']
                ] if status_result[0]['battles_count'] >= 1000 else {}
            )
            region_rating = self.get_rating_by_data(
                ship_data = user_ship_data,
                server_data = [
                    status_result[user['region_id']]['wins'], 
                    status_result[user['region_id']]['damage_dealt'], 
                    status_result[user['region_id']]['frags']
                ] if status_result[user['region_id']]['battles_count'] >= 1000 else {}
            )
            if region_rating[0] == -1:
                continue
            sort_dict[user['account_id']] = region_rating[0]
            rating_diff = int(region_rating[0]) - int(basic_rating[0])
            rating_info = str(int(basic_rating[0])) + (' + ' + str(rating_diff) if rating_diff >= 0 else ' - ' + str(abs(rating_diff)))
            temp = {
                # 用户信息
                'account_id': str(user['account_id']),
                'region_id': str(user['region_id']),
                'clan_id': user_info[1],
                'user_name': user_info[0],
                'clan_tag': str(clan_info[1]) + '|' + clan_info[0] if clan_info else None,
                # 场次
                'battles_count': str(user['battles_count']),
                'battle_type': str(self.get_content_class(4, user['battle_type_1']/battles_count*100)) + '|' + str(round(user['battle_type_1']/battles_count*100,2)),
                # 评分
                'rating': str(self.get_content_class(3, region_rating[0])) + '|' + str(int(region_rating[0])),
                'rating_info': rating_info,
                # 基本数据
                'win_rate': str(self.get_content_class(0, user['wins']/battles_count*100)) + '|' + str(round(user['wins']/battles_count*100, 2)),
                'avg_dmg': str(self.get_content_class(1, region_rating[1])) + '|' + str(int(user['damage_dealt']/battles_count)),
                'avg_frags': str(self.get_content_class(2, region_rating[2])) + '|' + str(round(user['frags']/battles_count, 2)),
                'avg_exp': str(int(user['exp']/battles_count)),
                # 最高记录
                'max_dmg': str(user['max_damage_dealt']),
                'max_frags': str(user['max_frags']),
                'max_exp': str(user['max_exp'])
            }
            leaderboard[user['account_id']] = temp
        logger.debug(f"{ship_id} | ├── 不活跃下榜用户数量 {remove_user}")
        sorted_dict = dict(sorted(sort_dict.items(), key=lambda item: item[1], reverse=True))
        if len(sorted_dict) == 0:
            return
        i = 0
        data = []
        region_ids = {
            '1': 'Asia',
            '2': 'Eu',
            '3': 'Na',
            '4': 'Ru',
            '5': 'Cn'
        }
        for k, _ in sorted_dict.items():
            user_data = leaderboard[k]
            user_data['region'] = region_ids.get(user_data['region_id'])
            user_data['battle_type'] = user_data['battle_type'] + '%'
            user_data['win_rate'] = user_data['win_rate'] + '%'
            data.append(user_data)
            i += 1
        csv_file_path = os.path.join(settings.LEADER_PATH, f'{ship_id}.csv')
        fields = ['region', 'region_id', 'clan_tag', 'clan_id', 'user_name', 'account_id', 'battles_count', 'battle_type', 'rating', 'rating_info', 'win_rate', 'avg_dmg', 'avg_frags', 'avg_exp', 'max_dmg', 'max_frags', 'max_exp']
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()  # 写入表头
            writer.writerows(data)  # 写入数据
        logger.debug(f"{ship_id} | ├── 排行榜数据更新完成")
        return 
    
    def update_json(file_path: str, ship_id: int, ship_data: dict):
        if os.path.exists(file_path):
            data = None
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                data = {}  # 解析失败或文件不存在时返回默认值
            data[str(ship_id)] = ship_data
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(json.dumps(data, ensure_ascii=False))
        else:
            data = {}
            data[str(ship_id)] = ship_data
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(json.dumps(data, ensure_ascii=False))
        
    def get_rating_by_data(
        ship_data: list,
        server_data: list
    ):
        '''计算pr

        ship_data [battles_count, actual_wins, actual_dmg, actual_frags]
        server_data [expected_wins, expected_dmg, expected_frags]
        '''
        battles_count = ship_data[0]
        if battles_count <= 0:
            return [0,-1,-1,-1]
        # 获取服务器数据
        if server_data == {} or server_data is None:
            return [0,-1,-1,-1]
        # 用户数据
        actual_wins = ship_data[1] / battles_count * 100
        actual_dmg = ship_data[2] / battles_count
        actual_frags = ship_data[3] / battles_count
        # 服务器数据
        expected_wins = server_data[0]*100
        expected_dmg = server_data[1]
        expected_frags = server_data[2]
        # 计算PR
        # Step 1 - ratios:
        r_wins = actual_wins / expected_wins
        r_dmg = actual_dmg / expected_dmg
        r_frags = actual_frags / expected_frags
        # Step 2 - normalization:
        n_wins = max(0, (r_wins - 0.7) / (1 - 0.7))
        n_dmg = max(0, (r_dmg - 0.4) / (1 - 0.4))
        n_frags = max(0, (r_frags - 0.1) / (1 - 0.1))
        # Step 3 - PR value:
        personal_rating = 700 * n_dmg + 300 * n_frags + 150 * n_wins
        return [
            round(personal_rating, 6),
            round(actual_dmg / expected_dmg, 6),
            round(actual_frags / expected_frags, 6)
        ]
        
    def get_content_class(
        index: int, 
        value: int | float
    ) -> int:
        '''index [wr, dmg, frag, pr, sr]'''
        index_list = [
            [45, 49, 51, 52.5, 55, 60, 70],
            [0.8, 0.95, 1.0, 1.1, 1.2, 1.4, 1.7],
            [0.2, 0.3, 0.6, 1.0, 1.3, 1.5, 2],
            [750, 1100, 1350, 1550, 1750, 2100, 2450],
            [10, 30, 40, 50, 60, 70, 80]
        ]
        if value == -2:
            return 0
        if value == -1:
            return 0
        data = index_list[index]
        for i in range(len(data)):
            if value < data[i]:
                return i + 1
        return 8
    