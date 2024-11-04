# -*- coding: utf-8 -*-

from pydantic_settings import BaseSettings

class LoadConfig(BaseSettings):
    API_HOST: str
    API_PORT: int

    MYSQL_HOST: str
    MYSQL_PORT: int
    MYSQL_USERNAME: str
    MYSQL_PASSWORD: str

    SQLITE_PATH: str
    
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str

    USE_PROXY: int

    class Config:
        env_file = ".env"

class EnvConfig:
    __cache = None

    @classmethod
    def get_config(self) -> LoadConfig:
        if self.__cache is None:
            config = LoadConfig()
            self.__cache = config
            return config
        else:
            return self.__cache
