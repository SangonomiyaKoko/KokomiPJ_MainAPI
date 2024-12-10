from app.utils.algo_utils import Rating_Algorithm
from app.utils.rank import Rank_utils
from app.models.ship_rank import RankDataModel

class Rank_tasks:
    async def get_ship_ids():
        '''获取所有船的id'''
        ship_ids = await RankDataModel.get_ship_id()
        return ship_ids
    
    async def update_rank():
        '''更新排行榜数据'''
        ship_ids = await Rank_tasks.get_ship_ids()
        for ship_id in ship_ids:
            for region_id in range(1, 6):
                await Rating_Algorithm.batch_pr_by_data(ship_id, region_id, "pr")
            Rank_utils.update_rank_all(ship_id)
        return 'ok'
        