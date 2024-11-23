from typing import Optional

from fastapi import APIRouter

from .schemas import (
    RegionList, 
    LanguageList, 
    UserInfoUpdateModel
)
from app.apis.platform import Search, Update, GameUser
from app.utils import UtilityFunctions
from app.response import JSONResponse, ResponseDict
from app.middlewares import record_api_call

router = APIRouter()

@router.get("/search/user/")
async def searchUser(
    region: RegionList,
    nickname: str,
    limit: Optional[int] = 10,
    check: Optional[bool] = False
) -> ResponseDict:
    """用户搜索接口

    搜索输入的用户名称

    参数:
    - region: 服务器
    - nickname: 搜索的名称
    - limit: 搜索返回值的限制
    - check: 是否检查并返回唯一合适的结果

    返回:
    - ResponseDict
    """
    # 参数效验
    region_id = UtilityFunctions.get_region_id(region)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    if not 3 <= len(nickname) <= 25:
        return JSONResponse.API_1011_IllegalUserName
    # 调用函数
    result = await Search.search_user(
        region_id = region_id,
        nickname = nickname,
        limit = limit,
        check = check
    )
    await record_api_call(result['status'])
    # 返回结果
    return result

@router.get("/search/clan/")
async def searchClan(
    region: RegionList,
    tag: str,
    limit: Optional[int] = 10,
    check: Optional[bool] = False
) -> ResponseDict:
    """工会搜索接口

    搜索输入的工会名称

    参数:
    - region: 服务器
    - tag: 搜索的名称
    - limit: 搜索返回值的限制
    - check: 是否检查并返回唯一合适的结果

    返回:
    - ResponseDict
    """
    # 参数效验
    region_id = UtilityFunctions.get_region_id(region)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    if not 2 <= len(tag) <= 5:
        return JSONResponse.API_1012_IllegalClanTag
    # 调用函数
    result = await Search.search_clan(
        region_id = region_id,
        tag = tag,
        limit = limit,
        check = check
    )
    await record_api_call(result['status'])
    # 返回结果
    return result

@router.get("/search/ship/")
async def searchShip(
    region: RegionList,
    language: LanguageList,
    shipname: str
) -> ResponseDict:
    """船只搜索接口

    搜索输入的船只名称

    参数:
    - region: 服务器
    - language: 搜索的语言
    - shipname: 搜索的名称

    返回:
    - ResponseDict
    """
    region_id = UtilityFunctions.get_region_id(region)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    result = await Search.search_ship(
        region_id = region_id,
        ship_name = shipname,
        language = language
    )
    await record_api_call(result['status'])
    return result

@router.put("/update/ship-name/")
async def updateShipName(region: RegionList) -> ResponseDict:
    """更新船只名称数据

    更新wg或者lesta船只的数据
    
    参数:
    - region: 服务器，推荐使用na和ru来更新
    
    返回:
    - ResponseDict
    """
    region_id = UtilityFunctions.get_region_id(region)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    result = await Update.update_ship_name(region_id)
    await record_api_call(result['status'])
    return result

@router.get("/game/users/number/")
async def get_user_max_number() -> ResponseDict:
    """获取user表中id最大值

    用于user表的遍历更新

    参数:
    - None

    返回:
    - ResponseDict
    """
    result = await GameUser.get_user_max_number()
    await record_api_call(result['status'])
    return result

@router.get("/game/user/{region}/{account_id}/info/")
async def get_user_info(region: RegionList, account_id: int) -> ResponseDict:
    """获取user_info表中的数据

    用于recent相关更新用户数据使用

    参数:
    - account_id: 用户id

    返回:
    - ResponseDict
    """
    region_id = UtilityFunctions.get_region_id(region)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    if UtilityFunctions.check_aid_and_rid(account_id, region_id) == False:
        return JSONResponse.API_1003_IllegalAccoutIDorRegionID
    result = await GameUser.get_user_info_data(account_id,region_id)
    await record_api_call(result['status'])
    return result

@router.put("/game/user/info/")
async def post_user_info(user_data: UserInfoUpdateModel) -> ResponseDict:
    """更新user_info和user_basic表

    如果数据发生改变则更新，反之则更新update_time

    参数:
    - UserInfoModel

    返回:
    - ResponseDict
    """
    user_data: dict = user_data.model_dump()
    print('TEST_RECENT: ',str(user_data))
    result = JSONResponse.API_1000_Success
    if user_data.get('user_basic', None):
        result = await GameUser.check_user_basic_data(user_data['user_basic'])
    if user_data.get('user_info', None):
        result = await GameUser.check_user_info_data(user_data['user_info'])
    await record_api_call(result['status'])
    return result
