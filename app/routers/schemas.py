from enum import Enum

class RegionList(str, Enum):
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