import httpx
import asyncio
from typing import Optional
from datetime import datetime

from log import log as logger

CLAN_API_URL_LIST = {
    1: 'https://clans.worldofwarships.asia',
    2: 'https://clans.worldofwarships.eu',
    3: 'https://clans.worldofwarships.com',
    4: 'https://clans.korabli.su',
    5: 'https://clans.wowsgame.cn'
}

REGION_LIST = {
    1: 'asia',
    2: 'eu',
    3: 'na',
    4: 'ru',
    5: 'cn'
}

clan_url_dict = {
    1: [
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=sg&league=0&division=1&offset=0&limit=1000',
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=sg&league=1&division=1&offset=0&limit=1000',
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=sg&league=1&division=2&offset=0&limit=1000',
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=sg&league=1&division=3&offset=0&limit=1000',
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=sg&league=2&division=1&offset=0&limit=1000',
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=sg&league=2&division=2&offset=0&limit=1000',
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=sg&league=2&division=3&offset=0&limit=1000',
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=sg&league=3&division=1&offset=0&limit=1000',
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=sg&league=3&division=2&offset=0&limit=1000',
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=sg&league=3&division=3&offset=0&limit=1000',
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=sg&league=4&division=1&offset=0&limit=1000',
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=sg&league=4&division=2&offset=0&limit=1000',
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=sg&league=4&division=3&offset=0&limit=1000'
    ],
    2: [
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=eu&league=0&division=1&offset=0&limit=1000',
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=eu&league=1&division=1&offset=0&limit=1000',
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=eu&league=1&division=2&offset=0&limit=1000',
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=eu&league=1&division=3&offset=0&limit=1000',
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=eu&league=2&division=1&offset=0&limit=1000',
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=eu&league=2&division=2&offset=0&limit=1000',
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=eu&league=2&division=3&offset=0&limit=1000',
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=eu&league=3&division=1&offset=0&limit=1000',
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=eu&league=3&division=2&offset=0&limit=1000',
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=eu&league=3&division=3&offset=0&limit=1000',
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=eu&league=4&division=1&offset=0&limit=1000',
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=eu&league=4&division=2&offset=0&limit=1000',
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=eu&league=4&division=3&offset=0&limit=1000'
    ],
    3: [
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=us&league=0&division=1&offset=0&limit=1000',
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=us&league=1&division=1&offset=0&limit=1000',
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=us&league=1&division=2&offset=0&limit=1000',
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=us&league=1&division=3&offset=0&limit=1000',
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=us&league=2&division=1&offset=0&limit=1000',
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=us&league=2&division=2&offset=0&limit=1000',
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=us&league=2&division=3&offset=0&limit=1000',
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=us&league=3&division=1&offset=0&limit=1000',
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=us&league=3&division=2&offset=0&limit=1000',
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=us&league=3&division=3&offset=0&limit=1000',
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=us&league=4&division=1&offset=0&limit=1000',
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=us&league=4&division=2&offset=0&limit=1000',
        'https://clans.worldofwarships.asia/api/ladder/structure/?realm=us&league=4&division=3&offset=0&limit=1000'
    ],
    4: [
        'https://clans.korabli.su/api/ladder/structure/?realm=ru&league=0&division=1&offset=0&limit=1000',
        'https://clans.korabli.su/api/ladder/structure/?realm=ru&league=1&division=1&offset=0&limit=1000',
        'https://clans.korabli.su/api/ladder/structure/?realm=ru&league=1&division=2&offset=0&limit=1000',
        'https://clans.korabli.su/api/ladder/structure/?realm=ru&league=1&division=3&offset=0&limit=1000',
        'https://clans.korabli.su/api/ladder/structure/?realm=ru&league=2&division=1&offset=0&limit=1000',
        'https://clans.korabli.su/api/ladder/structure/?realm=ru&league=2&division=2&offset=0&limit=1000',
        'https://clans.korabli.su/api/ladder/structure/?realm=ru&league=2&division=3&offset=0&limit=1000',
        'https://clans.korabli.su/api/ladder/structure/?realm=ru&league=3&division=1&offset=0&limit=1000',
        'https://clans.korabli.su/api/ladder/structure/?realm=ru&league=3&division=2&offset=0&limit=1000',
        'https://clans.korabli.su/api/ladder/structure/?realm=ru&league=3&division=3&offset=0&limit=1000',
        'https://clans.korabli.su/api/ladder/structure/?realm=ru&league=4&division=1&offset=0&limit=1000',
        'https://clans.korabli.su/api/ladder/structure/?realm=ru&league=4&division=2&offset=0&limit=1000',
        'https://clans.korabli.su/api/ladder/structure/?realm=ru&league=4&division=3&offset=0&limit=1000'
    ],
    5: [
        'https://clans.wowsgame.cn/api/ladder/structure/?realm=cn360&league=0&division=1&offset=0&limit=1000',
        'https://clans.wowsgame.cn/api/ladder/structure/?realm=cn360&league=1&division=1&offset=0&limit=1000',
        'https://clans.wowsgame.cn/api/ladder/structure/?realm=cn360&league=1&division=2&offset=0&limit=1000',
        'https://clans.wowsgame.cn/api/ladder/structure/?realm=cn360&league=1&division=3&offset=0&limit=1000',
        'https://clans.wowsgame.cn/api/ladder/structure/?realm=cn360&league=2&division=1&offset=0&limit=1000',
        'https://clans.wowsgame.cn/api/ladder/structure/?realm=cn360&league=2&division=2&offset=0&limit=1000',
        'https://clans.wowsgame.cn/api/ladder/structure/?realm=cn360&league=2&division=3&offset=0&limit=1000',
        'https://clans.wowsgame.cn/api/ladder/structure/?realm=cn360&league=3&division=1&offset=0&limit=1000',
        'https://clans.wowsgame.cn/api/ladder/structure/?realm=cn360&league=3&division=2&offset=0&limit=1000',
        'https://clans.wowsgame.cn/api/ladder/structure/?realm=cn360&league=3&division=3&offset=0&limit=1000',
        'https://clans.wowsgame.cn/api/ladder/structure/?realm=cn360&league=4&division=1&offset=0&limit=1000',
        'https://clans.wowsgame.cn/api/ladder/structure/?realm=cn360&league=4&division=2&offset=0&limit=1000',
        'https://clans.wowsgame.cn/api/ladder/structure/?realm=cn360&league=4&division=3&offset=0&limit=1000'
    ]
}

class Network:
    async def fetch_data(url, method: str = 'get', data: Optional[dict] = None):
        async with httpx.AsyncClient() as client:
            try:
                if method == 'get':
                    res = await client.get(url, timeout=5)
                elif method == 'delete':
                    res = await client.delete(url, timeout=5)
                elif method == 'post':
                    res = await client.post(url, json=data, timeout=5)
                elif method == 'put':
                    res = await client.put(url, json=data, timeout=5)
                else:
                    return {'status': 'ok','code': 7000,'message': 'InvalidParameter','data': None}
                requset_code = res.status_code
                requset_result = res.json()
                if requset_code == 200:
                    if '//clans.' in url:
                        return {'status': 'ok','code': 1000,'message': 'Success','data': requset_result}
                    else:
                        return requset_result
                elif requset_code == 503 and '//clans.' in url:
                    return {'status': 'ok','code': 1002,'message': 'ClanNotExist','data' : None}
                return {'status': 'ok','code': 2000,'message': 'NetworkError','data': None}
            except httpx.ConnectTimeout:
                return {'status': 'ok','code': 2001,'message': 'NetworkError','data': None}
            except httpx.ReadTimeout:
                return {'status': 'ok','code': 2002,'message': 'NetworkError','data': None}
            except httpx.TimeoutException:
                return {'status': 'ok','code': 2003,'message': 'NetworkError','data': None}
            except httpx.ConnectError:
                return {'status': 'ok','code': 2004,'message': 'NetworkError','data': None}
            except httpx.ReadError:
                return {'status': 'ok','code': 2005,'message': 'NetworkError','data': None}

    # @classmethod
    # async def update_clan_data(self, clan_data: dict):
    #     platform_api_url = API_URL
    #     url = f'{platform_api_url}/p/game/clan/update/'
    #     result = await self.fetch_data(url, method='put', data=clan_data)
    #     if result.get('code', None) == 2004:
    #         logger.debug(f"0 | ├── 接口请求失败，休眠 5 s")
    #         await asyncio.sleep(5)
    #         result = await self.fetch_data(url, method='put', data=clan_data)
    #     elif result.get('code', None) == 8000:
    #         logger.debug(f"0 | ├── 服务器维护中，休眠 60 s")
    #         await asyncio.sleep(60)
    #         result = await self.fetch_data(url, method='put', data=clan_data)
    #     return result

    @classmethod
    async def get_clan_rank_data(self, region_id: int):
        season_number = None
        clan_data_list = []
        urls = clan_url_dict.get(region_id)
        i = 0
        for url in urls:
            i += 1
            result = await self.fetch_data(url)
            if result.get('code', None) != 1000:
                logger.debug(f"{region_id} | ├── 网络请求失败，Error: {result.get('code')} {result.get('message')}")
                continue
            else:
                logger.debug(f"{region_id} | ├── 第 {i}/13 个API请求成功")
            season, data = self.__clan_data_processing(result)
            if season == None:
                continue
            if season_number == None:
                season_number = season
            if season_number != season:
                return None, []
            clan_data_list = clan_data_list + data
        return season_number, clan_data_list
    
    @classmethod
    async def get_clan_cvc_data(self, clan_id: int, region_id: int, season: int):
        api_url = CLAN_API_URL_LIST.get(region_id)
        url = f'{api_url}/api/members/{clan_id}/?battle_type=cvc'
        result = await self.fetch_data(url)
        if result.get('code', None) != 1000:
            return result
        else:
            if result['data']['is_hidden_statistics']:
                return None
            else:
                result = self.__cvc_data_processing(clan_id, region_id, season, result)
                return {'status': 'ok', 'code': 1000, 'message': 'Success', 'data': result}
    
    @classmethod
    async def get_clan_cvc_data2(self, clan_id: int, region_id: int, season: int):
        api_url = CLAN_API_URL_LIST.get(region_id)
        url = f'{api_url}/api/clanbase/{clan_id}/claninfo/'
        result = await self.fetch_data(url)
        if result.get('code', None) != 1000:
            return result
        else:
            result = self.__cvc_data2_processing(clan_id, region_id, season, result)
            return {'status': 'ok', 'code': 1000, 'message': 'Success', 'data': result}

    def __clan_data_processing(response: dict) -> tuple:
        result = []
        season_number = None
        for temp_data in response['data']:
            if season_number == None:
                season_number = temp_data['season_number']
            result.append({
                'id': temp_data['id'],
                'tag': temp_data['tag'],
                'public_rating': temp_data['public_rating'],
                'league': temp_data['league'],
                'division': temp_data['division'],
                'division_rating': temp_data['division_rating'],
                'last_battle_at': int(datetime.fromisoformat(temp_data['last_battle_at']).timestamp())
            })
        return season_number, result
    
    def __cvc_data_processing(clan_id: int, region_id: int, season: int, response: dict):
        last_battle_at = response['data']['clan_statistics']['last_battle_at']
        clan_null_data = {
            'battles_count': 0, 
            'wins_count': 0, 
            'public_rating': 1100, 
            'league': 4, 
            'division': 2, 
            'division_rating': 0, 
            'stage_type': None, 
            'stage_progress': None
        }
        result = {
            'clan_id': clan_id,
            'region_id': region_id,
            'season_number': season,
            'last_battle_time': int(datetime.fromisoformat(last_battle_at).timestamp()),
            'team_data': {
                1: clan_null_data,
                2: clan_null_data
            }
        }
        for team_data in response['data']['clan_statistics']['ratings']:
            if team_data['season_number'] != season:
                continue
            team_number = team_data['team_number']
            result['team_data'][team_number] = {
                'battles_count': team_data['battles_count'],
                'wins_count': team_data['wins_count'],
                'public_rating': team_data['public_rating'],
                'league': team_data['league'],
                'division': team_data['division'],
                'division_rating': team_data['division_rating'],
                'stage_type': None,
                'stage_progress': None
            }
            if team_data['stage']:
                if team_data['stage']['type'] == 'promotion':
                    result['team_data'][team_number]['stage_type'] = '1'
                else:
                    result['team_data'][team_number]['stage_type'] = '2'
                stage_progress = []
                for progress in team_data['stage']['progress']:
                    if progress == 'victory':
                        stage_progress.append(1)
                    else:
                        stage_progress.append(0)
                result['team_data'][team_number]['stage_progress'] = str(stage_progress)
        return result
    
    def __cvc_data2_processing(clan_id: int, region_id: int, season: int, response: dict):
        last_battle_at = response['data']['clanview']['wows_ladder']['last_battle_at']
        clan_null_data = {
            'battles_count': 0, 
            'wins_count': 0, 
            'public_rating': 1100, 
            'league': 4, 
            'division': 2, 
            'division_rating': 0, 
            'stage_type': None, 
            'stage_progress': None
        }
        result = {
            'clan_id': clan_id,
            'region_id': region_id,
            'season_number': season,
            'last_battle_time': int(datetime.fromisoformat(last_battle_at).timestamp()),
            'team_data': {
                1: clan_null_data,
                2: clan_null_data
            }
        }
        for team_data in response['data']['clanview']['wows_ladder']['ratings']:
            if team_data['season_number'] != season:
                continue
            team_number = team_data['team_number']
            result['team_data'][team_number] = {
                'battles_count': team_data['battles_count'],
                'wins_count': team_data['wins_count'],
                'public_rating': team_data['public_rating'],
                'league': team_data['league'],
                'division': team_data['division'],
                'division_rating': team_data['division_rating'],
                'stage_type': None,
                'stage_progress': None
            }
            if team_data['stage']:
                if team_data['stage']['type'] == 'promotion':
                    result['team_data'][team_number]['stage_type'] = '1'
                else:
                    result['team_data'][team_number]['stage_type'] = '2'
                stage_progress = []
                for progress in team_data['stage']['progress']:
                    if progress == 'victory':
                        stage_progress.append(1)
                    else:
                        stage_progress.append(0)
                result['team_data'][team_number]['stage_progress'] = str(stage_progress)
        return result

