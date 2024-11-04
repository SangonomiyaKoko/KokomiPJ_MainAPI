#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
from log import log as recent_logger
from config import CLIENT_TYPE, SALVE_REGION

if __name__ == "__main__":
    recent_logger.info('开始运行Recent更新进程')
    if CLIENT_TYPE == 'master':
        recent_logger.debug(f'当前角色: Master-主服务')
    else:
        recent_logger.debug(f'当前角色: Salve-从服务')
    if CLIENT_TYPE != 'master':
        recent_logger.debug(f'Slave支持的列表: {str(SALVE_REGION)}')
    recent_logger.info('Recent更新进程已关闭')
    # asyncio.run(

    # )