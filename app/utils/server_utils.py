from app.json import JsonData
from app.utils import UtilityFunctions

class ShipData:
    def get_ship_data_by_sid_and_rid(region_id: int, ship_id: int):
        "通过ship_id(int)获取船只的服务器数据"
        result = {}
        region = UtilityFunctions.get_region(region_id)
        ship_data = JsonData.read_json_data('ship_data')['ship_data']
        if str(ship_id) not in ship_data:
            return result
        else:
            result[ship_id] = [
                ship_data[str(ship_id)][region]['win_rate'],
                ship_data[str(ship_id)][region]['avg_damage'],
                ship_data[str(ship_id)][region]['avg_frags']
            ]
        return result

    def get_ship_data_by_sids_and_rid(region_id: int, ship_id_list: list):
        "通过ship_id(int)列表批量获取船只的服务器数据"
        result = {}
        region = UtilityFunctions.get_region(region_id)
        ship_data = JsonData.read_json_data('ship_data')['ship_data']
        for ship_id in ship_id_list:
            if str(ship_id) not in ship_data:
                continue
            else:
                result[ship_id] = [
                    ship_data[str(ship_id)][region]['win_rate'],
                    ship_data[str(ship_id)][region]['avg_damage'],
                    ship_data[str(ship_id)][region]['avg_frags']
                ]
        return result
        
