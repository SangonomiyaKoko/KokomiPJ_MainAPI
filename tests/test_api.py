import requests
import time

url = 'https://vortex.worldofwarships.asia/api/accounts/2023619512/ships/'
result = requests.get(url).json()
data = {}
for ship_id, ship_data in result['data']["2023619512"]["statistics"].items():
    data[int(ship_id)] = ship_data['pvp'].get('battles_count',0)
print(len(data.keys()))
t1 = time.time()
str_data = str(data)
t2 = time.time()
print(t2-t1)
print("Size in bytes:", len(str_data))
t3 = time.time()
eval(str_data)
t4 = time.time()
print(t4-t3)