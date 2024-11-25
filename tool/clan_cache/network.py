import httpx
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
                    if '//clans' in url:
                        return {'status': 'ok','code': 1000,'message': 'Success','data': requset_result}
                    else:
                        return requset_result
                return {'status': 'ok','code': 2000,'message': 'NetworkError','data': None}
            except httpx.ConnectTimeout:
                return {'status': 'ok','code': 2001,'message': 'NetworkError','data': None}
            except httpx.ReadTimeout:
                return {'status': 'ok','code': 2002,'message': 'NetworkError','data': None}
            except httpx.TimeoutException:
                return {'status': 'ok','code': 2003,'message': 'NetworkError','data': None}

    @classmethod
    async def get_clan_rank_data(self, region_id: int):
        season_number = None
        clan_data_list = []
        urls = clan_url_dict.get(region_id)
        for url in urls:
            result = await self.fetch_data(url)
            if result.get('code', None) != 1000:
                logger.error(f"{region_id} | ├── 网络请求失败，Error: {result.get('message')}")
                continue
            season, data = self.__clan_data_processing(result)
            if season_number == None:
                season_number = season
            if season_number != season:
                return []
            clan_data_list = clan_data_list + data
        return season_number, clan_data_list

    @classmethod
    async def update_clan_data(self, clan_data: dict):
        platform_api_url = API_URL
        url = f'{platform_api_url}/p/game/clan/update/'
        result = await self.fetch_data(url, method='put', data=clan_data)
        return result

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