import uuid
import asyncio
import traceback

import httpx

from .api_base import BaseUrl
from app.log import write_error_info
from app.response import JSONResponse


class DetailsAPI:
    '''其他接口
    '''
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
        except httpx.ConnectTimeout:
            error_id = str(uuid.uuid4())
            write_error_info(
                error_id = error_id,
                error_type = 'Network',
                error_name = 'ConnectTimeout',
                error_file = __file__,
                error_info = f'\nErrorURL: {url}'
            )
            return JSONResponse.get_error_response(2001,'NetworkError',error_id)
        except httpx.ReadTimeout:
            error_id = str(uuid.uuid4())
            write_error_info(
                error_id = error_id,
                error_type = 'Network',
                error_name = 'ReadTimeout',
                error_file = __file__,
                error_info = f'\nErrorURL: {url}'
            )
            return JSONResponse.get_error_response(2002,'NetworkError',error_id)
        except httpx.TimeoutException:
            error_id = str(uuid.uuid4())
            write_error_info(
                error_id = error_id,
                error_type = 'Network',
                error_name = 'RequestTimeout',
                error_file = __file__,
                error_info = f'\nErrorURL: {url}'
            )
            return JSONResponse.get_error_response(2003,'NetworkError',error_id)
        except httpx.HTTPStatusError as e:
            error_id = str(uuid.uuid4())
            write_error_info(
                error_id = error_id,
                error_type = 'Network',
                error_name = 'NetworkError',
                error_file = __file__,
                error_info = f'\nErrorURL: {url}\nStatusCode: {e.response.status_code}'
            )
            return JSONResponse.get_error_response(2000,'NetworkError',error_id)
        except Exception as e:
            error_id = str(uuid.uuid4())
            write_error_info(
                error_id = error_id,
                error_type = 'Program',
                error_name = str(type(e).__name__),
                error_file = __file__,
                error_info = f'\n{traceback.format_exc()}'
            )
            return JSONResponse.get_error_response(5000,'ProgramError',error_id)

    @classmethod
    async def get_user_detail(
        self,
        account_id: int,
        region_id: int,
        type_list: list,
        ac_value: str = None
    ) -> list:
        '''获取用户基础信息和工会信息

        参数：
            account_id： 用户id
            region_id； 用户服务器id
            type_list: 数据类型，支持[pvp,pvp_solo,pvp_div2,pvp_div3,rank_solo]
            ac_value: 是否使用ac查询数据

        返回：
            用户详细数据
        '''
        # 参数效验
        if type_list == None or type_list == []:
            raise ValueError('The type_list argument must be provided')
        api_url = BaseUrl.get_vortex_base_url(region_id)
        urls = []
        for match_type in type_list:
            urls.append(f'{api_url}/api/accounts/{account_id}/ships/{match_type}/' + (f'?ac={ac_value}' if ac_value else ''))
        tasks = []
        responses = []
        async with asyncio.Semaphore(len(urls)):
            for url in urls:
                tasks.append(self.fetch_data(url))
            responses = await asyncio.gather(*tasks)
            return responses