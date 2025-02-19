from app.middlewares import RedisConnection
from redis import Redis
class Rank_utils:
    async def update_rank_all(ship_id: int, redis : Redis):
        '''工具函数，根据各服务器排行榜更新总排行榜数据'''
        keys = [
            f'region:1:ship:{ship_id}',
            f'region:2:ship:{ship_id}',
            f'region:3:ship:{ship_id}',
            f'region:4:ship:{ship_id}',
            f'region:5:ship:{ship_id}',
        ]

        all_members = {}
    
        for key in keys:
            members = redis.zrange(key, 0, -1, withscores=True)
            
            for member, score in members:
                all_members[member] = score
        
        if all_members:
            redis.zadd(f'region:all:ship:{ship_id}', all_members)
            redis.expire(f'region:all:ship:{ship_id}', 3600)
        print(ship_id, "数据整合完成")