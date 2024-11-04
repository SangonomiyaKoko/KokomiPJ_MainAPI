import os
import json

class JsonData:
    '''加载json数据
    '''
    __file_path = os.path.dirname(__file__)

    @classmethod
    def read_json_data(self, json_file_name: str):
        file_path = os.path.join(self.__file_path,f'{json_file_name}.json')
        temp = open(file_path, "r", encoding="utf-8")
        data = json.load(temp)
        temp.close()
        return data
    
    @classmethod
    def write_json_data(self, json_file_name: str, json_data: dict):
        file_path = os.path.join(self.__file_path,f'{json_file_name}.json')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(json_data, ensure_ascii=False))
        f.close()