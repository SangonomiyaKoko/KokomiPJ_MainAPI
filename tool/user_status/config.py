# -*- coding: utf-8 -*-

from pydantic_settings import BaseSettings

class LoadConfig(BaseSettings):
    LOG_PATH: str
    CACHE_PATH: str
    LEADER_PATH: str

    MYSQL_HOST: str
    MYSQL_PORT: int
    MYSQL_USERNAME: str
    MYSQL_PASSWORD: str

    DB_NAME_MAIN: str
    DB_NAME_BOT: str
    DB_NAME_SHIP: str
    
    RABBITMQ_HOST: str
    RABBITMQ_USERNAME: str
    RABBITMQ_PASSWORD: str

    class Config:
        env_file = ".env"
        extra = 'allow'

settings = LoadConfig()