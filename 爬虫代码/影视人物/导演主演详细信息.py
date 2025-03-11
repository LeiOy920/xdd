import re
import pandas as pd
import requests
from lxml import etree
from bs4 import BeautifulSoup
import csv
import re
import pandas as pd
import requests

df = pd.read_csv('D:\python_project\shixun\pythonProject02\movie5\主演链接.csv')
data = []
姓名 = []
性别 = []
星座 = []
出生日期 = []
出生地=[]
for index, row in df.iterrows():
    url = row['链接']
    print(f"正在爬取: {url}")
    headers = {
        "user-agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0"
    }

    resp = requests.get(url=url, headers=headers)
    resp.encoding = 'utf-8'
    html = resp.text
    soup = BeautifulSoup(html, 'lxml')

    div= soup.find('div',class_='celebrity-wrap')
    姓名.append(div.find('div',class_='celebrity').find('div',class_='intro').find('span',class_='cn-name').text.strip())
    性别.append(div.find('div',class_='intro-wrap').find('div',class_='props').find_all('span')[0].text.strip())

    spans = div.find('div',class_='intro-wrap').find('div',class_='props').find_all('span')
    if len(spans)>1:
        星座.append(spans[1].text.strip())
    else:
        星座.append('')

    # 星座.append(div.find('div',class_='intro-wrap').find('div',class_='props').find_all('span')[1].text.strip())
    spans1= div.find('div',class_='intro-wrap').find('div',class_='born').find_all('span')
    if len(spans1)>0:
        出生日期.append(spans1[0].text.strip())
    else:
        出生日期.append('')
    # 出生日期.append(div.find('div',class_='intro-wrap').find('div',class_='born').find_all('span')[0].text.strip())
    if len(spans1)>1:
        出生地.append(spans1[1].text.strip())
    else:
        出生地.append('')

    # 出生地.append(div.find('div',class_='intro-wrap').find('div',class_='born').find_all('span')[1].text.strip())

# print(姓名)
# print(性别)
# print(星座)

for i in range(len(姓名)):
    data.append([姓名[i], 性别[i], 星座[i], 出生日期[i], 出生地[i]])

df = pd.DataFrame(data, columns=['姓名', '性别', '星座', '出生日期', '出生地'])
df.to_csv('主演详细信息.csv', encoding='utf-8',index=False)
