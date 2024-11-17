from fastapi import APIRouter

from app.response import ResponseDict
from app.apis.root import RootData

router = APIRouter()

@router.get("/users/overview/")
async def getUsersOverview() -> ResponseDict:
    # 请求数据
    result = await RootData.get_basic_user_overview()
    return result

@router.get("/clans/overview/")
async def getClansOverview() -> ResponseDict:
    # 请求数据
    result = await RootData.get_basic_user_overview()
    return result

@router.get("/recent/overview/")
async def getRecentOverview() -> ResponseDict:
    # 请求数据
    result = await RootData.get_recent_user_overview()
    return result

@router.get("/mysql/trx/")
async def getTrx() -> ResponseDict:
    # 请求数据
    result = await RootData.get_innodb_trx()
    return result

@router.get("/mysql/processlist/")
async def getProcessList() -> ResponseDict:
    # 请求数据
    result = await RootData.get_innodb_processlist()
    return result