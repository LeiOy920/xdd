import re
import pandas as pd
import requests
from lxml import etree
from bs4 import BeautifulSoup
import csv
import re
import pandas as pd
import requests

url = f"https://m.maoyan.com/asgard/celebrity/boxrank/1"
headers = {
    "user-agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0",
    "cookie":
        "_lxsdk_cuid=19544e63cb2c8-062decdeba796d-4c657b58-e1000-19544e63cb2c8; _ga=GA1.1.403183281.1740624104; uuid_n_v=v1; iuuid=550431B0F4DE11EFB003BDBE4561AA1222CC5347ABAA4687B341C467D4DA668C; webp=true; selectci=true; selectci=true; selectci=true; ci=292%2C%E5%8C%97%E6%B5%B7; ci=292%2C%E5%8C%97%E6%B5%B7; ci=292%2C%E5%8C%97%E6%B5%B7; featrues=[object Object]; _last_page=c_movie_epshkvsz; _lxsdk=550431B0F4DE11EFB003BDBE4561AA1222CC5347ABAA4687B341C467D4DA668C; _lx_utm=utm_source%3Dbing%26utm_medium%3Dorganic; _ga_WN80P4PSY7=GS1.1.1740645042.3.1.1740645247.0.0.0; _lxsdk_s=1954687887a-885-cca-910%7C%7C54"

}


resp = requests.get(url=url, headers=headers)
resp.encoding = 'utf-8'
html = resp.text
soup = BeautifulSoup(html, 'lxml')
print(soup)

divs = soup.find('div', class_='page-content box-rank-page').find_all('a')
data = []

rank = []
name = []
work = []
money = []
num =[]
r = 1
for div in divs:
    rank.append(str(r))
    r += 1

    name.append(div.find('div', class_='name text-ellipsis').text.strip())
    work.append(div.find('div', class_='work text-ellipsis').text.strip())
    value = div.find('div', class_='box-box').find('span', class_='box').text.strip()
    unit = div.find('div', class_='box-box').find('span', class_='unit').text.strip()
    money.append(f"{value}{unit}")
    num.append(div.find('div', class_='box-box').find('span', class_='num').text.strip())



for i in range(len(name)):
    data.append([rank[i], name[i], work[i], money[i],num[i]])

df = pd.DataFrame(data, columns=['排名', '导演名称', '代表作', '票房','作品数'])
df.to_csv('导演票房排名2.csv', encoding='utf-8')