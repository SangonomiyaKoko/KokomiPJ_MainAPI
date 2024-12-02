from app.utils import ShipName,ShipData,Rating_Algorithm, ColorUtils
from app.response import JSONResponse, ResponseDict

def process_signature_data(
    account_id: int,
    region_id: int,
    responses: list,
    language: str,
    algo_type: str = None
) -> ResponseDict:
    # 返回数据的格式
    result = {
        'overall': {}
    }
    processed_data = {}
    formatted_data = {}
    ship_ids = set()
    response = responses[0]
    battle_type = 'pvp'
    for ship_id, ship_data in response['data'][str(account_id)]['statistics'].items():
        if (
            ship_data[battle_type] == {} or 
            ship_data[battle_type]['battles_count'] == 0
        ):
            continue
        ship_id = int(ship_id)
        ship_ids.add(ship_id)
        processed_data[ship_id] = {}
        processed_data[ship_id][battle_type] = {
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
                processed_data[ship_id][battle_type][index] = ship_data[battle_type][index]
    ship_info_dict = ShipName.get_ship_info_batch(region_id,language,ship_ids)
    ship_data_dict = ShipData.get_ship_data_batch(region_id,ship_ids)
    for ship_id in ship_ids:
        ship_data = processed_data.get(ship_id)[battle_type]
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
            processed_data[ship_id][battle_type]['value_battles_count'] += rating_data[0]
            processed_data[ship_id][battle_type]['personal_rating'] += rating_data[1]
            processed_data[ship_id][battle_type]['n_damage_dealt'] += rating_data[2]
            processed_data[ship_id][battle_type]['n_frags'] += rating_data[3]
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
        ship_data = processed_data.get(ship_id)[battle_type]
        ship_info = ship_info_dict.get(ship_id,None)
        if ship_info is None:
            continue
        for index in ['battles_count','wins','damage_dealt','frags']:
            overall_data[index] += ship_data[index]
        if ship_data['value_battles_count'] > 0:
            for index in ['value_battles_count','personal_rating','n_damage_dealt','n_frags']:
                overall_data[index] += ship_data[index]
    formatted_data = {
        'battles_count': 0,
        'win_rate': 0.0,
        'avg_damage': 0,
        'avg_frags': 0.0,
        'personal_rating': 0,
        'win_rate_color': '#808080',
        'avg_damage_color': '#808080',
        'avg_frags_color': '#808080',
        'rating_color': '#808080'
    }
    if overall_data['battles_count'] == 0:
        return JSONResponse.API_1006_UserDataisNone
    else:
        formatted_data['battles_count'] = overall_data['battles_count']
        formatted_data['win_rate'] = round(overall_data['wins']/overall_data['battles_count']*100,2)
        formatted_data['avg_damage'] = int(overall_data['damage_dealt']/overall_data['battles_count'])
        formatted_data['avg_frags'] = round(overall_data['frags']/overall_data['battles_count'],2)
        if not algo_type:
            formatted_data['personal_rating'] = -2
            formatted_data['win_rate_color'] = ColorUtils.get_rating_color(0,-1)
            formatted_data['avg_damage_color'] = ColorUtils.get_rating_color(1,-2)
            formatted_data['avg_frags_color'] = ColorUtils.get_rating_color(2,-2)
            formatted_data['rating_color'] = ColorUtils.get_rating_color(3,-2)
        elif overall_data['value_battles_count'] != 0:
            formatted_data['personal_rating'] = int(overall_data['personal_rating']/overall_data['value_battles_count'])
            formatted_data['win_rate_color'] = ColorUtils.get_rating_color(0,formatted_data['win_rate'])
            formatted_data['avg_damage_color'] = ColorUtils.get_rating_color(1,overall_data['n_damage_dealt']/overall_data['value_battles_count'])
            formatted_data['avg_frags_color'] = ColorUtils.get_rating_color(2,overall_data['n_frags']/overall_data['value_battles_count'])
            formatted_data['rating_color'] = ColorUtils.get_rating_color(3,overall_data['personal_rating']/overall_data['value_battles_count'])
        else:
            formatted_data['personal_rating'] = -1
            formatted_data['win_rate_color'] = ColorUtils.get_rating_color(0,-1)
            formatted_data['avg_damage_color'] = ColorUtils.get_rating_color(1,-1)
            formatted_data['avg_frags_color'] = ColorUtils.get_rating_color(2,-1)
            formatted_data['rating_color'] = ColorUtils.get_rating_color(3,-1)
        formatted_data['win_rate_color'] = "#{:02X}{:02X}{:02X}".format(*formatted_data['win_rate_color'])
        formatted_data['avg_damage_color'] = "#{:02X}{:02X}{:02X}".format(*formatted_data['avg_damage_color'])
        formatted_data['avg_frags_color'] = "#{:02X}{:02X}{:02X}".format(*formatted_data['avg_frags_color'])
        formatted_data['rating_color'] = "#{:02X}{:02X}{:02X}".format(*formatted_data['rating_color'])
    formatted_data['battles_count'] = '{:,}'.format(formatted_data['battles_count']).replace(',', ' ')
    formatted_data['win_rate'] = '{:.2f}%'.format(formatted_data['win_rate'])
    formatted_data['avg_damage'] = '{:,}'.format(formatted_data['avg_damage']).replace(',', ' ')
    formatted_data['avg_frags'] = '{:.2f}'.format(formatted_data['avg_frags'])
    formatted_data['personal_rating'] = '{:,}'.format(formatted_data['personal_rating']).replace(',', ' ')

    result['overall'] = formatted_data
    return JSONResponse.get_success_response(result)

def process_lifetime_data(
    account_id: int,
    region_id: int,
    responses: list,
    language: str,
    algo_type: str = None
) -> ResponseDict:
    result = {
        'overall': {},
        'lifetime': {}
    }
    processed_data = {}
    formatted_data = {}
    ship_ids = set()
    response = responses[0]
    battle_type = 'pvp'
    for ship_id, ship_data in response['data'][str(account_id)]['statistics'].items():
        if (
            ship_data[battle_type] == {} or 
            ship_data[battle_type]['battles_count'] == 0
        ):
            continue
        ship_id = int(ship_id)
        ship_ids.add(ship_id)
        processed_data[ship_id] = {}
        processed_data[ship_id][battle_type] = {
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
                processed_data[ship_id][battle_type][index] = ship_data[battle_type][index]
    lifetime_data = {
        'lifetime': None
    }
    response = responses[1]
    if (
        response['status'] == 'ok' and 
        response['data'] != None and 
        response['data'][str(account_id)] != None
    ):
        lifetime_data['lifetime'] = response['data'][str(account_id)]['private']['battle_life_time']
    else:
        return JSONResponse.API_1020_AC2isInvalid
    ship_info_dict = ShipName.get_ship_info_batch(region_id,language,ship_ids)
    ship_data_dict = ShipData.get_ship_data_batch(region_id,ship_ids)
    for ship_id in ship_ids:
        ship_data = processed_data.get(ship_id)[battle_type]
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
            processed_data[ship_id][battle_type]['value_battles_count'] += rating_data[0]
            processed_data[ship_id][battle_type]['personal_rating'] += rating_data[1]
            processed_data[ship_id][battle_type]['n_damage_dealt'] += rating_data[2]
            processed_data[ship_id][battle_type]['n_frags'] += rating_data[3]
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
        ship_data = processed_data.get(ship_id)[battle_type]
        ship_info = ship_info_dict.get(ship_id,None)
        if ship_info is None:
            continue
        for index in ['battles_count','wins','damage_dealt','frags']:
            overall_data[index] += ship_data[index]
        if ship_data['value_battles_count'] > 0:
            for index in ['value_battles_count','personal_rating','n_damage_dealt','n_frags']:
                overall_data[index] += ship_data[index]
    formatted_data = {
        'battles_count': 0,
        'win_rate': 0.0,
        'avg_damage': 0,
        'avg_frags': 0.0,
        'personal_rating': 0,
        'win_rate_color': '#808080',
        'avg_damage_color': '#808080',
        'avg_frags_color': '#808080',
        'rating_color': '#808080'
    }
    if overall_data['battles_count'] == 0:
        return JSONResponse.API_1006_UserDataisNone
    else:
        formatted_data['battles_count'] = overall_data['battles_count']
        formatted_data['win_rate'] = round(overall_data['wins']/overall_data['battles_count']*100,2)
        formatted_data['avg_damage'] = int(overall_data['damage_dealt']/overall_data['battles_count'])
        formatted_data['avg_frags'] = round(overall_data['frags']/overall_data['battles_count'],2)
        if not algo_type:
            formatted_data['personal_rating'] = -2
            formatted_data['win_rate_color'] = ColorUtils.get_rating_color(0,-1)
            formatted_data['avg_damage_color'] = ColorUtils.get_rating_color(1,-2)
            formatted_data['avg_frags_color'] = ColorUtils.get_rating_color(2,-2)
            formatted_data['rating_color'] = ColorUtils.get_rating_color(3,-2)
        elif overall_data['value_battles_count'] != 0:
            formatted_data['personal_rating'] = int(overall_data['personal_rating']/overall_data['value_battles_count'])
            formatted_data['win_rate_color'] = ColorUtils.get_rating_color(0,formatted_data['win_rate'])
            formatted_data['avg_damage_color'] = ColorUtils.get_rating_color(1,overall_data['n_damage_dealt']/overall_data['value_battles_count'])
            formatted_data['avg_frags_color'] = ColorUtils.get_rating_color(2,overall_data['n_frags']/overall_data['value_battles_count'])
            formatted_data['rating_color'] = ColorUtils.get_rating_color(3,overall_data['personal_rating']/overall_data['value_battles_count'])
        else:
            formatted_data['personal_rating'] = -1
            formatted_data['win_rate_color'] = ColorUtils.get_rating_color(0,-1)
            formatted_data['avg_damage_color'] = ColorUtils.get_rating_color(1,-1)
            formatted_data['avg_frags_color'] = ColorUtils.get_rating_color(2,-1)
            formatted_data['rating_color'] = ColorUtils.get_rating_color(3,-1)
        formatted_data['win_rate_color'] = "#{:02X}{:02X}{:02X}".format(*formatted_data['win_rate_color'])
        formatted_data['avg_damage_color'] = "#{:02X}{:02X}{:02X}".format(*formatted_data['avg_damage_color'])
        formatted_data['avg_frags_color'] = "#{:02X}{:02X}{:02X}".format(*formatted_data['avg_frags_color'])
        formatted_data['rating_color'] = "#{:02X}{:02X}{:02X}".format(*formatted_data['rating_color'])
    formatted_data['battles_count'] = '{:,}'.format(formatted_data['battles_count']).replace(',', ' ')
    formatted_data['win_rate'] = '{:.2f}%'.format(formatted_data['win_rate'])
    formatted_data['avg_damage'] = '{:,}'.format(formatted_data['avg_damage']).replace(',', ' ')
    formatted_data['avg_frags'] = '{:.2f}'.format(formatted_data['avg_frags'])
    formatted_data['personal_rating'] = '{:,}'.format(formatted_data['personal_rating']).replace(',', ' ')
    translations = {
        "en": ["Hour", "Minute", "Second"],
        "cn": ["小时", "分钟", "秒"],
        "ja": ["時間", "分", "秒"]
    }
    lifetime_seconds = lifetime_data['lifetime']
    words = translations.get(language, translations["en"])
    hours = lifetime_seconds // 3600
    minutes = (lifetime_seconds % 3600) // 60
    seconds = lifetime_seconds % 60
    lifetime_data['lifetime'] = f"{hours} {words[0]}  {minutes} {words[1]}  {seconds} {words[2]}"

    result['lifetime'] = lifetime_data
    result['overall'] = formatted_data
    return JSONResponse.get_success_response(result)