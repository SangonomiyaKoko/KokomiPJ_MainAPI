import time
import sys


def to_binary_data(key, value):
    # 确保 key 和 value 都在允许的范围内
    if not (0 <= key < 2**34):
        raise ValueError("key must be a non-negative integer less than 2^34.")
    if not (0 <= value < 2**22):
        raise ValueError("value must be a non-negative integer less than 2^22.")
    
    # 将 key 和 value 转换为二进制字符串，确保它们有足够的位数
    key_bin = f'{key:034b}'  # 34 位二进制，确保 key 为 34 位
    value_bin = f'{value:022b}'  # 22 位二进制，确保 value 为 22 位
    
    # 将二进制字符串拼接成一个 56 位的字符串
    full_bin = key_bin + value_bin
    
    # 将 56 位二进制字符串按 8 位分割，并转换为字节
    byte_data = bytearray()
    for i in range(0, len(full_bin), 8):
        byte_data.append(int(full_bin[i:i+8], 2))  # 每 8 位转换为一个字节
    
    # 返回字节数据，应该是 7 字节大小
    return bytes(byte_data)

def from_binary_data(byte_data):
    # 确保字节数据的长度是7字节
    if len(byte_data) != 7:
        raise ValueError("Byte data must be exactly 7 bytes.")
    
    # 将字节数据转换为二进制字符串
    full_bin = ''.join(f'{byte:08b}' for byte in byte_data)
    
    # 提取前 34 位作为 key 和后 22 位作为 value
    key_bin = full_bin[:34]
    value_bin = full_bin[34:]
    
    # 将二进制字符串转换为整数
    key = int(key_bin, 2)
    value = int(value_bin, 2)
    
    return key, value

def to_binary_data_dict(data_dict):
    # 存储合并后的二进制数据
    result = bytearray()
    
    for key, value in data_dict.items():
        # 获取每个键值对的二进制数据并合并
        result.extend(to_binary_data(key, value))
    
    # 返回合并后的二进制数据
    return bytes(result)

def from_binary_data_dict(binary_data):
    # 存储转换后的字典
    result = {}
    
    # 每个数据项的字节数是 7 字节
    # 根据字节流的长度，计算出有多少个数据项
    num_items = len(binary_data) // 7
    
    for i in range(num_items):
        # 提取 7 字节的数据
        item_data = binary_data[i * 7:(i + 1) * 7]
        
        # 将字节数据转换为 key 和 value
        key, value = from_binary_data(item_data)
        
        # 将 key 和 value 存入字典
        result[key] = value
    
    return result

data_dict = {0000000000:0}

print("Size in bytes:", sys.getsizeof(data_dict))

# 获取合并后的二进制数据
t1 = time.time()
merged_binary_data = to_binary_data_dict(data_dict)
t2 = time.time()
print(t2-t1)
print(merged_binary_data)
# 打印合并后的二进制数据
print("Size in bytes:", len(merged_binary_data))

# 从字节数据转换回字典
t3 = time.time()
converted_dict = from_binary_data_dict(merged_binary_data)
t4 = time.time()
print(t4-t3)
print(converted_dict)
# 打印转换回来的字典
print("Size in bytes:", sys.getsizeof(converted_dict))
