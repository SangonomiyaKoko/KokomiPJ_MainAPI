#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core import EnvConfig, api_logger
from app.db import MysqlConnection
from app.middlewares import RedisConnection, rate_limit, check_ip_whilelist, check_ip_blacklist

from app.routers import platform_router

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

@app.middleware("http")
async def request_rate_limiter(request: Request, call_next):
    client_ip = request.client.host
    if check_ip_blacklist(client_ip):
        # ip是否在黑名单
        return JSONResponse(
            status_code=403,
            content={"detail": "Forbidden"}
        )
    if check_ip_whilelist(client_ip) == False:
        # ip是否在白名单，在则跳过限速检查
        check_rate_limiter = await rate_limit(client_ip)
        if check_rate_limiter is None:
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


app.include_router(
    platform_router, 
    prefix="/p", 
    tags=['Platform Interface']
)
 
async def _shutdown(self):
    await origin_shutdown(self)
    wait_second = 3
    while wait_second > 0:
        api_logger.info(f'App will close after {wait_second} seconds')
        await asyncio.sleep(1)
        wait_second -= 1
    api_logger.info('App has been closed')

origin_shutdown = asyncio.BaseEventLoop.shutdown_default_executor
asyncio.BaseEventLoop.shutdown_default_executor = _shutdown  