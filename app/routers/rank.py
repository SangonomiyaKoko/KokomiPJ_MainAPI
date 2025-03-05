from fastapi import APIRouter, HTTPException
from app.middlewares import RedisConnection
from app.middlewares.rank import Rank_tasks
from app.response import JSONResponse

import asyncio

router = APIRouter()

# @router.get("/{region_id}/{ship_id}/{page}")
# async def get_rank(region_id: int, ship_id: int, page: int):
#     return JSONResponse.API_1000_Success
#     '''获取排行榜数据'''
#     redis = RedisConnection.get_connection(3)
#     key = f"region:{region_id}:ship:{ship_id}"
#     count = await redis.zcard(key)
#     start = (page - 1) * 100
#     end = min(start + 99, count)
#     results = await redis.zrevrange(key, start, end, withscores=True)
#     final_result = []
#     if not results:
#         raise HTTPException(status_code=404, detail=JSONResponse.API_7000_InvalidParameter)
#     for i in range(len(results)):
#         ship_data = await redis.hgetall(f"ship_data:{ship_id}:{results[i][0]}")
#         user_data = await redis.hgetall(f"user_data:{results[i][0]}")
#         result = {
#             'account_id': results[i][0],
#             'pr': results[i][1],
#             'ship_data': ship_data,
#             'user_data': user_data
#         }
#         final_result.append(result)
#     return JSONResponse.get_success_response(final_result)

# @router.get("/all/{ship_id}/{page}")
# async def get_rank_all(ship_id: int, page: int):
#     '''获取总排行榜数据'''
#     redis = RedisConnection.get_connection(db=3)
#     key = f"region:all:ship:{ship_id}"
#     count = await redis.zcard(key)
#     start = (page - 1) * 100
#     end = min(start + 99, count)
#     results = await redis.zrevrange(key, start, end, withscores=True)
#     final_result = []
#     if not results:
#         raise HTTPException(status_code=404, detail=JSONResponse.API_7000_InvalidParameter)
#     for i in range(len(results)):
#         ship_data = await redis.hgetall(f"ship_data:{ship_id}:{results[i][0]}")
#         user_data = await redis.hgetall(f"user_data:{results[i][0]}")
#         result = {
#             'account_id': results[i][0],
#             'pr': results[i][1],
#             'ship_data': ship_data,
#             'user_data': user_data
#         }
#         final_result.append(result)
#     return JSONResponse.get_success_response(final_result)

# @router.get("/personal/{region_id}/{ship_id}/{account_id}")
# async def get_personal_rank(region_id: int, ship_id: int, account_id: int):
#     '''获取个人排名'''
#     redis = RedisConnection.get_connection(db=3)
#     key = f"region:{region_id}:ship:{ship_id}"
#     rank = await redis.zrevrank(key, account_id) + 1
#     if not rank:
#         raise HTTPException(status_code=404, detail=JSONResponse.API_1006_UserDataisNone)
#     ship_data = await redis.hgetall(f"ship_data:{ship_id}:{account_id}")
#     user_data = await redis.hgetall(f"user_data:{account_id}")
#     if not ship_data or not user_data:
#         raise HTTPException(status_code=404, detail=JSONResponse.API_1006_UserDataisNone)
#     result = {
#         'account_id': account_id,
#         'rank' : rank,
#         'ship_data': ship_data,
#         'user_data': user_data
#     }
#     return JSONResponse.get_success_response(result)

# @router.get("/personal/n/{region_id}/{ship_id}/{account_id}")
# async def get_personal_rank_near(region_id: int, ship_id: int, account_id: int):
#     '''获取个人排名附近的玩家'''
#     redis = RedisConnection.get_connection(db=3)
#     key = f"region:{region_id}:ship:{ship_id}"
#     rank = await redis.zrevrank(key, account_id)
#     if not rank:
#         raise HTTPException(status_code=404, detail=JSONResponse.API_1006_UserDataisNone)
#     start = max(0, rank - 4)
#     end = rank + 5
#     members = await redis.zrevrange(key, start, end, withscores=True)
#     members.insert(4, (str(account_id), await redis.zscore(key, account_id)))
#     final_result = []
#     rank = max(0, rank - 4) + 1
#     for i in range(len(members)):
#         ship_data = await redis.hgetall(f"ship_data:{ship_id}:{members[i][0]}")
#         user_data = await redis.hgetall(f"user_data:{members[i][0]}")
#         if not ship_data or not user_data:
#             raise HTTPException(status_code=404, detail=JSONResponse.API_1006_UserDataisNone)
#         result = {
#             'account_id': members[i][0],
#             'rank' : rank + i,
#             'pr': members[i][1],
#             'ship_data': ship_data,
#             'user_data': user_data
#         }
#         final_result.append(result)
#     return JSONResponse.get_success_response(final_result)

# @router.post("/update/")
# async def update_rank():
#     '''更新排行榜数据'''
#     result = await Rank_tasks.update_rank()
#     return JSONResponse.get_success_response(result)