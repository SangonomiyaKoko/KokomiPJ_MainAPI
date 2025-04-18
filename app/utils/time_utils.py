import time
from datetime import datetime, timezone, timedelta
from typing import Optional

# 各服务器默认UTC时区配置
REGION_UTC_LIST = {
    1: 8,
    2: 1,
    3: -7,
    4: 3,
    5: 8
}

class TimeFormat:
    '''时间相关工具函数

    用于获取时间以及时间格式化
    
    '''

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
    
    def db_timestamp(region_id: int):
        tz_offset = REGION_UTC_LIST.get(region_id, 8)
        return int(time.strftime("%Y%m%d", time.gmtime(int(time.time()) + tz_offset * 3600)))

    def db_timestamp2date(timestamp: int, region_id: int) -> int:
        tz_offset = REGION_UTC_LIST.get(region_id, 8)
        date = time.strftime("%Y%m%d", time.gmtime(timestamp + tz_offset * 3600))
        return int(date)

    def db_date2timestamp(date_number: int, region_id: int) -> int:
        tz_offset = REGION_UTC_LIST.get(region_id, 8)
        # 将数字格式转换为字符串格式日期
        date_str = str(date_number)
        dt = datetime.strptime(date_str, "%Y%m%d")
        # 构造对应的时区
        tz = timezone(timedelta(hours=tz_offset))
        # 添加时区信息
        dt = dt.replace(tzinfo=tz)
        # 返回对应时间戳
        return int(dt.timestamp())
    
    def db_generate_date_list(year: int):
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
        delta = timedelta(days=1)
        
        date_list = []
        current = start_date
        while current <= end_date:
            date_list.append(int(current.strftime("%Y%m%d")))
            current += delta
        return date_list
