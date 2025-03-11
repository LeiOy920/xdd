import time

import requests
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from lxml.html import etree
from bs4 import BeautifulSoup
import pandas as pd
import os
import re
import random
from selenium.webdriver.edge.service import Service

data = []
链接 = []
片名 = []
英文名 = []
年份 = []
导演 = []
编剧 = []
主演 = []
类型 = []
地区 = []
语言 = []
图片 = []
片长 = []
评分 = []
简介 = []


class Movie():
    def __init__(self, name):
        self.url = f'https://search.douban.com/movie/subject_search?search_text={name}'


    def get_movie_info(self, movie):
        # 在影片详情页面提取影片基本信息
        name = movie[0]  # 影片名字
        print(f'正在爬取：{name}')
        url = movie[1]  # 影片链接url

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0',
            'Cookie':'_pk_id.100001.4cf6=a2be222050247838.1739859935.; __yadk_uid=bHFMIy1oWpg88fIproxBuD8Pqdhfyt7n; ll="118318"; push_noty_num=0; push_doumail_num=0; bid=hKR2pe-PUwQ; dbcl2="154327675:h0Zm/8iKAzA"; ck=amkj; frodotk_db="4343d7927f5bfa42c9cb86b77e13eec6"; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1741656224%2C%22https%3A%2F%2Fsearch.douban.com%2Fmovie%2Fsubject_search%3Fsearch_text%3D%E6%AD%BB%E4%BA%A1%E4%B9%8B%E9%9B%AA2%26cat%3D1002%22%5D; _pk_ses.100001.4cf6=1'
        }
        resp = requests.get(url, headers=headers)
        resp.encoding = 'utf-8'
        html = resp.text
        soup = BeautifulSoup(html, 'lxml')
        链接.append(url)
        div = soup.find('div', id='content')
        # print(div)
        片名.append(div.find('h1').find('span').text.split(' ')[0])
        英文名s = div.find('h1').find('span').text.split(' ')
        if len(英文名s) > 1:
            英文名.append(' '.join(英文名s[1:]))
        else:
            英文名.append(' ')


        年份.append(div.find('h1').find('span', class_='year').text.strip('()'))
        图片.append(div.find('div', class_='subject clearfix').find('div', id='mainpic').find('a').find('img')['src'])
        # 导演.append(div.find('div', class_='subject clearfix').find('div', id='info').find_all('span')[0].find('span',class_='attrs').find('a').text.strip())
        # 编剧.append(div.find('div', class_='subject clearfix').find('div', id='info').find_all('span',recursive=False)[1].find('span', class_='attrs').find('a').text.strip())

        director_span = div.find('div', class_='subject clearfix').find('div', id='info').find('span', class_='pl', string='导演')
        if director_span:
            导演.append(director_span.find_next('span', class_='attrs').get_text(strip=True))
        else:
            导演.append(None)
        writer_span = div.find('div', class_='subject clearfix').find('div', id='info').find('span', class_='pl', string='编剧')
        if writer_span:
            编剧.append(writer_span.find_next('span', class_='attrs').get_text(strip=True))
        else:
            编剧.append(None)

        # 主演0 = div.find('div', class_='subject clearfix').find('div', id='info').find_all('span',recursive=False)[2].find('span',class_='attrs').find_all('span')[0].find('a').text.strip()
        # 主演0 = div.find('div', class_='subject clearfix').find('div', id='info').find_all('span',recursive=False)[2].find('span',class_='attrs').find_all('a')[0].text.strip()
        # 主演1 = div.find('div', class_='subject clearfix').find('div', id='info').find_all('span',recursive=False)[2].find('span',class_='attrs').find_all('a')[1].text.strip()
        # 主演2 = div.find('div', class_='subject clearfix').find('div', id='info').find_all('span',recursive=False)[2].find('span',class_='attrs').find_all('a')[2].text.strip()
        # 主演.append(主演0 + ' ' + 主演1 + ' ' + 主演2)
        actor_span = div.find('div', class_='subject clearfix').find('div', id='info').find('span', class_='pl', string='主演')
        if actor_span:
            actors = actor_span.find_next('span', class_='attrs').find_all('a')
            max_actors = 3  # 可以根据需要调整
            actor_names = [actor.text.strip() for actor in actors[:max_actors]]
            主演.append(' '.join(actor_names))
        else:
            主演.append(None)

        类型s = div.find('div', class_='subject clearfix').find('div', id='info').find_all('span',property='v:genre')
        类型 .append(' '.join([span.text.strip() for span in 类型s]))
        地区.append(div.find('div', class_='subject clearfix').find('div', id='info').find('span',string="制片国家/地区:").next_sibling.strip())
        语言s = div.find('div', class_='subject clearfix').find('div', id='info').find('span',string="语言:")
        if 语言s:
            语言.append(语言s.next_sibling.strip())
        else:
            语言.append(None)
        # 片长.append(div.find('div', class_='subject clearfix').find('div', id='info').find('span',property='v:runtime').text.strip())
        片长数字 = div.find('div', class_='subject clearfix').find('div', id='info').find('span',property='v:runtime')
        if 片长数字:
            片长.append(re.search(r'\d+', 片长数字.text.strip()).group())
        else:
            片长数字 = div.find('div', class_='subject clearfix').find('div', id='info').find('span',class_='pl', string='片长')
            if 片长数字:
                片长.append(re.search(r'\d+', 片长数字.text.strip()).group())
            else:
                片长.append(None)

        评分0 = div.find('div', id='interest_sectl')
        if 评分0:
            评分.append(div.find('div', id='interest_sectl').find('div', class_='rating_self clearfix').find('strong').text.strip())
        else:
            评分.append(' ')
        # 简介0 = div.find('div', class_='indent')
        # if 简介0:
        #     简介.append(div.find('div', class_='indent').find('span').text.strip())
        # else:
        #     简介.append('无')


def main():
    影片名称 = []
    # df = pd.read_csv(r'D:\python_project\shixun\pythonProject02\movie8\地图电影_豆瓣id.csv')
    # df = pd.read_csv(r'D:\python_project\shixun\pythonProject02\movie7\国内总榜详情\temp.csv')

    temp_df = pd.read_csv(r'D:\python_project\shixun\pythonProject02\movie8\地图电影_豆瓣id.csv')
    detail_df = pd.read_csv(r'D:\python_project\shixun\pythonProject02\movie8\地图电影详情.csv')

    # 找出 temp.csv 中有但 地图详情.csv 中没有的 豆瓣id
    temp_names = set(temp_df['movie_name'])
    detail_names = set(detail_df['影片名称'])
    names_to_crawl = temp_names - detail_names

    # 过滤出需要爬取的行
    df_to_crawl = temp_df[temp_df['movie_name'].isin(names_to_crawl)]


    # output_file = '国内总榜详情2_2.csv'
    output_file1 = '地图电影详情1.csv'
    # file_exists = os.path.exists(output_file)  # 检查文件是否已存在
    file_exists1 = os.path.exists(output_file1)  # 检查文件是否已存在

    for index, row in df_to_crawl.iterrows():
        name = row['movie_name']
        url = 'https://movie.douban.com/subject/' + str(row['豆瓣id']) + '/'
        # url = 'https://movie.douban.com/subject/1994562/'
        print(f'当前搜索：{url}')
        影片名称.append(name)

        # try:
        m = Movie(name)
        # movies = m.get_search()  # 得到搜索结果
        movies = [[name, url]]

        num = 0  # 选择第一个搜索结果
        m.get_movie_info(movies[num])
        print(len(影片名称), len(链接), len(片名), len(英文名), len(年份), len(导演),
              len(编剧), len(主演), len(类型), len(地区), len(语言), len(图片), len(片长), len(评分))
        movie_data = [[影片名称[-1], 链接[-1], 片名[-1], 英文名[-1], 年份[-1], 导演[-1], 编剧[-1], 主演[-1], 类型[-1], 地区[-1], 语言[-1], 图片[-1], 片长[-1], 评分[-1]]]

        df_temp = pd.DataFrame(movie_data, columns=['影片名称', '链接', '片名', '英文名', '年份', '导演', '编剧', '主演', '类型', '地区', '语言', '图片', '片长', '评分'])
        # df_temp = pd.DataFrame(movie_data1, columns=['影片名称', '链接', '片名'])
        df_temp.to_csv(output_file1, mode='a', encoding='utf-8', index=False, header=not file_exists1)

        file_exists1 = True  # 确保后续写入时不再写入表头
        delay = random.uniform(2, 10)
        time.sleep(delay)
        # # 提示用户输入任意字符继续
        # user_input = input("按回车键继续，或输入 'q' 退出：")
        # if user_input.lower() == 'q':
        #     print("用户主动退出程序。")
        #     break  # 退出循环

        # except Exception as e:
        #     print(f"爬取 {name} 失败，错误信息：{e}")
        #     continue  # 继续爬取下一个电影
        # break

if __name__ == '__main__':
    main()
