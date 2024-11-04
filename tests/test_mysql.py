import sys
sys.path.append('F:\Kokomi_PJ_Api')

import asyncio
import traceback

from app.core import EnvConfig
from app.db import MysqlConnection
from app.models import UserModel

async def main():
    # 从环境中加载配置
    try: 
        EnvConfig.get_config()
        # 初始化mysql并测试mysql连接
        await MysqlConnection.test_mysql()
        data = {
            'is_active': -1,
            'active_level': 0,
            'is_public': 0,
            'total_battles': 0,
            'last_battle_time': 0
        }
        res = await UserModel.check_user_info(2023619512,data)
        print(res)
    except:
        traceback.print_exc()
    finally:
        await MysqlConnection.close_mysql()
        await asyncio.sleep(3)

if __name__ == '__main__':
    asyncio.run(main())