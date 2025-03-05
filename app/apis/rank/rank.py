import os
import json
import pandas as pd

from app.log import ExceptionLogger
from app.response import JSONResponse
from app.middlewares import RedisConnection
from app.core import EnvConfig
from app.utils import TimeFormat

config = EnvConfig.get_config()

class Leaderboard:
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
    
    @ExceptionLogger.handle_program_exception_async
    async def get_paginated_data(ship_id: int, region_id: int, page: int = 1, page_size: int = 100):
        """按页读取排行榜数据"""
        csv_file = os.path.join(config.LEADER_PATH, f'{ship_id}.csv')
        if os.path.exists(csv_file) is False:
            return JSONResponse.API_1000_Success
        df = pd.read_csv(csv_file, encoding='utf-8')
        if region_id != 0:
            df = df[df['region_id'] == region_id]
        total_rows = len(df)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        if start_idx >= total_rows:
            return JSONResponse.API_1000_Success
        end_idx = min(end_idx, total_rows)
        df_page = df.iloc[start_idx:end_idx].copy()
        df_page['clan_tag'] = df_page['clan_tag'].apply(lambda x: x if pd.notna(x) else 'nan')
        df_page['clan_id'] = df_page['clan_id'].apply(lambda x: str(int(x)) if pd.notna(x) else 'nan')
        begin = start_idx + 1
        df_page.loc[:, 'rank'] = range(begin, begin + len(df_page))
        cols = ['rank'] + [col for col in df_page.columns if col != 'rank']
        df_page = df_page[cols]
        df_page = df_page.astype(str)
        page_data = df_page.to_dict(orient='records')
        last_modified = os.path.getmtime(csv_file)
        current_time = TimeFormat.get_current_timestamp()
        time_diff = current_time - last_modified
        minutes = int(time_diff // 60)
        cache_data = {
            'update_time': f"{minutes}m",
            'page_data': page_data
        }
        if len(page_data) != 0:
            redis = await RedisConnection.get_connection()
            json_data = json.dumps(cache_data)
            key = f"leaderboard:{region_id}:{ship_id}:{page}"
            await redis.setex(key, 1800, json_data)
        return JSONResponse.get_success_response(cache_data)