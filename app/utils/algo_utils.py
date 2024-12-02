from typing import List

from .server_utils import ShipData

class Rating_Algorithm:
    # 评分算法
    def get_pr_by_sid_and_region(
        ship_id: str,
        region_id: str,
        algo_type: str,
        game_type: str,
        ship_data: List[int]
    ):
        '''计算单条船只数据的评分数据

        一次只能计算一个船只的数据，每次计算都会从读取一次本地文件
        所以不适合进行批量计算评分数据，如需请使用其他方法

        注意，此处计算的pr值是带服务器修正后的数据

        参数:
            ship_id 船只id
            region_id 服务器id
            algo_type 评分算法
            game_type 数据对局类型 [pvp,rank,...]
            ship_data 用户的数据 [battles,wins,damage,frag]
        
        返回:
            Dict
        '''
        if algo_type == 'pr':
            result = {
                'value_battles_count': 0,
                'personal_rating': -1,
                'n_damage_dealt': -1,
                'n_frags': -1
            }
            battles_count = ship_data[0]
            if battles_count <= 0:
                return result
            # 获取服务器数据
            server_data = ShipData.get_ship_data_by_sid_and_rid(region_id,ship_id)
            if server_data == {}:
                return result
            # 用户数据
            actual_wins = ship_data[1] / battles_count * 100
            actual_dmg = ship_data[2] / battles_count
            actual_frags = ship_data[3] / battles_count
            # 服务器数据
            server_data = server_data[ship_id]
            expected_wins = server_data['win_rate']
            expected_dmg = server_data['avg_damage']
            expected_frags = server_data['avg_frags']
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
            if game_type in ['rank', 'rank_solo']:
                personal_rating = 600 * n_dmg + 350 * n_frags + 400 * n_wins
            else:
                personal_rating = 700 * n_dmg + 300 * n_frags + 150 * n_wins
            result['value_battles_count'] = battles_count
            result['personal_rating'] = round(personal_rating * battles_count, 6)
            result['n_damage_dealt'] = round((actual_dmg / expected_dmg) * battles_count, 6)
            result['n_frags'] = round((actual_frags / expected_frags) * battles_count, 6)
            return result
        
    def get_rating_by_data(
        algo_type: str,
        game_type: str,
        ship_data: List[int | float],
        server_data: List[int | float] | None
    ):
        if algo_type == 'pr':
            result = [0,-1,-1,-1]
            battles_count = ship_data[0]
            if battles_count <= 0:
                return result
            # 获取服务器数据
            if server_data == {}:
                return result
            # 用户数据
            actual_wins = ship_data[1] / battles_count * 100
            actual_dmg = ship_data[2] / battles_count
            actual_frags = ship_data[3] / battles_count
            # 服务器数据
            expected_wins = server_data[0]
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
            if game_type in ['rank', 'rank_solo']:
                personal_rating = 600 * n_dmg + 350 * n_frags + 400 * n_wins
            else:
                personal_rating = 700 * n_dmg + 300 * n_frags + 150 * n_wins
            return [
                battles_count,
                round(personal_rating * battles_count, 6),
                round((actual_dmg / expected_dmg) * battles_count, 6),
                round((actual_frags / expected_frags) * battles_count, 6)
            ]
        else:
            raise ValueError('Invaild Algorithm Parameters')