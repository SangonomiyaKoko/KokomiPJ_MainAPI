from typing import List
from redis import Redis
from .server_utils import ShipData
from app.response import JSONResponse
from app.log import ExceptionLogger

class Rating_Algorithm:
    # 评分算法
    def get_pr_by_sid_and_region(
        ship_id: int,
        region_id: int,
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
        if not algo_type:
            return [0,-1,-1,-1]
        if algo_type == 'pr':
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
        
    def get_rating_class(
        algo_type: str, 
        rating: int | float, 
        show_eggshell: bool = False
    ):
        '''获取pr的等级以及距离下一级的差值

        其中启用彩蛋功能才会返回彩色评分
        
        '''
        if algo_type == 'pr':
            if rating == -2:
                return 0, 2
            if rating == -1:
                return 0, 1
            if show_eggshell:
                data = [750, 1100, 1350, 1550, 1750, 2100, 2450, 3250]
                for i in range(len(data)):
                    if rating < data[i]:
                        return i + 1, int(data[i]-rating)
                return 9, int(rating - 3250)
            else:
                data = [750, 1100, 1350, 1550, 1750, 2100, 2450]
                for i in range(len(data)):
                    if rating < data[i]:
                        return i + 1, int(data[i]-rating)
                return 8, int(rating - 2450)
        else:
            return 0, 2
        
    def get_content_class(
        algo_type: str, 
        index: int, 
        value: int | float
    ) -> int:
        index_list = [
            [45, 49, 51, 52.5, 55, 60, 70],
            [0.8, 0.95, 1.0, 1.1, 1.2, 1.4, 1.7],
            [0.2, 0.3, 0.6, 1.0, 1.3, 1.5, 2],
            [750, 1100, 1350, 1550, 1750, 2100, 2450]
        ]
        if algo_type == 'pr':
            if value == -2:
                return 0
            if value == -1:
                return 0
            data = index_list[index]
            for i in range(len(data)):
                if value < data[i]:
                    return i + 1
            return 8
        else:
            raise ValueError('Invaild Algorithm Parameters')
       
    @ExceptionLogger.handle_database_exception_async
    async def batch_pr_by_data(
        ship_id: int,
        region_id: int,
        algo_type: str,
        redis: Redis,
    ):

        from app.models.ship_rank import RankDataModel
        data = await RankDataModel.get_ship_data(ship_id, region_id)
        if data['code'] != 1000:
            print(ship_id, region_id, '无服务器数据')
            return None
        data = data['data']
        x = len(data)
        if algo_type == 'pr':
            result = {}
            # 获取服务器数据
            server_data = ShipData.get_ship_data_by_sid_and_rid(region_id, ship_id)
            if not server_data:
                return
            server_data = server_data[ship_id]
            if server_data == {}:
                return result
            expected_wins = server_data[0]
            expected_dmg = server_data[1]
            expected_frags = server_data[2]
            # excepted_exp = server_data[3]
            final_user_ship_data = {}
            final_pr = {}
            final_user_data = {}
            # 遍历用户数据
            for i in range(x):
                user_data = {}
                battles_count = data[i][1]
                actual_wins = data[i][2] / battles_count * 100
                actual_dmg = data[i][3] / battles_count
                actual_frags = data[i][4] / battles_count
                actual_exp = data[i][5] / battles_count
                lose_count = battles_count - data[i][2]
                user_id = data[i][0]
                # 计算PR
                r_wins = actual_wins / expected_wins
                r_dmg = actual_dmg / expected_dmg
                r_frags = actual_frags / expected_frags
                n_wins = max(0, (r_wins - 0.7) / (1 - 0.7))
                n_dmg = max(0, (r_dmg - 0.4) / (1 - 0.4))
                n_frags = max(0, (r_frags - 0.1) / (1 - 0.1))
                personal_rating = 700 * n_dmg + 300 * n_frags + 150 * n_wins
                cWins = (data[i][2] * 1.5 + lose_count) / battles_count
                cExp = actual_exp / cWins
                personal_rating = personal_rating + cExp * 0.2
                user_data = {
                    "Player": user_id,
                    "battle_count": battles_count,
                    "PR": round(personal_rating),
                    "win_rate": round(actual_wins, 2),
                    "avg_frag": round(actual_frags, 2),
                    "max_frag": data[i][8],
                    "avg_Dmg": round(actual_dmg),
                    "max_Dmg": data[i][7],
                    "avg_Exp": round(actual_exp),
                    "max_Exp": data[i][6],
                }
                final_pr[f"{user_id}"] = personal_rating
                final_user_ship_data[f"ship_data:{ship_id}:{user_id}"] = user_data
                user_data_response = await RankDataModel.get_user(user_id, region_id)
                if user_data_response['status'] == 'ok':
                    username = user_data_response['data'][0][0]
                    clan_id_response = await RankDataModel.get_clan_id(user_id)
                    if clan_id_response['status'] == 'ok':
                        clan_id = clan_id_response['data'][0][0]
                        if not clan_id:
                            clan = clan_id = league = 'NULL'
                        else:
                            clan_response = await RankDataModel.get_clan(clan_id, region_id)
                            clan_data = clan_response['data']
                            league = clan_data[0][1]
                            clan = clan_data[0][0]
                        user_data_dict = {
                            "username": username,
                            "clan_id": clan_id,
                            "clan_tag": clan,
                            "clan_rank": league
                        }
                        final_user_data[f"user_data:{user_id}"] = user_data_dict
                    else:
                        continue
                else:
                    continue
            pipeline = redis.pipeline()
            size = 100
            key = f"region:{region_id}:ship:{ship_id}"
            try:
                for i in range(0, len(final_pr), size):
                    batch = dict(list(final_pr.items())[i:i + size]) 
                    pipeline.zadd(key, batch)
                pipeline.expire(key, 3600)
                for hash_name, userdata in final_user_ship_data.items():
                    pipeline.hset(hash_name, mapping=userdata)
                    pipeline.expire(hash_name, 3600)
                for hash_name, userdata in final_user_data.items():
                    pipeline.hset(hash_name, mapping=userdata)
                    pipeline.expire(hash_name, 3600)
                pipeline.execute()
            except Exception as e:
                raise e
            return JSONResponse.get_success_response()
        else:
            raise ValueError('Invalid Algorithm Parameters')