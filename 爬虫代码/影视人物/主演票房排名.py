from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service  # 导入 Service 类
from bs4 import BeautifulSoup
import pandas as pd
import time

# 设置 Edge 浏览器驱动路径
edge_driver_path = "D:\shixun_install\webdriver\edgedriver_win64\msedgedriver.exe"  # 替换为你的 Edge WebDriver 路径

# 设置 Edge 浏览器路径
edge_binary_path = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"  # 替换为你的 Edge 浏览器路径

# 初始化 Edge 浏览器
options = webdriver.EdgeOptions()
options.binary_location = edge_binary_path  # 指定 Edge 浏览器路径
options.add_argument("--headless")  # 无头模式（不显示浏览器界面）

# 使用 Service 类指定驱动路径
service = Service(executable_path=edge_driver_path)
driver = webdriver.Edge(service=service, options=options)

# 打开目标网页
url = "https://m.maoyan.com/asgard/celebrity/boxrank/0?ci=292"
driver.get(url)

# 等待页面加载
# time.sleep(3)
time.sleep(10)

# 模拟滚动加载
# scroll_pause_time = 2  # 每次滚动后的等待时间
scroll_pause_time = 10  # 每次滚动后的等待时间
scroll_count = 15  # 滚动次数（根据数据量调整）

for _ in range(scroll_count):
    # 滚动到页面底部
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scroll_pause_time)

# 获取页面源码
html = driver.page_source

# 使用 BeautifulSoup 解析页面
soup = BeautifulSoup(html, 'lxml')

# 提取数据
divs = soup.find('div', class_='page-content box-rank-page').find_all('a')
data = []

rank = []
name = []
work = []
money = []
num = []
r = 1

链接= []
for div in divs:
    rank.append(str(r))
    r += 1

    链接.append(div['href'])
    name.append(div.find('div', class_='name text-ellipsis').text.strip())
    work.append(div.find('div', class_='work text-ellipsis').text.strip())
    value = div.find('div', class_='box-box').find('span', class_='box').text.strip()
    unit = div.find('div', class_='box-box').find('span', class_='unit').text.strip()
    money.append(f"{value}")
    num.append(div.find('div', class_='box-box').find('span', class_='num').text.strip())

# 将数据存储到 DataFrame
for i in range(len(name)):
    data.append([链接[i],rank[i], name[i], work[i], money[i], num[i]])

df = pd.DataFrame(data, columns=['链接','排名', '主演名称', '代表作', '票房', '作品数'])
df.to_csv('主演链接.csv', encoding='utf-8', index=False)

# 关闭浏览器
driver.quit()