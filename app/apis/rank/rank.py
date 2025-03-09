import os
import json
import pandas as pd
import numpy as np

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
        if total_rows == 0:
            return JSONResponse.API_1000_Success
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
        last_modified = int(os.path.getmtime(csv_file))
        cache_data = {
            'update_time': last_modified,
            'page_data': page_data
        }
        if len(page_data) != 0:
            redis = await RedisConnection.get_connection()
            json_data = json.dumps(cache_data)
            key = f"leaderboard:{region_id}:{ship_id}:{page}"
            await redis.setex(key, 1800, json_data)
        return JSONResponse.get_success_response(cache_data)
    
    @ExceptionLogger.handle_program_exception_async
    async def get_user_data_by_sid(region_id: int, ship_id: int, account_id: int):
        """读取某个用户在榜中的位置"""
        csv_file = os.path.join(config.LEADER_PATH, f'{ship_id}.csv')
        if os.path.exists(csv_file) is False:
            return JSONResponse.API_1000_Success
        df = pd.read_csv(csv_file, encoding='utf-8')
        if region_id != 0:
            # 筛选后，index 还是原始 DataFrame 的索引，需要reset index
            df = df[df['region_id'] == region_id].reset_index(drop=True)
        total_rows = len(df)
        if total_rows == 0:
            return JSONResponse.API_1000_Success
        user_idx = df.index[df["account_id"] == account_id].to_list()
        if not user_idx:
            return JSONResponse.API_1000_Success
        user_idx = user_idx[0]
        # 计算 rating 分布
        new_rating = df["rating"].apply(lambda x: int(x.split("|")[1]) if isinstance(x, str) and "|" in x else None).dropna().astype(int)
        new_rating_df = pd.DataFrame({"rating": new_rating})
        max_rating = new_rating_df['rating'].max()
        min_rating = 0
        # 计算合理的 bin 范围，以10为步长
        bin_size = 200
        bins = np.arange(min_rating - (min_rating % bin_size), max_rating + bin_size, bin_size)
        # 使用 histogram 计算分布
        hist, bin_edges = np.histogram(new_rating_df, bins=bins)
        # 计算用户 rating 超过多少用户
        percentage = str(round((1 - (user_idx + 1) / total_rows) * 100, 2)) + '%'
        rank_data = {
            'rank': user_idx + 1,
            'percentage': percentage,
            'distribution': {
                'user_bin': None,
                'bins': bin_edges.tolist(),
                'counts': hist.tolist(),
                'sum': sum(hist.tolist())
            }
        }
        start_idx = max(0, user_idx - 5)
        end_idx = min(start_idx + 11, total_rows - 1)
        if total_rows > 11 and end_idx - start_idx < 11:
            start_idx = max(0, start_idx - (end_idx - start_idx))
        df_page = df.iloc[start_idx:end_idx].copy()
        df_page['clan_tag'] = df_page['clan_tag'].apply(lambda x: x if pd.notna(x) else 'nan')
        df_page['clan_id'] = df_page['clan_id'].apply(lambda x: str(int(x)) if pd.notna(x) else 'nan')
        begin = start_idx + 1
        df_page.loc[:, 'rank'] = range(begin, begin + len(df_page))
        cols = ['rank'] + [col for col in df_page.columns if col != 'rank']
        df_page = df_page[cols]
        df_page = df_page.astype(str)
        page_data = df_page.to_dict(orient="records")
        user_data = {
            'rating': None,
            'battles_count': None,
            'win_rate': None,
            'avg_dmg': None,
            'avg_frags': None,
            'avg_exp': None
        }
        for i in range(len(page_data)):
            if page_data[i]['account_id'] == str(account_id):
                page_data[i]['is_user'] = '1'
                user_data['rating'] = page_data[i]['rating']
                user_rating = eval(page_data[i]['rating'].split('|')[1] if '|' in page_data[i]['rating'] else page_data[i]['rating'])
                rank_data['distribution']['user_bin'] = int(user_rating / bin_size) * bin_size
                user_data['battles_count'] = page_data[i]['battles_count']
                user_data['win_rate'] = page_data[i]['win_rate']
                user_data['avg_dmg'] = page_data[i]['avg_dmg']
                user_data['avg_frags'] = page_data[i]['avg_frags']
                user_data['avg_exp'] = page_data[i]['avg_exp']
            else:
                page_data[i]['is_user'] = '0'
        cache_data = {
            'rank_data': rank_data,
            'user_data': user_data,
            'page_data': page_data
        }
        return JSONResponse.get_success_response(cache_data)