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

class PlatformList(str, Enum):
    qq_bot = 'qq_bot'
    qq_group = 'qq_group'
    qq_guild = 'qq_guild'
    discord = 'discord'

class LanguageList(str, Enum):
    chinese = 'chinese'
    english = 'english'
    japanese = 'japanese'
    # 俄语仅在搜索船只接口可用其他接口不支持
    russian = 'russian'

class AlgorithmList(str, Enum):
    pr = 'pr'

class UserBaseModel(BaseModel):
    region_id: int = Field(..., description='服务器id')
    account_id: int = Field(..., description='用户id')

class RecentEnableModel(UserBaseModel):
    recent_class: Optional[int] = Field(30, description='需要更新的字段')

class BotUserBindModel(BaseModel):
    platform: str = Field(..., description='平台')
    user_id: str = Field(..., description='用户id')
    region_id: int = Field(..., description='服务器id')
    account_id: int = Field(..., description='用户id')

class APPUserRegisterModel(BaseModel):
    email: str = Field(..., description="邮箱")
    password: str = Field(..., description="密码")
    verification_code: str = Field(..., description="验证码")
    invitation_code: str = Field(..., description="邀请码")

class APPUserLoginModel(BaseModel):
    email: str = Field(..., description="邮箱")
    password: str = Field(..., description="密码")

class APPUserLogoutModel(BaseModel):
    token: str = Field(..., description="需要登出用户的token")