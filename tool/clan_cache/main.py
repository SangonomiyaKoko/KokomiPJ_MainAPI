#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import asyncio

from log import log as logger
from update import Update
from db import DatabaseConnection


class ContinuousUserCacheUpdater:
    def __init__(self):
        self.stop_event = asyncio.Event()  # 停止信号

    async def update_user(self):
        start_time = int(time.time())
        # 更新用户
        for region_id in [1,2,3,4,5]:
            logger.info(f'{region_id} | ---------------------------------')
            await Update.main(region_id)
        end_time = int(time.time())
        # 避免测试时候的循环bug
        if end_time - start_time <= 190:
            sleep_time = 200 - (end_time - start_time)
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
    updater = ContinuousUserCacheUpdater()

    # 创建并启动异步更新任务
    update_task = asyncio.create_task(updater.continuous_update())
    try:
        await update_task
    except asyncio.CancelledError:
        updater.stop()

if __name__ == "__main__":
    logger.info('开始运行ClanCache更新进程')
    DatabaseConnection.init_pool()
    # 开始不间断更新
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('收到进程关闭信号')
    # 退出并释放资源
    DatabaseConnection.close_pool()
    wait_second = 3
    while wait_second > 0:
        logger.info(f'进程将在 {wait_second} s后关闭')
        time.sleep(1)
        wait_second -= 1
    logger.info('UserCache更新进程已停止')