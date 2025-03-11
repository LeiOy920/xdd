import pandas as pd
import requests
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import csv
import re
import pandas as pd
import requests
from lxml import etree


def getData():
    list = []
    name = []
    img = []
    yname = []
    bname = []
    dir = []
    year = []
    area = []
    lab = []
    score = []
    num = []
    summary = []
    rank = []
    r = 1
    for i in range(0, 10):
        page = i * 25
        url = f'https://movie.douban.com/top250?start={str(page)}'

        headers = {
            "user-agent":
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0",
            "cookie":
                "bid=Vao2KNHFCpA; _pk_id.100001.4cf6=a2be222050247838.1739859935.; __yadk_uid=bHFMIy1oWpg88fIproxBuD8Pqdhfyt7n; ll=\"118318\"; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1740560028%2C%22https%3A%2F%2Fcn.bing.com%2F%22%5D; _pk_ses.100001.4cf6=1; ap_v=0,6.0"
        }

        resp = requests.get(url=url, headers=headers)
        resp.encoding = 'utf-8'
        html = resp.text

        soup = BeautifulSoup(html, 'lxml')

        lis = soup.find('ol', class_='grid_view').find_all('li')
        for li in lis:
            rank.append(str(r))
            r += 1

            影片名 = li.find('div', class_='hd').find_all('span', class_='title')[0].text.strip()
            name.append(影片名)
            # print(影片名)
            # break
            影片图片 = li.find('div', class_='pic').a.img['src']
            img.append(影片图片)
            # 去除无关字符串
            titles = li.find('div', class_='hd').find_all('span', class_='title')
            if len(titles) > 1:  # 确保有足够的 span 标签
                电影英文名 = titles[1].text.strip()
            else:
                电影英文名 = "无英文名"
            电影英文名 = re.sub(r'\/|\xa0', '', 电影英文名)
            yname.append(电影英文名)

            电影别名 = li.find('div', class_='hd').find('span', class_='other').text
            电影别名 = re.sub(r'\/|\xa0', '', 电影别名)
            bname.append(电影别名)

            导演 = li.find('div', class_='bd').p.text.split('/')[0].split(':')[1].split(';')[0].split('\xa0')[0]
            dir.append(导演)
            年份 = li.find('div', class_='bd').p.text
            年份 = re.search(r'\d{4}', 年份).group()
            year.append(年份)
            # 这个也是导演
            # 年份 = li.find('div', class_='bd').p.text.split('\xa0')[0]

            # 地区 = li.find('div', class_='bd').p.text.split('<br>')[1].split('\xa0')[1].split('\xa0')[1].split('\xa0')[0].lstrip(';')
            # 标签 = li.find('div', class_='bd').p.text.split('<br>')[1].split('\xa0')[1].split('\xa0')[1].split('\xa0')[1].split('\xa0')[1].lstrip(';')

            地区 = li.find('div', class_='bd').p.text.split('\n')[2].split('/')[1].lstrip(';').strip()
            # 地区 = li.find('div', class_='bd').p.text.split('\n')[2]
            #         1994 / 美国 / 犯罪 剧情

            area.append(地区)
            标签 = li.find('div', class_='bd').p.text.split('\n')[2].split('/')[2].lstrip(';').strip()
            lab.append(标签)

            评分 = li.find('div', class_='bd').find('span', class_='rating_num').text
            score.append(评分)
            评分人数 = li.find('div', class_='bd').find('div', class_='star').find_all('span')[3].text
            评分人数 = re.findall(r'\d+', 评分人数)
            num.append(评分人数)

            ps = li.find('div', class_='bd').find_all('p')
            if len(ps) > 1:  # 确保有足够的 span 标签
                概况 = ps[1].span.text
            else:
                概况 = "无"
            # 概况 = li.find('div', class_='bd').find_all('p')[1].span.text
            summary.append(概况)

    for j in range(len(name)):
        list.append(
            [rank[j],name[j], img[j], yname[j], bname[j], dir[j], year[j], area[j], lab[j], score[j], num[j], summary[j]])

    df = pd.DataFrame(list,
                      columns=['排名','影片名', '影片图片', '电影英文名', '电影别名', '导演', '年份', '地区', '标签', '评分',
                               '评价人数',
                               '概况'])
    # 保存到Excel文件
    df.to_excel('豆瓣250_1.xlsx', index=False)
    # df.to_csv('豆瓣250_1.csv',encoding='utf-8',index=False)


if __name__ == '__main__':
    getData()
