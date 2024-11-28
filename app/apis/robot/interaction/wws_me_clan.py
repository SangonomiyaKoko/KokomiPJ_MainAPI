from ..clan_basic import get_clan_tag_and_league
from app.log import ExceptionLogger
from app.network import DetailsAPI
from app.response import JSONResponse
from app.models import UserAccessToken

@ExceptionLogger.handle_program_exception_async
async def main(
    clan_id: int, 
    region_id: int, 
    language: str, 
    algo_type: str
):
    '''用于`wws me`功能的接口

    返回用户基本数据
    
    '''
    try:
        # 返回数据的格式
        data = {
            'clan': {},
            'season': {},
            'statistics': {}
        }
        # 请求获取user和clan数据
        user_and_clan_result = await get_clan_tag_and_league(
            clan_id=clan_id,
            region_id=region_id
        )
        if user_and_clan_result['code'] != 1000:
            return user_and_clan_result
        else:
            data['clan'] = user_and_clan_result['data']['clan']
            data['season'] = user_and_clan_result['data']['season']
        # TODO: 获取其他数据
        type_list = ['pvp_solo','pvp_div2','pvp_div3','rank_solo']
        # details_data = await DetailsAPI.get_user_detail(account_id,region_id,type_list,ac_value)
        # for response in details_data:
        #     if response['code'] != 1000:
        #         return response
        # TODO: 数据处理

        # 返回结果
        return JSONResponse.get_success_response(data)
    except Exception as e:
        raise e
