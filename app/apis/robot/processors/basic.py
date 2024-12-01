from app.utils import ShipName,ShipData,Rating_Algorithm, ColorUtils
from app.response import JSONResponse

def process_signature_data(
    account_id: int,
    region_id: int,
    responses: list,
    language: str,
    algo_type: str
):
    # 返回数据的格式
    result = {
        'overall': {}
    }
    temp_data = {}
    ship_ids = set()
    response = responses[0]
    battle_type = 'pvp'
    for ship_id, ship_data in response['data'][account_id]['statistics'].items():
        if (
            ship_data[battle_type] == {} or 
            ship_data[battle_type]['battles_count'] == 0
        ):
            continue
        ship_id = int(ship_id)
        ship_ids.add(ship_id)
        temp_data[ship_id] = {}
        temp_data[ship_id][battle_type] = {
            'battles_count': 0,
            'wins': 0,
            'damage_dealt': 0,
            'frags': 0,
            'value_battles_count': 0,
            'personal_rating': 0,
            'n_damage_dealt': 0,
            'n_frags': 0
        }
        if ship_data[battle_type] != {}:
            for index in ['battles_count','wins','damage_dealt','frags']:
                temp_data[ship_id][battle_type][index] = ship_data[battle_type][index]
    ship_info_dict = ShipName.get_ship_info_batch(region_id,language,ship_ids)
    ship_data_dict = ShipData.get_ship_data_batch(region_id,ship_ids)
    for ship_id in ship_ids:
        ship_data = temp_data.get(ship_id)
        account_data = [
            ship_data['battles_count'],
            ship_data['wins'],
            ship_data['damage_dealt'],
            ship_data['frags']
        ]
        if ship_data_dict.get(ship_id):
            server_data = ship_data_dict.get(ship_id)
        else:
            server_data = None
        rating_data = Rating_Algorithm.get_rating_by_data(
            algo_type,
            battle_type,
            account_data,
            server_data
        )
        if rating_data[0] > 0:
            temp_data[ship_id][battle_type]['value_battles_count'] += rating_data[0]
            temp_data[ship_id][battle_type]['personal_rating'] += rating_data[1]
            temp_data[ship_id][battle_type]['n_damage_dealt'] += rating_data[2]
            temp_data[ship_id][battle_type]['n_frags'] += rating_data[3]
    overall_data = {
        'battles_count': 0,
        'wins': 0,
        'damage_dealt': 0,
        'frags': 0,
        'value_battles_count': 0,
        'personal_rating': 0,
        'n_damage_dealt': 0,
        'n_frags': 0
    }
    for ship_id in ship_ids:
        ship_data = temp_data.get(ship_id)
        ship_info = ship_info_dict.get(ship_id,None)
        if ship_info is None:
            continue
        for index in ['battles_count','wins','damage_dealt','frags']:
            overall_data[index] += ship_data[battle_type][index]
        if ship_data[battle_type]['value_battles_count'] > 0:
            for index in ['value_battles_count','personal_rating','n_damage_dealt','n_frags']:
                overall_data[index] += ship_data[battle_type][index]
    pro_data = {
        'battles_count': 0,
        'win_rate': 0.0,
        'avg_damage': 0,
        'avg_frags': 0.0,
        'personal_rating': 0,
        'win_rate_color': '#808080',
        'avg_damage_color': '#808080',
        'avg_frags_color': '#808080'
    }
    if overall_data['battles_count'] == 0:
        return JSONResponse.API_1006_UserDataisNone
    else:
        pro_data['battles_count'] = overall_data['battles_count']
        pro_data['win_rate'] = round(overall_data['wins']/overall_data['battles_count']*100,2)
        pro_data['avg_damage'] = int(overall_data['damage_dealt']/overall_data['battles_count'])
        pro_data['avg_frags'] = round(overall_data['frags']/overall_data['battles_count'],2)
        pro_data['win_rate_color'] = ColorUtils.get_rating_color(0,pro_data['win_rate'])
        if not algo_type:
            pro_data['avg_damage_color'] = ColorUtils.get_rating_color(1,-2)
        elif overall_data['value_battles_count'] != 0:
            pro_data['avg_damage_color'] = ColorUtils.get_rating_color(1,overall_data['n_damage_dealt']/overall_data['value_battles_count'])
        else:
            pro_data['avg_damage_color'] = ColorUtils.get_rating_color(1,-1)
        if not algo_type:
            pro_data['avg_frags_color'] = ColorUtils.get_rating_color(2,-2)
        elif overall_data['value_battles_count'] != 0:
            pro_data['avg_frags_color'] = ColorUtils.get_rating_color(2,overall_data['n_frags']/overall_data['value_battles_count'])
        else:
            pro_data['avg_frags_color'] = ColorUtils.get_rating_color(2,-1)
        pro_data['win_rate_color'] = "#{:02X}{:02X}{:02X}".format(*pro_data['win_rate_color'])
        pro_data['avg_damage_color'] = "#{:02X}{:02X}{:02X}".format(*pro_data['avg_damage_color'])
        pro_data['avg_frags_color'] = "#{:02X}{:02X}{:02X}".format(*pro_data['avg_frags_color'])
    pro_data['battles_count'] = '{:,}'.format(pro_data['battles_count']).replace(',', ' ')
    pro_data['win_rate'] = '{:.2f}%'.format(pro_data['win_rate'])
    pro_data['avg_damage'] = '{:,}'.format(pro_data['avg_damage']).replace(',', ' ')
    pro_data['avg_frags'] = '{:.2f}'.format(pro_data['avg_frags'])
    result['overall'] = pro_data
    return result