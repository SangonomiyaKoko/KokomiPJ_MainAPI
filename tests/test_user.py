test_user_list = [
    [2023619512, 1],    # 亚服，正常账号
    [2023619510, 1],    # 亚服，账号无数据
    [2023619518, 1],    # 亚服，账号删除(404)
    [213712262,  4],    # 俄服，正常账号

]
import sys

data_dict = str([2023619512,2023619513,2023619514])
print(len(data_dict))

print("Size in bytes:", sys.getsizeof(data_dict))