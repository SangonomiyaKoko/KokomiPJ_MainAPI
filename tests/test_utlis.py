import sys
sys.path.append('F:\Kokomi_PJ_Api')

import asyncio
import traceback

from app.utils import UtilityFunctions, ColorUtils
from app.utils import ShipName


async def main():
    # 从环境中加载配置
    try: 
        result = ColorUtils.get_rating_color(0,80) 
        print(result)
    except:
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())