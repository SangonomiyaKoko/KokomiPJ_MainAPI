#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import asyncio

from log import log as logger
from config import settings
from db import DatabaseConnection
from update import Update
from model import get_user_token, get_recent_users


CLIENT_TYPE = settings.API_TYPE

class ContinuousUserUpdater:
    def __init__(self):
        self.stop_event = asyncio.Event()  # 停止信号

    async def update_user(self):
        start_time = int(time.time())
        # 更新用户
        for region_id in [1, 2, 3, 4, 5]:
            token_result = get_user_token(region_id)
            if token_result['code'] != 1000:
                logger.error(f"获取UserToken时发生错误，Error: {request_result.get('message')}")
            logger.debug(token_result)
            request_result = get_recent_users(region_id)
            if request_result['code'] != 1000:
                logger.error(f"获取RecentUser时发生错误，Error: {request_result.get('message')}")
                continue
            logger.debug(request_result)
            for account_id in request_result['data']:
                if str(region_id) + str(account_id) in request_result['data']:
                    ac_value = request_result['data'][str(region_id) + str(account_id)]
                else:
                    ac_value = None
                logger.info(f'{region_id} - {account_id} | ---------------------------------')
                await Update.main(account_id,region_id,ac_value)
        end_time = int(time.time())
        # 避免测试时候的循环bug
        if end_time - start_time <= 50:
            sleep_time = 60 - (end_time - start_time)
            logger.info(f'更新线程休眠 {round(sleep_time,2)} s')
            await asyncio.sleep(sleep_time)

    async def continuous_update(self):
        # 持续循环更新，直到接收到停止信号
        # 似乎写不写没区别(
        while not self.stop_event.is_set():  
            await self.update_user()

    def stop(self):
        self.stop_event.set()  # 设置停止事件

async def main():
    updater = ContinuousUserUpdater()

    # 创建并启动异步更新任务
    update_task = asyncio.create_task(updater.continuous_update())
    try:
        await update_task
    except asyncio.CancelledError:
        updater.stop()

if __name__ == "__main__":
    logger.info('开始运行Recent更新进程')
    DatabaseConnection.init_pool()
    # 启动配置
    if CLIENT_TYPE == 'master':
        logger.debug(f'当前角色: Master-主服务')
    else:
        logger.debug(f'当前角色: Salve-从服务')
    # if CLIENT_TYPE != 'master':
    #     logger.debug(f'Slave支持的列表: {str(SALVE_REGION)}')
    # 开始不间断更新
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('收到进程关闭信号')
    DatabaseConnection.close_pool()
    # 退出并释放资源
    wait_second = 3
    while wait_second > 0:
        logger.info(f'进程将在 {wait_second} s后关闭')
        time.sleep(1)
        wait_second -= 1
    logger.info('Recent更新进程已停止')