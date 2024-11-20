class UserAccessToken:
    '''存储用户ac数据

    用户ac数据格式 
    
    account_id： 'access_token'
    '''
    access_token_list = {1:{},2:{},3:{},4:{211817574:'X3mXceQus5lufCl5pJi5CMG6IKY'},5:{}}
    
    @classmethod
    def get_ac_value_by_rid(self, region_id: int) -> dict:
        return self.access_token_list.get(region_id)
    
    @classmethod
    def get_ac_value_by_aid(self, account_id: int,region_id: int) -> str | None:
        return self.access_token_list[region_id].get(account_id, None)
    