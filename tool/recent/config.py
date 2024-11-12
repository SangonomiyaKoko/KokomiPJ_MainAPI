CLIENT_TYPE = 'master'    # 主从模式，master/salve
CLIENT_NAME = 'Master_01'
LOG_PATH = r'F:\Kokomi_PJ_Api\temp\log'
LOG_LEVEL = 'debug' # 日志模式，debug/info

REGION_UTC_LIST = {1:8, 2:1, 3:-7, 4:3, 5:8}

# master配置
MASTER_DB_PATH = r''
MASTER_API_URL = '12.7.0.0.1:8000'

# slave配置
SALVE_REGION = [1,2,3,4,5]
SALVE_API_URL = ''