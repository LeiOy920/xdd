import re
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
from lxml import etree
from datetime import date
import random
import csv
from fake_useragent import UserAgent  # ⽣成随机User-Agent以避免被识别为⾃动化脚本
import json
import openpyxl
from sqlalchemy import create_engine,text

while True:
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",

    ]
    headers1 = {
        'User-Agent': random.choice(user_agents),
        'path': '/pmcnox/zomqdg.htm?uvck=MjYxOWU3NWNjZDhiOTBlYWNlYmZjMTdiNTA1OTQ0MGU%3D&uv7=bWNfXzZl&uv8=bWNtbXRhbWltZGFudF9fMTdhZTk0ODA1ZGE5Yw%3D%3D&uv9=bWNtOTZtdHFtZW5kaW90eW9fXzhlNTAzNzc5NTYzYTgyYTEx&uva=c2JfX21jX19tYw%3D%3D&uvb=YXIwX19tY21fX21jbg%3D%3D&uvc=Mjc2&uv5=bWNfXzE3&uv6=bWNvZGVtOW45ZW1fXzQwNjQwODc2OTM4&uvd=aHR0cHM6Ly9tb3ZpZS5kb3ViYW4uY29tL2NpbmVtYS9sYXRlci9sZXNoYW4v&uve=NQ%3D%3D',
        'referer': 'https://zgdypf.zgdypw.cn/',
        'Cookie': '__jsluid_s=c146af2c1875226bb4d18675a900b9b0; Hm_lvt_d7c7037093938390bc160fc28becc542=1741164317; HMACCOUNT=785A3CB4CCB7A011; Hm_lpvt_d7c7037093938390bc160fc28becc542=1741165868'
    }
    url1 = 'https://zgdypf.zgdypw.cn/box'
    box = []
    resp = requests.get(url=url1, headers=headers1)
    time.sleep(random.uniform(1, 3))  # 每次请求间隔 1 秒
    resp.encoding = 'UTF-8'
    html1 = resp.text
    soup = BeautifulSoup(html1, 'lxml')
    total_box = soup.find('div', class_='box-data').get_text().split('万')[0]
    box.append({
        'movie_name': '总票房',
        'today_box': total_box
    })
    trs = soup.find('div', class_='tiny-table-content').find('tbody').find_all('tr')
    for tr in trs:
        tds = tr.find_all('td')
        name = tds[0].find('p', class_='movie-name').string
        today_box = tds[1].find('span').string
        if today_box != '<0.1':
            box.append({
                'movie_name': name,
                'today_box': today_box
            })
    time.sleep(10)
    ua = UserAgent()
    today = date.today().strftime("%Y%m%d")
    headers = {'User-Agent': ua.random}
    url = f'https://piaofang.maoyan.com/dashboard-ajax/movie?showDate={today}&orderType=0&uuid=19540ec141fc8-0080115b3239ee-4c657b58-13c680-19540ec141fc8&timeStamp=1740711822981&User-Agent=TW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEzMy4wLjAuMCBTYWZhcmkvNTM3LjM2IEVkZy8xMzMuMC4wLjA%3D&index=869&channelId=40009&sVersion=2&signKey=e5b890af79dce01106cb717257e0b0a3&WuKongReady=h5'
    response = requests.get(url, headers=headers)
    html = response.text
    data = json.loads(html)
    data = data["movieList"]["list"]


    for cbo_data in data:
        # 上座率数据
        movieName = cbo_data['movieInfo']['movieName']
        for movie in box:
            if movieName in movie.values():
                avgSeatView = cbo_data['avgSeatView']
                # 场均人次
                avgShowView = cbo_data['avgShowView']
                # 票房占比
                boxRate = cbo_data['boxRate']
                # 电影名称
                movieName = cbo_data['movieInfo']['movieName']
                # 上映时间
                releaseInfo = cbo_data['movieInfo']['releaseInfo']
                showCount = cbo_data['showCount']
                # 排片占比
                showCountRate = cbo_data['showCountRate']

                # # 趋势数据记录
                # movieId = cbo_data['movieInfo']['movieId']
                # # time.sleep(10)
                # url01 = f'https://piaofang.maoyan.com/dashboard-ajax/movie?movieId={movieId}&orderType=0&uuid=19540ec141fc8-0080115b3239ee-4c657b58-13c680-19540ec141fc8&timeStamp=1741232869142&User-Agent=TW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEzMy4wLjAuMCBTYWZhcmkvNTM3LjM2IEVkZy8xMzMuMC4wLjA%3D&index=587&channelId=40009&sVersion=2&signKey=31942602dfbd7122202d6917a53a6ac7&WuKongReady=h5'
                # response01 = requests.get(url01, headers=headers)
                # html01 = response01.text
                # data01 = json.loads(html01)
                # data01 = data01["movieInfo"]["boxTrends"]


                # 因为有时会出错，出错则每隔10s自动刷新直到正确,最多刷新2次
                max_retries = 2
                retry_delay = 10
                for attempt in range(max_retries):
                    try:
                        movieId = cbo_data['movieInfo']['movieId']
                        url01 = f'https://piaofang.maoyan.com/dashboard-ajax/movie?movieId={movieId}&orderType=0&uuid=19540ec141fc8-0080115b3239ee-4c657b58-13c680-19540ec141fc8&timeStamp=1741232869142&User-Agent=TW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEzMy4wLjAuMCBTYWZhcmkvNTM3LjM2IEVkZy8xMzMuMC4wLjA%3D&index=587&channelId=40009&sVersion=2&signKey=31942602dfbd7122202d6917a53a6ac7&WuKongReady=h5'
                        response01 = requests.get(url01, headers=headers)
                        if response01.status_code == 200:
                            html01 = response01.text
                            data01 = json.loads(html01)
                            data01 = data01["movieInfo"]["boxTrends"]
                            break
                    except KeyError:
                        print(f"第 {attempt + 1} 次尝试{url01}，数据结构异常，重新请求...")
                    time.sleep(retry_delay)
                if attempt == max_retries - 1:
                    data01 = []
                    print(f"将{url01}的票房趋势设置为[]数据")

                # 定义字典的键
                # keys = ['day_4', 'day_3', 'day_2', 'day_1','day_0']
                keys = ['day_0', 'day_1', 'day_2', 'day_3', 'day_4']
                # 字典推导式初始化字典
                trends = {key: 0 for key in keys}
                # 遍历 data 列表，将 boxDesc 值依次赋给对应的键
                for i, item in enumerate(data01):
                    if i < len(keys):
                        if str(item["boxDesc"]).endswith("万"):
                            trends[keys[len(data01) - i - 1]] = str(item["boxDesc"]).split('万')[0]
                        elif str(item["boxDesc"]).endswith("亿"):
                            trends[keys[len(data01) - i - 1]] = float(str(item["boxDesc"]).split('亿')[0])*10000
                        else:
                            trends[keys[len(data01) - i - 1]] = float(item["boxDesc"])/10000

                movie['day4_box'] = (trends['day_4'])
                movie['day3_box'] = (trends['day_3'])
                movie['day2_box'] = (trends['day_2'])
                movie['day1_box'] = (trends['day_1'])
                try:
                    # 综合票房
                    sumBoxDesc = cbo_data['sumBoxDesc']
                except KeyError as e:
                    # 综合票房
                    sumBoxDesc = '无数据'
                movie['proportion'] = boxRate
                movie['slots_num'] = showCount
                movie['slots_proportion'] = showCountRate
                movie['release_days'] = releaseInfo
                movie['average_person'] = avgShowView
                movie['occupancy_rate'] = avgSeatView
                movie['total_box'] = sumBoxDesc

    df = pd.DataFrame(box)
    subset = df.iloc[1:]
    cleaned_subset = subset.dropna()
    cleaned_df = pd.concat([df.iloc[:1], cleaned_subset], ignore_index=True)
    print(cleaned_df)
    # 指定要保存的 Excel 文件路径
    engine = create_engine("mysql://root:123456@192.168.58.41/moviedb")
    truncate_statement = text("TRUNCATE TABLE box_timely")
    # 将 DataFrame 写入 Excel 文件
    with engine.connect() as connection:
        connection.execute(truncate_statement)
    cleaned_df.to_sql('box_timely', con=engine, if_exists='append', index=False)
    time.sleep(60)