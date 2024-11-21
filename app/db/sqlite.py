import os
import sqlite3
from sqlite3 import Connection

from app.core import EnvConfig

class SQLiteConnection:
    config = EnvConfig.get_config()

    @classmethod
    def get_recent_db_path(self, account_id: int,region_id: int) -> str:
        "获取db文件path"
        return os.path.join(self.config.SQLITE_PATH, f'{region_id}', f'{account_id}.db')
    
    @classmethod
    def get_del_dir_path(self) -> str:
        "获取暂存删除数据的目录"
        return os.path.join(self.config.SQLITE_PATH, 'del')

    def get_db_connection(db_path: str) -> Connection:
        "获取数据库连接"
        connection = sqlite3.connect(db_path)
        return connection
    