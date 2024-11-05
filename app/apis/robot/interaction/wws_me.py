import uuid
import traceback

from ..user_basic import get_user_name_and_clan
from app.log import write_error_info
from app.network import DetailsAPI
from app.response import JSONResponse

async def main(
    account_id: int, 
    region_id: int, 
    language: str, 
    algo_type: str, 
    ac_value: str
):
    '''用于`wws me`功能的接口

    返回用户基本数据
    
    '''
    try:
        # 返回数据的格式
        data = {
            'user': {},
            'clan': {},
            'overview':{},
            'match_type': {},
            'ship_type': {},
            'charts': {}
        }
        # 请求获取user和clan数据
        user_and_clan_result = await get_user_name_and_clan(
            account_id=account_id,
            region_id=region_id,
            ac_value=ac_value
        )
        if user_and_clan_result['code'] != 1000:
            return user_and_clan_result
        else:
            data['user'] = user_and_clan_result['data']['user']
            data['clan'] = user_and_clan_result['data']['clan']
        # TODO: 获取其他数据
        type_list = ['pvp_solo','pvp_div2','pvp_div3','rank_solo']
        details_data = await DetailsAPI.get_user_detail(account_id,region_id,type_list,ac_value)
        for response in details_data:
            if response['code'] != 1000:
                return response
        # TODO: 数据处理

        # 返回结果
        return JSONResponse.get_success_response(data)
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
