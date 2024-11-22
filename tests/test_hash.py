import hashlib

def sort_and_hash(data_dict: dict[int, int]) -> tuple[dict[int, int], str]:
    """
    按照字典中的键（id）从小到大排序，并计算排序后的哈希值。
    :param data_dict: 输入的字典，格式为 {id: data}，其中 id 和 data 均为整数。
    :return: (排序后的字典, 排序后字典的哈希值)
    """
    # 按键（id）排序
    sorted_dict = dict(sorted(data_dict.items()))
    
    # 转为字符串形式以计算哈希值
    sorted_str = str(sorted_dict)
    
    # 计算哈希值（SHA256）
    hash_value = hashlib.sha256(sorted_str.encode('utf-8')).hexdigest()
    
    return sorted_dict, hash_value


# 测试代码
if __name__ == "__main__":
    test_dict = {3: 300, 1: 100, 2: 200}
    
    sorted_result, hash_result = sort_and_hash(test_dict)
    print(f"排序后的字典：{sorted_result}")
    print(f"排序后字典的哈希值：{hash_result}")
