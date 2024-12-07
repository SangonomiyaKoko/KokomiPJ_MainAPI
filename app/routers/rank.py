from fastapi import APIRouter, HTTPException
from app.middlewares import RedisConnection
from app.response import JSONResponse

import asyncio

router = APIRouter()

@router.get("/rank/{region_id}/{ship_id}/{page}")
async def get_rank(region_id: int, ship_id: int, page: int):
    '''获取排行榜数据'''
    redis = RedisConnection.get_connection()
    key = f"region:{region_id}:ship:{ship_id}"
    start = (page - 1) * 100
    end = start + 99
    results = await redis.zrevrange(key, start, end, withscores=True)
    final_result = []
    if not results:
        raise HTTPException(status_code=404, detail=JSONResponse.API_1001_NoData)
    for i in range(len(results)):
        ship_data = await redis.hgetall(f"ship_data:{ship_id}:{results[i][0]}")
        user_data = await redis.hgetall(f"user_data:{results[i][0]}")
        result = {
            'account_id': results[i][0],
            'pr': results[i][1],
            'ship_data': ship_data,
            'user_data': user_data
        }
        final_result.append(result)
    return JSONResponse.get_success_response(final_result)