"""
错误类型：
1. 网络错误
2. 数据库错误
3. 缓存错误
4. 后台任务错误
5. 其他程序错误

错误日志（基础结构）
错误id
错误类型
错误文件
错误时间
错误信息
"""

import os

from app.utils import TimeFormat

log_path = r'F:\Kokomi_PJ_Api\temp\log'

def write_error_info(
    error_id: str,
    error_type: str,
    error_name: str,
    error_file: str,
    error_info: str
):
    now_day = TimeFormat.get_today()
    form_time = TimeFormat.get_form_time()
    with open(os.path.join(log_path, f'{now_day}.txt'), "a", encoding="utf-8") as f:
        f.write('-------------------------------------------------------------------------------------------------------------\n')
        f.write(f">Platform:     API\n")
        f.write(f">Error ID:     {error_id}\n")
        f.write(f">Error Type:   {error_type}\n")
        f.write(f">Error Name:   {error_name}\n")
        f.write(f">Error File:   {error_file}\n")
        f.write(f">Error Time:   {form_time}\n")
        f.write(f">Error Info: {error_info}\n")
        f.write('-------------------------------------------------------------------------------------------------------------\n')
    f.close()