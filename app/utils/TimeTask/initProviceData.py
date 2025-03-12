import random
import time
from apscheduler.schedulers.background import BackgroundScheduler
import requests
from bs4 import BeautifulSoup



def getProviceBox():
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
    url1 = 'https://zgdypf.zgdypw.cn/cinema?tab=3&selectedId1=0&selectedId2=0'
    box = []
    resp = requests.get(url=url1, headers=headers1)
    time.sleep(random.uniform(1, 3))  # 每次请求间隔 1 秒
    resp.encoding = 'UTF-8'
    html1 = resp.text
    soup = BeautifulSoup(html1, 'lxml')

    trs = soup.find('div', class_='tiny-table-content').find('tbody').find_all('tr')
    for tr in trs:
        tds = tr.find_all('td')
        name = tds[0].find('span', class_='table-cell-content').string
        today_box = tds[1].find('span').string
        if today_box.endswith('万'):
            today_box = str(today_box).split('万')[0]
        elif today_box.endswith('亿'):
            today_box = float(str(today_box).split('万')[0]) * 10000
        else:
            today_box = float(today_box)/10000
        box.append({
            'province': name,
            'today_box': today_box
        })
    print(box)
    return box