import httpx
import asyncio
from typing import Optional
from datetime import datetime

from log import log as logger
from config import API_URL

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
                    res = await client.put(url, json=data, timeout=60)
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
    
    @classmethod
    async def get_cache_clans(self, offset: int = None, limit: int = None):
        "获取用户缓存的数量，用于确定offset边界"
        platform_api_url = API_URL
        if offset != None and limit != None:
            url = f'{platform_api_url}/p/game/clans/cache/?offset={offset}&limit={limit}'
        elif offset == None and limit == None:
            url = f'{platform_api_url}/p/game/clans/cache/'
        else:
            raise ValueError('Invaild Params')
        result = await self.fetch_data(url)
        if result.get('code', None) == 2004:
            logger.debug(f"接口请求失败，休眠 5 s")
            await asyncio.sleep(5)
            result = await self.fetch_data(url)
        elif result.get('code', None) == 8000:
            logger.debug(f"服务器维护中，休眠 60 s")
            await asyncio.sleep(60)
            result = await self.fetch_data(url)
        return result
    
    @classmethod 
    async def update_user_data(self, data: dict):
        platform_api_url = API_URL
        url = f'{platform_api_url}/p/game/clan/update/'
        result = await self.fetch_data(url, method='put', data=data)
        if result.get('code', None) == 2004:
            logger.debug(f"0 - 0000000000 | ├── 接口请求失败，休眠 5 s")
            await asyncio.sleep(5)
            result = await self.fetch_data(url, method='put', data=data)
        elif result.get('code', None) == 8000:
            logger.debug(f"0 - 0000000000 | ├── 服务器维护中，休眠 60 s")
            await asyncio.sleep(60)
            result = await self.fetch_data(url, method='put', data=data)
        return result

    @classmethod
    async def get_basic_data(
        self,
        clan_id: int,
        region_id: int
    ):
        api_url = CLAN_API_URL_LIST.get(region_id)
        urls = [
            f'{api_url}/api/members/{clan_id}/'
        ]
        tasks = []
        responses = []
        async with asyncio.Semaphore(len(urls)):
            for url in urls:
                tasks.append(self.fetch_data(url))
            responses = await asyncio.gather(*tasks)
        if responses[0].get('code', None) == 1002:
            return responses[0]
        elif responses[0].get('code', None) != 1000:
            logger.error(f"{region_id} - {clan_id} | ├── 网络请求失败，Error: {responses[0].get('code')} {responses[0].get('message')}")
            return responses[0]
        else:
            result = self.__clan_data_processing(clan_id, region_id, responses[0])
            return {'status': 'ok', 'code': 1000, 'message': 'Success', 'data': {'clan_users': result}}
        
    @classmethod
    async def get_cache_data(
        self,
        clan_id: int,
        region_id: int
    ):
        api_url = CLAN_API_URL_LIST.get(region_id)
        urls = [
            f'{api_url}/api/members/{clan_id}/',
            f'{api_url}/api/clanbase/{clan_id}/claninfo/'
        ]
        data = {
            'clan_basic': {},
            'clan_users': {}
        }
        tasks = []
        responses = []
        async with asyncio.Semaphore(len(urls)):
            for url in urls:
                tasks.append(self.fetch_data(url))
            responses = await asyncio.gather(*tasks)
        
        if responses[0].get('code', None) == 1002:
            return responses[0]
        elif responses[0].get('code', None) != 1000:
            logger.error(f"{region_id} - {clan_id} | ├── 网络请求失败，Error: {responses[0].get('code')} {responses[0].get('message')}")
            return responses[0]
        else:
            result = self.__clan_data_processing(clan_id, region_id, responses[0])
            data['clan_users'] = result
        
        if responses[1].get('code', None) == 1002:
            return responses[1]
        elif responses[1].get('code', None) != 1000:
            logger.error(f"{region_id} - {clan_id} | ├── 网络请求失败，Error: {responses[1].get('code')} {responses[1].get('message')}")
            return responses[1]
        else:
            result = self.__clan_info_data_processing(clan_id, region_id, responses[1])
            data['clan_basic'] = result
        return {'status': 'ok', 'code': 1000, 'message': 'Success', 'data': data}
    
    def __clan_data_processing(clan_id: int, region_id: int, response: dict):
        result = {
            'clan_id': clan_id,
            'region_id': region_id,
            'clan_users': [],
            'user_list': []
        }
        for user_data in response['data']['items']:
            account_id = user_data['id']
            nickname = user_data['name']
            data = {
                'account_id': account_id,
                'region_id': region_id,
                'nickname': nickname
            }
            result['user_list'].append(account_id)
            result['clan_users'].append(data)
        sorted_list = sorted(result['user_list'])
        result['user_list'] = sorted_list
        return result
    
    def __clan_info_data_processing(clan_id: int, region_id: int, response: dict):
        if 'tag' not in response['data']['clanview']['clan']:
            return {
                'region_id': region_id,
                'clan_id': clan_id,
                'is_active': 1,
                'season_number': response['data']['clanview']['wows_ladder']['season_number'],
                'public_rating': response['data']['clanview']['wows_ladder']['public_rating'],
                'league': response['data']['clanview']['wows_ladder']['league'],
                'division': response['data']['clanview']['wows_ladder']['division'],
                'division_rating': response['data']['clanview']['wows_ladder']['division_rating'],
                'last_battle_at': None
            }
        result = {
            'region_id': region_id,
            'clan_id': clan_id,
            'is_active': 1,
            'tag': response['data']['clanview']['clan']['tag'],
            'season_number': response['data']['clanview']['wows_ladder']['season_number'],
            'public_rating': response['data']['clanview']['wows_ladder']['public_rating'],
            'league': response['data']['clanview']['wows_ladder']['league'],
            'division': response['data']['clanview']['wows_ladder']['division'],
            'division_rating': response['data']['clanview']['wows_ladder']['division_rating']
        }
        if response['data']['clanview']['wows_ladder']['last_battle_at']:
            result['last_battle_at'] = int(
                datetime.fromisoformat(response['data']['clanview']['wows_ladder']['last_battle_at']).timestamp()
            )
        return result
