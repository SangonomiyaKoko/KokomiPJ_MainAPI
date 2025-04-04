import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

file_path = r'F:\Kokomi_PJ_MainAPI\temp\db\1\2023619512.db'
conn = sqlite3.connect(file_path)
cursor = conn.cursor()
table_create_query = 'select date, leveling_points from user_info'
cursor.execute(table_create_query)
data = cursor.fetchall()
cursor.close()
conn.close()

# 解析数据
date_list = [datetime.strptime(str(d[0]), "%Y%m%d") for d in data]
values = [d[1] for d in data]

# 计算每日贡献（差值）
contributions = [0]  # 第一条数据的贡献值为 0
for i in range(1, len(values)):
    contributions.append(values[i] - values[i - 1])

# 创建 DataFrame
df = pd.DataFrame({"date": date_list, "contribution": contributions})
# 获取当前日期
today = datetime.today()

# 计算最近一年的起始日期
one_year_ago = today - timedelta(days=365)

# 过滤掉一年以前的数据
df = df[df["date"] >= one_year_ago]
# 补充缺失日期
start_date = df["date"].min()
end_date = df["date"].max()
full_date_range = pd.date_range(start=start_date, end=end_date)
df = df.set_index("date").reindex(full_date_range, fill_value=0).reset_index()
df.rename(columns={"index": "date"}, inplace=True)

# 计算周和星期
df["week"] = df["date"].dt.strftime("%Y-%U")  # 按年-周编号
df["day_of_week"] = df["date"].dt.weekday  # 0=Monday, 6=Sunday

# 正确的 pivot 语法
heatmap_data = df.pivot(index="day_of_week", columns="week", values="contribution")

# 画图
fig, ax = plt.subplots(figsize=(12, 4))
sns.heatmap(
    heatmap_data, cmap="Greens", linewidths=0.5, linecolor="white", cbar=False, ax=ax
)
ax.set_xlabel("Week")
ax.set_ylabel("Day of Week")
ax.set_title("GitHub Contribution Heatmap")

plt.show()