#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio

from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core import EnvConfig, api_logger
from app.db import MysqlConnection
from app.response import JSONResponse as API_JSONResponse
from app.middlewares import RedisConnection, IPAccessListManager, rate_limit

from app.routers import platform_router, robot_router, recent_1_router, root_router, rank_router


# 应用程序的生命周期
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 从环境中加载配置
    EnvConfig.get_config()
    # 初始化redis并测试redis连接
    await RedisConnection.test_redis()
    # 初始化mysql并测试mysql连接
    await MysqlConnection.test_mysql()

    # 启动 lifespan
    yield

    # 应用关闭时释放连接
    await RedisConnection.close_redis()
    await MysqlConnection.close_mysql()

app = FastAPI(lifespan=lifespan)

# 捕获 RequestValidationError 异常 (HTTP_422_Unprocessable_Entity)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # 返回自定义的 JSON 错误响应
    return JSONResponse(
        content=API_JSONResponse.API_7000_InvalidParameter
    )

# 请求中间件
@app.middleware("http")
async def request_rate_limiter(request: Request, call_next):
    client_ip = request.client.host
    if IPAccessListManager.is_blacklisted(client_ip):
        # ip是否在黑名单
        return JSONResponse(
            status_code=403,
            content={"detail": "Forbidden"}
        )
    if not IPAccessListManager.is_whitelisted(client_ip):
        # ip是否在白名单，在则跳过限速检查
        check_rate_limiter = await rate_limit(client_ip)
        if check_rate_limiter not in [True, False]:
            return JSONResponse(
                status_code=500,
                content={"dateil": "Internal server error"}
            )
        if check_rate_limiter:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"}
            )
    response = await call_next(request)
    return response

@app.get("/", summary='Root', tags=['Default'])
async def root():
    """Root router

    Args:
    - None

    Returns:
    - dict

    """
    return {'status':'ok','messgae':'Hello! Welcome to Kokomi Interface.'}


# 在主路由中注册子路由
app.include_router(
    root_router, 
    prefix="/s", 
    tags=['Root Interface']
)

app.include_router(
    platform_router, 
    prefix="/p", 
    tags=['Platform Interface']
)

app.include_router(
    robot_router, 
    prefix="/r", 
    tags=['Robot Interface']
)

app.include_router(
    recent_1_router,
    prefix='/r1',
    tags=['Recent Interface']
)

app.include_router(
    rank_router,
    prefix='/rank',
    tags=['Rank Interface']
)
# 重写shutdown函数，避免某些协程bug
async def _shutdown(self, any = None):
    await origin_shutdown(self)
    wait_second = 3
    while wait_second > 0:
        api_logger.info(f'App will close after {wait_second} seconds')
        await asyncio.sleep(1)
        wait_second -= 1
    api_logger.info('App has been closed')

origin_shutdown = asyncio.BaseEventLoop.shutdown_default_executor
asyncio.BaseEventLoop.shutdown_default_executor = _shutdown  