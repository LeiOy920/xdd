import requests
from lxml import etree
import pandas as pd

df = []
# 注：猫眼电影有时要滑块验证，所以print打印出来为猫眼验证中心,要先登录网址通过滑块验证
# base_url = 'https://maoyan.com/board/4?offset={}'
base_url = 'https://www.maoyan.com/board/4?requestCode=1741052670834-169005405-7180756&offset={}'
headers = {
    'Cookie': '__mta=219119526.1740624104403.1740988148028.1740988166727.20; _lxsdk_cuid=19544e63cb2c8-062decdeba796d-4c657b58-e1000-19544e63cb2c8; uuid_n_v=v1; uuid=60B574D0F4B411EF9B764BD6646CBC938A06EA74585D41CDB967675CD0B5DCBF; _ga=GA1.1.403183281.1740624104; ci=292%2C%E5%8C%97%E6%B5%B7; __mta=244039226.1740624247535.1740660566448.1740660610270.6; featrues=[object Object]; _csrf=92c8b55bb31550cf197252bc7618943528b16438dd49ce30e7cee8fa96bca87a; theme=moviepro; selectci=true; _lxsdk=550431B0F4DE11EFB003BDBE4561AA1222CC5347ABAA4687B341C467D4DA668C; _lx_utm=utm_source%3Dbing%26utm_medium%3Dorganic; _ga_WN80P4PSY7=GS1.1.1741015814.16.0.1741015814.0.0.0; _lxsdk_s=1955eb153bb-93-d92-b7e%7C%7C1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0'
}
columns = ['排名', '片名', '主演', '上映时间', '评分','链接']
paiming = []
pianming = []
zhuyan = []
shijian = []
score = []
链接 = []

for i in range(10):
    url = base_url.format(str(i * 10))
    response = requests.get(url, headers=headers)
    html = response.text
    xp = etree.HTML(html)

    # 查找每个电影条目，使用正确的 XPath 表达式
    dds = xp.xpath('//dl/dd')  # 这里可能需要根据网页的具体结构调整 XPath

    for dd in dds:
        paiming = dd.xpath('i/text()')[0]
        pianming = dd.xpath('.//div[@class="movie-item-info"]/p[1]/a/text()')[0]
        zhuyan = dd.xpath('.//div[@class="movie-item-info"]/p[2]/text()')[0].replace("主演：", "").strip() if dd.xpath(
            './/div[@class="movie-item-info"]/p[2]/text()') else ''
        shijian = dd.xpath('.//div[@class="movie-item-info"]/p[3]/text()')[0].replace("上映时间：",
                                                                                      "").strip() if dd.xpath(
            './/div[@class="movie-item-info"]/p[3]/text()') else ''
        score1 = dd.xpath('.//div[@class="movie-item-number score-num"]/p/i[1]/text()')[0]
        score2 = dd.xpath('.//div[@class="movie-item-number score-num"]/p/i[2]/text()')[0]
        score = score1 + score2
        链接 = dd.xpath('.//div[@class="movie-item-info"]/p[1]/a/@href')[0]

        # 将数据追加到df中
        df.append([paiming, pianming, zhuyan, shijian, score,链接])

# 将所有数据保存到 CSV 文件中，放在循环外面
d = pd.DataFrame(df, columns=columns)
d.to_csv("猫眼电影_链接.csv", index=False)
print("爬取并保存完成！")
