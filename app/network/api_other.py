import httpx

from .api_base import BaseUrl
from app.log import ExceptionLogger
from app.response import JSONResponse


class OtherAPI:
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
    async def get_ship_name_data(
        self,
        region_id: int
    ) -> list:
        '''获取船只信息数据

        分为wg和lesta两个数据，目前不考虑CN这块的数据

        默认使用na和ru的数据

        参数：
            region_id； 服务器id
        返回：
            JSONResponse
        '''
        api_url = BaseUrl.get_vortex_base_url(region_id)
        url = f'{api_url}/api/encyclopedia/en/vehicles/'
        result = await self.fetch_data(url)
        if result['code'] != 1000:
            return result
        return result