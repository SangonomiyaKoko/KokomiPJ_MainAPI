import sqlite3
import json

def main():
    db_path = r'F:\Kokomi_PJ_MainAPI\temp\db\1\2023619512.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    sql = f'''
    SELECT date, valid, leveling_points FROM user_info;
    '''
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    # 获取日期最小是
    tz_offset = 8
    min_date = max(min(t[0] for t in rows), 20221231)
    db_data = {}
    for row in rows:
        db_data[row[0]] = [True if row[1] == 0 else False, row[2]]
    min_timestamp = date2timestamp(min_date, tz_offset)
    max_timestamp = date2timestamp(int(time.strftime("%Y%m%d", time.gmtime(int(time.time()) + tz_offset * 3600))), tz_offset)
    current_timestamp = min_timestamp
    db_result = {}
    exists_years = []
    while current_timestamp <= max_timestamp - 24*60*60:
        date_1 = timestamp2date(current_timestamp, tz_offset)
        date_1_data = db_data.get(date_1)
        current_timestamp += 24*60*60
        date_2 = timestamp2date(current_timestamp, tz_offset)
        year = int(str(date_2)[:4])
        if year not in exists_years:
            exists_years.append(year)
        date_2_data = db_data.get(date_2)
        if date_1_data and date_2_data:
            if date_1_data[0] and date_2_data[0]:
                counts = date_2_data[1] - date_1_data[1]
                db_result[date_2] = counts
            else:
                # Hidden
                db_result[date_2] = -1
        else:
            # error
            db_result[date_2] = -2
    result = {
        'years': exists_years,
        'data': {}
    }
    for year in exists_years:
        year_data = []
        days = generate_date_list(year)
        for day in days:
            if day not in db_result:
                year_data.append(None)
            else:
                year_data.append(db_result[day])
        result['data'][year] = year_data
    print(result)

import time
from datetime import datetime, timezone, timedelta

def timestamp2date(timestamp: int, tz_offset: int) -> int:
    date = time.strftime("%Y%m%d", time.gmtime(timestamp + tz_offset * 3600))
    return int(date)

def generate_date_list(year: int):
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)
    delta = timedelta(days=1)
    
    date_list = []
    current = start_date
    while current <= end_date:
        date_list.append(int(current.strftime("%Y%m%d")))
        current += delta
    return date_list

def date2timestamp(date_number: int, tz_offset: int) -> int:
    # 将数字格式转换为字符串格式日期
    date_str = str(date_number)
    dt = datetime.strptime(date_str, "%Y%m%d")
    
    # 构造对应的时区
    tz = timezone(timedelta(hours=tz_offset))
    
    # 添加时区信息
    dt = dt.replace(tzinfo=tz)
    
    # 返回对应时间戳
    return int(dt.timestamp())

if __name__ == '__main__':
    main()