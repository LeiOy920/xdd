# 2.3 电影搜索API
from flask import request, jsonify, Blueprint

from app.config import connect_to_elasticsearch

ess = Blueprint('ess', __name__)

es = connect_to_elasticsearch()
@ess.route('/search', methods=['GET'])
def search_movies():
    query = request.args.get('query', '')
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 10))
    from_val = (page - 1) * size

    # 基本搜索查询
    search_query = {
        "from": from_val,
        "size": size,
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["movie_name", "director", "screenwriter", "starring", "also_known_as"]
            }
        },
        "highlight": {
            "fields": {
                "movie_name": {},
                "director": {},
                "screenwriter": {},
                "starring": {},
                "also_known_as": {}
            }
        }
    }
    result = es.search(index="movie_detail", body=search_query)

    hits = result["hits"]["hits"]
    total = result["hits"]["total"]["value"]

    movies = []
    for hit in hits:
        movie = hit["_source"]

        # 添加高亮信息
        if "highlight" in hit:
            movie["highlights"] = hit["highlight"]

        movies.append(movie)

    return jsonify({
        "results": movies,
        "total": total,
        "page": page,
        "pages": (total + size - 1) // size
    })