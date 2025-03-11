# -*- coding:utf-8 -*-
#  @Time : 2017-11-28 10:52
#  @File : wordcloud_generate.py
#  @Description:
import os
from wordcloud import WordCloud
import jieba
import matplotlib.pyplot as plt

# 定义停用词
stopwords = [',', '。', '【', '】', '”', '“', '，', '《', '》', '！', '、', '？', '.', '…', '1', '2', '3', '4', '5', '[',
             ']', '（', '）', ' ']

all_final_words_flt = []

# 遍历comment1.txt至comment250.txt
for i in range(251, 371):
    file_path = f"../豆瓣短评/comments{i}.txt"
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f_comment:
            words = []
            for line in f_comment.readlines():
                if len(line) == 12:
                    continue
                A = jieba.cut(line)
                words.append(" ".join(A))

            # 去除停用词
            new_words = []
            for sent in words:
                word_in = sent.split(' ')
                new_word_in = []
                for word in word_in:
                    if word in stopwords:
                        continue
                    else:
                        new_word_in.append(word)
                new_sent = " ".join(new_word_in)
                new_words.append(new_sent)

            final_words = []
            for sent in new_words:
                sent = sent.split(' ')
                final_words += sent

            final_words_flt = []
            for word in final_words:
                if word == ' ':
                    continue
                else:
                    final_words_flt.append(word)

            all_final_words_flt.extend(final_words_flt)

text = " ".join(all_final_words_flt)