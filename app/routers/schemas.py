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

class UserBasicAndInfoModel(BaseModel):
    basic: Optional[UserBasicModel] = Field(None, description='用户基础数据')
    info: Optional[UserInfoModel] = Field(None, description='用户详细数据')

class UserRecentModel(UserBaseModel):
    recent_class: Optional[int] = Field(None, description='需要更新的字段')
    last_query_time: Optional[int] = Field(None, description='需要更新的字段')
    last_update_time: Optional[int] = Field(None, description='需要更新的字段')

class RecentEnableModel(UserBaseDerivedModel):
    recent_class: Optional[int] = Field(30, description='需要更新的字段')

class UserCacheModel(UserBaseModel):
    battles_count: int = Field(None, description='战斗总场次')
    hash_value: str = Field(None, description='缓存数据的哈希值')
    ships_data: bytes = Field(None, description='二进制存储的用户船只数据')
    delete_ship_list: list = Field(None, description='需要删除的船只数据')
    replace_ship_dict: dict = Field(None, description='需要修改的船只数据')
