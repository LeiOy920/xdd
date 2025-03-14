import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 读取Excel文件
file_path = '1905type30.xlsx'
df = pd.read_excel(file_path, sheet_name='Sheet1')

# 设置字体为黑体并解决负号显示问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 计算每个类型的平均分数
average_scores = df.groupby('类型')['评分'].mean().sort_values(ascending=False)

# 创建一个新的DataFrame来保存平均分数
average_scores_df = average_scores.reset_index()

# 将结果写入新的Excel文件
output_file = '1905type_average_scores.xlsx'
average_scores_df.to_excel(output_file, index=False)
print(f"Average scores written to {output_file}")
# 打印结果以检查
# print(average_scores)

# 设置绘图风格
# sns.set(style="whitegrid")
#
#
# # 创建一个水平条形图
# plt.figure(figsize=(10, 8))
# ax = sns.barplot(x=average_scores.values, y=average_scores.index, palette="viridis")
#
# # 添加数值标签
# for i, v in enumerate(average_scores.values):
#     ax.text(v + 0.05, i, f'{v:.2f}', color='black', va='center')
#
# # 添加标题和标签
# plt.title('各类型的平均评分', fontsize=16)
# plt.xlabel('平均评分', fontsize=14)
# plt.ylabel('类型', fontsize=14)
#
# # 显示图表
# plt.tight_layout()
# plt.show()