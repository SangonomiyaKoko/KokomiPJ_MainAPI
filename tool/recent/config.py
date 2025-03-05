# -*- coding: utf-8 -*-

from pydantic_settings import BaseSettings

class LoadConfig(BaseSettings):
    API_TYPE: str

    LOG_PATH: str

    MYSQL_HOST: str
    MYSQL_PORT: int
    MYSQL_USERNAME: str
    MYSQL_PASSWORD: str

    DB_NAME_MAIN: str
    DB_NAME_BOT: str
    DB_NAME_SHIP: str

    class Config:
        env_file = ".env"
        extra = 'allow'

settings = LoadConfig()