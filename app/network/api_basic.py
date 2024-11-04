import uuid
import asyncio
import traceback

import httpx

from .api_base import BaseUrl
from app.log import write_error_info
from app.response import JSONResponse
from app.const import ClanColor
from app.middlewares.celery import task_check_clan_basic, task_check_user_basic


class BasicAPI:
    '''基础接口
    
    基础数据接口，包括以下功能：
    
    1. 获取用户基本数据
    2. 获取用户和工会的基本数据
    3. 获取搜索用户的结果
    4. 获取搜索工会的结果
    '''
    async def fetch_data(url):
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(url=url, timeout=BaseUrl.REQUEST_TIME_OUT)
                requset_code = res.status_code
                requset_result = res.json()
                if '/clans.' in url:
                    if '/api/search/autocomplete/' in url and requset_code == 200:
                        # 查询工会接口的返回值处理
                        data = requset_result['search_autocomplete_result']
                        return JSONResponse.get_success_response(data)
                    if '/api/clanbase/' in url and requset_code == 200:
                        # 用户基础信息接口的返回值
                        data = requset_result['clanview']
                        return JSONResponse.get_success_response(data)
                    if '/api/clanbase/' in url and requset_code == 503:
                        return JSONResponse.API_1002_ClanNotExist
                elif (
                    '/clans/' in url
                    and requset_code == 404
                ):
                    # 用户所在工会接口，如果用户没有在工会会返回404
                    data = {
                        "clan_id": None,
                        "role": None, 
                        "joined_at": None, 
                        "clan": {},
                    }
                    return JSONResponse.get_success_response(data)
                elif (
                    '/accounts/search/' in url
                    and requset_code in [400, 500, 503]
                ):
                    # 用户搜索接口可能的返回值
                    data = []
                    return JSONResponse.get_success_response([])
                elif requset_code == 404:
                    # 用户不存在或者账号删除的情况
                    return JSONResponse.API_1001_UserNotExist
                elif requset_code == 200:
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
    async def get_user_basic(
        self,
        account_id: int,
        region_id: int,
        use_ac: bool = False,
        ac: str = None
    ) -> list:
        '''获取用户基础信息

        参数：
            account_id： 用户id
            region_id； 用户服务器id
            use_ac: 是否使用ac查询数据
            ac； ac值

        返回：
            用户基础数据
        '''
        api_url = BaseUrl.get_vortex_base_url(region_id)
        urls = [
            f'{api_url}/api/accounts/{account_id}/' + (f'?ac={ac}' if use_ac else '')
        ]
        tasks = []
        responses = []
        async with asyncio.Semaphore(len(urls)):
            for url in urls:
                tasks.append(self.fetch_data(url))
            responses = await asyncio.gather(*tasks)
            return responses
        
    @classmethod
    async def get_user_basic_and_clan(
        self,
        account_id: int,
        region_id: int,
        use_ac: bool = False,
        ac: str = None
    ) -> list:
        '''获取用户基础信息和工会信息

        参数：
            account_id： 用户id
            region_id； 用户服务器id
            use_ac: 是否使用ac查询数据
            ac； ac值

        返回：
            用户基础数据
            用户工会信息
        '''
        api_url = BaseUrl.get_vortex_base_url(region_id)
        urls = [
            f'{api_url}/api/accounts/{account_id}/' + (f'?ac={ac}' if use_ac else ''),
            f'{api_url}/api/accounts/{account_id}/clans/'
        ]
        tasks = []
        responses = []
        async with asyncio.Semaphore(len(urls)):
            for url in urls:
                tasks.append(self.fetch_data(url))
            responses = await asyncio.gather(*tasks)
            return responses
        

    @classmethod
    async def get_clan_basic(
        self,
        clan_id: int,
        region_id: int,
    ):
        '''获取工会基础信息

        参数：
            clan_id： 工会id
            region_id； 工会服务器id

        返回：
            工会基础数据
        '''
        api_url = BaseUrl.get_clan_basse_url(region_id)
        urls = [
            f'{api_url}/api/clanbase/{clan_id}/claninfo/'
        ]
        tasks = []
        responses = []
        async with asyncio.Semaphore(len(urls)):
            for url in urls:
                tasks.append(self.fetch_data(url))
            responses = await asyncio.gather(*tasks)
            return responses

    @classmethod
    async def get_user_search(
        self,
        region_id: int,
        nickname: str,
        limit: int = 10,
        check: bool = False
    ):
        '''获取用户名称搜索结构

        通过输入的用户名称搜索用户账号

        参数：
            region_id: 用户服务器id
            nickname: 用户名称
            limit: 搜索最多返回值，default=10，max=10
            check: 是否对结果进行匹配，返回唯一一个完全匹配的结果
        
        返回：
            结果列表
        '''
        if limit < 1:
            limit = 1
        if limit > 10:
            limit = 10
        nickname = nickname.lower()
        api_url = BaseUrl.get_vortex_base_url(region_id)
        url = f'{api_url}/api/accounts/search/{nickname.lower()}/?limit={limit}'
        result = await self.fetch_data(url)
        if result['code'] != 1000:
            return result
        # 获取所有的结果，通过后台任务更新数据库
        delay_list = []
        for temp_data in result.get('data',None):
            delay_list.append(
                (temp_data['spa_id'],
                region_id,
                temp_data['name'])
            )
        task_check_user_basic.delay(delay_list)
        search_data = []
        if check:
            for temp_data in result.get('data',None):
                if nickname == temp_data['name'].lower():
                    search_data.append({
                        'account_id':temp_data['spa_id'],
                        'region_id': region_id,
                        'name':temp_data['name']
                    })
                    break
        else:
            for temp_data in result.get('data',None):
                search_data.append({
                    'account_id':temp_data['spa_id'],
                    'region_id': region_id,
                    'name':temp_data['name']
                })
        result['data'] = search_data
        return result
    
    @classmethod
    async def get_clan_search(
        self,
        region_id: int,
        tag: str,
        limit: int = 10,
        check: bool = False
    ):
        '''获取工会名称搜索结果

        通过输入的工会名称搜索工会账号

        参数：
            region_id: 工会服务器id
            tga: 工会名称
            limit: 搜索最多返回值，default=10，max=10
            check: 是否对结果进行匹配，返回唯一一个完全匹配的结果
        
        返回：
            结果列表
        '''
        if limit < 1:
            limit = 1
        if limit > 10:
            limit = 10
        tag = tag.lower()
        api_url = BaseUrl.get_clan_basse_url(region_id)
        url = f'{api_url}/api/search/autocomplete/?search={tag}&type=clans'
        result = await self.fetch_data(url)
        if result['code'] != 1000:
            return result
        # 获取所有的结果，通过后台任务更新数据库
        delay_list = []
        for temp_data in result.get('data', None):
            delay_list.append(
                (temp_data['id'],
                region_id,
                temp_data['tag'],
                ClanColor.CLAN_COLOR_INDEX_2.get(temp_data['hex_color'], 5))
            )
        task_check_clan_basic.delay(delay_list)
        search_data = []
        if check:
            for temp_data in result.get('data',None):
                if tag == temp_data['tag'].lower():
                    search_data.append({
                        'clan_id':temp_data['id'],
                        'region_id': region_id,
                        'tag':temp_data['tag']
                    })
                    break
        else:
            for temp_data in result.get('data',None):
                if len(search_data) > limit:
                    break
                if tag in temp_data['tag'].lower():
                    search_data.append({
                        'clan_id':temp_data['id'],
                        'region_id': region_id,
                        'tag':temp_data['tag']
                    })
        result['data'] = search_data
        return result
            
