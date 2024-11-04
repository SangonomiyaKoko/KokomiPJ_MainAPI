import time
from typing import Optional
from datetime import datetime, timedelta

class TimeFormat:
    '''时间相关工具函数

    用于获取时间以及时间格式化
    
    '''
    # 各服务器默认UTC时区配置
    REGION_UTC_LIST = {
        'asia': 8,
        'eu': 1,
        'na': -7,
        'ru': 3,
        'cn': 8
    }

    def get_current_timestamp() -> int:
        "获取当前时间戳"
        return int(time.time())
    
    def get_today():
        return time.strftime("%Y-%m-%d", time.localtime(time.time()))
    
    @classmethod
    def get_form_time(
        self,
        timestamp: Optional[int] = None, 
        time_format: str = "%Y-%m-%d %H:%M:%S"
    ):
        if isinstance(timestamp, int):
            return time.strftime(time_format, time.localtime(timestamp))
        else:
            timestamp = self.get_current_timestamp()
            return time.strftime(time_format, time.localtime(timestamp))
    
    def convert_timestamp_with_offset(self, timestamp, region):
        offset = self.REGION_UTC_LIST.get(region, 0)
        # 将时间戳转换为 UTC 时间
        utc_time = datetime.fromtimestamp(timestamp)
        # 根据偏移量创建时间差
        time_offset = timedelta(hours=offset)
        # 转换为目标时区时间
        target_time = utc_time + time_offset
        return target_time