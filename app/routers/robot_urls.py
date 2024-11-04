from typing import Optional

from fastapi import APIRouter

from .schemas import RegionList, LanguageList
from app.utils import UtilityFunctions
from app.response import JSONResponse
from app.apis.robot.data_request import data_me

router = APIRouter()

@router.get("/user-basic/")
async def getUserBasic(
    region: RegionList,
    account_id: int,
    language: LanguageList,
    ac_value: Optional[str] = None
):
    
    # 参数效验
    region_id = UtilityFunctions.get_region_id(region)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    if UtilityFunctions.check_aid_and_rid(account_id, region_id) == False:
        return JSONResponse.API_1003_IllegalAccoutIDorRegionID
    # 请求数据
    result = await data_me.main(account_id,region_id,language,'pr',ac_value)
    return result