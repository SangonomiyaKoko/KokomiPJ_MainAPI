from typing import Optional

from fastapi import APIRouter

from .schemas import (
    RegionList, 
    LanguageList, 
    UserUpdateModel,
    ClanUpdateModel
)
from app.apis.platform import (
    Search, Update, GameUser, GameBasic,
    GameClan, UserCache, ClanCache
)
from app.core import ServiceStatus
from app.utils import UtilityFunctions
from app.response import JSONResponse, ResponseDict
from app.middlewares import record_api_call

router = APIRouter()

@router.get("/game/version/")
async def getGameVersion(
    region: RegionList
):
    """获取服务器当前版本
    
    获取Version

    参数:
    - region: 服务器

    返回:
    - ResponseDict
    """
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    region_id = UtilityFunctions.get_region_id(region)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    result = await GameBasic.get_game_version(region_id)
    await record_api_call(result['status'])
    return result

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
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    region_id = UtilityFunctions.get_region_id(region)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    if not 3 <= len(nickname) <= 25:
        return JSONResponse.API_1011_IllegalUserName
    result = await Search.search_user(
        region_id = region_id,
        nickname = nickname,
        limit = limit,
        check = check
    )
    await record_api_call(result['status'])
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
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    region_id = UtilityFunctions.get_region_id(region)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    if not 2 <= len(tag) <= 5:
        return JSONResponse.API_1012_IllegalClanTag
    result = await Search.search_clan(
        region_id = region_id,
        tag = tag,
        limit = limit,
        check = check
    )
    await record_api_call(result['status'])
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
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
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
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    region_id = UtilityFunctions.get_region_id(region)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    result = await Update.update_ship_name(region_id)
    await record_api_call(result['status'])
    return result

@router.get("/game/users/cache/")
async def getUserCache(offset: Optional[int] = None, limit: Optional[int] = None) -> ResponseDict:
    """批量获取用户的Cache数据

    从offset开始获取最大limit的数据

    参数:
    - offset: 偏移量
    - limit: 最多返回值数量

    返回:
    - ResponseDict
    """
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    if offset == None:
        result = await UserCache.get_user_max_number()
    else:
        result = await UserCache.get_user_cache_data_batch(offset, limit)
    await record_api_call(result['status'])
    return result

@router.get("/game/clans/cache/")
async def getClanCache(offset: Optional[int] = None, limit: Optional[int] = None) -> ResponseDict:
    """批量获取工会的Cache数据

    从offset开始获取最大limit的数据

    参数:
    - offset: 偏移量
    - limit: 最多返回值数量

    返回:
    - ResponseDict
    """
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    if offset == None:
        result = await ClanCache.get_clan_max_number()
    else:
        result = await ClanCache.get_clan_cache_data_batch(offset, limit)
    await record_api_call(result['status'])
    return result

@router.put("/game/user/update/")
async def updateUserCache(user_data: UserUpdateModel) -> ResponseDict:
    """更新用户的数据

    通过传入的数据更新数据库

    参数:
    - UserUpdateModel
    
    返回:
    - ResponseDict
    """
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    result = await GameUser.update_user_data(user_data.model_dump())
    await record_api_call(result['status'])
    return result

@router.put("/game/clan/update/")
async def updateUserCache(clan_data: ClanUpdateModel) -> ResponseDict:
    """更新工会的数据

    通过传入的数据更新数据库

    参数:
    - ClanUsersModel
    
    返回:
    - ResponseDict
    """
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    result = await GameClan.update_clan_data(clan_data.model_dump())
    await record_api_call(result['status'])
    return result
