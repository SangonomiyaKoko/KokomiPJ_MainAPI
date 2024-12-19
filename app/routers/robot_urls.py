from fastapi import APIRouter

from .schemas import RegionList, PlatformList, BotUserBindModel
from app.utils import UtilityFunctions
from app.core import ServiceStatus
from app.response import JSONResponse, ResponseDict
from app.apis.robot import BotUser
from app.middlewares import record_api_call

router = APIRouter()

@router.get("/version/", summary="获取robot的最新版本")
async def getVersion() -> ResponseDict:
    """获取bot的版本"""
    # 临时返回值
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    data = {    
        'code': '5.0.0.bate1',
        'image': '5.0.0.bate1'
    }
    result = JSONResponse.get_success_response(data)
    await record_api_call(result['status'])
    return result

@router.get("/user/bind/", summary="获取用户的绑定信息")
async def getUserBind(
    platform: PlatformList,
    user_id: str
) -> ResponseDict:
    """获取用户的绑定信息"""
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    result = await BotUser.get_user_bind(platform.name, user_id)
    await record_api_call(result['status'])
    return result

@router.post("/user/bind/", summary="更新用户的绑定信息")
async def postUserBind(
    user_data: BotUserBindModel
) -> ResponseDict:
    """更新或者写入用户的绑定信息"""
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    result = await BotUser.post_user_bind(user_data.model_dump())
    await record_api_call(result['status'])
    return result

@router.get("/user/account/", summary="获取数据库中用户的基本信息")
async def getUserAccountData(
    region: RegionList,
    account_id: int
) -> ResponseDict:
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    region_id = UtilityFunctions.get_region_id(region.name)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    if UtilityFunctions.check_aid_and_rid(account_id, region_id) == False:
        return JSONResponse.API_1003_IllegalAccoutIDorRegionID
    result = await BotUser.get_user_basic(account_id, region_id)
    await record_api_call(result['status'])
    return result

@router.get("/user/clan/", summary="获取数据库中工会的基本信息")
async def getUserAccountData(
    region: RegionList,
    clan_id: int
) -> ResponseDict:
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    region_id = UtilityFunctions.get_region_id(region.name)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    if UtilityFunctions.check_cid_and_rid(clan_id, region_id) == False:
        return JSONResponse.API_1004_IllegalClanIDorRegionID
    result = await BotUser.get_clan_basic(clan_id, region_id)
    await record_api_call(result['status'])
    return result