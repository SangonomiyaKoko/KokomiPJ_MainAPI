def numbers_to_binary(numbers: list[int]) -> bytes:
    """
    将数字列表转换为二进制数据流，每个数字占用5字节。
    :param numbers: 数字列表，列表长度不超过50，每个数字为十位以内的正整数。
    :return: 拼接后的二进制数据。
    """
    binary_data = bytearray()
    for number in numbers:
        if not (0 <= number <= 9_999_999_999):
            raise ValueError(f"数字 {number} 超出了十位范围！")
        # 将数字转为5字节二进制数据（固定大小）
        binary_data.extend(number.to_bytes(5, byteorder='big'))
    return bytes(binary_data)


def binary_to_numbers(binary_data: bytes) -> list[int]:
    """
    将二进制数据流转换为数字列表。
    : param binary_data: 输入的二进制数据。
    : return: 解码后的数字列表。
    """
    if len(binary_data) % 5 != 0:
        raise ValueError("二进制数据长度不合法，无法解析为固定的5字节块！")
    
    numbers = []
    for i in range(0, len(binary_data), 5):
        # 从二进制数据中每次取出5字节，转换为数字
        chunk = binary_data[i:i + 5]
        number = int.from_bytes(chunk, byteorder='big')
        numbers.append(number)
    return numbers


# 测试代码
if __name__ == "__main__":
    # 示例列表
    numbers_list = [123, 456789, 9876543210, 42, 9999999999]
    
    # 转换为二进制
    binary_result = numbers_to_binary(numbers_list)
    print(f"二进制数据：{binary_result.hex()}")

    # 从二进制恢复为数字列表
    restored_numbers = binary_to_numbers(binary_result)
    print(f"还原后的数字列表：{restored_numbers}")
