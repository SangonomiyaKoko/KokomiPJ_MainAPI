from typing import List, Set

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
        elif 'win_rate' not in ship_data[str(ship_id)][region]:
            return None
        else:
            result[ship_id] = [
                ship_data[str(ship_id)][region]['win_rate'],
                ship_data[str(ship_id)][region]['avg_damage'],
                ship_data[str(ship_id)][region]['avg_frags'],
                ship_data[str(ship_id)][region]['avg_exp']
            ]
        return result

    def get_ship_data_batch(region_id: int, ship_ids: List[int] | Set[int]) -> dict:
        "通过ship_id(int)列表批量获取船只的服务器数据"
        result = {}
        region = UtilityFunctions.get_region(region_id)
        ship_data = JsonData.read_json_data('ship_data')['ship_data']
        for ship_id in ship_ids:
            if (
                str(ship_id) in ship_data and
                ship_data[str(ship_id)][region]['battles_count'] >= 1000
            ):
                result[ship_id] = [
                    ship_data[str(ship_id)][region]['win_rate'],
                    ship_data[str(ship_id)][region]['avg_damage'],
                    ship_data[str(ship_id)][region]['avg_frags']
                ]
        return result
        
