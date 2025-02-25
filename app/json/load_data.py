import os
import json
from app.core import EnvConfig

config = EnvConfig.get_config()

class JsonData:
    '''加载json数据'''
    def read_json_data(self, json_file_name: str):
        file_path = os.path.join(config.JSON_PATH,f'{json_file_name}.json')
        temp = open(file_path, "r", encoding="utf-8")
        data = json.load(temp)
        temp.close()
        return data
    
    def write_json_data(self, json_file_name: str, json_data: dict):
        file_path = os.path.join(config.JSON_PATH,f'{json_file_name}.json')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(json_data, ensure_ascii=False))
        f.close()