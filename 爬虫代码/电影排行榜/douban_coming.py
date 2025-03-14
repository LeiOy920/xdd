import re
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
from lxml import etree
import os

import random

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
url ='https://movie.douban.com/coming'
coming =[]
resp = requests.get(url=url, headers=headers)
time.sleep(random.uniform(1, 4))  # 每次请求间隔 1 秒
resp.encoding = 'UTF-8'
html = resp.text
soup = BeautifulSoup(html, 'lxml')
trs = soup.find('tbody').find_all('tr')
if trs is not None:
   for tr in trs:
       tds = tr.find_all('td')
       releasetime = tds[0].string.strip()
       url = tds[1].find('a')['href']
       name = tds[1].find('a').string.strip()
       type = tds[2].string.strip().replace("/", " ")
       area = tds[3].string.strip()
       followers = tds[4].string.split('人')[0].strip()
       coming.append({
           '上映时间': releasetime,
           '连接': url,
           '名字': name,
           '类型': type,
           '地区': area,
           '想看': followers
       })
df = pd.DataFrame(coming)
output_file = 'douban_coming.xlsx'
df.to_excel(output_file, index=False, engine='openpyxl')

