# 网址：https://piaofang.maoyan.com/rankings/year

import csv
import random
import time
import requests
import parsel


def get_one():
    print(f'----------------------正在采集年的数据----------------------')

    headers = {

        "Sec-Fetch-Site": "same-origin",
        "Uid": "8dfd9b45c82013f7cc1d5aee48987679adf6120b",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.95 Safari/537.36",

    }
    url = "https://piaofang.maoyan.com/rankings/year"
    params = {
        "year": f"",
        "limit": "100",
        "tab": "3",
        "WuKongReady": "h5"
    }
    response = requests.get(url, headers=headers)

    response_txt = response.text
    parsel_txt = parsel.Selector(response_txt)

    uls = parsel_txt.css('ul.row')

    for ul in uls[1:]:
        lis = ul.css('li')
        rank = lis[0].css('::text').get()
        name = lis[1].css('.first-line::text').get()  # 片名
        time_ = lis[1].css('.second-line::text').get()  # 上映时间
        put_time = time_.split(' ')[0]
        box_office = lis[2].css('::text').get()  # 票房(万元)
        average_fare = lis[3].css('::text').get()  # 平均票价
        average_person = lis[4].css('::text').get()  # 场均人次
        dic = {
            '排名': rank,
            '片名': name,
            '上映时间': put_time,
            '票房(万元)': box_office,
            '平均票价': average_fare,
            '场均人次': average_person,
        }
        print(dic)
        csv_write.writerow(dic)


if __name__ == '__main__':
    f = open('movie_全部1.csv', mode='w', encoding='utf-8', newline='')
    csv_write = csv.DictWriter(f, [
        '排名',
        '片名',
        '上映时间',
        '票房(万元)',
        '平均票价',
        '场均人次',
    ])
    csv_write.writeheader()

    year_list = [i for i in range(2011, 2026)]
    # for year in year_list:
    #     get_one(year)
    #     time.sleep(random.uniform(2, 5))

    get_one()
    print('采集结束')
    f.close()
