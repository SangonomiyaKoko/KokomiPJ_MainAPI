class UserAccessToken:
    '''存储用户ac数据

    VortexAPI的AccessToken
    
    account_id： 'access_token'
    '''
    access_token_list = {1:{},2:{},3:{},4:{211817574:'X3mXceQus5lufCl5pJi5CMG6IKY'},5:{}} # 测试数据
    
    @classmethod
    def get_ac_value_by_rid(cls, region_id: int) -> dict:
        return cls.access_token_list.get(region_id)
    
    @classmethod
    def get_ac_value_by_id(cls, account_id: int,region_id: int) -> str | None:
        return cls.access_token_list[region_id].get(account_id, None)
    
class UserAccessToken2:
    '''用户ac2数据
    
    OfficialAPI的AccessToken
    '''

    def get_ac_value_by_id(account_id: int, region_id: int) -> str | None:
        if account_id == 2023619512:
            # 测试Token过期时间：2024/12/15 23:59:59
            return '368a12ec52c9572915f0620c67c83ab7a5396cd4' # 测试数据
        else:
            return None
    
    def set_ac_value(account_id: int, region_id: int, ac_value: str):
        return None