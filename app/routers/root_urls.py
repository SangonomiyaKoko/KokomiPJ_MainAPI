from fastapi import APIRouter

from app.response import ResponseDict, JSONResponse
from app.core import ServiceStatus
from app.apis.root import RootData
from app.middlewares import record_api_call

router = APIRouter()

@router.get("/service/status")
async def getServiceStatus() -> ResponseDict:
    """获取当前服务的状态
    
    返回True或者False表示是否处于维护状态

    参数:
    - None

    返回:
    - ResponseDict
    """
    result = ServiceStatus.is_service_available()
    if result:
        data = {
            'status': 'Maintenance'
        }
    else:
        data = {
            'status': 'OK'
        }
    return JSONResponse.get_success_response(data)

@router.post("service/status")
async def setServiceStatus(set: bool = False) -> ResponseDict:
    """修改服务器当前的状态
    
    设置服务器为维护或者运行状态
    """
    if set:
        ServiceStatus.service_set_available()
    else:
        ServiceStatus.service_set_unavailable()
    return JSONResponse.API_1000_Success

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
    await record_api_call(result['status'])
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
    result = await RootData.get_basic_clan_overview()
    await record_api_call(result['status'])
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
    await record_api_call(result['status'])
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
    await record_api_call(result['status'])
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
    await record_api_call(result['status'])
    return result