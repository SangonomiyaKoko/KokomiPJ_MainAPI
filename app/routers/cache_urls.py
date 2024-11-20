from fastapi import APIRouter

from app.response import ResponseDict
from app.apis.cache import UserCache
from .schemas import UserCacheModel

router = APIRouter()

@router.get("/user/cache/")
async def getUserCache(offset: int, limit: int = 1000) -> ResponseDict:
    """批量获取用户的Cache数据

    从offset开始获取最大limit的数据

    参数:
    - offset: 偏移量
    - limit: 最多返回值数量

    返回:
    - ResponseDict
    """
    result = await UserCache.get_user_cache_data_batch(offset, limit)
    return result

@router.put("/user/cache/")
async def updateUserCache(user_cache: UserCacheModel) -> ResponseDict:
    """更新用户的Cache数据

    通过传入的数据更新Cache数据库

    参数:
    - UserCacheModel
    
    返回:
    - ResponseDict
    """
    result = await UserCache.update_user_cache_data(user_cache.model_dump())
    return result