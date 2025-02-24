from typing import Optional

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse as ReturnJSONResponse

from .schemas import (
    APPUserRegisterModel, APPUserLoginModel, APPUserLogoutModel
)
from app.core import ServiceStatus
from app.utils import UtilityFunctions
from app.response import JSONResponse, ResponseDict
from app.middlewares import record_api_call

router = APIRouter()

SUPPORTED_VERSIONS = ["1.0", "2.0"]

@router.post("/auth/register/", summary="用户注册接口")
async def userRegister(request: Request, UserRegisterData: APPUserRegisterModel) -> ResponseDict:
    """用户注册功能
    
    注册用户，注册成功返回code1000

    参数:
    - (Header)Accept-Version: str
    - UserRegisterData: APPUserRegisterModel

    返回:
    - ResponseDict
    """
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    app_version = request.headers.get("Accept-Version")
    if not app_version or app_version not in SUPPORTED_VERSIONS:
        # TODO: 返回版本不支持
        pass
    result = JSONResponse.get_success_response(UserRegisterData.model_dump())
    # TODO: 用户注册功能     参数效验->验证码效验->邀请码效验
    await record_api_call(result['status'])
    return result

@router.post("/auth/login/", summary="用户登录接口")
async def userLogin(request: Request, UserLoginData: APPUserLoginModel) -> ResponseDict:
    """用户登录功能
    
    登录成功返回set_cookie和code1000

    参数:
    - (Header)Accept-Version: str
    - UserLoginData: APPUserLoginModel

    返回:
    - ResponseDict
    """
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    app_version = request.headers.get("Accept-Version")
    if not app_version or app_version not in SUPPORTED_VERSIONS:
        # TODO: 返回版本不支持
        pass
    result = JSONResponse.get_success_response(UserLoginData.model_dump())
    # TODO: 用户登录功能     检查账号或者密码是否正确
    response = ReturnJSONResponse(content=result)
    response.set_cookie(
        key='access_token',
        value='123456abc',
        expires=60,
        httponly=True
    )
    await record_api_call(result['status'])
    return response

@router.post("/auth/logout/", description="用户登出接口")
async def userLogout(request: Request, UserLogoutData: APPUserLogoutModel) -> ResponseDict:
    """用户登出功能
    
    删除用户的登录token，删除成功返回code1000

    参数:
    - (Header)Accept-Version: str
    - UserLogoutData: APPUserLogoutModel

    返回:
    - ResponseDict
    """
    if not ServiceStatus.is_service_available():
        return JSONResponse.API_8000_ServiceUnavailable
    app_version = request.headers.get("Accept-Version")
    if not app_version or app_version not in SUPPORTED_VERSIONS:
        # TODO: 返回版本不支持
        pass
    result = JSONResponse.get_success_response(UserLogoutData.model_dump())
    await record_api_call(result['status'])
    return result
