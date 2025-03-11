import time
import requests
import pandas as pd
import pymysql
from bs4 import BeautifulSoup

# 配置数据库连接
db_config = {
    "host": "192.168.58.41",  # 你的 MySQL 服务器地址
    "user": "root",
    "password": "123456",
    "database": "moviedb",
    "charset": "utf8mb4"
}

# 目标 URL
url = "https://piaofang.maoyan.com/i/globalBox/historyRank"
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0"
}


def fetch_data():
    """爬取网页数据"""
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'lxml')

    divs = soup.find('div', class_='list-content').find_all('div', class_='movie-item')
    data = []

    rank = 1
    for div in divs:
        name = div.find('div', class_='movie-rank').find('div', class_='movie-name').text.strip()
        year = div.find('div', class_='movie-year').text.strip()
        money = div.find('div', class_='movie-money').find('div').text.rstrip('亿').strip()
        排行榜类型 = '全球票房榜'
        data.append((rank, name, year, money, 排行榜类型))
        rank += 1

    return data


def update_database(data):
    """将数据存入 MySQL，并检查是否需要更新"""
    try:
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()

        for rank, name, year, money, 排行榜类型 in data:
            # 查询是否存在 id 在 1~20 之间的电影
            cursor.execute("SELECT id FROM rankings WHERE id BETWEEN 1 AND 20")
            result = cursor.fetchall()
            existing_ids = {row[0] for row in result}  # 提取已有的 id

            if rank in existing_ids:
                # 如果 id 在 1~20 之间，更新数据
                sql = """
                        UPDATE rankings 
                        SET movie_name=%s, r_rank=%s, quantity=%s, ranking_type=%s
                        WHERE id=%s
                """
                cursor.execute(sql, (name, rank, money, 排行榜类型, rank))
            else:
                # 如果 id 超过 20 或不存在，则插入新数据
                sql = """
                            INSERT INTO rankings (movie_name, r_rank, quantity, ranking_type)
                            VALUES (%s, %s, %s, %s)
                            """
                cursor.execute(sql, (name, rank, money, 排行榜类型))

        connection.commit()
        cursor.close()
        connection.close()
        print("数据库已更新")

    except Exception as e:
        print("数据库操作失败:", e)


if __name__ == "__main__":
    while True:
        print("开始爬取...")
        movie_data = fetch_data()
        print("爬取完成，开始更新数据库...")
        update_database(movie_data)
        print("等待 60 秒后进行下一次爬取...")
        time.sleep(60)  # 等待 60 秒
