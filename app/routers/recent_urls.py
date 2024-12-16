from fastapi import APIRouter

from .schemas import RegionList, RecentEnableModel
from app.utils import UtilityFunctions
from app.core import ServiceStatus
from app.response import JSONResponse, ResponseDict
from app.apis.recent import RecentBasic, RecentData
from app.apis.platform import GameUser
from app.middlewares import record_api_call

router = APIRouter()

@router.get("/features/users/{region}/", summary="获取所有启用功能用户的列表")
async def enabledFeatureUsers(region: RegionList) -> ResponseDict:
    """获取服务器下所有启用功能用户的列表

    用于recent功能的遍历更新

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
    result = await RecentBasic.get_recent(region_id)
    await record_api_call(result['status'])
    return result 

@router.get("/features/user/{region}/{account_id}/overview/", summary="判断用户是否启用的recent更新")
async def get_recent_data_overview(region: RegionList,account_id: int) -> ResponseDict:
    """判断用户是否启用的recent更新

    检查用户是否启用并返回True或者False

    参数:
    - region: 服务器
    - account_id: 用户id

    返回:
    - ResponseDict
    """
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    region_id = UtilityFunctions.get_region_id(region)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    if UtilityFunctions.check_aid_and_rid(account_id, region_id) == False:
        return JSONResponse.API_1003_IllegalAccoutIDorRegionID
    result = await RecentData.get_data_overview(account_id,region_id)
    await record_api_call(result['status'])
    return result 

@router.get("/features/user/{region}/{account_id}/info/", summary="获取用户user_info表中的数据")
async def get_user_info(region: RegionList, account_id: int) -> ResponseDict:
    """获取user_info表中的数据

    用于recent相关更新用户数据使用

    参数:
    - account_id: 用户id

    返回:
    - ResponseDict
    """
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    region_id = UtilityFunctions.get_region_id(region)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    if UtilityFunctions.check_aid_and_rid(account_id, region_id) == False:
        return JSONResponse.API_1003_IllegalAccoutIDorRegionID
    result = await GameUser.get_user_info_data(account_id,region_id)
    await record_api_call(result['status'])
    return result

@router.get("/features/user/{region}/{account_id}/", summary="获取用户recent的数据")
async def getUserFeatureData(region: RegionList,account_id: int) -> ResponseDict:
    """获取用户recent的数据

    用于recent功能更新用户数据

    参数:
    - region: 服务器
    - account_id: 用户id

    返回:
    - ResponseDict
    """
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    region_id = UtilityFunctions.get_region_id(region)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    if UtilityFunctions.check_aid_and_rid(account_id, region_id) == False:
        return JSONResponse.API_1003_IllegalAccoutIDorRegionID
    result = await RecentBasic.get_user_recent(account_id,region_id)
    await record_api_call(result['status'])
    return result  

@router.post("/features/user/", summary="启用用户的recent功能")
async def enableFeature(enable_data: RecentEnableModel) -> ResponseDict: 
    """启用用户的recent功能

    只有传入的recent_class大于数据库中的才会修改

    参数:
    - RecentEnableModel

    返回:
    - ResponseDict
    """
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    region_id = UtilityFunctions.get_region_id(enable_data.region)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    if UtilityFunctions.check_aid_and_rid(enable_data.account_id, region_id) == False:
        return JSONResponse.API_1003_IllegalAccoutIDorRegionID
    result = await RecentBasic.add_recent(enable_data.account_id,region_id,enable_data.recent_class)
    await record_api_call(result['status'])
    return result

@router.delete("/features/user/{region}/{account_id}/", summary="删除用户的recent功能")
async def disableFeature(region: RegionList,account_id: int) -> ResponseDict: 
    """删除用户的recent功能

    删除用户recent功能

    参数:
    - None

    返回:
    - ResponseDict
    """
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    region_id = UtilityFunctions.get_region_id(region)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    if UtilityFunctions.check_aid_and_rid(account_id, region_id) == False:
        return JSONResponse.API_1003_IllegalAccoutIDorRegionID
    result = await RecentBasic.del_recent(account_id,region_id)
    await record_api_call(result['status'])
    return result