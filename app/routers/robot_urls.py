from typing import Optional

from fastapi import APIRouter

from .schemas import RegionList, LanguageList
from app.utils import UtilityFunctions
from app.response import JSONResponse, ResponseDict
from app.apis.robot import wws_me
from app.middlewares import record_api_call

router = APIRouter()

@router.get("/user-basic/")
async def getUserBasic(
    region: RegionList,
    account_id: int,
    language: LanguageList,
    ac_value: Optional[str] = None
) -> ResponseDict:
    """

    -

    参数:
    - None

    返回:
    - ResponseDict
    """
    region_id = UtilityFunctions.get_region_id(region)
    if not region_id:
        return JSONResponse.API_1010_IllegalRegion
    if UtilityFunctions.check_aid_and_rid(account_id, region_id) == False:
        return JSONResponse.API_1003_IllegalAccoutIDorRegionID
    result = await wws_me.main(account_id,region_id,language,'pr',ac_value)
    await record_api_call(result['status'])
    return result