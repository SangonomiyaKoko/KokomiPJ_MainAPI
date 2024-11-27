import httpx
import asyncio
from typing import Optional

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
    async def get_recent_users_by_rid(self, region_id: int):
        platform_api_url = API_URL
        region = REGION_LIST.get(region_id)
        url = f'{platform_api_url}/p/game/clans/{region}/'
        result = await self.fetch_data(url)
        return result
        
    @classmethod
    async def get_clan_data(self, region_id: int, clan_id: int):
        "获取用户缓存的数量，用于确定offset边界"
        api_url = CLAN_API_URL_LIST.get(region_id)
        url = f'{api_url}/api/members/{clan_id}/'
        result = await self.fetch_data(url)
        if result.get('code', None) == 1002:
            return result
        elif result.get('code', None) != 1000:
            logger.error(f"{region_id} - {clan_id} | ├── 网络请求失败，Error: {result.get('message')}")
            return result
        else:
            result = self.__clan_data_processing(clan_id, region_id, result)
            return {'status': 'ok', 'code': 1000, 'message': 'Success', 'data': result}
    
    @classmethod 
    async def update_user_data(self, data: dict):
        platform_api_url = API_URL
        url = f'{platform_api_url}/p/game/clan/update/'
        result = await self.fetch_data(url, method='put', data=data)
        return result
    
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
