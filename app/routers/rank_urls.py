from fastapi import APIRouter, Query
from app.apis.rank.rank import Rank
from app.middlewares import record_api_call
from app.response import JSONResponse, ResponseDict
router = APIRouter()

@router.get("/leaderboard/", summary="获取排行榜数据")
async def get_leaderboard(
    region: int = Query(..., description="区域id global使用0"),
    ship_id: int = Query(..., description="船只 ID"),
    page: int = Query(1, ge=1, description="页码，最小值为 1")
) -> ResponseDict :
    data = await Rank.rank(region, ship_id, page)
    result = JSONResponse.get_success_response(data)
    if not result:
        return []
    await record_api_call(result['status'])
    return result