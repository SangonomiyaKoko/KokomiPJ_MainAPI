import json
import os
import time

def main():
    file_path = os.path.join(r'F:\Kokomi_PJ_Api\temp\tempArenaInfo_wg_pvp.json')
    temp = open(file_path, "r", encoding="utf-8")
    data = json.load(temp)
    temp.close()
    battle_time = data['dateTime']
    match_id = None
    result = {
        'version': data['clientVersionFromExe'].replace(',','.'),
        'match': {
            'type': data['matchGroup'],
            'time': None,
            'name': data['name']
        },
        'map': {
            'id': data['mapId'],
            'name': data['mapDisplayName']
        },
        'players': None
    }
    player_list = {
        1: [],
        2: []
    }
    name_list = []
    for player in data['vehicles']:
        if player['relation'] == 2:
            relation = 2
        else:
            relation = 1
        name = player['name']
        ship_id = player['shipId']
        name_list.append(name)
        player_list[relation].append({'user':name,'ship':ship_id})
    name_list.sort()
    print(name_list)

if __name__ == '__main__':
    main()
