# -*- coding: utf-8 -*-

from pydantic_settings import BaseSettings

class LoadConfig(BaseSettings):
    API_TYPE: str

    LOG_PATH: str
    CACHE_PATH: str
    LEADER_PATH: str
    JSON_PATH: str

    MYSQL_HOST: str
    MYSQL_PORT: int
    MYSQL_USERNAME: str
    MYSQL_PASSWORD: str

    DB_NAME_MAIN: str
    DB_NAME_BOT: str
    DB_NAME_SHIP: str

    SQLITE_PATH: str
    
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str
    
    RABBITMQ_HOST: str
    RABBITMQ_USERNAME: str
    RABBITMQ_PASSWORD: str

    WG_API_TOKEN: str
    LESTA_API_TOKEN: str

    class Config:
        env_file = ".env"

class EnvConfig:
    __cache = None

    @classmethod
    def get_config(cls) -> LoadConfig:
        if cls.__cache is None:
            config = LoadConfig()
            cls.__cache = config
            return config
        else:
            return cls.__cache
