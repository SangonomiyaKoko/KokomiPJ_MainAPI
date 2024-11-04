from typing import Optional

from fastapi import APIRouter

from .schemas import RegionList, LanguageList
from app.apis.platform import Search, Update
from app.utils import UtilityFunctions
from app.response import JSONResponse
from app.middlewares import record_api_call

router = APIRouter()

@router.get("/search/user/")
async def searchUser(
    region: RegionList,
    nickname: str,
    limit: Optional[int] = 10,
    check: Optional[bool] = False
):
    """用户搜索接口

    搜索输入的用户名称

    参数:
    - region: 服务器
    - nickname: 搜索的名称
    - limit: 搜索返回值的限制
    - check: 是否检查并返回唯一合适的结果

    返回:
    - JSONResponse: 返回值
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
):
    """工会搜索接口

    搜索输入的工会名称

    参数:
    - region: 服务器
    - tag: 搜索的名称
    - limit: 搜索返回值的限制
    - check: 是否检查并返回唯一合适的结果

    返回:
    - JSONResponse: 返回值
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
):
    """船只搜索接口

    搜索输入的船只名称

    参数:
    - region: 服务器
    - language: 搜索的语言
    - shipname: 搜索的名称

    返回:
    - JSONResponse: 返回值
    """
    # 参数效验
    region_id = UtilityFunctions.get_region_id(region)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    # 调用函数
    result = await Search.search_ship(
        region_id = region_id,
        ship_name = shipname,
        language = language
    )
    await record_api_call(result['status'])
    # 返回结果
    return result

@router.put("/update/ship-name/")
async def updateShipName(
    region: RegionList,
):
    """更新船只名称数据

    更新wg或者lesta船只的数据
    
    参数:
    - region: 服务器
    返回:
    - JSONResponse
    """
    # 参数效验
    region_id = UtilityFunctions.get_region_id(region)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    result = await Update.update_ship_name(region_id)
    await record_api_call(result['status'])
    # 返回结果
    return result

