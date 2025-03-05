import pandas as pd
from app.middlewares import RedisConnection
import os
import json

class Rank:
    async def rank(region_id, ship_id, page):
        """获取单船排名

        Args:
            region_id (int): 服务器id
            ship_id (int): 船只id
            page (int): 页码

        Returns:
            json: 排名数据
        """
        file_path = os.path.join('temp/leader/', f'{ship_id}.csv')
        df = pd.read_csv(file_path)
        r = await RedisConnection.get_connection(0)
        
        # 根据 region_id 过滤数据
        if region_id != 0:
            df = df[df['region_id'] == region_id]
        
        # 计算切片范围
        total_records = len(df)
        start_idx = (page - 1) * 100
        end_idx = min(start_idx + 100, total_records)  # 防止越界

        df_page = df.iloc[start_idx:end_idx].copy()

        begin = start_idx + 1

        df_page.loc[:, 'rank'] = range(begin, begin + len(df_page))
        
        cols = ['rank'] + [col for col in df_page.columns if col != 'rank']
        df_page = df_page[cols]
        
        data = df_page.to_dict(orient='records')
        
        key = f"leaderboard:{region_id}:{ship_id}:{page}"
        for player in data:
            player_json = json.dumps(player)
            await r.rpush(key, player_json)

        await r.expire(key, 1800)

        return data
