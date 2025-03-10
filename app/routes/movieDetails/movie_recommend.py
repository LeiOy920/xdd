from flask import Blueprint, request, jsonify

from app.config import app
from app.utils.MovieRecommendSystem import MovieRecommendationSystem

# 创建Flask Blueprint
mr_blueprint = Blueprint('mr', __name__)

@mr_blueprint.record_once
def initialize_recommender(state):
    """在第一个请求之前初始化推荐系统"""
    global recommender
    with app.app_context():
        recommender = MovieRecommendationSystem()
        recommender.load_data_from_db()
        recommender.preprocess_data()
        print("电影推荐系统已初始化")


@mr_blueprint.route('/recommend', methods=['GET'])
def recommend_movies():
    """基本推荐API"""
    movie_name = request.args.get('movie_name')
    top_n = request.args.get('top_n', default=10, type=int)

    if not movie_name:
        return jsonify({"error": "请提供电影名称参数 'movie_name'"}), 400

    recommendations = recommender.get_recommendations(movie_name, top_n)

    return jsonify({
        "movie_name": movie_name,
        "recommendations": recommendations
    })

@mr_blueprint.route('/recommend-by-id', methods=['GET'])
def recommend_movies_by_id():
    """基于ID的推荐API"""
    movie_id = request.args.get('movie_id', type=int)
    top_n = request.args.get('top_n', default=10, type=int)

    if not movie_id:
        return jsonify({"error": "请提供电影ID参数 'movie_id'"}), 400

    recommendations = recommender.get_recommendations_by_id(movie_id, top_n)

    return jsonify({
        "movie_id": movie_id,
        "recommendations": recommendations
    })


@mr_blueprint.route('/recommend-advanced', methods=['GET'])
def recommend_movies_advanced():
    """高级推荐API，支持特征权重调整"""
    movie_id = request.args.get('movie_id', type=int)
    top_n = request.args.get('top_n', default=10, type=int)

    # 获取权重参数
    genre_weight = request.args.get('genre_weight', default=1.0, type=float)
    director_weight = request.args.get('director_weight', default=0.8, type=float)
    starring_weight = request.args.get('starring_weight', default=0.7, type=float)
    country_weight = request.args.get('country_weight', default=0.5, type=float)
    language_weight = request.args.get('language_weight', default=0.3, type=float)

    if not movie_id:
        return jsonify({"error": "请提供电影ID参数 'movie_id'"}), 400

    recommendations = recommender.get_recommendations_advanced(
        movie_id,
        genre_weight=genre_weight,
        director_weight=director_weight,
        starring_weight=starring_weight,
        country_weight=country_weight,
        language_weight=language_weight,
        top_n=top_n
    )

    return jsonify({
        "movie_id": movie_id,
        "weights": {
            "genre": genre_weight,
            "director": director_weight,
            "starring": starring_weight,
            "country": country_weight,
            "language": language_weight
        },
        "recommendations": recommendations
    })


# 使用示例
if __name__ == "__main__":
    with app.app_context():
        # 初始化推荐系统
        recommender = MovieRecommendationSystem()

        # 加载数据
        if recommender.load_data_from_db():
            # 预处理数据
            recommender.preprocess_data()

            # 获取推荐
            movie_name = "一一"  # 示例电影名
            recommendations = recommender.get_recommendations(movie_name, top_n=5)

            print(f"与《{movie_name}》类似的电影推荐:")
            for i, movie in enumerate(recommendations, 1):
                print(f"{i}. {movie['movie_name']} - 相似度: {movie['similarity_score']:.2f}")