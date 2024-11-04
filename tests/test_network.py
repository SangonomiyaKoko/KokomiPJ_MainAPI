import sys
sys.path.append('F:\Kokomi_PJ_Api')

import asyncio
import traceback

from app.network import BasicAPI


async def main():
    # 从环境中加载配置
    try: 
        result = await BasicAPI.get_clan_search(region='asia',tag='neu')
        print(result)
    except:
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())