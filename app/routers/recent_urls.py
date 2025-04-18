from fastapi import APIRouter

from .schemas import RecentEnableModel
from app.utils import UtilityFunctions
from app.core import ServiceStatus
from app.response import JSONResponse, ResponseDict
from app.apis.recent import RecentBasic, RecentData
from app.middlewares import record_api_call


router = APIRouter()

@router.get("/features/user/{region_id}/{account_id}/", summary="判断用户是否启用的recent更新")
async def get_recent_data_overview(region_id: int,account_id: int) -> ResponseDict:
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
    if region_id not in [1, 2, 3, 4, 5]:
        return JSONResponse.API_1010_IllegalRegion
    if UtilityFunctions.check_aid_and_rid(account_id, region_id) == False:
        return JSONResponse.API_1003_IllegalAccoutIDorRegionID
    result = await RecentData.get_data_overview(account_id,region_id)
    await record_api_call(result['status'])
    return result 

@router.get("/features/user/{region_id}/{account_id}/info/", summary="查看用户的recent数据库信息")
async def get_recent_data_overview(region_id: int,account_id: int) -> ResponseDict:
    """判断用户数据库是否有问题

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
    result = await RecentBasic.get_recent_info(account_id,region_id)
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
    region_id = enable_data.region_id
    if region_id not in [1, 2, 3, 4, 5]:
        return JSONResponse.API_1010_IllegalRegion
    if UtilityFunctions.check_aid_and_rid(enable_data.account_id, region_id) == False:
        return JSONResponse.API_1003_IllegalAccoutIDorRegionID
    result = await RecentBasic.add_recent(enable_data.account_id,region_id,enable_data.recent_class)
    await record_api_call(result['status'])
    return result

@router.delete("/features/user/{region_id}/{account_id}/", summary="删除用户的recent功能")
async def disableFeature(region_id: int, account_id: int) -> ResponseDict: 
    """删除用户的recent功能

    删除用户recent功能

    参数:
    - None

    返回:
    - ResponseDict
    """
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    if region_id not in [1, 2, 3, 4, 5]:
        return JSONResponse.API_1010_IllegalRegion
    if UtilityFunctions.check_aid_and_rid(account_id, region_id) == False:
        return JSONResponse.API_1003_IllegalAccoutIDorRegionID
    result = await RecentBasic.del_recent(account_id,region_id)
    await record_api_call(result['status'])
    return result