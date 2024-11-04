import sys
sys.path.append('F:\Kokomi_PJ_Api')

import asyncio
import traceback

from app.utils import UtilityFunctions
from app.utils import ShipName


async def main():
    # 从环境中加载配置
    try: 
        result = ShipName.search_ship('4501',1,'cn')
        print(result)
    except:
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())