import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# 读取数据
data1 = pd.read_csv(r'F:\Kokomi_PJ_MainAPI\temp\leader\4273977328.csv', index_col=False)
data2 = pd.read_csv(r'F:\Kokomi_PJ_MainAPI\temp\leader\3655317296.csv', index_col=False)
data3 = pd.read_csv(r'F:\Kokomi_PJ_MainAPI\temp\leader\3760175056.csv', index_col=False)
data4 = pd.read_csv(r'F:\Kokomi_PJ_MainAPI\temp\leader\4179605488.csv', index_col=False)
data5 = pd.read_csv(r'F:\Kokomi_PJ_MainAPI\temp\leader\3550459600.csv', index_col=False)
data6 = pd.read_csv(r'F:\Kokomi_PJ_MainAPI\temp\leader\4179605200.csv', index_col=False)
data7 = pd.read_csv(r'F:\Kokomi_PJ_MainAPI\temp\leader\4179604944.csv', index_col=False)
data8 = pd.read_csv(r'F:\Kokomi_PJ_MainAPI\temp\leader\4179605296.csv', index_col=False)
data9 = pd.read_csv(r'F:\Kokomi_PJ_MainAPI\temp\leader\4074747856.csv', index_col=False)
data10 = pd.read_csv(r'F:\Kokomi_PJ_MainAPI\temp\leader\3760175088.csv', index_col=False)

# 数据清洗，移除 '%' 符号并转换为 float 类型
# data1['win_rate'] = data1['win_rate'].replace('%', '', regex=True).astype(float)
# data2['win_rate'] = data2['win_rate'].replace('%', '', regex=True).astype(float)
# data3['win_rate'] = data3['win_rate'].replace('%', '', regex=True).astype(float)
# data4['win_rate'] = data4['win_rate'].replace('%', '', regex=True).astype(float)
# data5['win_rate'] = data5['win_rate'].replace('%', '', regex=True).astype(float)
# data6['win_rate'] = data6['win_rate'].replace('%', '', regex=True).astype(float)

# KDE plots for each data file
sns.kdeplot(data=data1['avg_dmg'], label="Essex", fill=True)
sns.kdeplot(data=data2['avg_dmg'], label="M. Immelmann", fill=True)
sns.kdeplot(data=data3['avg_dmg'], label="Malta", fill=True)
# sns.kdeplot(data=data4['avg_dmg'], label="Midway", fill=True)
sns.kdeplot(data=data5['avg_dmg'], label="Shinano", fill=True)
# sns.kdeplot(data=data6['avg_dmg'], label="Hakuryū", fill=True)
# sns.kdeplot(data=data7['avg_dmg'], label="Nakhimov", fill=True)
# sns.kdeplot(data=data8['avg_dmg'], label="M. Richthofen", fill=True)
# sns.kdeplot(data=data9['avg_dmg'], label="Audacious", fill=True)
sns.kdeplot(data=data10['avg_dmg'], label="F. D. Roosevelt", fill=True)

# 设置标题和轴标签
plt.title("Distribution of Damage")  # 图表标题
plt.xlabel("Damage")  # x轴标题
plt.ylabel("Density")  # y轴标题

# 显示图例
plt.legend(title='Files', loc='upper right')

# 显示图表
plt.show()
