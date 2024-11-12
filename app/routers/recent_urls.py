from fastapi import APIRouter

from .schemas import RegionList, UserRecentModel
from app.utils import UtilityFunctions
from app.response import JSONResponse
from app.apis.recent import Recent

router = APIRouter()

@router.post("/features/enable/")
async def enableFeature(
    region: RegionList,
    account_id: int,
    recent_class: int = 30
):  
    # 参数效验
    region_id = UtilityFunctions.get_region_id(region)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    if UtilityFunctions.check_aid_and_rid(account_id, region_id) == False:
        return JSONResponse.API_1003_IllegalAccoutIDorRegionID
    # 请求数据
    result = await Recent.add_recent(account_id,region_id,recent_class)
    return result

@router.delete("/features/disable/")
async def disableFeature(
    region: RegionList,
    account_id: int
):  
    # 参数效验
    region_id = UtilityFunctions.get_region_id(region)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    if UtilityFunctions.check_aid_and_rid(account_id, region_id) == False:
        return JSONResponse.API_1003_IllegalAccoutIDorRegionID
    # 请求数据
    result = await Recent.del_recent(account_id,region_id)
    return result

@router.get("/features/users/overview/")
async def overviewFeature():
    # TODO: 获取当前功能启用用户的概况
    return JSONResponse.API_1000_Success

@router.get("/features/users/enabled/")
async def enabledFeatureUsers(
    region: RegionList,
):  
    # 参数效验
    region_id = UtilityFunctions.get_region_id(region)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    # 请求数据
    result = await Recent.get_recent(region_id)
    return result

@router.get("/features/user/")
async def getUserFeatureData(
    region: RegionList,
    account_id: int
):  
    # 参数效验
    region_id = UtilityFunctions.get_region_id(region)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    if UtilityFunctions.check_aid_and_rid(account_id, region_id) == False:
        return JSONResponse.API_1003_IllegalAccoutIDorRegionID
    # 请求数据
    result = await Recent.get_user_recent(account_id,region_id)
    return result   

@router.post("/features/user/")
async def postUserFeatureDatae(
    user_recent: UserRecentModel
):  
    # 参数效验
    if UtilityFunctions.check_aid_and_rid(user_recent.account_id, user_recent.region_id) == False:
        return JSONResponse.API_1003_IllegalAccoutIDorRegionID
    # 请求数据
    result = await Recent.update_recent(user_recent)
    return result