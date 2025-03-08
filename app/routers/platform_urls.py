from typing import Optional

from fastapi import APIRouter

from .schemas import RegionList
from app.apis.platform import Update, GameBasic
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
async def updateShipName(region_id: int) -> ResponseDict:
    """更新船只名称数据

    更新wg或者lesta船只的数据
    
    参数:
    - region: 服务器，推荐使用na和ru来更新
    
    返回:
    - ResponseDict
    """
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    if region_id not in [1, 2, 3, 4, 5]:
        return JSONResponse.API_1010_IllegalRegion
    result = await Update.update_ship_name(region_id)
    await record_api_call(result['status'])
    return result 