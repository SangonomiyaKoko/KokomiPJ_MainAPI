import asyncio

import httpx

from .api_base import BaseUrl
from app.log import ExceptionLogger
from app.response import JSONResponse


class DetailsAPI:
    '''其他接口
    '''
    @ExceptionLogger.handle_network_exception_async
    async def fetch_data(url):
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(url=url, timeout=BaseUrl.REQUEST_TIME_OUT)
                requset_code = res.status_code
                requset_result = res.json()
                if requset_code == 200:
                    # 正常返回值的处理
                    data = requset_result['data']
                    return JSONResponse.get_success_response(data)
                else:
                    res.raise_for_status()  # 其他状态码
        except Exception as e:
            raise e

    @classmethod
    async def get_user_detail(
        self,
        account_id: int,
        region_id: int,
        type_list: list,
        ac_value: str = None,
        ac2_value: str = None
    ) -> list:
        '''获取用户基础信息和工会信息

        参数：
            account_id： 用户id
            region_id； 用户服务器id
            type_list: 数据类型
            ac_value: vortex接口的token
            ac_value2: official接口的token

        支持的数据类型： [
            pvp, pvp_solo, pvp_div2, pvp_div3,
            rank_solo, achievement, lifetime, 
            oper, clan
        ]

        返回：
            用户详细数据
        '''
        # 参数效验
        if type_list == None or type_list == []:
            raise ValueError('The type_list argument must be provided')
        vortex_api_url = BaseUrl.get_vortex_base_url(region_id)
        urls = []
        for match_type in type_list:
            if match_type in ['pvp','pvp_solo','pvp_div2','pvp_div3','rank_solo']:
                urls.append(f'{vortex_api_url}/api/accounts/{account_id}/ships/{match_type}/' + (f'?ac={ac_value}' if ac_value else ''))
            else:
                raise ValueError('The entered `match_type` parameter is invalid')
        tasks = []
        responses = []
        async with asyncio.Semaphore(len(urls)):
            for url in urls:
                tasks.append(self.fetch_data(url))
            responses = await asyncio.gather(*tasks)
            return responses