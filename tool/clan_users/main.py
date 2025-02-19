#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import asyncio

from log import CLIENT_NAME
from log import log as logger
from update import Update
from db import DatabaseConnection
from model import get_clan_max_number, get_clan_cache_batch



class ContinuousUserCacheUpdater:
    def __init__(self):
        self.stop_event = asyncio.Event()  # 停止信号

    async def update_user(self):
        start_time = int(time.time())

        limit = 10
        request_result = get_clan_max_number()
        if request_result['code'] != 1000:
            logger.error(f"获取MaxClanID时发生错误，Error: {request_result.get('message')}")
        else:
            max_id = request_result['data']['max_id']
            max_offset = (int(max_id / limit) + 1) * limit
            offset = 0
            while offset <= max_offset:
                clans_result = get_clan_cache_batch(offset, limit)
                if clans_result['code'] == 1000:
                    i = 0
                    for clan in clans_result['data']:
                        clan_id = clan['clan_basic']['clan_id']
                        region_id = clan['clan_basic']['region_id']
                        logger.info(f'{region_id} - {clan_id} | ------------------[ {offset + i} / {max_id} ]')
                        await Update.main(clan_id, region_id, clan)
                        await asyncio.sleep(10)
                        i += 1
                else:
                    logger.error(f"获取CacheClans时发生错误，Error: {clans_result.get('message')}")
                offset += limit
        end_time = int(time.time())
        # 避免测试时候的循环bug
        if end_time - start_time <= 6*60*60-10:
            sleep_time = 6*60*60 - (end_time - start_time)
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
    logger.info(f'开始运行{CLIENT_NAME}更新进程')
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
    logger.info(f'{CLIENT_NAME}更新进程已停止')