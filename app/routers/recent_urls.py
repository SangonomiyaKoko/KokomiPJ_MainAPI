from fastapi import APIRouter

from .schemas import RegionList, UserRecentModel, RecentEnableModel, RecentDisableModel
from app.utils import UtilityFunctions
from app.response import JSONResponse, ResponseDict
from app.apis.recent import RecentBasic, RecentData

router = APIRouter()

@router.post("/features/enable/", description="启用用户Recent功能")
async def enableFeature(enable_data: RecentEnableModel) -> ResponseDict:  
    # 参数效验
    region_id = UtilityFunctions.get_region_id(enable_data.region)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    if UtilityFunctions.check_aid_and_rid(enable_data.account_id, enable_data.region_id) == False:
        return JSONResponse.API_1003_IllegalAccoutIDorRegionID
    # 请求数据
    result = await RecentBasic.add_recent(enable_data.account_id,region_id,enable_data.recent_class)
    return result

@router.delete("/features/disable/", description="删除用户Recent功能")
async def disableFeature(disable_data: RecentDisableModel) -> ResponseDict:  
    # 参数效验
    region_id = UtilityFunctions.get_region_id(disable_data.region)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    if UtilityFunctions.check_aid_and_rid(disable_data.account_id, region_id) == False:
        return JSONResponse.API_1003_IllegalAccoutIDorRegionID
    # 请求数据
    result = await RecentBasic.del_recent(disable_data.account_id,region_id)
    return result

@router.get("/features/users/{region}/enabled/", description="获取服务器下所有启用用户的id")
async def enabledFeatureUsers(region: RegionList) -> ResponseDict:  
    # 参数效验
    region_id = UtilityFunctions.get_region_id(region)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    # 请求数据
    result = await RecentBasic.get_recent(region_id)
    return result

@router.get("/features/user/{region}/{account_id}/", description="获取用户Recent功能的数据")
async def getUserFeatureData(region: RegionList,account_id: int) -> ResponseDict:  
    # 参数效验
    region_id = UtilityFunctions.get_region_id(region)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    if UtilityFunctions.check_aid_and_rid(account_id, region_id) == False:
        return JSONResponse.API_1003_IllegalAccoutIDorRegionID
    # 请求数据
    result = await RecentBasic.get_user_recent(account_id,region_id)
    return result   

@router.post("/features/user/", description="更新用户Recent功能的数据")
async def postUserFeatureDatae(user_recent: UserRecentModel) -> ResponseDict:  
    # 参数效验
    if UtilityFunctions.check_aid_and_rid(user_recent.account_id, user_recent.region_id) == False:
        return JSONResponse.API_1003_IllegalAccoutIDorRegionID
    # 请求数据
    result = await RecentBasic.update_recent(user_recent.model_dump())
    return result

@router.get("/features/recent/user/{region}/{account_id}/overview/", description="获取用户Recent功能的数据")
async def get_recent_data_overview(region: RegionList,account_id: int) -> ResponseDict:  
    # 参数效验
    region_id = UtilityFunctions.get_region_id(region)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    if UtilityFunctions.check_aid_and_rid(account_id, region_id) == False:
        return JSONResponse.API_1003_IllegalAccoutIDorRegionID
    # 请求数据
    result = await RecentData.get_data_overview(account_id,region_id)
    return result 