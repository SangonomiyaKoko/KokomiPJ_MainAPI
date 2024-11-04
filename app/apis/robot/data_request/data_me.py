import uuid

from ..user_basic import get_user_name_and_clan
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

    # TODO: 数据处理

    # 返回结果
    return JSONResponse.get_success_response(data)
