import pandas as pd
from scipy.stats import linregress

# 读取Excel文件中的数据
file_path = '历年票房及2025预测.xlsx'
df = pd.read_excel(file_path, sheet_name='Sheet1')

# 打印原始数据以检查
print("原始数据：")
print(df)

# 假设我们通过观察或统计方法确定2020年为异常值，并将其从数据中移除
df_cleaned = df[df['年份'] != 2020]

# 显示清理后的数据
print("\n清理后的数据：")
print(df_cleaned)

# 提取用于预测的数据
years = df_cleaned['年份'].values
box_office = df_cleaned['票房'].values

# 使用线性回归模型进行拟合
slope, intercept, r_value, p_value, std_err = linregress(years, box_office)

# 预测2025年的票房
predicted_2025_box_office = slope * 2025 + intercept

print(f"\n预测2025年的票房为: {predicted_2025_box_office:.2f}亿元")

# 计算R平方值，评估模型拟合度
r_squared = r_value ** 2
print(f"模型的R平方值为: {r_squared:.2f}")

# 如果需要更详细的分析，可以打印出更多关于模型的信息
print(f"斜率: {slope:.2f}, 截距: {intercept:.2f}")