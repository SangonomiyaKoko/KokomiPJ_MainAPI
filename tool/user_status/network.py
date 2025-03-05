import httpx
import asyncio
from typing import Optional

from log import log as logger

VORTEX_API_URL_LIST = {
    1: 'http://vortex.worldofwarships.asia',
    2: 'http://vortex.worldofwarships.eu',
    3: 'http://vortex.worldofwarships.com',
    4: 'http://vortex.korabli.su',
    5: 'http://vortex.wowsgame.cn'
}

class Network:
    async def fetch_data(url, method: str = 'get', data: Optional[dict] = None):
        async with httpx.AsyncClient() as client:
            try:
                if method == 'get':
                    res = await client.get(url, timeout=10)
                elif method == 'delete':
                    res = await client.delete(url, timeout=10)
                elif method == 'post':
                    res = await client.post(url, json=data, timeout=10)
                elif method == 'put':
                    res = await client.put(url, json=data, timeout=10)
                else:
                    return {'status': 'ok','code': 7000,'message': 'InvalidParameter','data': None}
                requset_code = res.status_code
                requset_result = res.json()
                if requset_code == 200:
                    return {'status': 'ok','code': 1000,'message': 'Success','data': requset_result}
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
    async def get_game_version(
        self,
        region_id: int
    ):
        '''获取游戏当前版本'''
        api_url = VORTEX_API_URL_LIST.get(region_id)
        url = f'{api_url}/api/v2/graphql/glossary/version/'
        data = [{"query":"query Version {\n  version\n}"}]
        result = await self.fetch_data(url, method='post', data=data)
        data = {'version': None}
        if result['code'] != 1000 and result['code'] not in [2000,2001,2002,2003,2004,2005]:
            return result
        elif result['code'] != 1000:
            return {'status': 'ok','code': 1000,'message': 'Success','data': data}
        if result['data'] == []:
            return {'status': 'ok','code': 1000,'message': 'Success','data': data}
        version = result['data'][0]['data']['version']
        logger.debug(f'{region_id} | 服务器版本: {version}')
        return {'status': 'ok','code': 1000,'message': 'Success','data': data}
          