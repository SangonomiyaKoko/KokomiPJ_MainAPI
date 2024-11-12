import time
from typing import Optional

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
        time_format: str = "%Y-%m-%d %H:%M:%S",
        timestamp: Optional[int] = None
    ):
        if isinstance(timestamp, int):
            return time.strftime(time_format, time.localtime(timestamp))
        else:
            timestamp = self.get_current_timestamp()
            return time.strftime(time_format, time.localtime(timestamp))
