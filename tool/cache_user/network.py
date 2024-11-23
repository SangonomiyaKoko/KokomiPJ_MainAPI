import httpx
import asyncio
from typing import Optional
from dataclasses import dataclass

from log import log as logger
from config import API_URL

VORTEX_API_URL_LIST = {
    1: 'http://vortex.worldofwarships.asia',
    2: 'http://vortex.worldofwarships.eu',
    3: 'http://vortex.worldofwarships.com',
    4: 'http://vortex.korabli.su',
    5: 'http://vortex.wowsgame.cn'
}
REGION_LIST = {
    1: 'asia',
    2: 'eu',
    3: 'na',
    4: 'ru',
    5: 'cn'
}

@dataclass
class json_index:
    keywords: str
    index: int


recent_json_index = [
    json_index('battles_count',                  0),
    json_index('wins',                           1),
    json_index('losses',                         2),
    json_index('damage_dealt',                   3),
    json_index('ships_spotted',                  4),
    json_index('frags',                          5),
    json_index('survived',                       6),
    json_index('scouting_damage',                7),
    json_index('original_exp',                   8),
    json_index('exp',                            9),
    json_index('art_agro',                      10),
    json_index('tpd_agro',                      11),
    json_index('win_and_survived',              12),
    json_index('control_dropped_points',        13),
    json_index('control_captured_points',       14),
    json_index('team_control_captured_points',  15),
    json_index('team_control_dropped_points',   16),
    json_index('planes_killed',                 17),
    json_index('frags_by_ram',                  18),
    json_index('frags_by_tpd',                  19),
    json_index('frags_by_planes',               20),
    json_index('frags_by_dbomb',                21),
    json_index('frags_by_atba',                 22),
    json_index('frags_by_main',                 23),
    json_index('hits_by_main',                  24),
    json_index('shots_by_main',                 25),
    json_index('hits_by_skip',                  26),
    json_index('shots_by_skip',                 27),
    json_index('hits_by_atba',                  28),
    json_index('shots_by_atba',                 29),
    json_index('hits_by_rocket',                30),
    json_index('shots_by_rocket',               31),
    json_index('hits_by_bomb',                  32),
    json_index('shots_by_bomb',                 33),
    json_index('hits_by_tpd',                   34),
    json_index('shots_by_tpd',                  35),
    json_index('hits_by_tbomb',                 36),
    json_index('shots_by_tbomb',                37),
]

class UserCache_Network:
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
                    if 'vortex' in url:
                        return {'status': 'ok','code': 1000,'message': 'Success','data': requset_result['data']}
                    else:
                        return requset_result
                if requset_code == 404:
                    return {'status': 'ok','code': 1001,'message': 'UserNotExist','data' : None}
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
    async def get_user_cache(self, offset: int, limit: int = 1000):
        platform_api_url = API_URL
        url = f'{platform_api_url}/r1/features/user/'
        result = await self.fetch_data(url)
        return result
    
    @classmethod 
    async def update_user_cache_data(self, data: dict):
        platform_api_url = API_URL
        url = f'{platform_api_url}/p/game/user/info/'
        result = await self.fetch_data(url, method='put', data=data)
        return result
    
    @classmethod 
    async def update_user_info_data(self, data: dict):
        platform_api_url = API_URL
        url = f'{platform_api_url}/p/game/user/info/'
        result = await self.fetch_data(url, method='put', data=data)
        return result
    
    # @classmethod 
    # async def update_user_basic_data(self, data: dict):
    #     platform_api_url = API_URL
    #     url = f'{platform_api_url}/p/game/user/basic/'
    #     result = await self.fetch_data(url, method='put', data=data)
    #     return result

    @classmethod
    async def update_user_basic_and_info_data(self, data: dict):
        platform_api_url = API_URL
        url = f'{platform_api_url}/p/game/user/basic-and-info/'
        result = await self.fetch_data(url, method='put', data=data)
        return result

    @classmethod
    async def get_basic_data(
        self,
        account_id: int,
        region_id: int,
        ac_value: str = None
    ):
        api_url = VORTEX_API_URL_LIST.get(region_id)
        urls = [
            f'{api_url}/api/accounts/{account_id}/' + (f'?ac={ac_value}' if ac_value else '')
        ]
        tasks = []
        responses = []
        async with asyncio.Semaphore(len(urls)):
            for url in urls:
                tasks.append(self.fetch_data(url))
            responses = await asyncio.gather(*tasks)
            return responses
        
    @classmethod
    async def get_cache_data(
        self,
        account_id: int,
        region_id: int,
        ac_value: str = None
    ):
        api_url = VORTEX_API_URL_LIST.get(region_id)
        urls = [
            f'{api_url}/api/accounts/{account_id}/ships/' + (f'?ac={ac_value}' if ac_value else ''),
            f'{api_url}/api/accounts/{account_id}/ships/pvp/' + (f'?ac={ac_value}' if ac_value else '')
        ]
        tasks = []
        responses = []
        async with asyncio.Semaphore(len(urls)):
            for url in urls:
                tasks.append(self.fetch_data(url))
            responses = await asyncio.gather(*tasks)
        error = None
        for response in responses:
            if response.get('code', None) != 1000:
                logger.error(f"{region_id} - {account_id} | ├── 网络请求失败，Error: {response.get('message')}")
                error = response
        if not error:
            result = self.__ships_data_processing(account_id,responses)
            return {'status': 'ok', 'code': 1000, 'message': 'Success', 'data': result}
        else:
            return error
        
    def __ships_data_processing(account_id: int,responses: dict):
        result = {
            'basic': {},
            'details': {}
        }
        ships_data = responses[0]
        for ship_id, ship_data in ships_data['data'][str(account_id)]['statistics'].items():
            if ship_data != {} and ship_data['pvp'] != {} and ship_data['pvp']['battles_count'] > 0:
                result['basic'][int(ship_id)] = ship_data['pvp']['battles_count']
                result['details'][int(ship_id)] = [
                    ship_data['pvp']['battles_count'],
                    0 if ship_data['pvp_solo'] == {} else ship_data['pvp_solo']['battles_count'],
                    0 if ship_data['pvp_div2'] == {} else ship_data['pvp_div2']['battles_count'],
                    0 if ship_data['pvp_div3'] == {} else ship_data['pvp_div3']['battles_count'],
                ]
        pvp_data = responses[1]['data'][str(account_id)]['statistics']
        for ship_id in result['basic'].keys():
            ship_data = pvp_data[str(ship_id)]['pvp']
            if ship_data == {}:
                del result['basic'][ship_id]
                del result['details'][ship_id]
            basic_data = result['details'][ship_id]
            extra_data = [
                ship_data['wins'],
                ship_data['damage_dealt'],
                ship_data['frags'],
                ship_data['exp'],
                ship_data['survived'],
                ship_data['scouting_damage'],
                ship_data['art_agro'],
                ship_data['planes_killed'],
                ship_data['max_exp'],
                ship_data['max_damage_dealt'],
                ship_data['max_frags']
            ]
            result['details'][ship_id] = basic_data + extra_data
        return result
            
                