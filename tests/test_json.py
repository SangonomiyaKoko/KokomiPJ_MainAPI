import json
import os

file_path = os.path.join(r'F:\Kokomi_PJ_Api\app\json\ship_name_lesta.json')
temp = open(file_path, "r", encoding="utf-8")
data = json.load(temp)
temp.close()

result = {
    0:0, 2:0, 4:0, 6:0, 8:0 
}

for ship_id, _ in data.items():
    result[int(ship_id)%10] += 1

print(result)