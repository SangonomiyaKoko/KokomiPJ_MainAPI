from typing import Optional

from fastapi import APIRouter

from .schemas import (
    RegionList,
    UserUpdateModel,
    ClanUpdateModel
)
from app.apis.platform import (
    Update, GameUser, GameBasic,
    GameClan, UserCache, ClanCache
)
from app.core import ServiceStatus
from app.utils import UtilityFunctions
from app.response import JSONResponse, ResponseDict
from app.middlewares import record_api_call

router = APIRouter()

@router.get("/game/version/", summary="获取游戏当前版本")
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
    region_id = UtilityFunctions.get_region_id(region.name)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    result = await GameBasic.get_game_version(region_id)
    await record_api_call(result['status'])
    return result

@router.put("/update/ship-name/", summary="更新船只名称的json数据")
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
    region_id = UtilityFunctions.get_region_id(region.name)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    result = await Update.update_ship_name(region_id)
    await record_api_call(result['status'])
    return result

@router.get("/update/user-cache/{region}/{account_id}/", summary="更新用户的cache数据")
async def getUserFeatureData(region: RegionList,account_id: int) -> ResponseDict:
    """更新用户的cache数据

    用于排行榜数据的更新

    参数:
    - region: 服务器
    - account_id: 用户id

    返回:
    - ResponseDict
    """
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    region_id = UtilityFunctions.get_region_id(region.name)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    if UtilityFunctions.check_aid_and_rid(account_id, region_id) == False:
        return JSONResponse.API_1003_IllegalAccoutIDorRegionID
    result = UserCache.update_user_cache(region_id, account_id)
    await record_api_call(result['status'])
    return result  

# @router.get("/game/users/cache/", summary="获取用户的数据库中数据")
# async def getUserCache(offset: Optional[int] = None, limit: Optional[int] = None) -> ResponseDict:
#     """批量获取用户的Cache数据

#     从offset开始获取最大limit的数据

#     参数:
#     - offset: 偏移量
#     - limit: 最多返回值数量

#     返回:
#     - ResponseDict
#     """
#     if not ServiceStatus.is_service_available():
#         return JSONResponse.API_8000_ServiceUnavailable
#     if offset == None:
#         result = await UserCache.get_user_max_number()
#     else:
#         result = await UserCache.get_user_cache_data_batch(offset, limit)
#     await record_api_call(result['status'])
#     return result

# @router.put("/game/user/update/", summary="更新用户的数据库数据")
# async def updateUserCache(user_data: UserUpdateModel) -> ResponseDict:
#     """更新用户的数据

#     通过传入的数据更新数据库

#     参数:
#     - UserUpdateModel
    
#     返回:
#     - ResponseDict
#     """
#     if not ServiceStatus.is_service_available():
#         return JSONResponse.API_8000_ServiceUnavailable
#     result = await GameUser.update_user_data(user_data.model_dump())
#     await record_api_call(result['status'])
#     return result

# @router.get("/game/clans/cache/", summary="获取工会的数据库中数据")
# async def getClanCache(offset: Optional[int] = None, limit: Optional[int] = None) -> ResponseDict:
#     """批量获取工会的Cache数据

#     从offset开始获取最大limit的数据

#     参数:
#     - offset: 偏移量
#     - limit: 最多返回值数量

#     返回:
#     - ResponseDict
#     """
#     if not ServiceStatus.is_service_available():
#         return JSONResponse.API_8000_ServiceUnavailable
#     if offset == None:
#         result = await ClanCache.get_clan_max_number()
#     else:
#         result = await ClanCache.get_clan_cache_data_batch(offset, limit)
#     await record_api_call(result['status'])
#     return result

# @router.put("/game/clan/update/", summary="更新工会的数据库数据")
# async def updateUserCache(clan_data: ClanUpdateModel) -> ResponseDict:
#     """更新工会的数据

#     通过传入的数据更新数据库

#     参数:
#     - ClanUsersModel
    
#     返回:
#     - ResponseDict
#     """
#     if not ServiceStatus.is_service_available():
#         return JSONResponse.API_8000_ServiceUnavailable
#     result = await GameClan.update_clan_data(clan_data.model_dump())
#     await record_api_call(result['status'])
#     return result
