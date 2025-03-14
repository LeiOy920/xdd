import pandas as pd

# 读取Excel文件
file_path = 'douban_coming.xlsx'
df = pd.read_excel(file_path)

# 初始化字典用于存储每种类型的总想看人数和出现次数
type_counts = {}
type_want_to_watch_sum = {}

# 遍历每一行数据
for index, row in df.iterrows():
    types = row['类型'].split()  # 按空格分割类型
    want_to_watch = row['想看']

    for movie_type in types:
        if movie_type not in type_counts:
            type_counts[movie_type] = 0
            type_want_to_watch_sum[movie_type] = 0

        type_counts[movie_type] += 1
        type_want_to_watch_sum[movie_type] += want_to_watch

# 计算每种类型的平均想看人数
average_want_to_watch_per_type = {movie_type: type_want_to_watch_sum[movie_type] / type_counts[movie_type]
                                  for movie_type in type_counts}

# 将结果转换为DataFrame
result_df = pd.DataFrame(average_want_to_watch_per_type.items(), columns=['类型', '平均想看人数'])

# 将结果写入新的Excel文件，注意是tyep不是type，因为第一次上传MinIO时就不小心写错了，于是一错再错吧。
output_file_path = 'coming_tyep.xlsx'
result_df.to_excel(output_file_path, index=False)

print(f"结果已成功写入到文件: {output_file_path}")