from app.json import JsonData
from app.const import GameData

class ShipName:
    '''船只相关数据'''
    def __name_format(in_str: str) -> str:
        in_str_list = in_str.split()
        in_str = None
        in_str = ''.join(in_str_list)
        en_list = {
            'a': ['à', 'á', 'â', 'ã', 'ä', 'å'],
            'e': ['è', 'é', 'ê', 'ë'],
            'i': ['ì', 'í', 'î', 'ï'],
            'o': ['ó', 'ö', 'ô', 'õ', 'ò', 'ō'],
            'u': ['ü', 'û', 'ú', 'ù', 'ū'],
            'y': ['ÿ', 'ý'],
            'l': ['ł']
        }
        for en, lar in en_list.items():
            for index in lar:
                if index in in_str:
                    in_str = in_str.replace(index, en)
                if index.upper() in in_str:
                    in_str = in_str.replace(index.upper(), en.upper())
        re_str = ['_', '-', '·', '.', '\'','(',')','（','）']
        for index in re_str:
            if index in in_str:
                in_str = in_str.replace(index, '')
        in_str = in_str.lower()
        return in_str
        
    @classmethod
    def search_ship(
        self,
        ship_name: str,
        region_id: int,
        language: str
    ):
        '''搜索船只

        参数:
            ship_name: 搜索的名称
            region_id: 服务器id
            language: 搜索的语言
            check: 使用完全匹配还是模糊匹配
        '''
        if region_id == 4:
            server = 'lesta'
        else:
            server = 'wg'
        nick_data = JsonData.read_json_data('ship_name_nick')
        main_data = JsonData.read_json_data(f'ship_name_{server}')
        ship_name_format: str = self.__name_format(ship_name)
        if ship_name_format.endswith(('old','旧')):
            old = True
        else:
            old = False

        result = {}
        # 别名表匹配
        for ship_id, ship_data in nick_data[language].items():
            for index in ship_data:
                if ship_name_format == self.__name_format(index):
                    result[ship_id] = {
                        'tier':main_data[ship_id]['tier'],
                        'type':main_data[ship_id]['type'],
                        'cn':main_data[ship_id]['ship_name']['cn'],
                        'en':main_data[ship_id]['ship_name']['en'],
                        'ja':main_data[ship_id]['ship_name']['ja'],
                        'ru':main_data[ship_id]['ship_name']['ru']
                    }
                    return result
        for ship_id, ship_data in main_data.items():
            if ship_name_format == self.__name_format(ship_data['ship_name']['en']):
                result[ship_id] = {
                    'tier':main_data[ship_id]['tier'],
                    'type':main_data[ship_id]['type'],
                    'cn':main_data[ship_id]['ship_name']['cn'],
                    'en':main_data[ship_id]['ship_name']['en'],
                    'ja':main_data[ship_id]['ship_name']['ja'],
                    'ru':main_data[ship_id]['ship_name']['ru']
                }
                return result
            if language in ['cn','ja','ru','en']:
                if language == 'en':
                    lang = 'en_l'
                else:
                    lang = language
                if ship_name_format == self.__name_format(ship_data['ship_name'][lang]):
                    result[ship_id] = {
                        'tier':main_data[ship_id]['tier'],
                        'type':main_data[ship_id]['type'],
                        'cn':main_data[ship_id]['ship_name']['cn'],
                        'en':main_data[ship_id]['ship_name']['en'],
                        'ja':main_data[ship_id]['ship_name']['ja'],
                        'ru':main_data[ship_id]['ship_name']['ru']
                    }
                    return result
        for ship_id, ship_data in main_data.items():
            if ship_name_format in self.__name_format(ship_data['ship_name']['en']):
                if old == False and ship_id in GameData.OLD_SHIP_ID_LIST:
                    continue
                result[ship_id] = {
                    'tier':main_data[ship_id]['tier'],
                    'type':main_data[ship_id]['type'],
                    'cn':main_data[ship_id]['ship_name']['cn'],
                    'en':main_data[ship_id]['ship_name']['en'],
                    'ja':main_data[ship_id]['ship_name']['ja'],
                    'ru':main_data[ship_id]['ship_name']['ru']
                }
            if language in ['cn','ja','ru','en']:
                if language == 'en':
                    lang = 'en_l'
                else:
                    lang = language
                if ship_name_format in self.__name_format(ship_data['ship_name'][lang]):
                    if old == False and ship_id in GameData.OLD_SHIP_ID_LIST:
                        continue
                    result[ship_id] = {
                        'tier':main_data[ship_id]['tier'],
                        'type':main_data[ship_id]['type'],
                        'cn':main_data[ship_id]['ship_name']['cn'],
                        'en':main_data[ship_id]['ship_name']['en'],
                        'ja':main_data[ship_id]['ship_name']['ja'],
                        'ru':main_data[ship_id]['ship_name']['ru']
                    }
        return result