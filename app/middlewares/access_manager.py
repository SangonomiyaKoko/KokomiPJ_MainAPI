# 由于需求不大，就不用数据库存储数据
IP_WHITE_LIST = ['127.0.0.1']
IP_BLACK_LIST = []
USER_BLACK_LIST = []
CLAN_BLACK_LIST = []

class IPAccessListManager:
    def is_blacklisted(host: str) -> bool:
        if host in IP_BLACK_LIST:
            return True
        else:
            return False
    def is_whitelisted(host: str) -> bool:
        if host in IP_WHITE_LIST:
            return True
        else:
            return False
        
class UserAccessListManager:
    def is_blacklisted(account_id: int) -> bool:
        if account_id in USER_BLACK_LIST:
            return True
        else:
            return False
    
class ClanAccessListManager:
    def is_blacklisted(clan_id: int) -> bool:
        if clan_id in CLAN_BLACK_LIST:
            return True
        else:
            return False