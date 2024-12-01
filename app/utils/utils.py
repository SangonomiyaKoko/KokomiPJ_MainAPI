import hashlib

from app.const import GameData, ClanColor
from .time_utils import TimeFormat


class UtilityFunctions: 
    '''存储一些公用的函数'''
    def get_user_default_name(account_id: int):
        "获取用户的默认名称"
        return f'User_{account_id}'
    
    def get_clan_default_name():
        "获取工会的默认名称"
        return f'N/A'
    
    def get_sha256_value(hash_str: str) -> str:
        "计算SHA256哈希值"
        hash_value = hashlib.sha256(hash_str.encode('utf-8')).hexdigest()
        return hash_value
    
    def check_clan_vaild(updated_at: int):
        "检查工会缓存的更新时间是否有效"
        if not updated_at:
            return False
        current_timestamp = TimeFormat.get_current_timestamp()
        if (current_timestamp - updated_at) > 3 * 24 * 60 * 60:
            return False
        else:
            return True

    def check_aid_and_rid(account_id: int, region_id: int) -> bool:
        "检查account_id和region_id是否合法"
        if not (isinstance(account_id, int) and isinstance(region_id, int)):
            return False
        if region_id < 1 and region_id > 5:
            return False
        account_id_len = len(str(account_id))
        if account_id_len > 10:
            return False
        # 由于不知道后续会使用什么字段
        # 目前的检查逻辑是判断aid不在其他的字段内

        # 俄服 1-9 [~5字段]
        if region_id == 4 and account_id_len < 9:
            return True
        elif (
            region_id == 4 and 
            account_id_len == 9 and 
            int(account_id/100000000) not in [5,6,7,8,9,]
        ):
            return True
        # 欧服 9 [5~字段] 
        if (
            region_id == 2 and
            account_id_len == 9 and
            int(account_id/100000000) not in [1,2,3,4]
        ):
            return True
        # 亚服 10 [2-3字段]
        if (
            region_id == 1 and 
            account_id_len == 10 and
            int(account_id/1000000000) not in [1,7]
        ):
            return True
        # 美服 10 [1字段]
        if (
            region_id == 3 and
            account_id_len == 10 and
            int(account_id/1000000000) not in [2,3,7]
        ):
            return True
        # 国服 10 [7字段]
        if (
            region_id == 5 and
            account_id_len == 10 and
            int(account_id/1000000000) not in [1,2,3]
        ):
            return True
        return False
    
    def check_cid_and_rid(clan_id: int, region_id: int) -> bool:
        "检查clan_id和region_id是否合法"
        if not (isinstance(clan_id, int) and isinstance(region_id, int)):
            return False
        if region_id < 1 and region_id > 5:
            return False
        clan_id_len = len(str(clan_id))
        # 亚服 10 [2字端]
        if (
            region_id == 1 and 
            clan_id_len == 10 and
            int(clan_id/1000000000) == 2
        ):
            return True
        # 欧服 9 [5字段]
        if (
            region_id == 2 and 
            clan_id_len == 9 and
            int(clan_id/100000000) == 5
        ):
            return True
        # 美服 10 [1字段]
        if (
            region_id == 3 and 
            clan_id_len == 10 and
            int(clan_id/1000000000) == 1
        ):
            return True
        # 俄服 6 [4字段]
        if (
            region_id == 4 and 
            clan_id_len == 6 and
            int(clan_id/100000) == 4
        ):
            return True
        # 国服 10 [7字段]
        if (
            region_id == 5 and 
            clan_id_len == 10 and
            int(clan_id/1000000000) == 7
        ):
            return True
        return False
    
    def get_rid_by_aid(account_id: int) -> int | None:
        "通过account_id的字段判断region_id，没匹配到返回为空"
        account_id_len = len(str(account_id))
        if account_id_len > 10:
            return None
        if account_id_len < 9:
            return 4
        elif account_id_len == 9:
            if int(account_id/100000000) < 5:
                return 4
            else:
                return 2
        elif int(account_id/1000000000) in [2,3]:
            return 1
        elif int(account_id/1000000000) in [5,6]:
            return 2
        elif int(account_id/1000000000) in [1]:
            return 3
        elif int(account_id/1000000000) in [7]:
            return 5
        else:
            return None
        
    def get_region(region_id: int) -> str:
        "从region_id获取region"
        for r, rid in GameData.REGION_LIST.items():
            if rid == region_id:
                return r
            
    def get_region_id(region: str) -> int:
        "从region获取region_id"
        for r, rid in GameData.REGION_LIST.items():
            if r == region:
                return rid
        return None
    
    def get_league_by_color(color: int) -> int:
        # 从接口获取的颜色id转换为league数字
        return ClanColor.CLAN_COLOR_INDEX.get(color, 5)
    
    def get_active_level(user_info: dict):
        "获取active_level"
        # 具体对应关系的表格
        # | is_plblic | total_battles | last_battle_time | active_level | decs    |
        # | --------- | ------------- | ---------------- | ------------ | ------- |
        # | 0         | -             | -                | 0            | 隐藏战绩 |
        # | 1         | 0             | 0                | 1            | 无数据   |
        # | 1         | -             | [0, 1d]          | 2            | 活跃    |
        # | 1         | -             | [1d, 3d]         | 3            | -       |
        # | 1         | -             | [3d, 7d]         | 4            | -       |
        # | 1         | -             | [7d, 1m]         | 5            | -       |
        # | 1         | -             | [1m, 3m]         | 6            | -       |
        # | 1         | -             | [3m, 6m]         | 7            | -       |
        # | 1         | -             | [6m, 1y]         | 8            | -       |
        # | 1         | -             | [1y, + ]         | 9            | 不活跃  |
        is_public = user_info['is_public']
        total_battles = user_info['total_battles']
        last_battle_time = user_info['last_battle_time']
        if not is_public:
            return 0
        if total_battles == 0 or last_battle_time == 0:
            return 1
        current_timestamp = TimeFormat.get_current_timestamp()
        time_differences = [
            (1 * 24 * 60 * 60, 2),
            (3 * 24 * 60 * 60, 3),
            (7 * 24 * 60 * 60, 4),
            (30 * 24 * 60 * 60, 5),
            (90 * 24 * 60 * 60, 6),
            (180 * 24 * 60 * 60, 7),
            (360 * 24 * 60 * 60, 8),
        ]
        time_since_last_battle = current_timestamp - last_battle_time
        for time_limit, return_value in time_differences:
            if time_since_last_battle <= time_limit:
                return return_value
        return 9
        