import re
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
from lxml import etree
import os
import random
movies = []
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
]


headers = {
    'User-Agent': random.choice(user_agents),
    'path':'/pmcnox/zomqdg.htm?uvck=MjYxOWU3NWNjZDhiOTBlYWNlYmZjMTdiNTA1OTQ0MGU%3D&uv7=bWNfXzZl&uv8=bWNtbXRhbWltZGFudF9fMTdhZTk0ODA1ZGE5Yw%3D%3D&uv9=bWNtOTZtdHFtZW5kaW90eW9fXzhlNTAzNzc5NTYzYTgyYTEx&uva=c2JfX21jX19tYw%3D%3D&uvb=YXIwX19tY21fX21jbg%3D%3D&uvc=Mjc2&uv5=bWNfXzE3&uv6=bWNvZGVtOW45ZW1fXzQwNjQwODc2OTM4&uvd=aHR0cHM6Ly9tb3ZpZS5kb3ViYW4uY29tL2NpbmVtYS9sYXRlci9sZXNoYW4v&uve=NQ%3D%3D',
    'referer' :'https://www.maoyan.com/board/4?timeStamp=1740636613286&sVersion=1&offset=0&index=5&webdriver=false&signKey=bf3e348533859a45dbe9614e5cab9fa1&channelId=40011&requestCode=1740640364554-169003076-8074661'
}

countrys = {'China':'中国', 'USA': '美国', 'France': '法国', 'Thailand': '泰国', 'India': '印度',
           'Germany': '德国', 'Sweden': '瑞典', 'Norway': '挪威', 'Vietnam': '越南', 'Iran': '伊朗',
           'Cuba': '古巴', 'Greece': '希腊', 'Brazil': '巴西', 'CzechRepublic': '捷克', 'Poland': '波兰',
           'Netherlands': '荷兰', 'Russia': '俄罗斯', 'Italy': '意大利', 'Mexico': '墨西哥',
           'NewZealand': '新西兰', 'Austria': '奥地利','NorthKorea': '朝鲜', 'Malaysia': '马来西亚',
           'Singapore': '新加坡', 'Portugal': '葡萄牙', 'Australia': '澳大利亚', 'Ukraine': '乌克兰',
           'Egypt': '埃及', 'Qatar': '卡塔尔', 'Argentina': '阿根廷', 'Iceland': '冰岛', 'Belgium': '比利时',
           'Denmark': '丹麦', 'Finland': '芬兰', 'Philippines': '菲律宾', 'Croatia': '克罗地亚', 'Morocco': '摩洛哥',
           'Peru': '秘鲁', 'Nepal': '尼泊尔', 'Switzerland': '瑞士', 'Spain': '西班牙', 'Israel': '以色列'
           }
for key, value in countrys.items():
    url = f'https://www.1905.com/mdb/film/list/country-{str(key)}/d0o1.html'
    resp = requests.get(url=url, headers=headers)
    # time.sleep(random.uniform(1, 4))  # 每次请求间隔 1 秒
    resp.encoding = 'UTF-8'
    html = resp.text
    soup = BeautifulSoup(html, 'lxml')
    lis = soup.find('ul',class_='inqList').find_all('li')[0:10]
    if lis is not None:
     num= 0
     for li in lis:
       num = num+1
       img_url= li.find('img')['src']
       ps=li.find_all('p')
       name = ps[0].string.strip()
       scorepre = ps[1].find('b')
       if scorepre is not None:
           score = scorepre.string.strip()
       else:
           score = '无评分'
       movies.append({
           '国家':value,
           '排名':num,
           '名字':name,
           '评分':score
       })
df = pd.DataFrame(movies)
output_file = '1905country10.xlsx'
df.to_excel(output_file, index=False, engine='openpyxl')

