from fastapi import APIRouter

from app.utils import UtilityFunctions
from app.core import ServiceStatus
from app.middlewares import record_api_call
from app.response import JSONResponse, ResponseDict
from app.apis.rank import Leaderboard, UserCache

router = APIRouter()

@router.get("/page/{ship_id}/{region_id}/", summary="获取排行榜单页数据")
async def get_leaderboard(
    ship_id: int,
    region_id: int = 0,
    page: int = 1,
    page_zise: int = 100
) -> ResponseDict :
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    if region_id not in [0, 1, 2, 3, 4, 5]:
        return JSONResponse.API_1010_IllegalRegion
    result = await Leaderboard.get_paginated_data(ship_id, region_id, page, page_zise)
    await record_api_call(result['status'])
    return result

@router.get("/user/{ship_id}/{region_id}/{account_id}/", summary="获取用户的单表排名")
async def get_user_rank(
    ship_id: int,
    account_id: int,
    region_id: int = 0
) -> ResponseDict :
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    if region_id not in [0, 1, 2, 3, 4, 5]:
        return JSONResponse.API_1010_IllegalRegion
    result = await Leaderboard.get_user_data_by_sid(region_id, ship_id, account_id)
    await record_api_call(result['status'])
    return result

@router.get("/update/{region_id}/{account_id}/", summary="更新用户的cache数据")
async def getUserFeatureData(region_id: int, account_id: int) -> ResponseDict:
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
    if region_id not in [1, 2, 3, 4, 5]:
        return JSONResponse.API_1010_IllegalRegion
    if UtilityFunctions.check_aid_and_rid(account_id, region_id) == False:
        return JSONResponse.API_1003_IllegalAccoutIDorRegionID
    result = UserCache.update_user_cache(region_id, account_id)
    await record_api_call(result['status'])
    return result 