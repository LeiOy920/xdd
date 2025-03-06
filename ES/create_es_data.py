# """
# 电影大数据分析项目 - Elasticsearch整合方案
# 架构: Vue + Flask + MySQL + Elasticsearch
# """
#
# # 1. 安装和配置
#
# ## 1.1 安装Elasticsearch
# # 下载: https://www.elastic.co/downloads/elasticsearch
# # 或使用Docker:
# # docker
# # run - d - -name
# # elasticsearch - p
# # 9200: 9200 - p
# # 9300: 9300 - e
# # "discovery.type=single-node"
# # elasticsearch: 7.14
# # .0
#
# ## 1.2 Python依赖
# # pip install elasticsearch flask-elasticsearch pymysql
#
# # 2. Flask应用中整合Elasticsearch
#
# from flask import Flask, request, jsonify
# from elasticsearch import Elasticsearch
# import pymysql
# import json
#
# app = Flask(__name__)
#
# # 连接到Elasticsearch
# es = Elasticsearch(["http://localhost:9200"])
#
#
# # 连接到MySQL
# def get_mysql_connection():
#     return pymysql.connect(
#         host="localhost",
#         user="your_username",
#         password="your_password",
#         database="movie_database",
#         charset="utf8mb4"
#     )
#
#
# # 2.1 初始化索引 - 创建电影索引并定义映射
# @app.route('/api/init_index', methods=['POST'])
# def init_elasticsearch_index():
#     # 创建电影索引 - 只需执行一次
#     index_name = "movies"
#
#     # 如果索引已存在则删除
#     if es.indices.exists(index=index_name):
#         es.indices.delete(index=index_name)
#
#     # 定义索引映射
#     mapping = {
#         "mappings": {
#             "properties": {
#                 "id": {"type": "integer"},
#                 "title": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart"},
#                 "original_title": {"type": "text", "analyzer": "ik_max_word"},
#                 "overview": {"type": "text", "analyzer": "ik_max_word"},
#                 "release_date": {"type": "date"},
#                 "popularity": {"type": "float"},
#                 "vote_average": {"type": "float"},
#                 "vote_count": {"type": "integer"},
#                 "genres": {"type": "keyword"},
#                 "director": {"type": "keyword"},
#                 "actors": {"type": "keyword"},
#                 "poster_path": {"type": "keyword"}
#             }
#         }
#     }
#
#     # 创建索引
#     es.indices.create(index=index_name, body=mapping)
#
#     return jsonify({"message": "Index created successfully"}), 200
#
#
# # 2.2 从MySQL导入数据到Elasticsearch
# @app.route('/api/import_data', methods=['POST'])
# def import_data_to_elasticsearch():
#     conn = get_mysql_connection()
#     cursor = conn.cursor(pymysql.cursors.DictCursor)
#
#     # 从MySQL获取电影数据
#     cursor.execute("""
#         SELECT m.id, m.title, m.original_title, m.overview, m.release_date,
#                m.popularity, m.vote_average, m.vote_count, m.poster_path,
#                GROUP_CONCAT(DISTINCT g.name) AS genres,
#                GROUP_CONCAT(DISTINCT c.name ORDER BY c.order LIMIT 5) AS actors,
#                d.name AS director
#         FROM movies m
#         LEFT JOIN movie_genre mg ON m.id = mg.movie_id
#         LEFT JOIN genres g ON mg.genre_id = g.id
#         LEFT JOIN movie_cast c ON m.id = c.movie_id AND c.cast_type = 'actor'
#         LEFT JOIN movie_crew d ON m.id = d.movie_id AND d.job = 'Director'
#         GROUP BY m.id
#         LIMIT 10000
#     """)
#
#     movies = cursor.fetchall()
#
#     # 批量导入Elasticsearch
#     bulk_data = []
#     for movie in movies:
#         # 处理日期格式
#         if movie['release_date']:
#             movie['release_date'] = movie['release_date'].strftime('%Y-%m-%d')
#
#         # 处理演员和类型数组
#         if movie['genres']:
#             movie['genres'] = movie['genres'].split(',')
#         else:
#             movie['genres'] = []
#
#         if movie['actors']:
#             movie['actors'] = movie['actors'].split(',')
#         else:
#             movie['actors'] = []
#
#         # 添加到批量操作
#         bulk_data.append({
#             "index": {
#                 "_index": "movies",
#                 "_id": movie['id']
#             }
#         })
#         bulk_data.append(movie)
#
#     # 执行批量导入
#     if bulk_data:
#         es.bulk(body=bulk_data)
#
#     cursor.close()
#     conn.close()
#
#     return jsonify({"message": f"Imported {len(movies)} movies to Elasticsearch"}), 200
#
#
# # 2.3 电影搜索API
# @app.route('/api/search', methods=['GET'])
# def search_movies():
#     query = request.args.get('query', '')
#     page = int(request.args.get('page', 1))
#     size = int(request.args.get('size', 10))
#     from_val = (page - 1) * size
#
#     # 基本搜索查询
#     search_query = {
#         "from": from_val,
#         "size": size,
#         "query": {
#             "bool": {
#                 "should": [
#                     {"match": {"title": {"query": query, "boost": 3}}},
#                     {"match": {"original_title": {"query": query, "boost": 2}}},
#                     {"match": {"overview": {"query": query, "boost": 1}}},
#                     {"match": {"director": {"query": query, "boost": 2}}},
#                     {"match": {"actors": {"query": query, "boost": 1.5}}}
#                 ],
#                 "minimum_should_match": 1
#             }
#         },
#         "highlight": {
#             "fields": {
#                 "title": {},
#                 "overview": {}
#             }
#         }
#     }
#
#     # 添加过滤条件
#     genre = request.args.get('genre')
#     year = request.args.get('year')
#     min_rating = request.args.get('min_rating')
#
#     filter_clauses = []
#
#     if genre:
#         filter_clauses.append({"term": {"genres": genre}})
#
#     if year:
#         filter_clauses.append({
#             "range": {
#                 "release_date": {
#                     "gte": f"{year}-01-01",
#                     "lte": f"{year}-12-31"
#                 }
#             }
#         })
#
#     if min_rating:
#         filter_clauses.append({
#             "range": {
#                 "vote_average": {
#                     "gte": float(min_rating)
#                 }
#             }
#         })
#
#     if filter_clauses:
#         search_query["query"]["bool"]["filter"] = filter_clauses
#
#     # 执行搜索
#     result = es.search(index="movies", body=search_query)
#
#     # 处理并返回结果
#     hits = result["hits"]["hits"]
#     total = result["hits"]["total"]["value"]
#
#     movies = []
#     for hit in hits:
#         movie = hit["_source"]
#
#         # 添加高亮信息
#         if "highlight" in hit:
#             movie["highlights"] = hit["highlight"]
#
#         movies.append(movie)
#
#     return jsonify({
#         "results": movies,
#         "total": total,
#         "page": page,
#         "pages": (total + size - 1) // size
#     })
#
#
# # 2.4 高级搜索API
# @app.route('/api/advanced_search', methods=['POST'])
# def advanced_search():
#     data = request.get_json()
#
#     page = data.get('page', 1)
#     size = data.get('size', 10)
#     from_val = (page - 1) * size
#
#     # 构建高级查询
#     search_query = {
#         "from": from_val,
#         "size": size,
#         "query": {
#             "bool": {
#                 "must": [],
#                 "should": [],
#                 "filter": []
#             }
#         }
#     }
#
#     # 处理查询条件
#     if 'title' in data and data['title']:
#         search_query["query"]["bool"]["should"].append(
#             {"match": {"title": {"query": data['title'], "boost": 3}}}
#         )
#
#     if 'content' in data and data['content']:
#         search_query["query"]["bool"]["should"].append(
#             {"match": {"overview": {"query": data['content'], "boost": 1}}}
#         )
#
#     # 类型过滤
#     if 'genres' in data and data['genres']:
#         search_query["query"]["bool"]["filter"].append(
#             {"terms": {"genres": data['genres']}}
#         )
#
#     # 年份范围
#     if 'year_from' in data or 'year_to' in data:
#         year_range = {"range": {"release_date": {}}}
#
#         if 'year_from' in data and data['year_from']:
#             year_range["range"]["release_date"]["gte"] = f"{data['year_from']}-01-01"
#
#         if 'year_to' in data and data['year_to']:
#             year_range["range"]["release_date"]["lte"] = f"{data['year_to']}-12-31"
#
#         search_query["query"]["bool"]["filter"].append(year_range)
#
#     # 评分范围
#     if 'rating_from' in data or 'rating_to' in data:
#         rating_range = {"range": {"vote_average": {}}}
#
#         if 'rating_from' in data and data['rating_from'] is not None:
#             rating_range["range"]["vote_average"]["gte"] = data['rating_from']
#
#         if 'rating_to' in data and data['rating_to'] is not None:
#             rating_range["range"]["vote_average"]["lte"] = data['rating_to']
#
#         search_query["query"]["bool"]["filter"].append(rating_range)
#
#     # 导演或演员
#     if 'person' in data and data['person']:
#         search_query["query"]["bool"]["should"].extend([
#             {"match": {"director": {"query": data['person'], "boost": 2}}},
#             {"match": {"actors": {"query": data['person'], "boost": 1.5}}}
#         ])
#
#     # 确保应该匹配至少一个should子句
#     if len(search_query["query"]["bool"]["should"]) > 0:
#         search_query["query"]["bool"]["minimum_should_match"] = 1
#
#     # 排序
#     if 'sort' in data and data['sort']:
#         sort_field = data['sort']
#         sort_order = data.get('order', 'desc')
#
#         # 添加排序
#         search_query["sort"] = [{sort_field: {"order": sort_order}}]
#
#     # 执行搜索
#     result = es.search(index="movies", body=search_query)
#
#     # 处理并返回结果
#     hits = result["hits"]["hits"]
#     total = result["hits"]["total"]["value"]
#
#     movies = []
#     for hit in hits:
#         movie = hit["_source"]
#         movie["score"] = hit["_score"]
#         movies.append(movie)
#
#     return jsonify({
#         "results": movies,
#         "total": total,
#         "page": page,
#         "pages": (total + size - 1) // size
#     })
#
#
# if __name__ == '__main__':
#     app.run(debug=True)


import pymysql

from app.config import connect_to_elasticsearch

es = connect_to_elasticsearch()


# 2.1 初始化索引 - 创建电影索引并定义映射
def init_elasticsearch_index():
    # 创建电影索引 - 只需执行一次
    index_name = "movie_detail"

    # 如果索引已存在则删除
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)

    # 定义索引映射
    mapping = {
                "mappings": {
                    "properties": {
                        "id": {"type": "integer"},
                        "movie_image": {"type": "text"},
                        "movie_name": {"type": "text", "analyzer": "standard", "search_analyzer": "standard"},
                        "director": {"type": "text", "analyzer": "standard"},
                        "screenwriter": {"type": "text", "analyzer": "standard"},
                        "starring": {"type": "text", "analyzer": "standard"},
                        "genre": {"type": "text", "analyzer": "standard"},
                        "production_country_region": {"type": "text", "analyzer": "standard"},
                        "language": {"type": "text", "analyzer": "standard"},
                        "release_date": {"type": "integer"},
                        "runtime": {"type": "integer"},
                        "also_known_as": {"type": "text", "analyzer": "standard"},
                        "douban_rating": {"type": "float"},
                        "review_file_path": {"type": "text"}
                    }
                }
    }

    # 创建索引
    es.indices.create(index=index_name, body=mapping)

    print({"message": "Index created successfully"})


# 2.2 从MySQL导入数据到Elasticsearch
def import_data_to_elasticsearch():
    conn = pymysql.connect(host="localhost", port=3306, user="root", password="123456", database="moviedb")
    cursor = conn.cursor()
    sql = "select * from moviedetail"
    cursor.execute(sql)
    results = cursor.fetchall()

    # 批量导入Elasticsearch
    bulk_data = []
    for row in results:
        # 添加到批量操作
        bulk_data.append({
            "index": {
                "_index": "movie_detail",
                "_id": row[0]
            }
        })
        message = {
            "id": row[0],
            "movie_image": row[1],
            "movie_name": row[2],
            "director": row[3],
            "screenwriter": row[4],
            "starring": row[5],
            "genre": row[6],
            "production_country_region": row[7],
            "language": row[8],
            "release_date": row[9],
            "runtime": row[10],
            "also_known_as": row[11],
            "douban_rating": row[12],
            "review_file_path": row[13]
        }
        bulk_data.append(message)

    # 执行批量导入
    if bulk_data:
        es.bulk(body=bulk_data)

    cursor.close()
    conn.close()

    print({"message": f"Imported {len(results)} movies to Elasticsearch"})


if __name__ == "__main__":
    init_elasticsearch_index()
    import_data_to_elasticsearch()





