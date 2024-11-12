class UserAccessToken:
    '''存储用户ac数据

    用户ac数据格式 
    
    account_id： 'access_token'
    '''
    access_token_list = {1:{},2:{},3:{},4:{},5:{}}
    
    @classmethod
    def get_ac_value_by_rid(self, region_id) -> dict:
        return self.access_token_list.get(region_id)