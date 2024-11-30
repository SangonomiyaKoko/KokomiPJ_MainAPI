class BinaryParserUtils:
    @classmethod
    def from_user_binary_data_to_dict(self, binary_data: bytes):
        '''从user的二进制数据中解析为dict数据'''
        # 存储转换后的字典
        result = {}
        if binary_data is None or binary_data == b'\x00\x00\x00\x00\x00\x00\x00':
            return result
        # 每个数据项的字节数是 7 字节
        # 根据字节流的长度，计算出有多少个数据项
        num_items = len(binary_data) // 7
        for i in range(num_items):
            # 提取 7 字节的数据
            item_data = binary_data[i * 7:(i + 1) * 7]
            # 将字节数据转换为 key 和 value
            key, value = self.__from_user_binary_data(item_data)
            # 将 key 和 value 存入字典
            result[key] = value
        return result
    
    def from_clan_binary_data_to_list(binary_data: bytes) -> list[int]:
        if len(binary_data) % 5 != 0:
            raise ValueError("Byte data must be exactly 7 bytes.")
        result = []
        if binary_data is None or binary_data == b'\x00\x00\x00\x00\x00':
            return result
        for i in range(0, len(binary_data), 5):
            # 从二进制数据中每次取出5字节，转换为数字
            chunk = binary_data[i:i + 5]
            number = int.from_bytes(chunk, byteorder='big')
            result.append(number)
        return result

    def __from_user_binary_data(byte_data):
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

class BinaryGeneratorUtils:
    @classmethod
    def to_user_binary_data_from_dict(self, data_dict: dict) -> bytes:
        '''从user的dict数据生成为存储的二进制数据'''
        if data_dict == {}:
            return b'\x00\x00\x00\x00\x00\x00\x00'
        # 存储合并后的二进制数据
        result = bytearray()
        for key, value in data_dict.items():
            if type(key) == str:
                key = int(key)
            # 获取每个键值对的二进制数据并合并
            result.extend(self.__to_user_binary_data(key, value))
        # 返回合并后的二进制数据
        return bytes(result)
    
    def to_clan_binary_data_from_list(data_list: list[int]) -> bytes:
        if data_list == []:
            return b'\x00\x00\x00\x00\x00'
        binary_data = bytearray()
        for number in data_list:
            if not (0 <= number <= 2**40):
                raise ValueError("key must be a non-negative integer less than 2^40.")
            # 将数字转为5字节二进制数据（固定大小）
            binary_data.extend(number.to_bytes(5, byteorder='big'))
        return bytes(binary_data)
    
    def __to_user_binary_data(key, value) -> bytes:
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
    