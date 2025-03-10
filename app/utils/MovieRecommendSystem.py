import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.models.moviedetail import MovieDetail


'''
这个推荐系统使用的是基于内容的推荐方法（Content-Based Recommendation），具体实现上采用了文本特征提取和向量相似度计算的技术组合。主要包括以下关键技术：

TF-IDF向量化：使用了sklearn的TfidfVectorizer将电影的各种文本特征（导演、类型、主演等）转换为数值向量。TF-IDF能够计算词语在文档中的重要性，同时考虑词频和逆文档频率。
余弦相似度：使用cosine_similarity计算电影之间的相似度。余弦相似度测量的是两个向量在多维空间中的夹角余弦值，值越接近1表示越相似。
特征加权：在advanced推荐方法中，系统对不同特征（类型、导演、主演、国家、语言）分别计算TF-IDF矩阵，然后根据用户指定的权重计算加权相似度，这允许用户调整不同特征对推荐结果的影响程度。

这种方法的优点是不需要用户行为数据，只需要电影的元数据就可以工作，适合冷启动场景。与协同过滤不同，它不依赖于用户评分或行为模式，而是直接分析电影本身的内容特征来找出相似的电影。
'''

class MovieRecommendationSystem:
    def __init__(self):
        """
        初始化电影推荐系统
        """
        self.movies_df = None
        self.tfidf_matrices = {}  # 存储不同特征的TF-IDF矩阵
        self.cosine_sims = {}  # 存储不同特征的余弦相似度
        self.indices = None

    def load_data_from_db(self):
        """从数据库加载电影数据"""
        # 从数据库查询电影数据
        movies = MovieDetail.query.all()

        # 将结果转换为DataFrame
        self.movies_df = pd.DataFrame([movie.__dict__ for movie in movies])
        print(f"加载了 {len(self.movies_df)} 部电影数据")

        return True

    def preprocess_data(self):
        """预处理数据，为推荐做准备"""
        if self.movies_df is None:
            print("请先加载数据")
            return False

        # 处理缺失值
        self.movies_df['director'] = self.movies_df['director'].fillna('')
        self.movies_df['screenwriter'] = self.movies_df['screenwriter'].fillna('')
        self.movies_df['starring'] = self.movies_df['starring'].fillna('')
        self.movies_df['genre'] = self.movies_df['genre'].fillna('')
        self.movies_df['production_country_region'] = self.movies_df['production_country_region'].fillna('')
        self.movies_df['language'] = self.movies_df['language'].fillna('')

        # 创建内容特征
        self.movies_df['content'] = (
                self.movies_df['director'] + ' ' +
                self.movies_df['screenwriter'] + ' ' +
                self.movies_df['starring'] + ' ' +
                self.movies_df['genre'] + ' ' +
                self.movies_df['production_country_region'] + ' ' +
                self.movies_df['language']
        )

        # 创建TF-IDF向量化器和计算不同特征的相似度矩阵
        tfidf = TfidfVectorizer(stop_words='english')

        # 计算整体内容的TF-IDF矩阵
        self.tfidf_matrices['content'] = tfidf.fit_transform(self.movies_df['content'])

        # 计算整体内容的余弦相似度
        self.cosine_sims['content'] = cosine_similarity(self.tfidf_matrices['content'], self.tfidf_matrices['content'])

        # 为不同特征计算单独的TF-IDF矩阵
        features = {
            'genre': 'genre',
            'director': 'director',
            'country': 'production_country_region',
            'starring': 'starring',
            'language': 'language'
        }

        for feature_name, column in features.items():
            feature_tfidf = TfidfVectorizer(stop_words='english')
            self.tfidf_matrices[feature_name] = feature_tfidf.fit_transform(self.movies_df[column])
            self.cosine_sims[feature_name] = cosine_similarity(
                self.tfidf_matrices[feature_name],
                self.tfidf_matrices[feature_name]
            )

        # 创建电影名称到索引的映射
        self.movies_df.reset_index(drop=True, inplace=True)
        self.indices = pd.Series(self.movies_df.index, index=self.movies_df['movie_name'])

        return True

    def get_recommendations(self, movie_name, top_n=10):
        """
        基于电影名称推荐类似电影

        Args:
            movie_name: 电影名称
            top_n: 推荐数量

        Returns:
            推荐电影列表
        """
        # 检查电影是否在数据集中
        if movie_name not in self.indices:
            print(f"电影 '{movie_name}' 不在数据库中")
            return []

        # 获取电影索引
        idx = self.indices[movie_name]

        # 获取相似度分数
        sim_scores = list(enumerate(self.cosine_sims['content'][idx]))

        # 按相似度排序
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # 获取前N个相似电影索引（排除自身）
        sim_scores = sim_scores[1:top_n + 1]
        movie_indices = [i[0] for i in sim_scores]

        # 返回推荐结果，包含相似度分数
        recommendations = []
        for i, movie_idx in enumerate(movie_indices):
            movie_data = self.movies_df.iloc[movie_idx].to_dict()
            movie_data['similarity_score'] = sim_scores[i][1]
            recommendations.append(movie_data)

        return recommendations

    def get_recommendations_by_id(self, movie_id, top_n=10):
        """
        基于电影ID推荐类似电影

        Args:
            movie_id: 电影ID
            top_n: 推荐数量

        Returns:
            推荐电影列表
        """
        # 查找电影
        movie_row = self.movies_df[self.movies_df['id'] == movie_id]

        if movie_row.empty:
            print(f"电影ID '{movie_id}' 不在数据库中")
            return []

        # 获取电影名称
        movie_name = movie_row['movie_name'].iloc[0]

        # 使用名称获取推荐
        return self.get_recommendations(movie_name, top_n)

    def get_recommendations_advanced(self, movie_id, genre_weight=1.0, director_weight=0.8,
                                     starring_weight=0.7, country_weight=0.5, language_weight=0.3, top_n=10):
        """
        高级推荐，允许调整不同特征的权重

        Args:
            movie_id: 电影ID
            genre_weight: 类型权重
            director_weight: 导演权重
            starring_weight: 主演权重
            country_weight: 国家/地区权重
            language_weight: 语言权重
            top_n: 推荐数量

        Returns:
            推荐电影列表
        """
        # 查找电影
        movie_row = self.movies_df[self.movies_df['id'] == movie_id]

        if movie_row.empty:
            print(f"电影ID '{movie_id}' 不在数据库中")
            return []

        # 获取电影索引
        movie_idx = movie_row.index[0]

        # 准备权重字典
        weights = {
            'genre': genre_weight,
            'director': director_weight,
            'starring': starring_weight,
            'country': country_weight,
            'language': language_weight
        }

        # 计算加权相似度
        weighted_sim = np.zeros_like(self.cosine_sims['content'][movie_idx])
        weight_sum = sum(weights.values())

        # 归一化权重并计算加权相似度
        for feature, weight in weights.items():
            if weight > 0 and feature in self.cosine_sims:
                normalized_weight = weight / weight_sum
                weighted_sim += normalized_weight * self.cosine_sims[feature][movie_idx]

        # 创建相似度得分列表
        sim_scores = list(enumerate(weighted_sim))

        # 按相似度排序
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # 获取前N个相似电影索引（排除自身）
        sim_scores = [score for score in sim_scores if score[0] != movie_idx][:top_n]
        movie_indices = [i[0] for i in sim_scores]

        # 返回推荐结果，包含相似度分数
        recommendations = []
        for i, movie_idx in enumerate(movie_indices):
            movie_row = self.movies_df.iloc[movie_idx]
            movie_data = {
                'id': int(movie_row['id']),
                'movie_name': str(movie_row['movie_name']),
                'movie_image': str(movie_row['movie_image']),
                'director': str(movie_row['director']),
                'screenwriter': str(movie_row['screenwriter']),
                'starring': str(movie_row['starring']),
                'genre': str(movie_row['genre']),
                'douban_rating': str(movie_row['douban_rating']),
                'release_date': str(movie_row['release_date']),
                'production_country_region': str(movie_row['production_country_region']),
                'language': str(movie_row['language']),
                'similarity_score': float(sim_scores[i][1])
            }
            recommendations.append(movie_data)

        return recommendations