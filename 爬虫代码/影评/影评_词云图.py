# 生成词云
import os.path
from wordcloud import WordCloud, ImageColorGenerator
import matplotlib.pyplot as plt
import imageio.v2 as imageio

font = 'D:/A_软件实训工具/FZSTJW.ttf'
bk = imageio.imread("pure_gold_image.png")  # 设置背景文件
# comment_file = '../豆瓣短评/comments251.txt'
# wordcloud_file = '豆瓣短评词云/word_cloud251.png'
for i in range(0,1097):
    comment_file = '../豆瓣短评/comments' + str(i) + '.txt'
    wordcloud_file = '豆瓣短评词云/word_cloud_gold' + str(i) + '.png'
    # 检查词云图片是否已存在
    if not os.path.exists(wordcloud_file):
        if os.path.exists(comment_file):
            with open(comment_file, 'r', encoding='utf-8') as file:
                text = file.read()
                # 检查文件内容是否为空
                if text.strip():
                    wc = WordCloud(collocations=False, mask=bk, font_path=font, width=1400, height=1400,
                                   margin=2).generate(
                        text.lower())
                    image_colors = ImageColorGenerator(bk)  # 读取背景文件色彩
                    plt.imshow(wc.recolor(color_func=image_colors))
                    wc.to_file(wordcloud_file)
                    print(wordcloud_file + 'ok!')
                else:
                    print(comment_file + '是空的')