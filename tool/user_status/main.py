#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio.selector_events
import time
import json
import asyncio
from log import log as logger

from update import Update
from network import Network
from db import DatabaseConnection
from model import update_game_version, get_game_version, get_ship_list


class ContinuousUserCacheUpdater:
    def __init__(self):
        self.stop_event = asyncio.Event()  # 停止信号

    async def update_user(self):
        start_time = int(time.time())
        # 更新游戏版本
        # for region_id in [1, 2, 3, 4, 5]:
        #     result = await Network.get_game_version(region_id)
        #     if result['code'] != 1000:
        #         logger.error(f'{region_id} | 获取服务器最新版本失败')
        #     if result['data']['version']:
        #         result = update_game_version(region_id, result['data']['version'])

        # result = get_game_version()
        result = {
            'status': 'ok', 
            'code': 1000, 
            'message': 'Success', 
            'data': {
                1: ['14.1', 1740219510], 
                2: ['14.1', 1740219511], 
                3: ['14.1', 1740219511], 
                4: ['25.2', 1740219512], 
                5: ['14.1', 1740219512]
            }
        }
        ship_data = {}
        json_file_path1 = r'F:\Kokomi_PJ_MainAPI\temp\json\ship_name_lesta.json'
        json_file_path2 = r'F:\Kokomi_PJ_MainAPI\temp\json\ship_name_wg.json'
        
        temp = open(json_file_path1, "r", encoding="utf-8")
        data = json.load(temp)
        temp.close()
        for k, v in data.items():
            ship_data[int(k)] = v['tier']
        temp = open(json_file_path2, "r", encoding="utf-8")
        data = json.load(temp)
        temp.close()
        for k, v in data.items():
            ship_data[int(k)] = v['tier']
        ship_id_data = get_ship_list()
        if result['code'] != 1000:
            logger.error(f'读取服务器版本失败')
        elif result['code'] != 1000:
            logger.error(f'读取服务器船只列表失败')
        else:
            user_cache = {}
            clan_cache = {}
            i = 0
            for ship_id in ship_id_data['data']:
                i += 1
                logger.info(f"{ship_id} 缓存数据 用户: {len(user_cache)} 工会: {len(clan_cache)}")
                await Update.main(ship_id, result['data'], user_cache, clan_cache, ship_data)
                logger.info(f"{ship_id} 数据更新完成   [{i}/{len(ship_id_data['data'])}]")
                # await asyncio.sleep(1)
        end_time = int(time.time())
        # 避免测试时候的循环bug
        if end_time - start_time <= 4*60*60-10:
            sleep_time = 4*60*60 - (end_time - start_time)
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
    logger.info('开始运行UserCache更新进程')
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