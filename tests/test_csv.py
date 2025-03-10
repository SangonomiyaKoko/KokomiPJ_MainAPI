import time
import pandas as pd
from tabulate import tabulate

# 记录开始时间
st = time.time()

# 假设 CSV 文件名为 'data.csv'
file_path = r'F:\Kokomi_PJ_MainAPI\temp\leader\3759585264.csv'
ship_name = 'X SS Gato'
# 需要展示的数据字段
fields_to_display = ['region', 'region_id', 'user_name', 'clan_tag', 'battles_count', 'battle_type', 'rating', 'rating_info', 'win_rate', 'avg_dmg', 'avg_frags', 'max_dmg', 'max_exp']

# 读取 CSV 文件并选择需要的字段
df = pd.read_csv(file_path, usecols=fields_to_display)
df = df[df['region_id'] == 4].reset_index(drop=True)
# 对数据进行排序（假设按 'rating' 排序，降序）
df_sorted = df.sort_values(by='rating', ascending=False).head(50)

# 创建新的列 `display_name`，将 `user_name` 和 `clan_tag` 合并
df_sorted['display_name'] = df_sorted.apply(
    lambda row: f"[{row['clan_tag']}] {row['user_name']}" if pd.notna(row['clan_tag']) else row['user_name'],
    axis=1
)

df_sorted['id'] = range(1, len(df_sorted) + 1)

# 创建列名映射字典（将英文列名映射为中文列名）
column_mapping = {
    'id': 'No',
    'region': '服务器',
    'display_name': '玩家名称',
    'battles_count': '对战场次',
    'battle_type': '单野占比',
    'rating': '评分',
    'rating_info': '服务器修正',
    'win_rate': '胜率',
    'avg_dmg': '场均伤害',
    'avg_frags': '场均击杀',
    'max_dmg': '最大伤害',
    'max_exp': '最大经验'
}

# 将列名替换为中文
df_sorted = df_sorted.rename(columns=column_mapping)
# 使用 tabulate 格式化输出表格
table = tabulate(df_sorted[['No', '服务器', '玩家名称', '对战场次', '单野占比', '评分', '服务器修正', '胜率', '场均伤害', '场均击杀', '最大伤害', '最大经验']], 
                 headers='keys', 
                 tablefmt='fancy_grid', 
                 showindex=False)

# 打印结果
print('\n')
print(f"【全服排行榜】 {ship_name}                                                                                                                          By KokomiBot V5")
print(table)

# 记录结束时间并输出执行时间
et = time.time()
print(f'Cost time: {round(et - st, 2)}s')
