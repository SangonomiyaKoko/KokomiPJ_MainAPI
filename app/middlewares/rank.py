from app.utils.algo_utils import Rating_Algorithm
from app.utils.rank import Rank_utils
from app.models.ship_rank import RankDataModel
import asyncio
import multiprocessing

import asyncio
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from app.middlewares import RedisConnection
import asyncio
from redis import Redis
        
class Rank_tasks:
    @staticmethod
    async def get_ship_ids():
        '''获取所有船的id'''
        ship_ids = await RankDataModel.get_ship_id()
        ship_ids = ship_ids['data']
        return ship_ids
    
    @staticmethod
    async def update_rank():
        '''更新排行榜数据'''
        ship_ids = await Rank_tasks.get_ship_ids()
        cpu_counts = min(multiprocessing.cpu_count() * 2, 61)
        size = (len(ship_ids) + cpu_counts - 1) // cpu_counts
        chunks = [ship_ids[i:i+size] for i in range(0, len(ship_ids), size)]
        
        # 启动多进程
        with ProcessPoolExecutor(max_workers=cpu_counts) as executor:
            # 将每个 chunk 提交到进程池
            await asyncio.gather(
                *[asyncio.get_event_loop().run_in_executor(executor, Rank_tasks.process, chunk) for chunk in chunks]
            )
        
        return 'ok'
    
    @staticmethod
    def process(chunk):
        redis_connection = Redis(host='localhost', port=6379, db=3)
        
        for ship_id_ in chunk:
            for ship_id in ship_id_:
                for region_id in range(1, 6):
                    asyncio.run(Rating_Algorithm.batch_pr_by_data(ship_id, region_id, "pr", redis_connection))
                asyncio.run(Rank_utils.update_rank_all(ship_id, redis_connection))