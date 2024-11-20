from fastapi import APIRouter

from app.response import ResponseDict
from app.apis.root import RootData

router = APIRouter()

@router.get("/users/overview/")
async def getUsersOverview() -> ResponseDict:
    """获取数据库中用户的overview

    根据服务器通过每个服务器下用户数量

    参数:
    - None

    返回:
    - ResponseDict
    """
    result = await RootData.get_basic_user_overview()
    return result

@router.get("/clans/overview/")
async def getClansOverview() -> ResponseDict:
    """获取数据库中工会的overview

    根据服务器通过每个服务器下工会数量

    参数:
    - None

    返回:
    - ResponseDict
    """
    result = await RootData.get_basic_user_overview()
    return result

@router.get("/recent/overview/")
async def getRecentOverview() -> ResponseDict:
    """获取数据库中启用recent用户的overview

    根据服务器通过每个服务器下用户数量

    参数:
    - None

    返回:
    - ResponseDict
    """
    result = await RootData.get_recent_user_overview()
    return result

@router.get("/mysql/trx/")
async def getTrx() -> ResponseDict:
    """获取数据库当前未提交事务的数量

    获取thread_id，用于删除未提交事务防止bug

    参数:
    - None

    返回:
    - ResponseDict
    """
    result = await RootData.get_innodb_trx()
    return result

@router.get("/mysql/processlist/")
async def getProcessList() -> ResponseDict:
    """获取数据库连接量

    用于检测数据库是否有异常使用

    参数:
    - None

    返回:
    - ResponseDict
    """
    result = await RootData.get_innodb_processlist()
    return result