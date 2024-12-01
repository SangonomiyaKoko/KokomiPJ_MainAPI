class UserAccessToken:
    '''存储用户ac数据

    VortexAPI的AccessToken
    
    account_id： 'access_token'
    '''
    access_token_list = {1:{},2:{},3:{},4:{211817574:'X3mXceQus5lufCl5pJi5CMG6IKY'},5:{}}
    
    @classmethod
    def get_ac_value_by_rid(self, region_id: int) -> dict:
        return self.access_token_list.get(region_id)
    
    @classmethod
    def get_ac_value_by_id(self, account_id: int,region_id: int) -> str | None:
        return self.access_token_list[region_id].get(account_id, None)
    
class UserAccessToken2:
    '''用户ac2数据
    
    OfficialAPI的AccessToken
    '''

    def get_ac_by_id(account_id: int, region_id: int) -> str | None:
        return None
    
    def set_ac_value(account_id: int, region_id: int, ac_value: str):
        return None