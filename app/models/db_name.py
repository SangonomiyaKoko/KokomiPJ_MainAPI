from app.core import EnvConfig

config = EnvConfig.get_config()

MAIN_DB = config.DB_NAME_MAIN
BOT_DB = config.DB_NAME_BOT
CACHE_DB = config.DB_NAME_SHIP