class PR_Algorithm:
    def get_pr_by_sid_and_region(
        sid: str,
        region: str,
        battle_type: str,
        ship_data: list
    ):
        '''
        计算船只数据的pr
        ship_data [battles,wins,damage,frag]
        '''
        result = {
            'value_battles_count': 0,
            'personal_rating': -1,
            'n_damage_dealt': -1,
            'n_frags': -1
        }
        # battles_count = ship_data[0]
        # if battles_count <= 0:
        #     return result
        # # 获取服务器数据
        # ship_data_class = Ship_Data()
        # server_data = ship_data_class.get_data_by_sid_and_region(
        #     sid=sid,
        #     region=region
        # )
        # if server_data == {}:
        #     return result
        # # 用户数据
        # actual_wins = ship_data[1] / battles_count * 100
        # actual_dmg = ship_data[2] / battles_count
        # actual_frags = ship_data[3] / battles_count
        # # 服务器数据
        # server_data: Ship_Data_Dict = server_data[sid]
        # expected_wins = server_data['win_rate']
        # expected_dmg = server_data['avg_damage']
        # expected_frags = server_data['avg_frags']
        # # 计算PR
        # # Step 1 - ratios:
        # r_wins = actual_wins / expected_wins
        # r_dmg = actual_dmg / expected_dmg
        # r_frags = actual_frags / expected_frags
        # # Step 2 - normalization:
        # n_wins = max(0, (r_wins - 0.7) / (1 - 0.7))
        # n_dmg = max(0, (r_dmg - 0.4) / (1 - 0.4))
        # n_frags = max(0, (r_frags - 0.1) / (1 - 0.1))
        # # Step 3 - PR value:
        # if battle_type in ['rank', 'rank_solo']:
        #     personal_rating = 600 * n_dmg + 350 * n_frags + 400 * n_wins
        # else:
        #     personal_rating = 700 * n_dmg + 300 * n_frags + 150 * n_wins
        # result['value_battles_count'] = battles_count
        # result['personal_rating'] = round(personal_rating * battles_count, 6)
        # result['n_damage_dealt'] = round((actual_dmg / expected_dmg) * battles_count, 6)
        # result['n_frags'] = round((actual_frags / expected_frags) * battles_count, 6)
        return result