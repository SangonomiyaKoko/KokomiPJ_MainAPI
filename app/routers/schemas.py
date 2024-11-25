from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional

class RegionList(str, Enum):
    '''
    关于region和region_id的区别

    region主要是用于和前端相关进行交互

    region_id主要是后端处理时使用
    '''
    asia = "asia"
    eu = "eu"
    na = "na"
    ru = "ru"
    cn = "cn"

class LanguageList(str, Enum):
    cn = 'cn'
    en = 'en'
    ja = 'ja'
    ru = 'ru'

class UserBaseModel(BaseModel):
    region_id: int = Field(..., description='服务器id')
    account_id: int = Field(..., description='用户id')

class ClanBaseModel(BaseModel):
    region_id: int = Field(..., description='服务器id')
    clan_id: int = Field(..., description='用户id')

class UserBaseDerivedModel(BaseModel):
    region: RegionList = Field(..., description='服务器')
    account_id: int = Field(..., description='用户id')

class UserInfoModel(UserBaseModel):
    is_active: int = Field(None, description='是否活跃')
    active_level: int = Field(None, description='活跃等级')
    is_public: int = Field(None, description='是否隐藏战绩')
    total_battles: int = Field(None, description='总战斗场次')
    last_battle_time: int = Field(None, description='最后战斗时间')

class UserBasicModel(UserBaseModel):
    nickname: str = Field(..., description='用户名称')

class RecentEnableModel(UserBaseDerivedModel):
    recent_class: Optional[int] = Field(30, description='需要更新的字段')

class UserRecentModel(UserBaseModel):
    recent_class: Optional[int] = Field(None, description='需要更新的字段')
    last_update_time: Optional[int] = Field(None, description='需要更新的字段')

class UserInfoUpdateModel(BaseModel):
    user_basic: UserBasicModel = Field(None, description='用户基础数据')
    user_info: UserInfoModel = Field(None, description='用户详细数据')

class UserCacheModel(UserBaseModel):
    battles_count: int = Field(None, description='战斗总场次')
    hash_value: str = Field(None, description='缓存数据的哈希值')
    ships_data: dict = Field(None, description='船只数据，简略')
    details_data: dict = Field(None, description='船只数据，详细')

class ClanUsersModel(ClanBaseModel):
    hash_value: str = Field(None, description='缓存数据的哈希值')
    user_list: list = Field(..., description='工会内用户id列表')
    clan_users: list = Field(..., description='工会内用户数据')
    
class UserUpdateModel(BaseModel):
    user_basic: UserBasicModel = Field(None, description='用户基础数据')
    user_info: UserInfoModel = Field(None, description='用户详细数据')
    user_recent: UserRecentModel = Field(None, description='用户recent功能数据')
    user_cache: UserCacheModel = Field(None, description='用户缓存数据')
